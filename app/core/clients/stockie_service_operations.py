import logging
from typing import Any, Awaitable, Callable

from app.core.clients.stockie_service_client import StockieServiceClient
from app.core.common.exceptions.custom_exceptions import BackendServerError

logger = logging.getLogger(__name__)


class StockieServiceOperations:
    def __init__(self, client: StockieServiceClient):
        self.client = client

    @staticmethod
    async def _make_request(
        func: Callable[..., Awaitable[Any]],
        *args,
        error_message: str = "Stockie Service request failed",
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
            "/health",
            error_message="Failed to contact backend",
        )


def get_stockie_service_operations() -> StockieServiceOperations:
    return StockieServiceOperations(client=StockieServiceClient())
