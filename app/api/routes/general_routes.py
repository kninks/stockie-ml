from fastapi import APIRouter, Depends

from app.api.controllers.general_controller import GeneralController
from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.api_key_auth import verify_role
from app.core.enums.roles_enum import RoleEnum

router = APIRouter(
    prefix="/general",
    tags=["General"],
    dependencies=[Depends(verify_role([]))],
)


@router.get("/health")
async def health_check(user_role: str = Depends(verify_role([RoleEnum.BACKEND.value]))):
    return await success_response(
        message="ML server is healthy", data={"role": user_role}
    )


@router.get("/get-stockie-be-health")
async def get_stockie_be_health_route(
    controller: GeneralController = Depends(),
):
    response = await controller.check_be_health_controller()
    return await success_response(data=response)
