from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import RiskAssessment, RiskLevel
from backend.app.schemas.domain import RiskAssessmentRequest, RiskAssessmentResponse
from backend.app.services.risk_service import RiskService

router = APIRouter(prefix="/risk", tags=["Risk Assessment"])


@router.post("/assess", response_model=RiskAssessmentResponse, status_code=status.HTTP_201_CREATED)
def assess_transaction_risk(
    request: RiskAssessmentRequest,
    db: Session = Depends(get_db),
):
    """
    Evaluates point-in-time return risk, computes feature attributions, expected loss,
    enforces bounded policies, logs audit records, and routes to human review if appropriate.
    """
    try:
        service = RiskService(db)
        return service.assess_return_risk(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Risk assessment failure: {str(e)}")


@router.get("/assessments", response_model=List[RiskAssessmentResponse])
def list_risk_assessments(
    risk_level: Optional[RiskLevel] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Lists risk assessments with optional risk level filtering."""
    query = db.query(RiskAssessment)
    if risk_level:
        query = query.filter(RiskAssessment.risk_level == risk_level)
    records = query.order_by(RiskAssessment.created_at.desc()).limit(limit).all()
    service = RiskService(db)
    return [service._to_response(r) for r in records]


@router.get("/{assessment_id}", response_model=RiskAssessmentResponse)
def get_risk_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves an existing risk assessment by ID."""
    service = RiskService(db)
    result = service.get_assessment(assessment_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Assessment '{assessment_id}' not found.")
    return result
