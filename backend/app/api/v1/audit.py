from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.domain import AuditEventResponse, AuditChainVerificationResponse
from backend.app.services.audit import AuditService

router = APIRouter(prefix="/audit", tags=["Tamper-Evident Audit Trail"])


@router.get("/verify", response_model=AuditChainVerificationResponse)
def verify_audit_ledger_integrity(
    assessment_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Verifies the cryptographic SHA-256 hash chain of the audit log.
    Returns VALID if untouched, or INVALID with corrupted event identification.
    """
    service = AuditService(db)
    return service.verify_audit_chain(assessment_id=assessment_id)


@router.get("/events", response_model=List[AuditEventResponse])
def list_all_audit_events(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Lists recent audit events across all assessments."""
    service = AuditService(db)
    return service.list_all_events(limit=limit)


@router.get("/{assessment_id}", response_model=List[AuditEventResponse])
def get_assessment_audit_trail(
    assessment_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves all chronological audit events recorded for an assessment."""
    service = AuditService(db)
    events = service.get_events_for_assessment(assessment_id)
    if not events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No audit records found for assessment '{assessment_id}'.")
    return events
