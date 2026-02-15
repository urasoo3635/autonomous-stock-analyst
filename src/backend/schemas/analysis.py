"""
分析・予測 API スキーマ
"""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class TechnicalIndicators(BaseModel):
    """テクニカル指標レスポンス"""

    model_config = ConfigDict(from_attributes=True)

    date: date
    # 基本
    open: float
    high: float
    low: float
    close: float
    volume: float
    # 指標
    sma_20: float | None = Field(None, alias="SMA_20")
    sma_50: float | None = Field(None, alias="SMA_50")
    sma_200: float | None = Field(None, alias="SMA_200")
    rsi_14: float | None = Field(None, alias="RSI_14")
    # MACD
    macd: float | None = Field(None, alias="MACD_12_26_9")
    macd_hist: float | None = Field(None, alias="MACDh_12_26_9")
    macd_signal: float | None = Field(None, alias="MACDs_12_26_9")
    # Bollinger Bands
    bb_upper: float | None = Field(None, alias="BBU_20_2.0")
    bb_middle: float | None = Field(None, alias="BBM_20_2.0")
    bb_lower: float | None = Field(None, alias="BBL_20_2.0")


class SentimentResponse(BaseModel):
    """センチメント分析レスポンス"""

    text: str
    label: str
    score: float


class SentimentRequest(BaseModel):
    """センチメント分析リクエスト"""

    text: str = Field(..., max_length=1000)


class PredictionResponse(BaseModel):
    """株価予測レスポンス"""

    ticker: str
    target_days: int
    predicted_return: float
    confidence: float | None = None
    features: dict[str, float] | None = None
