from typing import Optional

from app.api.schemas.predict_schema import InferenceResultSchema, PredictRequestSchema
from app.api.services.predict_service import PredictService, get_predict_service


class PredictController:
    def __init__(self, service: PredictService):
        self.service = service

    async def predict_controller(
        self, request: PredictRequestSchema
    ) -> list[InferenceResultSchema]:
        response: list[InferenceResultSchema] = await self.service.predict(request)
        return response

    async def load_model_with_path_controller(self, model_url: str) -> dict:
        await self.service.load_model_with_cache(model_url=model_url)
        return {"message": f"Model loaded from: {model_url}"}

    async def load_scaler_with_path_controller(self, scaler_url: str) -> dict:
        await self.service.load_scaler_with_cache(scaler_url=scaler_url)
        return {"message": f"Scaler loaded from: {scaler_url}"}

    async def normalize_trading_data_controller(
        self, close: list[float], volumes: Optional[list[float]] = None
    ) -> dict:
        normalized = await self.service.normalize_trading_data(
            close=close, volumes=volumes
        )
        return {
            "message": "Prices normalized successfully.",
            "normalized_prices": normalized.tolist(),
        }

    async def denormalize_prices_controller(
        self, normalized_prices: list[float]
    ) -> list[float]:
        response = await self.service.denormalize_prices(
            normalized_prices=normalized_prices
        )
        return response

    async def run_inference(
        self, normalized_trading_data: list[list[float]], days_ahead: int
    ) -> list[float]:
        response = await self.service.run_inference(
            normalized_trading_data=normalized_trading_data, days_ahead=days_ahead
        )
        return response

    def get_active_info_controller(self) -> dict:
        response = self.service.get_active_info()
        return response

    def get_cache_info_controller(self) -> dict:
        response = self.service.get_cache_info()
        return response

    def clear_cache_controller(
        self, model_url: Optional[str] = None, scaler_url: Optional[str] = None
    ) -> dict:
        response = self.service.clear_cache(model_url=model_url, scaler_url=scaler_url)
        return response


def get_predict_controller() -> PredictController:
    return PredictController(service=get_predict_service())
