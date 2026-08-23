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
from backend.app.services.audit import AuditService, GENESIS_HASH
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
        customer_id="CUST_REV_001",
        account_age_days=30,
        total_order_count=2,
        historical_return_count=1,
        historical_return_rate=0.5,
        historical_refund_amount=2000.0,
        historical_dispute_count=0,
    )
    order = Order(
        order_id="ORD_REV_001",
        customer_id="CUST_REV_001",
        order_timestamp=now - datetime.timedelta(days=10),
        order_amount=5000.0,
        item_count=1,
        product_category=ProductCategory.APPAREL,
        discount_amount=0.0,
        payment_method=PaymentMethod.CREDIT_CARD,
    )
    ret_req = ReturnRequest(
        return_id="RET_REV_001",
        order_id="ORD_REV_001",
        request_timestamp=now,
        return_reason=ReturnReason.WRONG_SIZE,
        item_condition_declared=ItemCondition.OPENED_UNUSED,
        refund_amount_requested=5000.0,
        return_method="MAIL_IN",
    )
    assmt = RiskAssessment(
        assessment_id="ASSMT_REV_001",
        return_id="RET_REV_001",
        order_id="ORD_REV_001",
        customer_id="CUST_REV_001",
        model_version="return-risk-hgb-v1",
        feature_version="v2_point_in_time_23f",
        risk_probability=0.78,
        risk_level=RiskLevel.HIGH,
        threshold_applied=0.30,
        expected_loss=4450.0,
        estimated_loss_if_abuse=5705.50,
        currency="INR",
        loss_calculation_version="v1_asymmetric_linear",
        policy_version="return-policy-v1",
        model_recommendation=BoundedRecommendation.MANUAL_REVIEW,
        top_risk_factors_json="[]",
    )
    db_session.add_all([cust, order, ret_req, assmt])
    db_session.commit()
    return assmt


def test_human_review_workflow_and_decision_separation(db_session, sample_assessment):
    review_svc = ReviewService(db_session)

    # 1. Create review case
    case = review_svc.create_review_case_if_needed(sample_assessment)
    assert case is not None
    assert case.status == ReviewStatus.PENDING_REVIEW
    assert case.model_recommendation == BoundedRecommendation.MANUAL_REVIEW
    assert case.human_decision is None

    # 2. Submit human decision
    submission = HumanDecisionSubmission(
        decision=HumanDecisionType.APPROVE_RETURN,
        reason="Verified customer provided valid invoice and garment tags attached.",
        reviewer_id="ANALYST_PRIYA",
        reviewer_role=UserRole.RISK_ANALYST,
    )
    resolved_case = review_svc.submit_human_decision(case.case_id, submission)
    assert resolved_case.status == ReviewStatus.RESOLVED
    assert resolved_case.model_recommendation == BoundedRecommendation.MANUAL_REVIEW
    assert resolved_case.human_decision == HumanDecisionType.APPROVE_RETURN
    assert resolved_case.reviewer_id == "ANALYST_PRIYA"
    assert resolved_case.resolved_at is not None

    # 3. Duplicate decision submission is prevented
    with pytest.raises(ValueError, match="already been resolved"):
        review_svc.submit_human_decision(case.case_id, submission)


def test_unauthorized_role_and_empty_reason_rejection(db_session, sample_assessment):
    review_svc = ReviewService(db_session)
    case = review_svc.create_review_case_if_needed(sample_assessment)

    # Unauthorized role (SYSTEM)
    with pytest.raises(PermissionError, match="Actor is not authorized"):
        submission_unauth = HumanDecisionSubmission(
            decision=HumanDecisionType.APPROVE_RETURN,
            reason="Approved without proper role",
            reviewer_id="SYSTEM_BOT",
            reviewer_role=UserRole.SYSTEM,
        )
        review_svc.submit_human_decision(case.case_id, submission_unauth)

    # Empty / whitespace-only reason rejection
    with pytest.raises(ValueError, match="at least 5 characters"):
        submission_empty = HumanDecisionSubmission(
            decision=HumanDecisionType.APPROVE_RETURN,
            reason="   ",
            reviewer_id="ANALYST_PRIYA",
            reviewer_role=UserRole.RISK_ANALYST,
        )
        review_svc.submit_human_decision(case.case_id, submission_empty)


