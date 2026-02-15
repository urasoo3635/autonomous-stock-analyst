"""
株式関連モデル
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class Stock(Base, TimestampMixin):
    """銘柄マスタ"""

    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100))
    market: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(default=True)

    # リレーション
    prices: Mapped[list["StockPrice"]] = relationship(back_populates="stock", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Stock(ticker={self.ticker}, name={self.name})>"


class StockPrice(Base, TimestampMixin):
    """株価データ（日足）"""

    __tablename__ = "stock_prices"

    __table_args__ = (
        UniqueConstraint("stock_id", "price_date", name="uq_stock_price_date"),
        Index("ix_stock_prices_stock_date", "stock_id", "price_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(nullable=False)
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    volume: Mapped[int] = mapped_column(nullable=False)
    adjusted_close: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))

    # リレーション
    stock: Mapped["Stock"] = relationship(back_populates="prices")

    def __repr__(self) -> str:
        return f"<StockPrice(stock_id={self.stock_id}, date={self.price_date}, close={self.close})>"
