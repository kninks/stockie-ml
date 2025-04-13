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
async def predict_route(
    request: PredictRequestSchema,
    controller: PredictController = Depends(get_predict_controller),
):
    """
    Predict the closing price of a list of stocks with model path, scaler path, and closing prices using the ML model.
    """
    response = await controller.predict_controller(request=request)
    return success_response(data=response)


@router.post("/load-model")
async def load_model_with_path_controller(
    model_path: str,
    controller: PredictController = Depends(get_predict_controller),
):
    """
    Load model with path.
    """
    response = await controller.load_model_with_path_controller(model_path=model_path)
    return success_response(data=response, message="Model loaded successfully.")


@router.post("/load-scaler")
async def load_scaler_with_path_controller(
    scaler_path: str,
    controller: PredictController = Depends(get_predict_controller),
):
    """
    Load scaler with path.
    """
    response = await controller.load_scaler_with_path_controller(
        scaler_path=scaler_path
    )
    return success_response(data=response, message="Scaler loaded successfully.")


@router.post("/normalize-prices")
async def normalize_prices_controller(
    prices: list[float],
    controller: PredictController = Depends(get_predict_controller),
):
    """
    Normalize closing prices.
    """
    response = await controller.normalize_prices_controller(prices=prices)
    return success_response(data=response, message="Prices normalized successfully.")


@router.post("/denormalize-prices")
async def denormalize_prices_controller(
    normalized_prices: list[float],
    controller: PredictController = Depends(get_predict_controller),
):
    """
    Denormalize predicted prices.
    """
    response = await controller.denormalize_prices_controller(
        normalized_prices=normalized_prices
    )
    return success_response(data=response, message="Prices denormalized successfully.")


@router.post("/run-inference")
async def run_inference(
    normalized_closing_prices: list[list[float]],
    controller: PredictController = Depends(get_predict_controller),
):
    """
    Run inference on the model.
    """
    response = await controller.run_inference(
        normalized_closing_prices=normalized_closing_prices
    )
    return success_response(data=response, message="Inference run successfully.")
