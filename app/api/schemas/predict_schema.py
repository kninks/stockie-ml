from typing import List

from pydantic import BaseModel


class StockToPredictRequestSchema(BaseModel):
    stock_tickers: str
    closing_price: List[float]
    model_path: str
    scaler_path: str


class PredictRequestSchema(BaseModel):
    stocks: List[StockToPredictRequestSchema]


class StockFromPredictResponseSchema(BaseModel):
    stock_ticker: str
    predicted_prices: List[float]


class PredictResponseSchema(BaseModel):
    predictions: List[StockFromPredictResponseSchema]
