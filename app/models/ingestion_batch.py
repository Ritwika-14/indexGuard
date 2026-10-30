from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BatchStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


def utc_now() -> datetime:
    return datetime.now(UTC)


class IngestionBatch(Base):
    __tablename__ = "ingestion_batches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[BatchStatus] = mapped_column(
        SQLAlchemyEnum(BatchStatus, name="batch_status"),
        default=BatchStatus.PENDING,
        nullable=False,
    )
    records_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_accepted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    constituents: Mapped[list["IndexConstituent"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )
