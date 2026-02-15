"""
株価データ取得モジュール
Yahoo Finance (yfinance) から株価データを取得して DB に保存する。
"""
import logging
from datetime import date

import yfinance as yf
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.stock import Stock, StockPrice

logger = logging.getLogger(__name__)


async def fetch_and_save_stock_prices(
    db: AsyncSession,
    ticker: str,
    period: str = "1y",
) -> int:
    """
    Yahoo Finance から株価データを取得して DB に保存する。

    Args:
        db: データベースセッション
        ticker: 銘柄コード（例: "7203.T"）
        period: 取得期間（"1mo", "3mo", "6mo", "1y", "2y", "5y", "max"）

    Returns:
        int: 新規保存した件数
    """
    # 銘柄の存在確認
    result = await db.execute(select(Stock).where(Stock.ticker == ticker))
    stock = result.scalar_one_or_none()
    if not stock:
        raise ValueError(f"銘柄 '{ticker}' が登録されていません。先に銘柄を登録してください")

    logger.info("株価データ取得開始: ticker=%s, period=%s", ticker, period)

    # yfinance でデータ取得（同期処理）
    yf_ticker = yf.Ticker(ticker)
    df = yf_ticker.history(period=period)

    if df.empty:
        logger.warning("株価データが取得できませんでした: ticker=%s", ticker)
        return 0

    # 既存データの日付を取得（重複防止）
    existing_result = await db.execute(
        select(StockPrice.price_date).where(StockPrice.stock_id == stock.id)
    )
    existing_dates: set[date] = {row[0] for row in existing_result.all()}

    # 新規データのみ保存
    saved_count = 0
    for idx, row in df.iterrows():
        price_date = idx.date()  # type: ignore[union-attr]

        if price_date in existing_dates:
            continue

        price = StockPrice(
            stock_id=stock.id,
            price_date=price_date,
            open=round(float(row["Open"]), 4),
            high=round(float(row["High"]), 4),
            low=round(float(row["Low"]), 4),
            close=round(float(row["Close"]), 4),
            volume=int(row["Volume"]),
        )
        db.add(price)
        saved_count += 1

    if saved_count > 0:
        await db.flush()

    logger.info("株価データ保存完了: ticker=%s, 新規=%d件", ticker, saved_count)
    return saved_count
