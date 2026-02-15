"""
株式関連スキーマ（リクエスト / レスポンス）
"""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Stock
# =============================================================================


class StockBase(BaseModel):
    """銘柄の共通フィールド"""

    ticker: str = Field(..., min_length=1, max_length=20, examples=["7203.T"])
    name: str = Field(..., min_length=1, max_length=200, examples=["トヨタ自動車"])
    sector: str | None = Field(None, max_length=100, examples=["輸送用機器"])
    market: str | None = Field(None, max_length=50, examples=["東証プライム"])
    description: str | None = Field(None, max_length=1000)


class StockCreate(StockBase):
    """銘柄登録リクエスト"""

    pass


class StockResponse(StockBase):
    """銘柄レスポンス"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class StockListResponse(BaseModel):
    """銘柄一覧レスポンス"""

    stocks: list[StockResponse]
    total: int


# =============================================================================
# StockPrice
# =============================================================================


class StockPriceResponse(BaseModel):
    """株価レスポンス"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    price_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    adjusted_close: Decimal | None


class StockPriceListResponse(BaseModel):
    """株価一覧レスポンス"""

    ticker: str
    prices: list[StockPriceResponse]
    total: int


class StockPriceFetchRequest(BaseModel):
    """株価取得リクエスト"""

    period: str = Field(
        "1y",
        description="取得期間",
        examples=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    )


class StockPriceFetchResponse(BaseModel):
    """株価取得結果レスポンス"""

    ticker: str
    saved_count: int
    message: str

