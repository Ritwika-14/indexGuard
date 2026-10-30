"""Ingestion routes will be implemented in Phase 3."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ingestion_batch import IngestionBatch
from app.schemas.constituent import (
    BatchCreateRequest,
    BatchCreateResponse,
    BatchDetailResponse,
)
from app.services.ingestion_service import ingest_batch

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/batches", response_model=BatchCreateResponse, status_code=201)
def create_ingestion_batch(
    request: BatchCreateRequest,
    db: Session = Depends(get_db),
) -> BatchCreateResponse:
    return ingest_batch(db, request)


@router.get("/batches/{batch_id}", response_model=BatchDetailResponse)
def get_ingestion_batch(
    batch_id: int,
    db: Session = Depends(get_db),
) -> BatchDetailResponse:
    batch = db.get(IngestionBatch, batch_id)

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ingestion batch {batch_id} was not found",
        )

    return BatchDetailResponse.model_validate(batch)
