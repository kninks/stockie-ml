import hashlib
import logging
import os
import pickle
from typing import Optional

import numpy as np
import requests
from tensorflow.keras.models import load_model

from app.api.schemas.predict_schema import (
    InferenceResultSchema,
    PredictRequestSchema,
)
from app.core.common.utils.time_logger import log_end, log_start

logger = logging.getLogger(__name__)


class PredictService:
    _model_cache = {}
    _scaler_cache = {}

    _active_model = None
    _active_model_url = None

    _active_scaler = None
    _active_scaler_url = None

    def __init__(self):
        pass

    async def predict(
        self, request: PredictRequestSchema
    ) -> list[InferenceResultSchema]:
        start_time, task = log_start(
            f"Request prediction for {len(request.stocks)} stocks"
        )
        response_list = []

        for stock in request.stocks:
            try:
                predicted = await self.predict_one(
                    close=stock.close,
                    model_path=stock.model_path,
                    scaler_path=stock.scaler_path,
                    volumes=stock.volumes,
                    days_ahead=request.days_ahead,
                )
                response_list.append(
                    InferenceResultSchema(
                        stock_ticker=stock.stock_ticker,
                        predicted_price=predicted,
                        success=True,
                        error_message=None,
                    )
                )
            except Exception as e:
                response_list.append(
                    InferenceResultSchema(
                        stock_ticker=stock.stock_ticker,
                        predicted_price=None,
                        success=False,
                        error_message=str(e),
                    )
                )

        log_end(start_time, task)
        return response_list

    async def predict_one(
        self,
        days_ahead: int,
        model_path: str,
        scaler_path: str,
        close: list[float],
        volumes: Optional[list[int]] = None,
    ) -> list[float]:
        await self.load_model_with_cache(model_url=model_path)
        await self.load_scaler_with_cache(scaler_url=scaler_path)

        normalized_trading_data = await self.normalize_trading_data(
            close=close, volumes=volumes
        )
        normalized_predicted_price = await self.run_inference(
            normalized_trading_data=normalized_trading_data,
            days_ahead=days_ahead,
        )
        predicted = await self.denormalize_prices(normalized_predicted_price)

        return predicted

    @staticmethod
    def _cached_path_from_url(url: str) -> str:
        ext = ".keras" if url.endswith(".keras") else ".h5"
        hashed = hashlib.md5(url.encode()).hexdigest()
        return f"/tmp/{hashed}{ext}"

    async def load_model_with_cache(self, model_url: str) -> None:
        using_cache = model_url in self._model_cache
        task = f"Loading model ({'cache' if using_cache else 'download'}): {model_url}"
        start_time, task = log_start(task)

        if not (model_url.endswith(".keras") or model_url.endswith(".h5")):
            raise ValueError("Invalid model format: must be .keras or .h5")

        if model_url in self._model_cache:
            self._active_model = self._model_cache[model_url]
            self._active_model_url = model_url

            log_end(start_time, task)
            return

        local_path = self._cached_path_from_url(model_url)
        if not os.path.exists(local_path):
            response = requests.get(model_url)
            if response.status_code != 200:
                raise RuntimeError(f"Failed to download model from {model_url}")
            with open(local_path, "wb") as f:
                f.write(response.content)

        model = load_model(local_path)
        self._model_cache[model_url] = model
        self._active_model = model
        self._active_model_url = model_url

        log_end(start_time, task)
        return

    async def load_scaler_with_cache(self, scaler_url: str) -> None:
        using_cache = scaler_url in self._scaler_cache
        task = (
            f"Loading scaler ({'cache' if using_cache else 'download'}): {scaler_url}"
        )
        start_time, task = log_start(task)

        if scaler_url in self._scaler_cache:
            self._active_scaler = self._scaler_cache[scaler_url]
            self._active_scaler_url = scaler_url
            log_end(start_time, task)
            return

        local_path = self._cached_path_from_url(scaler_url)
        if not os.path.exists(local_path):
            response = requests.get(scaler_url)
            if response.status_code != 200:
                raise RuntimeError(f"Failed to download scaler from {scaler_url}")
            with open(local_path, "wb") as f:
                f.write(response.content)

        with open(local_path, "rb") as f:
            scaler = pickle.load(f)

        self._scaler_cache[scaler_url] = scaler
        self._active_scaler = scaler
        self._active_scaler_url = scaler_url

        log_end(start_time, task)
        return

    async def normalize_trading_data(
        self, close: list[float], volumes: Optional[list[int]] = None
    ) -> np.ndarray:
        start_time, task = log_start("Normalizing trading data")

        scaler = self._active_scaler
        if scaler is None:
            raise ValueError("Scaler not loaded.")
        if len(close) < 60 or (volumes and len(volumes) != 60):
            raise ValueError("Need at least 60 data points.")

        num_features = scaler.n_features_in_
        if num_features == 1:
            input_array = np.array(close).reshape(-1, 1)
        elif num_features == 2:
            if not volumes or len(volumes) != 60:
                raise ValueError("Expected 60 volumes.")
            input_array = np.column_stack((close, volumes))
        else:
            raise ValueError(f"Unsupported num_features: {num_features}")

        log_end(start_time, task)
        return scaler.transform(input_array).reshape(1, 60, num_features)

    async def denormalize_prices(self, normalized_prices: list[float]) -> list[float]:
        start_time, task = log_start("Denormalizing prices")

        scaler = self._active_scaler
        if scaler is None:
            raise ValueError("Scaler not loaded.")

        try:
            num_features = scaler.n_features_in_
            padded = np.concatenate(
                [
                    np.array(normalized_prices).reshape(-1, 1),
                    np.zeros((len(normalized_prices), num_features - 1)),
                ],
                axis=1,
            )
        except Exception as e:
            raise RuntimeError(f"Error denormalizing: {e}")

        log_end(start_time, task)
        return scaler.inverse_transform(padded)[:, 0].tolist()

    async def run_inference(
        self, normalized_trading_data: list[list[float]] | np.ndarray, days_ahead: int
    ) -> list[float]:
        start_time, task = log_start("Running inference")

        model = self._active_model
        scaler = self._active_scaler
        if model is None or scaler is None:
            raise ValueError("Model or scaler not loaded.")

        try:
            sequence = np.array(normalized_trading_data).reshape(60, -1)
            predictions = []
            num_features = scaler.n_features_in_

            for _ in range(days_ahead):
                input_seq = sequence[-60:].reshape(1, 60, num_features)
                pred = model.predict(input_seq)
                close_pred = pred[0][0] if pred.ndim == 2 else pred[0]
                predictions.append(close_pred)
                next_input = [close_pred] + [0.0] * (num_features - 1)
                sequence = np.vstack([sequence, next_input])
        except Exception as e:
            raise RuntimeError(f"Inference failed: {e}")

        log_end(start_time, task)
        return predictions

    def get_active_info(self) -> dict:
        return {
            "active_model": self._active_model_url,
            "active_scaler": self._active_scaler_url,
        }

    def get_cache_info(self) -> dict:
        return {
            "cached_models": list(self._model_cache.keys()),
            "cached_scalers": list(self._scaler_cache.keys()),
        }

    def clear_cache(
        self, model_url: Optional[str] = None, scaler_url: Optional[str] = None
    ) -> dict:
        cleared = {"models": [], "scalers": []}

        if model_url:
            if model_url in self._model_cache:
                del self._model_cache[model_url]
                cleared["models"].append(model_url)
        else:
            cleared["models"] = list(self._model_cache.keys())
            self._model_cache.clear()

        if scaler_url:
            if scaler_url in self._scaler_cache:
                del self._scaler_cache[scaler_url]
                cleared["scalers"].append(scaler_url)
        else:
            cleared["scalers"] = list(self._scaler_cache.keys())
            self._scaler_cache.clear()

        logger.warning(f"Cache cleared: {cleared}")
        return cleared


def get_predict_service() -> PredictService:
    return PredictService()
