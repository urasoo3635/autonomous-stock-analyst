"""
分析・予測 API エンドポイント
"""
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from analyzers.sentiment import SentimentAnalyzer
from analyzers.technical import calculate_technical_indicators
from core.database import get_db
from predictors.price_predictor import PricePredictor
from schemas.analysis import (
    PredictionResponse,
    SentimentRequest,
    SentimentResponse,
    TechnicalIndicators,
)

router = APIRouter(prefix="/analysis")


@router.get("/{ticker}/technical", response_model=list[TechnicalIndicators])
async def get_technical_indicators(
    ticker: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """テクニカル指標を取得する（直近 N 日分）"""
    try:
        df = await calculate_technical_indicators(db, ticker, limit=days + 100)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if df.empty:
        return []

    # 直近 N 日分のみ返す
    recent_df = df.tail(days)
    result = []
    for date_idx, row in recent_df.iterrows():
        # NaN を None に変換
        row_dict = row.where(pd.notnull(row), None).to_dict()
        row_dict["date"] = date_idx  # index (date) を含める
        result.append(row_dict)

    return result


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(
    request: SentimentRequest,
) -> dict:
    """テキストのセンチメント分析を行う"""
    try:
        result = SentimentAnalyzer.analyze(request.text)
    except ImportError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析エラー: {e}")

    return {
        "text": request.text,
        "label": result["label"],
        "score": result["score"],
    }


@router.post("/{ticker}/predict", response_model=PredictionResponse)
async def predict_price(
    ticker: str,
    target_days: int = 30,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """株価予測を行う（簡易版: その場で直近データを使って学習・予測）"""
    # 本来は定期バッチで学習済みモデルを使うが、ここではデモとしてオンデマンド学習する
    try:
        df = await calculate_technical_indicators(db, ticker, limit=1000)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if df.empty or len(df) < 100:
        raise HTTPException(
            status_code=400,
            detail="予測に必要な十分なデータがありません（最低100日分）",
        )

    predictor = PricePredictor()
    try:
        # 学習（直近データを使って）
        predictor.train(df, target_days=target_days)
        # 予測
        predicted_return = predictor.predict(df, target_days=target_days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予測エラー: {e}")

    return {
        "ticker": ticker,
        "target_days": target_days,
        "predicted_return": predicted_return,
        "confidence": None,  # TODO: 信頼度スコアの実装
    }
