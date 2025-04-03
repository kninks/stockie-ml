from fastapi import Depends

from app.core.clients.stockie_be_operations import StockieBEOperations


class GeneralService:
    def __init__(
        self,
        be_operations: StockieBEOperations = Depends(StockieBEOperations),
    ):
        self.be_operations = be_operations

    async def check_be_health(self) -> None:
        """
        Check the health of the Stockie BE service.
        """
        response = await self.be_operations.check_health()
        return response
