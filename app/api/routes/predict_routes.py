from typing import Optional

from fastapi import APIRouter, Depends

from app.api.controllers.predict_controller import (
    PredictController,
    get_predict_controller,
)
from app.api.schemas.predict_schema import PredictRequestSchema
from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.api_key_auth import verify_role
from app.core.enums.roles_enum import RoleEnum

router = APIRouter(
    prefix="/predict",
    tags=["Predict"],
    dependencies=[Depends(verify_role([RoleEnum.BACKEND.value]))],
)


@router.post("")
async def get_predict_route(
    request: PredictRequestSchema,
    controller: PredictController = Depends(get_predict_controller),
):
    response = await controller.predict_controller(request=request)
    return success_response(data=response)


# @router.post("/load-model")
# async def load_model_with_path_route(
#     model_url: str,
#     controller: PredictController = Depends(get_predict_controller),
# ):
#     """
#     Load model with path.
#     """
#     response = await controller.load_model_with_path_controller(model_url=model_url)
#     return success_response(data=response, message="Model loaded successfully.")
#
#
# @router.post("/load-scaler")
# async def load_scaler_with_path_route(
#     scaler_url: str,
#     controller: PredictController = Depends(get_predict_controller),
# ):
#     """
#     Load scaler with path.
#     """
#     response = await controller.load_scaler_with_path_controller(scaler_url=scaler_url)
#     return success_response(data=response, message="Scaler loaded successfully.")
#
#
# @router.post("/normalize-trading-data")
# async def normalize_trading_data(
#     close: list[float],
#     volumes: Optional[list[float]] = None,
#     controller: PredictController = Depends(get_predict_controller),
# ):
#     """
#     Normalize closing prices.
#     """
#     response = await controller.normalize_trading_data_controller(
#         close=close, volumes=volumes
#     )
#     return success_response(data=response, message="Prices normalized successfully.")
#
#
# @router.post("/denormalize-prices")
# async def denormalize_prices_route(
#     normalized_prices: list[float],
#     controller: PredictController = Depends(get_predict_controller),
# ):
#     """
#     Denormalize predicted prices.
#     """
#     response = await controller.denormalize_prices_controller(
#         normalized_prices=normalized_prices
#     )
#     return success_response(data=response, message="Prices denormalized successfully.")
#
#
# @router.post("/run-inference")
# async def run_inference_route(
#     normalized_closing_prices: list[list[float]],
#     days_ahead: int = 16,
#     controller: PredictController = Depends(get_predict_controller),
# ):
#     """
#     Run inference on the model.
#     """
#     response = await controller.run_inference(
#         normalized_trading_data=normalized_closing_prices, days_ahead=days_ahead
#     )
#     return success_response(data=response, message="Inference run successfully.")
#
#
# @router.get("/active-info")
# async def get_active_info_route(
#     controller: PredictController = Depends(get_predict_controller),
# ):
#     """
#     Get active model and scaler info.
#     """
#     response = controller.get_active_info_controller()
#     return success_response(data=response)


@router.get("/cache-info")
async def get_cache_info_route(
    controller: PredictController = Depends(get_predict_controller),
):
    response = controller.get_cache_info_controller()
    return success_response(data=response)


@router.delete("/clear-cache")
async def clear_cache_route(
    model_url: Optional[str] = None,
    scaler_url: Optional[str] = None,
    controller: PredictController = Depends(get_predict_controller),
):
    response = controller.clear_cache_controller(
        model_url=model_url, scaler_url=scaler_url
    )
    return success_response(data=response)
