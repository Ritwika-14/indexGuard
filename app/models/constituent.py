from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class IndexConstituent(Base):
    __tablename__ = "index_constituents"
    __table_args__ = (
        UniqueConstraint("batch_id", "ticker", name="uq_batch_ticker"),
        CheckConstraint("price > 0", name="ck_constituent_price_positive"),
        CheckConstraint(
            "market_cap >= 0", name="ck_constituent_market_cap_nonnegative"
        ),
        CheckConstraint(
            "weight >= 0 AND weight <= 1", name="ck_constituent_weight_range"
        ),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("ingestion_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    market_cap: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    batch: Mapped["IngestionBatch"] = relationship(back_populates="constituents")
