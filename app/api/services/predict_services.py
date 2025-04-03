from typing import List

from fastapi import Depends

from app.api.schemas.predict_schema import (
    PredictRequestSchema,
    PredictResponseSchema,
    StockFromPredictResponseSchema,
)
from app.core.clients.stockie_be_operations import StockieBEOperations


class PredictService:
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

    # TODO: load model with the model_path
    @staticmethod
    async def load_model_with_path(model_path: str) -> None:
        """
        load model with path
        :param model_path:
        :return None:
        """
        return None

    # TODO: load scaler with the scaler_path
    @staticmethod
    async def load_scaler_with_path(scaler_path: str):
        """
        load scaler with path
        :param scaler_path:
        :return None:
        """
        return None

    # TODO: normalize all closing prices in the list
    @staticmethod
    async def normalize_prices(prices: List[float]) -> List[float]:
        """
        call the loaded scaler to normalize a list of closing prices
        :param prices:
        :return normalized_prices:
        """
        return prices

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
        denormalized_prices = normalized_prices
        return denormalized_prices

    # TODO: call the model to predict a list of closing prices
    # TODO: Raise exceptions if error occurs
    @staticmethod
    async def run_inference(normalized_closing_prices: List[float]) -> List[float]:
        """
        run inference on the loaded model to predict with a list of closing prices
        :param normalized_closing_prices:
        :return normalized_predicted_prices:
        """
        normalized_predicted_prices = normalized_closing_prices
        return normalized_predicted_prices