def test_tamper_evident_audit_chain_verification_and_corruption_detection(db_session, sample_assessment):
    audit_svc = AuditService(db_session)

    # Step 1: Record chained events
    e1 = audit_svc.record_event(
        assessment_id=sample_assessment.assessment_id,
        event_type=EventType.RISK_ASSESSMENT_CREATED,
        actor_type=ActorType.SYSTEM,
        actor_id="RISK_ENGINE",
        decision="HIGH",
        reason="Score 0.78 exceeds threshold",
        payload={"score": 0.78},
        model_version="return-risk-hgb-v1",
        policy_version="return-policy-v1",
    )
    e2 = audit_svc.record_event(
        assessment_id=sample_assessment.assessment_id,
        event_type=EventType.REVIEW_DECISION_MADE,
        actor_type=ActorType.MERCHANT_ANALYST,
        actor_id="ANALYST_PRIYA",
        decision="APPROVE_RETURN",
        reason="Verified photos",
        payload={"approved": True},
        model_version="return-risk-hgb-v1",
        policy_version="return-policy-v1",
    )

    # Verification passes
    res_valid = audit_svc.verify_audit_chain(assessment_id=sample_assessment.assessment_id)
    assert res_valid.status == "VALID"
    assert res_valid.total_events_checked >= 2
    assert res_valid.corrupted_event_id is None

    # Step 2: Simulate Tampering on e1 decision
    e1.decision = "LOW_TAMPERED"
    db_session.commit()

    # Verification detects corruption
    res_invalid = audit_svc.verify_audit_chain(assessment_id=sample_assessment.assessment_id)
    assert res_invalid.status == "INVALID"
    assert res_invalid.corrupted_event_id == e1.audit_id
    assert "Tampering detected" in res_invalid.message


def test_audit_tamper_scenarios_actor_payload_timestamp(db_session, sample_assessment):
    audit_svc = AuditService(db_session)

    # Test 1: Actor tampering
    e1 = audit_svc.record_event(
        assessment_id="ASSMT_TAMPER_01",
        event_type=EventType.RISK_ASSESSMENT_CREATED,
        actor_type=ActorType.SYSTEM,
        actor_id="RISK_ENGINE",
        decision="HIGH",
        reason="Score 0.85",
        payload={"score": 0.85},
    )
    e1.actor_id = "ANALYST_IMPERSONATED"
    db_session.commit()
    res1 = audit_svc.verify_audit_chain(assessment_id="ASSMT_TAMPER_01")
    assert res1.status == "INVALID"

    # Test 2: Payload tampering
    e2 = audit_svc.record_event(
        assessment_id="ASSMT_TAMPER_02",
        event_type=EventType.POLICY_EVALUATED,
        actor_type=ActorType.SYSTEM,
        actor_id="POLICY_ENGINE",
        decision="MANUAL_REVIEW",
        reason="Policy trigger",
        payload={"threshold": 0.30},
    )
    e2.payload_json = '{"threshold":0.99}'
    db_session.commit()
    res2 = audit_svc.verify_audit_chain(assessment_id="ASSMT_TAMPER_02")
    assert res2.status == "INVALID"

    # Test 3: Timestamp tampering
    e3 = audit_svc.record_event(
        assessment_id="ASSMT_TAMPER_03",
        event_type=EventType.REVIEW_STARTED,
        actor_type=ActorType.MERCHANT_ANALYST,
        actor_id="ANALYST_PRIYA",
        decision="UNDER_REVIEW",
        reason="Triage claim",
        payload={},
    )
    e3.timestamp = datetime.datetime(2020, 1, 1, 0, 0, 0)
    db_session.commit()
    res3 = audit_svc.verify_audit_chain(assessment_id="ASSMT_TAMPER_03")
    assert res3.status == "INVALID"


def test_human_override_analytics(db_session, sample_assessment):
    review_svc = ReviewService(db_session)
    case = review_svc.create_review_case_if_needed(sample_assessment)

    # Model recommended MANUAL_REVIEW, Human decides APPROVE_RETURN => Override
    submission = HumanDecisionSubmission(
        decision=HumanDecisionType.APPROVE_RETURN,
        reason="Override model with physical receipt proof",
        reviewer_id="ADMIN_VIKRAM",
        reviewer_role=UserRole.RISK_ADMIN,
    )
    resolved = review_svc.submit_human_decision(case.case_id, submission)
    assert resolved.human_decision == HumanDecisionType.APPROVE_RETURN
    assert resolved.model_recommendation == BoundedRecommendation.MANUAL_REVIEW
    # Both persisted distinctly
    assert resolved.human_decision.value != resolved.model_recommendation.value
