from fastapi import Depends

from app.api.services.save_service import SaveService


class SaveController:
    def __init__(self, save_service: SaveService = Depends(SaveService)):
        self.service = save_service

    async def save_model_and_scaler_and_metadata_controller(
        self,
        stock_ticker: str,
        version_tag: str,
        accuracy: float,
        model_metadata: dict,
    ) -> None:
        response = await self.service.save_model_and_scaler_and_metadata(
            stock_ticker=stock_ticker,
            version_tag=version_tag,
            accuracy=accuracy,
            model_metadata=model_metadata,
        )
        return response

    async def save_model_file_controller(self) -> str:
        response = await self.service.save_model_file()
        return response

    async def save_scaler_file_controller(self) -> str:
        response = await self.service.save_scaler_file()
        return response

    async def save_model_metadata_controller(
        self,
        stock_ticker: str,
        version: str,
        accuracy: float,
        model_path: str,
        scaler_path: str,
        model_metadata: dict,
    ) -> None:
        response = await self.service.save_model_metadata(
            stock_ticker=stock_ticker,
            version=version,
            accuracy=accuracy,
            model_path=model_path,
            scaler_path=scaler_path,
            model_metadata=model_metadata,
        )
        return response
