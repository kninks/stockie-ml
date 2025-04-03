from typing import List

from fastapi import Depends

from app.api.schemas.predict_schema import PredictRequestSchema, PredictResponseSchema
from app.api.services.predict_services import PredictService


class PredictController:
    def __init__(self, predict_service: PredictService = Depends(PredictService)):
        self.service = predict_service

    async def predict_controller(
        self, request: PredictRequestSchema
    ) -> PredictResponseSchema:
        response = await self.service.predict(request)
        return response

    async def load_model_with_path_controller(self, model_path: str) -> None:
        response = await self.service.load_model_with_path(model_path=model_path)
        return response

    async def load_scaler_with_path_controller(self, scaler_path: str) -> None:
        response = await self.service.load_scaler_with_path(scaler_path=scaler_path)
        return response

    async def normalize_prices_controller(self, prices: List[float]) -> List[float]:
        response = await self.service.normalize_prices(prices=prices)
        return response

    async def denormalize_prices_controller(
        self, normalized_prices: List[float]
    ) -> List[float]:
        response = await self.service.denormalize_prices(
            normalized_prices=normalized_prices
        )
        return response

    async def run_inference(
        self, normalized_closing_prices: List[float]
    ) -> List[float]:
        response = await self.service.run_inference(
            normalized_closing_prices=normalized_closing_prices
        )
        return response
