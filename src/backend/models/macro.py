"""
マクロ経済指標モデル
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class MacroIndicator(Base, TimestampMixin):
    """マクロ経済指標データ"""

    __tablename__ = "macro_indicators"

    __table_args__ = (
        UniqueConstraint("series_id", "indicator_date", name="uq_macro_series_date"),
        Index("ix_macro_series_date", "series_id", "indicator_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    series_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    indicator_date: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))

    def __repr__(self) -> str:
        return f"<MacroIndicator(series_id={self.series_id}, date={self.indicator_date}, value={self.value})>"
