"""
マクロ経済指標エンドポイント（DB 保存）
"""
from fastapi import APIRouter, Depends, HTTPException

from collectors.macro import (
    fetch_and_save_macro_indicator,
    get_saved_macro_data,
    list_available_indicators,
    MACRO_INDICATORS,
)
from core.config import get_settings
from core.database import get_db
from schemas.macro import (
    MacroDataPoint,
    MacroIndicatorFetchRequest,
    MacroIndicatorFetchResponse,
    MacroIndicatorListResponse,
    MacroIndicatorResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/macro")

settings = get_settings()


@router.get("", response_model=MacroIndicatorListResponse)
async def get_available_indicators() -> dict:
    """利用可能なマクロ経済指標の一覧を返す"""
    indicators = await list_available_indicators()
    return {"indicators": indicators}


@router.post("/{indicator_key}/fetch", response_model=MacroIndicatorFetchResponse)
async def fetch_macro_data(
    indicator_key: str,
    request: MacroIndicatorFetchRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """FRED API からマクロ指標を取得して DB に保存する"""
    api_key = settings.fred_api_key
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="FRED API キーが設定されていません。環境変数 FRED_API_KEY を設定してください",
        )

    limit = request.limit if request else 120

    try:
        saved_count = await fetch_and_save_macro_indicator(
            db, indicator_key, api_key, limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"マクロ指標の取得に失敗しました: {e}",
        )

    return {
        "indicator": indicator_key,
        "saved_count": saved_count,
        "message": f"{saved_count}件のデータを保存しました",
    }


@router.get("/{indicator_key}", response_model=MacroIndicatorResponse)
async def get_macro_indicator(
    indicator_key: str,
    limit: int = 120,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """保存済みのマクロ指標データを取得する"""
    indicator = MACRO_INDICATORS.get(indicator_key)
    if not indicator:
        available = ", ".join(MACRO_INDICATORS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"不明な指標: '{indicator_key}'。利用可能: {available}",
        )

    try:
        records = await get_saved_macro_data(db, indicator_key, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = [
        MacroDataPoint(indicator_date=r.indicator_date, value=r.value)
        for r in records
    ]

    return {
        "indicator": indicator_key,
        "name": indicator["name"],
        "series_id": indicator["series_id"],
        "data": data,
        "total": len(data),
    }
