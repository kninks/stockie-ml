from typing import cast

import uvicorn
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

# from app.core.common.middleware.role_auth_middleware import role_auth_middleware_factory
from app.core.settings.config import config

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
    allow_origins=config.ALLOWED_ORIGINS,  # Change this to restrict origins in production
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

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=config.ML_SERVER_PORT, reload=False
    )
