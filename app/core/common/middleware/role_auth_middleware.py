# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
#
# from app.core.common.exceptions.custom_exceptions import AuthError
# from app.core.settings.config import config
#
#
# class RoleAuthMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         if request.url.path.startswith(("/docs", "/redoc", "/api/openapi.json")):
#             return await call_next(request)
#
#         if hasattr(request.state, "user_role"):
#             return await call_next(request)
#
#         api_key = request.headers.get("X-API-Key")
#         if not api_key:
#             raise AuthError("API Key missing")
#
#         allowed_roles = config.ALLOWED_API_KEYS
#         for role, key in allowed_roles.items():
#             if api_key == key:
#                 request.state.user_role = role
#                 break
#         else:
#             raise AuthError("Invalid API Key")
#
#         return await call_next(request)
#
#
# def role_auth_middleware_factory():
#     return RoleAuthMiddleware
