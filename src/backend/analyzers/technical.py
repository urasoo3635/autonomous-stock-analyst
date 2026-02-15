"""
テクニカル分析モジュール
pandas-ta を使用して各種テクニカル指標を計算する。
"""
import logging
from datetime import date
from decimal import Decimal

import pandas as pd
import pandas_ta as ta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.stock import Stock, StockPrice

logger = logging.getLogger(__name__)


async def calculate_technical_indicators(
    db: AsyncSession,
    ticker: str,
    limit: int = 365,
) -> pd.DataFrame:
    """
    指定された銘柄の株価データを取得し、テクニカル指標を計算して DataFrame として返す。

    Args:
        db: データベースセッション
        ticker: 銘柄コード
        limit: 計算に使用する過去データの件数（少なすぎると指標が計算できない場合がある）

    Returns:
        pd.DataFrame: テクニカル指標が付与された DataFrame
    """
    # 銘柄の存在確認
    result = await db.execute(select(Stock).where(Stock.ticker == ticker))
    stock = result.scalar_one_or_none()
    if not stock:
        raise ValueError(f"銘柄 '{ticker}' が見つかりません")

    # 株価データ取得（日付昇順）
    # pandas-ta は時系列順のデータを期待するため昇順
    price_result = await db.execute(
        select(StockPrice)
        .where(StockPrice.stock_id == stock.id)
        .order_by(StockPrice.price_date.asc())
        .limit(limit * 2)  # 移動平均などを計算するために少し多めに取得
    )
    prices = price_result.scalars().all()

    if not prices:
        logger.warning("株価データがありません: ticker=%s", ticker)
        return pd.DataFrame()

    # DataFrame に変換
    data = [
        {
            "date": p.price_date,
            "open": float(p.open),
            "high": float(p.high),
            "low": float(p.low),
            "close": float(p.close),
            "volume": float(p.volume),
        }
        for p in prices
    ]
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)

    # --- テクニカル指標の計算 ---

    # 1. 移動平均線 (SMA)
    df["SMA_20"] = ta.sma(df["close"], length=20)
    df["SMA_50"] = ta.sma(df["close"], length=50)
    df["SMA_200"] = ta.sma(df["close"], length=200)

    # 2. 指数平滑移動平均線 (EMA)
    df["EMA_12"] = ta.ema(df["close"], length=12)
    df["EMA_26"] = ta.ema(df["close"], length=26)

    # 3. RSI (Relative Strength Index)
    df["RSI_14"] = ta.rsi(df["close"], length=14)

    # 4. MACD (Moving Average Convergence Divergence)
    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    if macd is not None:
        df = pd.concat([df, macd], axis=1)
        # pandas-ta の列名を統一的な名前にリネームする場合もあるが、
        # ここではデフォルト（MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9）を使用

    # 5. ボリンジャーバンド (Bollinger Bands)
    bbands = ta.bbands(df["close"], length=20, std=2)
    if bbands is not None:
        df = pd.concat([df, bbands], axis=1)
        # BBL_20_2.0, BBM_20_2.0, BBU_20_2.0 等が追加される

    # 6. その他の指標（必要に応じて追加）
    # df["ATR"] = ta.atr(df["high"], df["low"], df["close"], length=14)

    # NaN を処理（計算できない初期期間など）
    # ここでは削除せず、呼び出し元で fillna するか判断させるが、
    # API レスポンスとしては直近のデータだけ返すことが多いので、
    # 最新のデータを取得しやすいように tail で返す設計も考えられる。

    return df
