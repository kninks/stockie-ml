from fastapi import Depends

from app.api.services.general_service import GeneralService


class GeneralController:
    def __init__(self, general_service: GeneralService = Depends(GeneralService)):
        self.service = general_service

    async def check_be_health_controller(
        self,
    ) -> None:
        response = await self.service.check_be_health()
        return response
