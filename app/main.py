from typing import cast

from fastapi import FastAPI, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ExceptionHandler

from app.api.routes import general_routes, predict_routes
from app.core.common.exceptions.custom_exceptions import CustomAPIError
from app.core.common.exceptions.exception_handlers import (
    custom_api_exception_handler,
    global_exception_handler,
    http_exception_handler,
    starlette_http_exception_handler,
)
from app.core.common.middleware.logging_middleware import logging_middleware_factory
from app.core.settings.logging_config import setup_logging

setup_logging("INFO")

from app.core.settings.config import get_config

config = get_config()

app = FastAPI(
    title="Stockie ML API",
    description="API for Stockie ML server",
    version="1.0.0",
    debug=config.DEBUG,
    root_path="/api",
)

app.add_middleware(logging_middleware_factory())
# app.add_middleware(role_auth_middleware_factory())

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    StarletteHTTPException, cast(ExceptionHandler, starlette_http_exception_handler)
)
app.add_exception_handler(Exception, cast(ExceptionHandler, global_exception_handler))
app.add_exception_handler(HTTPException, cast(ExceptionHandler, http_exception_handler))
app.add_exception_handler(
    CustomAPIError, cast(ExceptionHandler, custom_api_exception_handler)
)

app.include_router(general_routes.router)
app.include_router(predict_routes.router)
