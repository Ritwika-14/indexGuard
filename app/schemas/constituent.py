"""Pydantic schemas will be implemented in Phase 3."""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConstituentInput(BaseModel):
    """Validate one incoming index constituent record."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    ticker: str = Field(min_length=1, max_length=20)
    company_name: str = Field(min_length=1, max_length=255)
    price: Decimal = Field(gt=0, max_digits=14, decimal_places=4)
    market_cap: Decimal = Field(ge=0, max_digits=20, decimal_places=2)
    weight: Decimal = Field(ge=0, le=1, max_digits=9, decimal_places=6)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.upper()

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, value: str) -> str:
        if not value:
            raise ValueError("Company name cannot be empty")
        return value


class BatchCreateRequest(BaseModel):
    """Request body for a batch of incoming records."""

    source_filename: str | None = Field(default=None, max_length=255)
    is_complete: bool = False
    records: list[dict[str, Any]] = Field(min_length=1, max_length=5000)


class RejectedRecord(BaseModel):
    """Validation errors for a rejected record."""

    record_number: int
    ticker: str | None = None
    errors: list[str]


class BatchCreateResponse(BaseModel):
    batch_id: int
    status: str
    records_received: int
    records_accepted: int
    records_rejected: int
    rejected_records: list[RejectedRecord]


class ConstituentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    company_name: str
    price: Decimal
    market_cap: Decimal
    weight: Decimal


class BatchDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_filename: str | None
    status: str
    records_received: int
    records_accepted: int
    records_rejected: int
    constituents: list[ConstituentResponse]
