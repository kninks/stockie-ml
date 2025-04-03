from typing import Optional

from fastapi import Depends

from app.core.clients.stockie_be_operations import StockieBEOperations


class SaveService:
    def __init__(
        self,
        be_operations: StockieBEOperations = Depends(StockieBEOperations),
    ):
        self.be_operations = be_operations

    # TODO: Add error handling
    async def save_model_and_scaler_and_metadata(
        self,
        stock_ticker: str,
        version_tag: str,
        accuracy: float,
        model_metadata: dict,
    ) -> None:
        """
        Save the model and scaler file to Google Cloud Storage and save model metadata to the database.
        """
        model_path = await self.save_model_file()
        scaler_path = await self.save_scaler_file()
        await self.save_model_metadata(
            stock_ticker=stock_ticker,
            version=version_tag,
            accuracy=accuracy,
            model_path=model_path,
            scaler_path=scaler_path,
            model_metadata=model_metadata,
        )

    # TODO
    @staticmethod
    async def save_model_file() -> str:
        """
        Save the model file to Google Cloud Storage and return the path.
        """
        pass

    # TODO
    @staticmethod
    async def save_scaler_file() -> str:
        """
        Save the scaler file to Google Cloud Storage and return the path.
        """
        pass

    # TODO (knink)
    async def save_model_metadata(
        self,
        stock_ticker: str,
        version: str,
        accuracy: float,
        model_path: str,
        scaler_path: str,
        model_metadata: Optional[dict],
    ) -> None:
        await self.be_operations.save_model(
            stock_ticker=stock_ticker,
            version=version,
            accuracy=accuracy,
            model_path=model_path,
            scaler_path=scaler_path,
            model_metadata=model_metadata,
        )
        """
        Save the model metadata to db by calling a backend endpoint.
        """
        pass
