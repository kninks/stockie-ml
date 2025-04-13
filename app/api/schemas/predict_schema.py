from pydantic import BaseModel


class StockToPredictRequestSchema(BaseModel):
    stock_tickers: str
    closing_prices: list[float]
    model_path: str
    scaler_path: str


class PredictRequestSchema(BaseModel):
    stocks: list[StockToPredictRequestSchema]


class StockFromPredictResponseSchema(BaseModel):
    stock_ticker: str
    predicted_prices: list[float]


class PredictResponseSchema(BaseModel):
    predictions: list[StockFromPredictResponseSchema]
