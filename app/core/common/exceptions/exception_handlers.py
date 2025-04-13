import logging

from fastapi import HTTPException, Request
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.common.exceptions.custom_exceptions import CustomAPIError
from app.core.common.utils.response_handlers import error_response
from app.core.enums.error_codes_enum import ErrorCodes

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    return error_response(
        status_code=ErrorCodes.INTERNAL_SERVER_ERROR.value,
        error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
        message="An unexpected internal server error occurred",
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    triggered by FastAPI HTTPException when is raised inside endpoints
    """

    return error_response(
        status_code=exc.status_code,
        error_code=ErrorCodes(exc.status_code),
        message=exc.detail,
    )


async def custom_api_exception_handler(request: Request, exc: CustomAPIError):
    try:
        error_code_enum = ErrorCodes(exc.error_code)
    except ValueError:
        logger.warning(f"Unknown error code: {exc.error_code}")
        error_code_enum = ErrorCodes.INTERNAL_SERVER_ERROR

    return error_response(
        error_code=error_code_enum,
        message=exc.message,
        status_code=exc.status_code,
    )


async def starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
):
    error_code = (
        ErrorCodes(exc.status_code).value
        if exc.status_code in {e.value for e in ErrorCodes}
        else ErrorCodes.BAD_REQUEST.value
    )

    return custom_api_exception_handler(
        request,
        CustomAPIError(
            status_code=exc.status_code,
            error_code=error_code,
            message=exc.detail or "An HTTP error occurred",
        ),
    )
