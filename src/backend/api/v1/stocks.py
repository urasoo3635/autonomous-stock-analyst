"""
銘柄 CRUD + 株価データエンドポイント
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from collectors.stock_price import fetch_and_save_stock_prices
from core.database import get_db
from models.stock import Stock, StockPrice
from schemas.stock import (
    StockCreate,
    StockListResponse,
    StockPriceFetchRequest,
    StockPriceFetchResponse,
    StockPriceListResponse,
    StockPriceResponse,
    StockResponse,
)

router = APIRouter(prefix="/stocks")


@router.get("", response_model=StockListResponse)
async def list_stocks(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """銘柄一覧を取得する"""
    count_result = await db.execute(select(func.count(Stock.id)))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Stock)
        .where(Stock.is_active.is_(True))
        .order_by(Stock.ticker)
        .offset(skip)
        .limit(limit)
    )
    stocks = result.scalars().all()

    return {"stocks": stocks, "total": total}


@router.post("", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
async def create_stock(
    stock_in: StockCreate,
    db: AsyncSession = Depends(get_db),
) -> Stock:
    """銘柄を登録する"""
    existing = await db.execute(select(Stock).where(Stock.ticker == stock_in.ticker))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"銘柄 '{stock_in.ticker}' は既に登録されています",
        )

    stock = Stock(**stock_in.model_dump())
    db.add(stock)
    await db.flush()
    await db.refresh(stock)
    return stock


@router.get("/{ticker}", response_model=StockResponse)
async def get_stock(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> Stock:
    """銘柄の詳細を取得する"""
    result = await db.execute(select(Stock).where(Stock.ticker == ticker))
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"銘柄 '{ticker}' が見つかりません",
        )

    return stock


@router.post("/{ticker}/fetch", response_model=StockPriceFetchResponse)
async def fetch_stock_prices(
    ticker: str,
    request: StockPriceFetchRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Yahoo Finance から株価データを取得して DB に保存する"""
    period = request.period if request else "1y"

    try:
        saved_count = await fetch_and_save_stock_prices(db, ticker, period)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"株価データの取得に失敗しました: {e}",
        )

    return {
        "ticker": ticker,
        "saved_count": saved_count,
        "message": f"{saved_count}件の株価データを保存しました",
    }


@router.get("/{ticker}/prices", response_model=StockPriceListResponse)
async def get_stock_prices(
    ticker: str,
    skip: int = 0,
    limit: int = 365,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """保存済みの株価データを取得する"""
    # 銘柄の存在確認
    stock_result = await db.execute(select(Stock).where(Stock.ticker == ticker))
    stock = stock_result.scalar_one_or_none()

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"銘柄 '{ticker}' が見つかりません",
        )

    # 件数取得
    count_result = await db.execute(
        select(func.count(StockPrice.id)).where(StockPrice.stock_id == stock.id)
    )
    total = count_result.scalar_one()

    # 株価データ取得（日付降順）
    result = await db.execute(
        select(StockPrice)
        .where(StockPrice.stock_id == stock.id)
        .order_by(StockPrice.price_date.desc())
        .offset(skip)
        .limit(limit)
    )
    prices = result.scalars().all()

    return {"ticker": ticker, "prices": prices, "total": total}

