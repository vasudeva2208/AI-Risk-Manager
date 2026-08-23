"""
Risk Assessment Coordinator Service.

Orchestrates:
Input Validation & Persistence
↓
Point-in-Time Point Feature Calculation & Model Scoring
↓
Technical Feature Attribution & Explainability
↓
Expected Loss Calculation (INR default / USD)
↓
Deterministic Bounded Policy Execution
↓
Risk Assessment Persistence
↓
Audit Event Chaining
↓
Review Queue Ingestion
"""

import uuid
import datetime
import json
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.entities import (
    Customer,
    Order,
    ReturnRequest,
    RiskAssessment,
    BoundedRecommendation,
    EventType,
    ActorType,
)
from backend.app.schemas.domain import (
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    RiskFactorContribution,
)
from backend.app.services.risk_scoring import risk_scoring_service
from backend.app.services.explainability import explainability_service
from backend.app.services.loss_estimator import loss_estimator_service
from backend.app.services.decision_engine import decision_engine_service
from backend.app.services.audit import AuditService
from backend.app.services.review_service import ReviewService


class RiskService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)
        self.reviews = ReviewService(db)

    def assess_return_risk(self, request: RiskAssessmentRequest) -> RiskAssessmentResponse:
        """
        Executes end-to-end idempotent risk assessment pipeline.
        """
        # 1. Idempotency Check
        if request.idempotency_key:
            existing_assmt = (
                self.db.query(RiskAssessment)
                .filter(RiskAssessment.idempotency_key == request.idempotency_key)
                .first()
            )
            if existing_assmt:
                return self._to_response(existing_assmt)

        # 2. Persist / Upsert Domain Entities (Customer, Order, ReturnRequest)
        self._upsert_customer(request.customer)
        self._upsert_order(request.order)
        self._upsert_return_request(request.return_request)

        # 3. Model Scoring
        score_result = risk_scoring_service.score_transaction(
            customer=request.customer,
            order=request.order,
            return_req=request.return_request,
            model_version=request.preferred_model_version,
        )
        risk_prob = score_result["risk_probability"]
        model_ver = score_result["model_version"]
        feat_ver = score_result["feature_version"]
        thresh_applied = score_result["threshold_applied"]
        df_row = score_result["df_row"]
        model_instance = score_result["model_instance"]

        # 4. Explainability
        factor_explanations = explainability_service.explain_prediction(
            model_instance=model_instance,
            df_row=df_row,
            top_k=4,
        )
        factors_json = json.dumps([f.model_dump() for f in factor_explanations])

        # 5. Expected Loss Calculation
        loss_result = loss_estimator_service.compute_expected_loss(
            risk_probability=risk_prob,
            refund_amount=float(request.return_request.refund_amount_requested),
            currency=request.target_currency,
        )
        expected_loss_val = loss_result.expected_loss
        estimated_loss_abuse = loss_result.estimated_loss_if_abuse

        # 6. Deterministic Bounded Policy Evaluation
        has_active_dispute = request.customer.historical_dispute_count > 0
        recommendation, risk_level, policy_reason = decision_engine_service.evaluate_policy(
            risk_probability=risk_prob,
            expected_loss=expected_loss_val,
            has_active_dispute=has_active_dispute,
            currency=request.target_currency,
        )

        # 7. Persist Risk Assessment
        assessment_id = f"ASSMT_{uuid.uuid4().hex[:12].upper()}"
        assessment = RiskAssessment(
            assessment_id=assessment_id,
            return_id=request.return_request.return_id,
            order_id=request.order.order_id,
            customer_id=request.customer.customer_id,
            idempotency_key=request.idempotency_key,
            model_version=model_ver,
            feature_version=feat_ver,
            risk_probability=risk_prob,
            risk_level=risk_level,
            threshold_applied=thresh_applied,
            expected_loss=expected_loss_val,
            estimated_loss_if_abuse=estimated_loss_abuse,
            currency=request.target_currency,
            loss_calculation_version=loss_estimator_service.version,
            policy_version=decision_engine_service.policy_version,
            model_recommendation=recommendation,
            top_risk_factors_json=factors_json,
            created_at=datetime.datetime.utcnow(),
        )

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        # 8. Audit Trail Events
        # Assessment created event
        self.audit.record_event(
            assessment_id=assessment_id,
            event_type=EventType.RISK_ASSESSMENT_CREATED,
            actor_type=ActorType.SYSTEM,
            actor_id="RISK_SCORING_ENGINE",
            decision=risk_level.value,
            reason=f"Point-in-time point risk evaluated: probability {risk_prob:.2f} ({risk_level.value}).",
            payload={
                "risk_probability": risk_prob,
                "expected_loss": expected_loss_val,
                "currency": request.target_currency,
                "threshold": thresh_applied,
            },
            model_version=model_ver,
            policy_version=decision_engine_service.policy_version,
        )

        # Policy recommendation event
        self.audit.record_event(
            assessment_id=assessment_id,
            event_type=EventType.POLICY_EVALUATED,
            actor_type=ActorType.SYSTEM,
            actor_id="BOUNDED_POLICY_ENGINE",
            decision=recommendation.value,
            reason=policy_reason,
            payload={
                "recommendation": recommendation.value,
                "policy_version": decision_engine_service.policy_version,
            },
            model_version=model_ver,
            policy_version=decision_engine_service.policy_version,
        )

        # 9. Review Queue Entry (for High risk or verification)
        if recommendation in [BoundedRecommendation.MANUAL_REVIEW, BoundedRecommendation.REQUIRE_ADDITIONAL_VERIFICATION]:
            self.reviews.create_review_case_if_needed(assessment)

        return self._to_response(assessment)

    def get_assessment(self, assessment_id: str) -> Optional[RiskAssessmentResponse]:
        """Retrieves a risk assessment by ID."""
        assmt = self.db.query(RiskAssessment).filter(RiskAssessment.assessment_id == assessment_id).first()
        if not assmt:
            return None
        return self._to_response(assmt)

    def _to_response(self, assmt: RiskAssessment) -> RiskAssessmentResponse:
        factors = []
        try:
            raw_factors = json.loads(assmt.top_risk_factors_json)
            factors = [RiskFactorContribution(**f) for f in raw_factors]
        except Exception:
            pass

        return RiskAssessmentResponse(
            assessment_id=assmt.assessment_id,
            return_id=assmt.return_id,
            order_id=assmt.order_id,
            customer_id=assmt.customer_id,
            risk_probability=assmt.risk_probability,
            risk_level=assmt.risk_level,
            threshold_applied=assmt.threshold_applied,
            expected_loss=assmt.expected_loss,
            estimated_loss_if_abuse=assmt.estimated_loss_if_abuse,
            currency=assmt.currency,
            model_version=assmt.model_version,
            feature_version=assmt.feature_version,
            policy_version=assmt.policy_version,
            recommendation=assmt.model_recommendation,
            top_risk_factors=factors,
            created_at=assmt.created_at,
        )

    def _upsert_customer(self, c):
        existing = self.db.query(Customer).filter(Customer.customer_id == c.customer_id).first()
        if not existing:
            cust = Customer(**c.model_dump())
            self.db.add(cust)
            self.db.commit()

    def _upsert_order(self, o):
        existing = self.db.query(Order).filter(Order.order_id == o.order_id).first()
        if not existing:
            order_record = Order(**o.model_dump())
            self.db.add(order_record)
            self.db.commit()

    def _upsert_return_request(self, r):
        existing = self.db.query(ReturnRequest).filter(ReturnRequest.return_id == r.return_id).first()
        if not existing:
            ret_record = ReturnRequest(**r.model_dump())
            self.db.add(ret_record)
            self.db.commit()
