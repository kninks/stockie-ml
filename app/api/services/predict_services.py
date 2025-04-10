from typing import List, Optional

from fastapi import Depends

from app.api.schemas.predict_schema import (
    PredictRequestSchema,
    PredictResponseSchema,
    StockFromPredictResponseSchema,
)
from app.core.clients.stockie_be_operations import StockieBEOperations

from google.cloud import storage
from tensorflow.keras.models import load_model
import pickle
import os
import numpy as np
import requests

class PredictService:
    model = None
    scaler = None

    def __init__(
        self,
        be_operations: StockieBEOperations = Depends(StockieBEOperations),
    ):
        self.be_operations = be_operations

    # TODO: combine all logics + (pls modify as necessary) + improve performance
    async def predict(self, request: PredictRequestSchema) -> PredictResponseSchema:
        """
        Perform inference using the model
        :param request:
        :return InferenceResponseSchema:
        """
        stocks = PredictRequestSchema.stocks
        response_list = []
        for stock in stocks:
            await self.load_model_with_path(stock.model_path)
            await self.load_scaler_with_path(stock.scaler_path)
            normalized_closing_prices = await self.normalize_prices(
                stock.closing_prices
            )
            normalized_predicted_prices = await self.run_inference(
                normalized_closing_prices=normalized_closing_prices
            )
            predicted_prices = await self.denormalize_prices(
                normalized_predicted_prices
            )
            response_list.append(
                StockFromPredictResponseSchema(
                    stock_ticker=request.stock_tickers,
                    predicted_prices=predicted_prices,
                )
            )

        return PredictResponseSchema(predictions=response_list)

    @staticmethod
    async def load_model_with_path(model_path: str) -> None:
        """
        load model with path
        :param model_path:
        :return None:
        """
        local_model_path = f"/tmp/{os.path.basename(model_path)}"
        
        response = requests.get(model_path)
        if response.status_code == 200:
            with open(local_model_path, "wb") as f:
                f.write(response.content)
            print(f"Model downloaded to: {local_model_path}")
        else:
            raise RuntimeError(f"Failed to download model from {model_path}, status code: {response.status_code}")
        
        PredictService.model = load_model(local_model_path)
        print(f"Model loaded successfully from: {model_path}")
        return None
    
    @staticmethod
    async def load_scaler_with_path(scaler_path: str):
        """
        load scaler with path
        :param scaler_path:
        :return None:
        """
        local_scaler_path = f"/tmp/{os.path.basename(scaler_path)}"

        response = requests.get(scaler_path)
        if response.status_code == 200:
            with open(local_scaler_path, "wb") as f:
                f.write(response.content)
            print(f"Scaler downloaded to: {local_scaler_path}")
        else:
            raise RuntimeError(f"Failed to download scaler from {scaler_path}, status code: {response.status_code}")
        
        with open(local_scaler_path, "rb") as f:
            PredictService.scaler = pickle.load(f)
        print(f"Scaler loaded successfully from: {scaler_path}")

        return None

    # TODO: normalize all closing prices in the list
    @staticmethod
    async def normalize_prices(prices: List[float], volumes: Optional[List[float]] = None) -> np.ndarray:
        """
        call the loaded scaler to normalize a list of closing prices
        :param prices: [100, 101, 102, ...]
        :return normalized_prices:
        """
        if PredictService.scaler is None:
            raise ValueError("Scaler not loaded. Please load it before normalization.")
        
        if len(prices) < 60:
            raise ValueError("Not enough data points for normalization. Need at least 60.")
        
        num_features = PredictService.scaler.n_features_in_
        if num_features == 1:
            # Only close prices
            if len(prices) != 60:
                raise ValueError("Expected 60 prices for input")
            input_array = np.array(prices).reshape(-1, 1)  # shape: (60, 1)

        elif num_features == 2:
            # Close and Volume
            if volumes is None or len(prices) != 60 or len(volumes) != 60:
                raise ValueError("Expected 60 prices and 60 volumes for input")
            input_array = np.column_stack((prices, volumes))  # shape: (60, 2)

        else:
            raise ValueError(f"Unsupported number of features: {num_features}")
        
        # Normalize and reshape to (1, 60, num_features)
        normalized_closing_prices = PredictService.scaler.transform(input_array)

        return normalized_closing_prices.reshape(1, 60, num_features)

    # TODO: denormalize all predicted prices in the list
    @staticmethod
    async def denormalize_prices(
        normalized_prices: List[float],
    ) -> List[float]:
        """
        call the loaded scaler to denormalize a list of closing prices
        :param normalized_prices:
        :return denormalized_prices:
        """
        global scaler
        if PredictService.scaler is None:   
            raise ValueError("Scaler not loaded. Please load it before denormalization.")
        
        try:
            num_features = PredictService.scaler.n_features_in_
        
            # Pad the normalized prices with zeros for other features
            padded = np.concatenate(
                [np.array(normalized_prices).reshape(-1, 1),
                np.zeros((len(normalized_prices), num_features - 1))],
                axis=1
            )
        
            # Inverse transform
            denormalized = PredictService.model.inverse_transform(padded)

            # Return only the 'Close' price column
            return denormalized[:, 0].tolist()

        except Exception as e:
            raise RuntimeError(f"Error in denormalizing prices: {e}")

    # TODO: call the model to predict a list of closing prices
    # TODO: Raise exceptions if error occurs
    @staticmethod
    async def run_inference(normalized_closing_prices: List[List[float]], days_ahead: int = 16) -> List[float]:
        """
        run inference on the loaded model to predict with a list of closing prices
        :param normalized_closing_prices:
        :return normalized_predicted_prices:
        """
        global model
        global scaler

        try: 
            if PredictService.model is None or PredictService.scaler is None:
                raise ValueError("Model or scaler not loaded. Please load it before inference.")
            
            sequence = np.array(normalized_closing_prices)  
            predictions = []

            for _ in range(days_ahead):
                input_seq = sequence[-60:].reshape(1, 60, PredictService.scaler.n_features_in_)
                pred = PredictService.model.predict(input_seq)
                pred_val = pred[0]  # shape: (1,) or (1, 1)

                # Append prediction to the sequence
                predictions.append(pred_val[0])
                sequence = np.vstack([sequence, pred_val])  # Add predicted value to sequence

            return predictions

        except Exception as e:
            print(f"Error in run_inference: {e}")