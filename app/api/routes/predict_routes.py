from fastapi import APIRouter, Depends

from app.api.controllers.predict_controller import PredictController
from app.api.schemas.predict_schema import PredictRequestSchema
from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.api_key_auth import verify_role
from app.core.enums.roles_enum import RoleEnum

router = APIRouter(
    prefix="/predict",
    tags=["Predict"],
    dependencies=[Depends(verify_role([]))],
)


@router.post("")
async def predict_route(
    request: PredictRequestSchema,
    controller: PredictController = Depends(),
    user_role: str = Depends(verify_role([RoleEnum.BACKEND.value])),
):
    """
    Predict the closing price of a list of stocks with model path, scaler path, and closing prices using the ML model.
    """
    response = await controller.predict_controller(request=request)
    return success_response(data=response)


@router.post("/load-model")
async def load_model_with_path_controller(
    model_path: str,
    controller: PredictController = Depends(PredictController),
):
    """
    Load model with path.
    """
    response = await controller.load_model_with_path_controller(model_path=model_path)
    return success_response(data=response)


@router.post("/load-scaler")
async def load_scaler_with_path_controller(
    scaler_path: str,
    controller: PredictController = Depends(PredictController),
):
    """
    Load scaler with path.
    """
    response = await controller.load_scaler_with_path_controller(
        scaler_path=scaler_path
    )
    return success_response(data=response)


@router.post("/normalized-closing-prices")
async def normalized_closing_prices_controller(
    closing_prices: list[float],
    controller: PredictController = Depends(PredictController),
):
    """
    Normalize closing prices.
    """
    response = await controller.normalized_closing_prices_controller(
        closing_prices=closing_prices
    )
    return success_response(data=response)


@router.post("/denormalized-predicted-prices")
async def denormalized_predicted_prices_controller(
    normalized_predicted_prices: list[float],
    controller: PredictController = Depends(PredictController),
):
    """
    Denormalize predicted prices.
    """
    response = await controller.denormalized_predicted_prices_controller(
        normalized_predicted_prices=normalized_predicted_prices
    )
    return success_response(data=response)


@router.post("/run-inference")
async def run_inference(
    normalized_closing_prices: list[float],
    controller: PredictController = Depends(PredictController),
):
    """
    Run inference on the model.
    """
    response = await controller.run_inference(
        normalized_closing_prices=normalized_closing_prices
    )
    return success_response(data=response)
