"""
マクロ経済指標スキーマ
"""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MacroDataPoint(BaseModel):
    """マクロ指標データポイント"""

    model_config = ConfigDict(from_attributes=True)

    indicator_date: date
    value: Decimal | None


class MacroIndicatorResponse(BaseModel):
    """マクロ指標レスポンス"""

    indicator: str
    name: str
    series_id: str
    data: list[MacroDataPoint]
    total: int


class MacroIndicatorFetchRequest(BaseModel):
    """マクロ指標取得リクエスト"""

    limit: int = Field(120, description="取得件数", ge=1, le=1000)


class MacroIndicatorFetchResponse(BaseModel):
    """マクロ指標取得結果レスポンス"""

    indicator: str
    saved_count: int
    message: str


class MacroIndicatorInfo(BaseModel):
    """利用可能なマクロ指標情報"""

    key: str
    name: str
    series_id: str


class MacroIndicatorListResponse(BaseModel):
    """利用可能なマクロ指標一覧"""

    indicators: list[MacroIndicatorInfo]
