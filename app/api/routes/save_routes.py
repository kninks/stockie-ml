from fastapi import APIRouter, Depends

from app.api.controllers.save_controller import SaveController
from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.api_key_auth import verify_role

router = APIRouter(
    prefix="/save",
    tags=["Save Model and Scaler and Model Metadata"],
    dependencies=[Depends(verify_role([]))],
)


@router.post("/model-and-scaler-and-metadata")
async def save_model_and_scaler_and_metadata_route(
    stock_ticker: str,
    version_tag: str,
    accuracy: float,
    additional_data: dict,
    controller: SaveController = Depends(),
):
    """
    Save the model and scaler file to Google Cloud Storage and save model metadata to the database.
    """
    response = await controller.save_model_and_scaler_and_metadata_controller(
        stock_ticker=stock_ticker,
        version_tag=version_tag,
        accuracy=accuracy,
        additional_data=additional_data,
    )
    return success_response(data=response)


@router.post("/model-file")
async def save_model_file_route(
    controller: SaveController = Depends(),
):
    """
    Save the model file to Google Cloud Storage.
    """
    response = await controller.save_model_file_controller()
    return success_response(data=response)


@router.post("/scaler-file")
async def save_scaler_file_route(
    controller: SaveController = Depends(),
):
    """
    Save the scaler file to Google Cloud Storage.
    """
    response = await controller.save_scaler_file_controller()
    return success_response(data=response)


@router.post("/model-metadata")
async def save_model_metadata_route(
    stock_ticker: str,
    version: str,
    accuracy: float,
    model_path: str,
    scaler_path: str,
    additional_data: dict,
    controller: SaveController = Depends(),
):
    """
    Save model metadata to the database via backend.
    """
    response = await controller.save_model_metadata_controller(
        stock_ticker=stock_ticker,
        version=version,
        accuracy=accuracy,
        model_path=model_path,
        scaler_path=scaler_path,
        additional_data=additional_data,
    )
    return success_response(data=response)
