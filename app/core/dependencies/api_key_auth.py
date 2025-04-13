from fastapi import Depends, Request, Security
from fastapi.security.api_key import APIKeyHeader

from app.core.common.exceptions.custom_exceptions import AuthError, ForbiddenError
from app.core.enums.roles_enum import RoleEnum
from app.core.settings.config import get_config

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise AuthError("API Key missing")

    for role, key in get_config().ALLOWED_API_KEYS.items():
        if api_key == key:
            return role

    raise AuthError("Invalid API Key")


def verify_role(extra_roles: list[str] = None):
    allowed_roles = {RoleEnum.ML_SERVER.value}
    if extra_roles:
        allowed_roles.update(extra_roles)

    async def role_checker(request: Request, user_role: str = Depends(verify_api_key)):
        if user_role not in allowed_roles:
            raise ForbiddenError("Unauthorized access")

        # ✅ Save to request state (in case later dependencies reuse it)
        request.state.user_role = user_role
        return user_role

    return role_checker
