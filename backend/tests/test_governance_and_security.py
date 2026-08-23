import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base
from backend.app.models.entities import (
    Customer,
    Order,
    ReturnRequest,
    RiskAssessment,
    ReviewCase,
    ReviewStatus,
    HumanDecisionType,
    UserRole,
    ProductCategory,
    PaymentMethod,
    ReturnReason,
    ItemCondition,
    RiskLevel,
    BoundedRecommendation,
    EventType,
    ActorType,
    AuditEvent,
)
from backend.app.services.review_service import ReviewService
from backend.app.services.audit import AuditService, compute_event_hash
from backend.app.services.loss_estimator import loss_estimator_service
from backend.app.services.decision_engine import decision_engine_service
from backend.app.schemas.domain import HumanDecisionSubmission


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_assessment(db_session):
    now = datetime.datetime.utcnow()
    cust = Customer(
        customer_id="CUST_GOV_001",
        account_age_days=45,
        total_order_count=5,
        historical_return_count=1,
        historical_return_rate=0.2,
        historical_refund_amount=1500.0,
        historical_dispute_count=0,
    )
    order = Order(
        order_id="ORD_GOV_001",
        customer_id="CUST_GOV_001",
        order_timestamp=now - datetime.timedelta(days=10),
        order_amount=3500.0,
        item_count=1,
        product_category=ProductCategory.APPAREL,
        discount_amount=0.0,
        payment_method=PaymentMethod.CREDIT_CARD,
    )
    ret_req = ReturnRequest(
        return_id="RET_GOV_001",
        order_id="ORD_GOV_001",
        request_timestamp=now,
        return_reason=ReturnReason.WRONG_SIZE,
        item_condition_declared=ItemCondition.OPENED_UNUSED,
        refund_amount_requested=3500.0,
        return_method="MAIL_IN",
    )
    assmt = RiskAssessment(
        assessment_id="ASSMT_GOV_001",
        return_id="RET_GOV_001",
        order_id="ORD_GOV_001",
        customer_id="CUST_GOV_001",
        model_version="return-risk-hgb-v1",
        feature_version="v2_point_in_time_23f",
        risk_probability=0.75,
        risk_level=RiskLevel.HIGH,
        threshold_applied=0.30,
        expected_loss=3000.0,
        estimated_loss_if_abuse=4205.50,
        currency="INR",
        loss_calculation_version="v1_asymmetric_linear",
        policy_version="return-policy-v1",
        model_recommendation=BoundedRecommendation.MANUAL_REVIEW,
        top_risk_factors_json="[]",
    )
    db_session.add_all([cust, order, ret_req, assmt])
    db_session.commit()
    return assmt


def test_resolved_decision_cannot_be_silently_modified(db_session, sample_assessment):
    review_svc = ReviewService(db_session)
    case = review_svc.create_review_case_if_needed(sample_assessment)

    submission = HumanDecisionSubmission(
        decision=HumanDecisionType.REQUEST_ADDITIONAL_VERIFICATION,
        reason="Ask customer for garment tag photos",
        reviewer_id="ANALYST_PRIYA",
        reviewer_role=UserRole.RISK_ANALYST,
    )
    resolved = review_svc.submit_human_decision(case.case_id, submission)
    assert resolved.status == ReviewStatus.RESOLVED

    # Second attempt to submit or overwrite must be blocked
    submission2 = HumanDecisionSubmission(
        decision=HumanDecisionType.APPROVE_RETURN,
        reason="Second decision attempt should fail",
        reviewer_id="ADMIN_VIKRAM",
        reviewer_role=UserRole.RISK_ADMIN,
    )
    with pytest.raises(ValueError, match="already been resolved"):
        review_svc.submit_human_decision(case.case_id, submission2)


def test_audit_event_deletion_detected(db_session, sample_assessment):
    audit_svc = AuditService(db_session)
    e1 = audit_svc.record_event(
        assessment_id="ASSMT_DEL_TEST",
        event_type=EventType.RISK_ASSESSMENT_CREATED,
        actor_type=ActorType.SYSTEM,
        actor_id="ENGINE",
        decision="HIGH",
        reason="Initial score",
        payload={"score": 0.8},
    )
    e2 = audit_svc.record_event(
        assessment_id="ASSMT_DEL_TEST",
        event_type=EventType.REVIEW_DECISION_MADE,
        actor_type=ActorType.MERCHANT_ANALYST,
        actor_id="ANALYST_1",
        decision="APPROVE",
        reason="Verified",
        payload={},
    )
    
    # Confirm initial valid chain
    res = audit_svc.verify_audit_chain(assessment_id="ASSMT_DEL_TEST")
    assert res.status == "VALID"

    # Delete e1
    db_session.delete(e1)
    db_session.commit()

    # Chain verification detects break (previous_hash of e2 no longer matches genesis)
    res_after_del = audit_svc.verify_audit_chain(assessment_id="ASSMT_DEL_TEST")
    assert res_after_del.status == "INVALID"


def test_no_adversarial_endpoints_or_methods():
    from backend.app.main import app
    routes = [route.path for route in app.routes]
    
    # Assert prohibited adversarial routes do not exist
    banned_routes = [
        "/api/v1/evade",
        "/api/v1/optimize-score",
        "/api/v1/gradients",
        "/api/v1/probe-threshold",
        "/api/v1/financial/deny",
        "/api/v1/financial/freeze",
    ]
    for banned in banned_routes:
        assert banned not in routes


def test_pii_minimization_in_audit_payload(db_session, sample_assessment):
    audit_svc = AuditService(db_session)
    evt = audit_svc.record_event(
        assessment_id=sample_assessment.assessment_id,
        event_type=EventType.RISK_ASSESSMENT_CREATED,
        actor_type=ActorType.SYSTEM,
        actor_id="RISK_SCORING_SERVICE",
        decision="HIGH",
        reason="Evaluated risk score",
        payload={
            "customer_id": "CUST_GOV_001",
            "score": 0.75,
            "risk_level": "HIGH",
        },
    )
    # Ensure sensitive raw PII is absent from payload
    assert "password" not in evt.payload_json
    assert "credit_card_full" not in evt.payload_json
    assert "ssn" not in evt.payload_json
    assert "bank_routing_number" not in evt.payload_json


def test_expected_loss_currency_conversion_consistency():
    loss_inr = loss_estimator_service.compute_expected_loss(0.5, 1000.0, currency="INR")
    loss_usd = loss_estimator_service.compute_expected_loss(0.5, 1000.0 / 83.0, currency="USD")
    assert pytest.approx(loss_inr.expected_loss, rel=1e-2) == round(loss_usd.expected_loss * 83.0, 2)


def test_unknown_human_decision_rejected():
    with pytest.raises(ValueError):
        HumanDecisionSubmission(
            decision="UNRECOGNIZED_ACTION",
            reason="This should fail schema validation",
            reviewer_id="ANALYST_1",
            reviewer_role=UserRole.RISK_ANALYST,
        )


def test_policy_output_is_recommendation_not_financial_execution():
    rec, tier, reason = decision_engine_service.evaluate_policy(risk_probability=0.10, expected_loss=100.0)
    assert rec == BoundedRecommendation.APPROVE
    assert "Policy recommendation: APPROVE" in reason
    assert "automatic authorization" not in reason.lower()
    # Confirm no financial execution function is called
    assert not hasattr(rec, "execute_refund")
    assert not hasattr(rec, "authorize_fund_transfer")
