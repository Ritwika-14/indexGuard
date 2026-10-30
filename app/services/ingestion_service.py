from decimal import Decimal

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.constituent import IndexConstituent
from app.models.ingestion_batch import BatchStatus, IngestionBatch
from app.schemas.constituent import (
    BatchCreateRequest,
    BatchCreateResponse,
    ConstituentInput,
    RejectedRecord,
)

WEIGHT_TOLERANCE = Decimal("0.005")


def ingest_batch(
    db: Session,
    request: BatchCreateRequest,
) -> BatchCreateResponse:
    """Validate a batch and persist accepted constituent records."""

    batch = IngestionBatch(
        source_filename=request.source_filename,
        status=BatchStatus.PENDING,
        records_received=len(request.records),
        records_accepted=0,
        records_rejected=0,
    )

    db.add(batch)
    db.flush()

    rejected_records: list[RejectedRecord] = []
    candidates: list[ConstituentInput] = []
    seen_tickers: set[str] = set()

    try:
        for record_number, raw_record in enumerate(request.records, start=1):
            raw_ticker = raw_record.get("ticker")
            ticker = raw_ticker.strip().upper() if isinstance(raw_ticker, str) else None

            try:
                constituent = ConstituentInput.model_validate(raw_record)
            except ValidationError as exc:
                rejected_records.append(
                    RejectedRecord(
                        record_number=record_number,
                        ticker=ticker,
                        errors=[
                            f"{'.'.join(str(part) for part in error['loc'])}: "
                            f"{error['msg']}"
                            for error in exc.errors()
                        ],
                    )
                )
                continue

            if constituent.ticker in seen_tickers:
                rejected_records.append(
                    RejectedRecord(
                        record_number=record_number,
                        ticker=constituent.ticker,
                        errors=["Duplicate ticker in this batch."],
                    )
                )
                continue

            seen_tickers.add(constituent.ticker)
            candidates.append(constituent)

        # A complete file must pass record validation as a whole.
        if request.is_complete and rejected_records:
            for record_number, constituent in enumerate(request.records, start=1):
                if not any(
                    rejected.record_number == record_number
                    for rejected in rejected_records
                ):
                    ticker_value = constituent.get("ticker")
                    rejected_records.append(
                        RejectedRecord(
                            record_number=record_number,
                            ticker=(
                                ticker_value.strip().upper()
                                if isinstance(ticker_value, str)
                                else None
                            ),
                            errors=[
                                "Complete batch rejected because another "
                                "record failed validation."
                            ],
                        )
                    )

            candidates = []

        # Check weights only when the caller declares a complete file.
        if request.is_complete and not rejected_records:
            total_weight = sum(
                (record.weight for record in candidates),
                start=Decimal("0"),
            )

            if abs(total_weight - Decimal("1")) > WEIGHT_TOLERANCE:
                for record_number, constituent in enumerate(candidates, start=1):
                    rejected_records.append(
                        RejectedRecord(
                            record_number=record_number,
                            ticker=constituent.ticker,
                            errors=[
                                f"Complete index weights total "
                                f"{total_weight:.6f}; expected approximately "
                                "1.000000 (100%)."
                            ],
                        )
                    )

                candidates = []

        for constituent in candidates:
            db.add(
                IndexConstituent(
                    batch_id=batch.id,
                    ticker=constituent.ticker,
                    company_name=constituent.company_name,
                    price=constituent.price,
                    market_cap=constituent.market_cap,
                    weight=constituent.weight,
                )
            )

        accepted_count = len(candidates)
        rejected_count = len(request.records) - accepted_count

        batch.records_accepted = accepted_count
        batch.records_rejected = rejected_count
        batch.status = (
            BatchStatus.COMPLETED if accepted_count > 0 else BatchStatus.FAILED
        )

        db.commit()
        db.refresh(batch)

        return BatchCreateResponse(
            batch_id=batch.id,
            status=batch.status.value,
            records_received=batch.records_received,
            records_accepted=batch.records_accepted,
            records_rejected=batch.records_rejected,
            rejected_records=rejected_records,
        )

    except Exception:
        db.rollback()
        raise
