"""
マクロ経済指標取得モジュール
FRED API からマクロ経済指標を取得して DB に保存する。
"""
import logging
from datetime import date, datetime
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.macro import MacroIndicator

logger = logging.getLogger(__name__)

# FRED API ベース URL
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"

# 主要な経済指標のシリーズ ID
MACRO_INDICATORS = {
    "cpi": {"series_id": "CPIAUCSL", "name": "消費者物価指数（CPI）"},
    "fed_rate": {"series_id": "FEDFUNDS", "name": "フェデラルファンド金利"},
    "gdp": {"series_id": "GDP", "name": "GDP（名目）"},
    "unemployment": {"series_id": "UNRATE", "name": "失業率"},
    "sp500": {"series_id": "SP500", "name": "S&P 500"},
    "usdjpy": {"series_id": "DEXJPUS", "name": "USD/JPY 為替レート"},
}


async def fetch_and_save_macro_indicator(
    db: AsyncSession,
    indicator_key: str,
    api_key: str,
    limit: int = 120,
) -> int:
    """
    FRED API からマクロ経済指標を取得して DB に保存する。

    Args:
        db: データベースセッション
        indicator_key: 指標キー（"cpi", "fed_rate" 等）
        api_key: FRED API キー
        limit: 取得件数

    Returns:
        int: 新規保存した件数
    """
    indicator = MACRO_INDICATORS.get(indicator_key)
    if not indicator:
        available = ", ".join(MACRO_INDICATORS.keys())
        raise ValueError(f"不明な指標: '{indicator_key}'。利用可能: {available}")

    series_id = indicator["series_id"]
    name = indicator["name"]

    logger.info("マクロ指標取得開始: %s (%s)", name, series_id)

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(FRED_API_URL, params=params)
        response.raise_for_status()

    data = response.json()
    observations = data.get("observations", [])

    # 既存データの日付を取得（重複防止）
    existing_result = await db.execute(
        select(MacroIndicator.indicator_date).where(
            MacroIndicator.series_id == series_id
        )
    )
    existing_dates: set[date] = {row[0] for row in existing_result.all()}

    # 新規データのみ保存
    saved_count = 0
    for obs in observations:
        obs_date = datetime.strptime(obs["date"], "%Y-%m-%d").date()

        if obs_date in existing_dates:
            continue

        value = Decimal(obs["value"]) if obs["value"] != "." else None

        record = MacroIndicator(
            series_id=series_id,
            name=name,
            indicator_date=obs_date,
            value=value,
        )
        db.add(record)
        saved_count += 1

    if saved_count > 0:
        await db.flush()

    logger.info("マクロ指標保存完了: %s, 新規=%d件", name, saved_count)
    return saved_count


async def get_saved_macro_data(
    db: AsyncSession,
    indicator_key: str,
    limit: int = 120,
) -> list[MacroIndicator]:
    """DB から保存済みのマクロ指標データを取得する"""
    indicator = MACRO_INDICATORS.get(indicator_key)
    if not indicator:
        available = ", ".join(MACRO_INDICATORS.keys())
        raise ValueError(f"不明な指標: '{indicator_key}'。利用可能: {available}")

    result = await db.execute(
        select(MacroIndicator)
        .where(MacroIndicator.series_id == indicator["series_id"])
        .order_by(MacroIndicator.indicator_date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_available_indicators() -> list[dict]:
    """利用可能なマクロ経済指標の一覧を返す"""
    return [
        {"key": key, "name": info["name"], "series_id": info["series_id"]}
        for key, info in MACRO_INDICATORS.items()
    ]
