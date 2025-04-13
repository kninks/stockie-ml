from app.api.services.general_service import GeneralService, get_general_service


class GeneralController:
    def __init__(self, service: GeneralService):
        self.service = service

    async def check_be_health_controller(
        self,
    ) -> None:
        response = await self.service.check_be_health()
        return response


def get_general_controller() -> GeneralController:
    return GeneralController(service=get_general_service())
