from typing import Optional

from pydantic import BaseModel


class StockToPredictRequestSchema(BaseModel):
    stock_ticker: str
    close: list[float]
    volumes: Optional[list[int]] = []
    high: Optional[list[float]] = []
    low: Optional[list[float]] = []
    open: Optional[list[float]] = []
    model_path: str
    scaler_path: str

    class Config:
        extra = "ignore"


class PredictRequestSchema(BaseModel):
    stocks: list[StockToPredictRequestSchema]
    days_ahead: int = 16


class InferenceResultSchema(BaseModel):
    stock_ticker: str
    predicted_price: Optional[list[float]] = None
    success: bool
    error_message: Optional[str] = None
