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
    AuditEvent,
    ProductCategory,
    PaymentMethod,
    ReturnReason,
    ItemCondition,
    RiskLevel,
    BoundedRecommendation,
    EventType,
    ActorType,
)
from backend.app.schemas.domain import (
    CustomerCreate,
    OrderCreate,
    ReturnRequestCreate,
)
from backend.app.services.decision_engine import decision_engine_service
from backend.app.services.audit import AuditService, GENESIS_HASH


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_customer_and_order_schema_validation():
    now = datetime.datetime.utcnow()
    cust_data = CustomerCreate(
        customer_id="CUST_00001",
        account_age_days=150,
        total_order_count=10,
        historical_return_count=1,
        historical_return_rate=0.10,
        historical_refund_amount=89.50,
        historical_dispute_count=0,
    )
    assert cust_data.customer_id == "CUST_00001"
    assert cust_data.historical_return_rate == 0.10

    order_data = OrderCreate(
        order_id="ORD_00001",
        customer_id="CUST_00001",
        order_timestamp=now,
        order_amount=120.00,
        item_count=2,
        product_category=ProductCategory.APPAREL,
        discount_amount=10.0,
        payment_method=PaymentMethod.CREDIT_CARD,
    )
    assert order_data.order_amount == 120.00
    assert order_data.product_category == ProductCategory.APPAREL


def test_bounded_policy_rules():
    # Low risk
    rec_low, tier_low, reason_low = decision_engine_service.evaluate_policy(
        risk_probability=0.15, expected_loss=15.0, currency="INR"
    )
    assert rec_low == BoundedRecommendation.APPROVE
    assert tier_low == RiskLevel.LOW

    # Medium risk
    rec_med, tier_med, reason_med = decision_engine_service.evaluate_policy(
        risk_probability=0.45, expected_loss=60.0, currency="INR"
    )
    assert rec_med == BoundedRecommendation.REQUIRE_ADDITIONAL_VERIFICATION
    assert tier_med == RiskLevel.MEDIUM

    # High risk
    rec_high, tier_high, reason_high = decision_engine_service.evaluate_policy(
        risk_probability=0.85, expected_loss=250.0, currency="INR"
    )
    assert rec_high == BoundedRecommendation.MANUAL_REVIEW
    assert tier_high == RiskLevel.HIGH

    # Dispute override
    rec_disp, tier_disp, reason_disp = decision_engine_service.evaluate_policy(
        risk_probability=0.20, expected_loss=20.0, has_active_dispute=True, currency="INR"
    )
    assert rec_disp == BoundedRecommendation.MANUAL_REVIEW


def test_tamper_evident_audit_service(db_session):
    audit = AuditService(db=db_session)
    assmt_id = "ASSMT_TEST_001"

    # Step 1: Initial event
    e1 = audit.record_event(
        assessment_id=assmt_id,
        event_type=EventType.RISK_ASSESSMENT_CREATED,
        actor_type=ActorType.SYSTEM,
        actor_id="RISK_ENGINE_V1",
        decision="REQUIRE_ADDITIONAL_VERIFICATION",
        reason="Moderate risk score (0.55)",
        payload={"score": 0.55, "loss": 75.0},
        model_version="return-risk-hgb-v1",
        policy_version="return-policy-v1",
    )
    assert e1.previous_event_hash == GENESIS_HASH
    assert len(e1.event_hash) == 64

    # Step 2: Analyst override event
    e2 = audit.record_event(
        assessment_id=assmt_id,
        event_type=EventType.REVIEW_DECISION_MADE,
        actor_type=ActorType.MERCHANT_ANALYST,
        actor_id="ANALYST_SARAH",
        decision="APPROVE_RETURN",
        reason="Verified customer provided valid receipt and product tag photo.",
        payload={"manual_override": True, "override_code": "PHOTO_VALIDATED"},
        model_version="return-risk-hgb-v1",
        policy_version="return-policy-v1",
    )
    assert e2.previous_event_hash == e1.event_hash

    # Step 3: Integrity verification passes
    ver_res = audit.verify_audit_chain(assessment_id=assmt_id)
    assert ver_res.status == "VALID"

    # Step 4: Tampering detection check
    e1.decision = "TAMPERED_DECISION"
    db_session.commit()
    ver_tampered = audit.verify_audit_chain(assessment_id=assmt_id)
    assert ver_tampered.status == "INVALID"
    assert ver_tampered.corrupted_event_id == e1.audit_id
