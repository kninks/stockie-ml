from app.core.clients.stockie_service_operations import (
    StockieServiceOperations,
    get_stockie_service_operations,
)


class GeneralService:
    def __init__(
        self,
        stockie_service_operations: StockieServiceOperations,
    ):
        self.stockie_service_operations = stockie_service_operations

    async def check_be_health(self) -> None:
        """
        Check the health of the Stockie BE service.
        """
        response = await self.stockie_service_operations.check_health()
        return response


def get_general_service() -> GeneralService:
    return GeneralService(
        stockie_service_operations=get_stockie_service_operations(),
    )
