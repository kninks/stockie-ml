import hashlib
import logging
import os
import pickle
import time
from typing import Optional

import numpy as np
import requests
from tensorflow.keras.models import load_model

from app.api.schemas.predict_schema import (
    InferenceResultSchema,
    PredictRequestSchema,
)
from app.core.common.utils.measurement import send_metric
from app.core.common.utils.time_logger import log_elapsed
from app.core.enums.measurement_enum import (
    MeasurementMetric,
    MeasurementTag,
    MeasurementValue,
)

logger = logging.getLogger(__name__)


class PredictService:
    _model_cache = {}
    _scaler_cache = {}

    def __init__(self):
        pass

    async def predict(
        self, request: PredictRequestSchema
    ) -> list[InferenceResultSchema]:
        start = time.perf_counter()
        response_list = []

        for stock in request.stocks:
            start_stock = time.perf_counter()
            status = MeasurementValue.success
            try:
                predicted = await self.predict_one(
                    close=stock.close,
                    model_path=stock.model_path,
                    scaler_path=stock.scaler_path,
                    volumes=stock.volumes,
                    high=stock.high,
                    low=stock.low,
                    open_p=stock.open,
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
                status = MeasurementValue.fail

            log_elapsed(
                start_time=start_stock,
                category="ML Predict",
                task="All predictions",
                tags=[stock.stock_ticker],
            )

            elapsed = time.perf_counter() - start_stock
            send_metric(
                metric=MeasurementMetric.total_predict_time,
                value=elapsed,
                tags={
                    MeasurementTag.ticker: stock.stock_ticker,
                    MeasurementTag.status: status,
                },
            )

        log_elapsed(start_time=start, category="ML Predict", task="All predictions")

        elapsed = time.perf_counter() - start
        send_metric(
            metric=MeasurementMetric.total_predict_time,
            value=elapsed,
            tags={
                MeasurementTag.ticker: "all",
            },
        )
        return response_list

    async def predict_one(
        self,
        days_ahead: int,
        model_path: str,
        scaler_path: str,
        close: list[float],
        volumes: Optional[list[int]] = None,
        high: Optional[list[float]] = None,
        low: Optional[list[float]] = None,
        open_p: Optional[list[float]] = None,
    ) -> list[float]:
        model = await self.load_model_with_cache(model_url=model_path)
        scaler = await self.load_scaler_with_cache(scaler_url=scaler_path)

        normalized_trading_data = await self.normalize_trading_data(
            scaler=scaler,
            close=close,
            volumes=volumes,
            high=high,
            low=low,
            open_p=open_p,
        )
        normalized_predicted_price = await self.run_inference(
            model=model,
            scaler=scaler,
            normalized_trading_data=normalized_trading_data,
            days_ahead=days_ahead,
        )
        predicted = await self.denormalize_prices(
            scaler=scaler, normalized_prices=normalized_predicted_price
        )

        return predicted

    @staticmethod
    def _cached_path_from_url(url: str) -> str:
        ext = ".keras" if url.endswith(".keras") else ".h5"
        hashed = hashlib.md5(url.encode()).hexdigest()
        return f"/tmp/{hashed}{ext}"

    async def load_model_with_cache(self, model_url: str):
        if not (model_url.endswith(".keras") or model_url.endswith(".h5")):
            raise ValueError("Invalid model format: must be .keras or .h5")

        start = time.perf_counter()

        if model_url in self._model_cache:
            elapsed = time.perf_counter() - start
            send_metric(
                metric=MeasurementMetric.load_time,
                value=elapsed,
                tags={
                    MeasurementTag.status: MeasurementValue.success,
                    MeasurementTag.source: MeasurementValue.cache,
                    MeasurementTag.file_type: MeasurementValue.model,
                },
            )
            return self._model_cache[model_url]

        local_path = self._cached_path_from_url(model_url)
        if not os.path.exists(local_path):
            response = requests.get(model_url)
            if response.status_code != 200:
                elapsed = time.perf_counter() - start
                send_metric(
                    metric=MeasurementMetric.load_time,
                    value=elapsed,
                    tags={
                        MeasurementTag.status: MeasurementValue.fail,
                        MeasurementTag.source: MeasurementValue.download,
                        MeasurementTag.file_type: MeasurementValue.model,
                    },
                )
                raise RuntimeError(f"Failed to download model from {model_url}")
            with open(local_path, "wb") as f:
                f.write(response.content)

        model = load_model(local_path)
        self._model_cache[model_url] = model

        elapsed = time.perf_counter() - start
        send_metric(
            metric=MeasurementMetric.load_time,
            value=elapsed,
            tags={
                MeasurementTag.status: MeasurementValue.success,
                MeasurementTag.source: MeasurementValue.download,
                MeasurementTag.file_type: MeasurementValue.model,
            },
        )

        return model

    async def load_scaler_with_cache(self, scaler_url: str):
        start = time.perf_counter()

        if scaler_url in self._scaler_cache:
            elapsed = time.perf_counter() - start
            send_metric(
                metric=MeasurementMetric.load_time,
                value=elapsed,
                tags={
                    MeasurementTag.status: MeasurementValue.success,
                    MeasurementTag.source: MeasurementValue.cache,
                    MeasurementTag.file_type: MeasurementValue.scaler,
                },
            )
            return self._scaler_cache[scaler_url]

        local_path = self._cached_path_from_url(scaler_url)
        if not os.path.exists(local_path):
            response = requests.get(scaler_url)
            if response.status_code != 200:
                elapsed = time.perf_counter() - start
                send_metric(
                    metric=MeasurementMetric.load_time,
                    value=elapsed,
                    tags={
                        MeasurementTag.status: MeasurementValue.fail,
                        MeasurementTag.source: MeasurementValue.download,
                        MeasurementTag.file_type: MeasurementValue.scaler,
                    },
                )
                raise RuntimeError(f"Failed to download scaler from {scaler_url}")
            with open(local_path, "wb") as f:
                f.write(response.content)

        with open(local_path, "rb") as f:
            scaler = pickle.load(f)

        self._scaler_cache[scaler_url] = scaler

        elapsed = time.perf_counter() - start
        send_metric(
            metric=MeasurementMetric.load_time,
            value=elapsed,
            tags={
                MeasurementTag.status: MeasurementValue.success,
                MeasurementTag.source: MeasurementValue.download,
                MeasurementTag.file_type: MeasurementValue.scaler,
            },
        )
        return scaler

    @staticmethod
    async def normalize_trading_data(
        scaler,
        close: list[float],
        volumes: Optional[list[int]] = None,
        high: Optional[list[float]] = None,
        low: Optional[list[float]] = None,
        open_p: Optional[list[float]] = None,
    ) -> np.ndarray:
        if scaler is None:
            raise ValueError("Scaler not loaded.")

        num_features = scaler.n_features_in_
        if num_features == 1:
            # Only close prices
            if len(close) != 60:
                raise ValueError("Expected 60 prices for input")
            input_array = np.array(close).reshape(-1, 1)  # shape: (60, 1)
        elif num_features == 2:
            # Close and Volume
            if volumes is None or len(close) != 60 or len(volumes) != 60:
                raise ValueError("Expected 60 prices and 60 volumes for input")
            input_array = np.column_stack((close, volumes))  # shape: (60, 2)
        elif num_features == 4:
            if any(x is None for x in [volumes, high, low]):
                raise ValueError("Expected volume, high, and low for 4-feature input")
            if not all(len(lst) == 60 for lst in [close, volumes, high, low]):
                raise ValueError("Expected 60 values for close, volume, high, and low")
            input_array = np.column_stack((close, volumes, high, low))  # (60, 4)
        else:
            raise ValueError(f"Unsupported num_features: {num_features}")

        normalized_closing_prices = scaler.transform(input_array)
        return normalized_closing_prices.reshape(1, 60, num_features)

    @staticmethod
    async def denormalize_prices(scaler, normalized_prices: list[float]) -> list[float]:
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

        return scaler.inverse_transform(padded)[:, 0].tolist()

    @staticmethod
    async def run_inference(
        model,
        scaler,
        normalized_trading_data: list[list[float]] | np.ndarray,
        days_ahead: int,
    ) -> list[float]:
        if model is None or scaler is None:
            raise ValueError("Model or scaler not loaded.")

        start = time.perf_counter()

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

            elapsed = time.perf_counter() - start
            send_metric(
                metric=MeasurementMetric.inference_time,
                value=elapsed,
                tags={
                    MeasurementTag.status: MeasurementValue.success,
                },
            )
            return predictions
        except Exception as e:
            elapsed = time.perf_counter() - start
            send_metric(
                metric=MeasurementMetric.inference_time,
                value=elapsed,
                tags={
                    MeasurementTag.status: MeasurementValue.fail,
                },
            )
            raise RuntimeError(f"Inference failed: {e}")

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
