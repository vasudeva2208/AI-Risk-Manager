from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import ReviewStatus
from backend.app.schemas.domain import HumanDecisionSubmission, ReviewCaseResponse
from backend.app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Human Review Queue"])


@router.get("", response_model=List[ReviewCaseResponse])
def list_review_cases(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lists review queue items with optional status filtering (e.g. PENDING_REVIEW, RESOLVED)."""
    service = ReviewService(db)
    status_enum = None
    if status:
        try:
            status_enum = ReviewStatus(status)
        except Exception:
            pass
    return service.list_review_cases(status=status_enum)


@router.get("/{case_id}", response_model=ReviewCaseResponse)
def get_review_case(
    case_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves a single review case with full risk factor breakdown and decision history."""
    service = ReviewService(db)
    result = service.get_review_case(case_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Review case '{case_id}' not found.")
    return result


@router.post("/{case_id}/decision", response_model=ReviewCaseResponse)
def submit_review_decision(
    case_id: str,
    submission: HumanDecisionSubmission,
    db: Session = Depends(get_db),
):
    """
    Submits an authorized human reviewer decision with mandatory rationale.
    Updates case resolution status, stores human decision separately from model recommendation,
    and logs a tamper-evident audit record.
    """
    service = ReviewService(db)
    try:
        return service.submit_human_decision(case_id, submission)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Review decision submission failed: {str(e)}")
