"""
Human Review Workflow Service.

Manages review queue cases, state transitions (PENDING_REVIEW -> RESOLVED),
analyst authorization controls, idempotency, and stores human decisions separately
from automated model recommendations.
"""

import uuid
import datetime
import json
from typing import List, Optional, Union
from sqlalchemy.orm import Session
from backend.app.models.entities import (
    ReviewCase,
    RiskAssessment,
    ReviewStatus,
    HumanDecisionType,
    UserRole,
    EventType,
    ActorType,
)
from backend.app.schemas.domain import HumanDecisionSubmission, ReviewCaseResponse, RiskFactorContribution
from backend.app.services.audit import AuditService


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def create_review_case_if_needed(self, assessment: RiskAssessment) -> Optional[ReviewCase]:
        """Creates a review queue case if an assessment is flagged for verification or manual review."""
        existing_case = self.db.query(ReviewCase).filter(ReviewCase.assessment_id == assessment.assessment_id).first()
        if existing_case:
            return existing_case

        case_id = f"CASE_{uuid.uuid4().hex[:12].upper()}"
        case = ReviewCase(
            case_id=case_id,
            assessment_id=assessment.assessment_id,
            return_id=assessment.return_id,
            order_id=assessment.order_id,
            customer_id=assessment.customer_id,
            status=ReviewStatus.PENDING_REVIEW,
            model_recommendation=assessment.model_recommendation,
        )

        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)

        # Audit review queue entry
        self.audit.record_event(
            assessment_id=assessment.assessment_id,
            event_type=EventType.REVIEW_STARTED,
            actor_type=ActorType.SYSTEM,
            actor_id="REVIEW_DISPATCHER",
            decision=assessment.model_recommendation.value,
            reason=f"Case added to risk analyst triage queue with status {ReviewStatus.PENDING_REVIEW.value}.",
            payload={"case_id": case_id, "risk_probability": assessment.risk_probability},
            model_version=assessment.model_version,
            policy_version=assessment.policy_version,
        )

        return case

    def list_review_cases(self, status: Optional[Union[ReviewStatus, str]] = None) -> List[ReviewCaseResponse]:
        """Lists review queue cases with optional status filtering."""
        query = self.db.query(ReviewCase, RiskAssessment).join(
            RiskAssessment, ReviewCase.assessment_id == RiskAssessment.assessment_id
        )
        if status:
            if isinstance(status, str):
                try:
                    status = ReviewStatus(status)
                except Exception:
                    pass
            query = query.filter(ReviewCase.status == status)

        records = query.order_by(ReviewCase.created_at.desc()).all()
        results = []

        for case, assmt in records:
            factors = []
            try:
                raw_factors = json.loads(assmt.top_risk_factors_json)
                factors = [RiskFactorContribution(**f) for f in raw_factors]
            except Exception:
                pass

            results.append(ReviewCaseResponse(
                case_id=case.case_id,
                assessment_id=assmt.assessment_id,
                return_id=case.return_id,
                order_id=case.order_id,
                customer_id=case.customer_id,
                status=case.status,
                model_recommendation=case.model_recommendation,
                risk_probability=assmt.risk_probability,
                risk_level=assmt.risk_level,
                expected_loss=assmt.expected_loss,
                currency=assmt.currency,
                top_risk_factors=factors,
                human_decision=case.human_decision,
                decision_reason=case.decision_reason,
                reviewer_id=case.reviewer_id,
                reviewer_role=case.reviewer_role,
                created_at=case.created_at,
                resolved_at=case.resolved_at,
            ))

        return results

    def get_review_case(self, case_id: str) -> Optional[ReviewCaseResponse]:
        """Retrieves a single review case with full risk context."""
        record = (
            self.db.query(ReviewCase, RiskAssessment)
            .join(RiskAssessment, ReviewCase.assessment_id == RiskAssessment.assessment_id)
            .filter(ReviewCase.case_id == case_id)
            .first()
        )
        if not record:
            return None

        case, assmt = record
        factors = []
        try:
            raw_factors = json.loads(assmt.top_risk_factors_json)
            factors = [RiskFactorContribution(**f) for f in raw_factors]
        except Exception:
            pass

        return ReviewCaseResponse(
            case_id=case.case_id,
            assessment_id=assmt.assessment_id,
            return_id=case.return_id,
            order_id=case.order_id,
            customer_id=case.customer_id,
            status=case.status,
            model_recommendation=case.model_recommendation,
            risk_probability=assmt.risk_probability,
            risk_level=assmt.risk_level,
            expected_loss=assmt.expected_loss,
            currency=assmt.currency,
            top_risk_factors=factors,
            human_decision=case.human_decision,
            decision_reason=case.decision_reason,
            reviewer_id=case.reviewer_id,
            reviewer_role=case.reviewer_role,
            created_at=case.created_at,
            resolved_at=case.resolved_at,
        )

    def submit_human_decision(
        self,
        case_id: str,
        submission: HumanDecisionSubmission,
    ) -> ReviewCaseResponse:
        """
        Records an authorized analyst decision, updates review case state,
        and logs a tamper-evident audit record.
        """
        if submission.reviewer_role not in [UserRole.RISK_ANALYST, UserRole.RISK_ADMIN]:
            raise PermissionError("Actor is not authorized to submit human risk review decisions.")

        case = self.db.query(ReviewCase).filter(ReviewCase.case_id == case_id).first()
        if not case:
            raise ValueError(f"Review case '{case_id}' not found.")

        if case.status == ReviewStatus.RESOLVED:
            raise ValueError(f"Review case '{case_id}' has already been resolved with decision '{case.human_decision}'. Duplicate submissions are prevented.")

        now = datetime.datetime.utcnow()
        case.status = ReviewStatus.RESOLVED
        case.human_decision = submission.decision
        case.decision_reason = submission.reason
        case.reviewer_id = submission.reviewer_id
        case.reviewer_role = submission.reviewer_role
        case.resolved_at = now

        self.db.commit()
        self.db.refresh(case)

        assmt = self.db.query(RiskAssessment).filter(RiskAssessment.assessment_id == case.assessment_id).first()
        
        self.audit.record_event(
            assessment_id=case.assessment_id,
            event_type=EventType.REVIEW_DECISION_MADE,
            actor_type=ActorType.MERCHANT_ANALYST if submission.reviewer_role == UserRole.RISK_ANALYST else ActorType.RISK_ADMIN,
            actor_id=submission.reviewer_id,
            decision=submission.decision.value,
            reason=submission.reason,
            payload={
                "case_id": case_id,
                "human_decision": submission.decision.value,
                "model_recommendation": case.model_recommendation.value,
                "disagreement": (case.model_recommendation.value != submission.decision.value),
            },
            model_version=assmt.model_version if assmt else None,
            policy_version=assmt.policy_version if assmt else None,
            timestamp=now,
        )

        return self.get_review_case(case_id)
