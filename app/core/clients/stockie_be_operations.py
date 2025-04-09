import logging
from typing import Any, Awaitable, Callable, Optional

from fastapi import Depends

from app.core.clients.stockie_be_client import StockieBEClient
from app.core.common.exceptions.custom_exceptions import BackendServerError

logger = logging.getLogger(__name__)


class StockieBEOperations:
    def __init__(self, client: StockieBEClient = Depends(StockieBEClient)):
        self.client = client

    @staticmethod
    async def _make_request(
        func: Callable[..., Awaitable[Any]],
        *args,
        error_message: str = "Backend request failed",
        **kwargs,
    ) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}")
            raise BackendServerError(f"{error_message}: {str(e)}")

    async def check_health(self) -> Any:
        return await self._make_request(
            self.client.get,
            "/general/health",
            error_message="Failed to contact backend",
        )

    async def save_model(
        self,
        stock_ticker: str,
        version: str,
        accuracy: float,
        model_path: str,
        scaler_path: str,
        additional_data: Optional[dict],
    ) -> Any:
        payload = {
            "stock_ticker": stock_ticker,
            "version": version,
            "accuracy": accuracy,
            "model_path": model_path,
            "scaler_path": scaler_path,
            "additional_data": additional_data,
        }
        return await self._make_request(
            self.client.post,
            "/ml-ops/model-metadata",
            data=payload,
            error_message="Failed to save to db via backend",
        )
