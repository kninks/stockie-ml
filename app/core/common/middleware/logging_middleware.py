import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming API requests and execution time."""

    async def dispatch(self, request: Request, call_next):
        try:
            request_data = await request.body()
            request_body = (
                request_data.decode("utf-8", "ignore") if request_data else "No Body"
            )
        except Exception:
            request_body = "Unreadable Body"

        logger.info(f"Request | {request.method} {request.url} | Body: {request_body}")

        return await call_next(request)


def logging_middleware_factory():
    return LoggingMiddleware
