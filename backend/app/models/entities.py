import datetime
import enum
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    Boolean,
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class ProductCategory(str, enum.Enum):
    APPAREL = "APPAREL"
    ELECTRONICS = "ELECTRONICS"
    LUXURY_GOODS = "LUXURY_GOODS"
    BEAUTY = "BEAUTY"
    HOME_GARDEN = "HOME_GARDEN"


class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    BUY_NOW_PAY_LATER = "BUY_NOW_PAY_LATER"
    STORE_CREDIT = "STORE_CREDIT"


class ReturnReason(str, enum.Enum):
    DEFECTIVE = "DEFECTIVE"
    WRONG_SIZE = "WRONG_SIZE"
    NOT_AS_DESCRIBED = "NOT_AS_DESCRIBED"
    CHANGED_MIND = "CHANGED_MIND"
    ARRIVED_LATE = "ARRIVED_LATE"


class ItemCondition(str, enum.Enum):
    UNOPENED = "UNOPENED"
    OPENED_UNUSED = "OPENED_UNUSED"
    WORN_OR_USED = "WORN_OR_USED"
    DAMAGED = "DAMAGED"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class BoundedRecommendation(str, enum.Enum):
    APPROVE = "APPROVE"
    REQUIRE_ADDITIONAL_VERIFICATION = "REQUIRE_ADDITIONAL_VERIFICATION"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class ReviewStatus(str, enum.Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"


class HumanDecisionType(str, enum.Enum):
    APPROVE_RETURN = "APPROVE_RETURN"
    REQUEST_ADDITIONAL_VERIFICATION = "REQUEST_ADDITIONAL_VERIFICATION"
    ESCALATE = "ESCALATE"


class UserRole(str, enum.Enum):
    RISK_ANALYST = "RISK_ANALYST"
    RISK_ADMIN = "RISK_ADMIN"
    SYSTEM = "SYSTEM"


class EventType(str, enum.Enum):
    RISK_ASSESSMENT_CREATED = "RISK_ASSESSMENT_CREATED"
    MODEL_RECOMMENDATION_CREATED = "MODEL_RECOMMENDATION_CREATED"
    REVIEW_STARTED = "REVIEW_STARTED"
    REVIEW_DECISION_MADE = "REVIEW_DECISION_MADE"
    POLICY_EVALUATED = "POLICY_EVALUATED"
    AUDIT_RECORD_CREATED = "AUDIT_RECORD_CREATED"


class ActorType(str, enum.Enum):
    SYSTEM = "SYSTEM"
    MERCHANT_ANALYST = "MERCHANT_ANALYST"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"
    RISK_ADMIN = "RISK_ADMIN"


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(64), primary_key=True, index=True)
    account_age_days = Column(Integer, nullable=False, default=0)
    total_order_count = Column(Integer, nullable=False, default=0)
    historical_return_count = Column(Integer, nullable=False, default=0)
    historical_return_rate = Column(Float, nullable=False, default=0.0)
    historical_refund_amount = Column(Float, nullable=False, default=0.0)
    historical_dispute_count = Column(Integer, nullable=False, default=0)
    orders_last_7d = Column(Integer, nullable=False, default=0)
    orders_last_30d = Column(Integer, nullable=False, default=0)
    orders_last_90d = Column(Integer, nullable=False, default=0)
    returns_last_7d = Column(Integer, nullable=False, default=0)
    returns_last_30d = Column(Integer, nullable=False, default=0)
    returns_last_90d = Column(Integer, nullable=False, default=0)
    customer_avg_order_value = Column(Float, nullable=False, default=100.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(64), primary_key=True, index=True)
    customer_id = Column(String(64), ForeignKey("customers.customer_id"), nullable=False, index=True)
    order_timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    order_amount = Column(Float, nullable=False)
    item_count = Column(Integer, nullable=False, default=1)
    product_category = Column(SQLEnum(ProductCategory), nullable=False)
    discount_amount = Column(Float, nullable=False, default=0.0)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    delivery_region = Column(String(32), nullable=False, default="IN_NORTH")
    fulfillment_method = Column(String(32), nullable=False, default="STANDARD_GROUND")
    delivery_timestamp = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="orders")
    returns = relationship("ReturnRequest", back_populates="order")


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    return_id = Column(String(64), primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), nullable=False, index=True)
    request_timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    return_reason = Column(SQLEnum(ReturnReason), nullable=False)
    item_condition_declared = Column(SQLEnum(ItemCondition), nullable=False)
    refund_amount_requested = Column(Float, nullable=False)
    return_method = Column(String(32), nullable=False, default="MAIL_IN")
    return_abuse_label = Column(Integer, nullable=True)  # Ground truth known post-inspection

    order = relationship("Order", back_populates="returns")
    risk_assessment = relationship("RiskAssessment", back_populates="return_request", uselist=False)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    assessment_id = Column(String(64), primary_key=True, index=True)
    return_id = Column(String(64), ForeignKey("return_requests.return_id"), nullable=False, unique=True, index=True)
    order_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    idempotency_key = Column(String(64), nullable=True, unique=True, index=True)
    
    # ML Scoring
    model_version = Column(String(64), nullable=False)
    feature_version = Column(String(64), nullable=False, default="v2_point_in_time")
    risk_probability = Column(Float, nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    threshold_applied = Column(Float, nullable=False)
    
    # Expected Loss Economics
    expected_loss = Column(Float, nullable=False)
    estimated_loss_if_abuse = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="INR")
    loss_calculation_version = Column(String(32), nullable=False, default="v1_asymmetric")
    
    # Policy Decision & Explanations
    policy_version = Column(String(64), nullable=False)
    model_recommendation = Column(SQLEnum(BoundedRecommendation), nullable=False)
    top_risk_factors_json = Column(Text, nullable=False, default="[]")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    return_request = relationship("ReturnRequest", back_populates="risk_assessment")
    review_case = relationship("ReviewCase", back_populates="risk_assessment", uselist=False)
    audit_events = relationship("AuditEvent", back_populates="risk_assessment")


class ReviewCase(Base):
    __tablename__ = "review_cases"

    case_id = Column(String(64), primary_key=True, index=True)
    assessment_id = Column(String(64), ForeignKey("risk_assessments.assessment_id"), nullable=False, unique=True, index=True)
    return_id = Column(String(64), nullable=False, index=True)
    order_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    
    status = Column(SQLEnum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING_REVIEW)
    model_recommendation = Column(SQLEnum(BoundedRecommendation), nullable=False)
    
    # Separate Human Decision Fields (Never overwriting model recommendation)
    human_decision = Column(SQLEnum(HumanDecisionType), nullable=True)
    decision_reason = Column(Text, nullable=True)
    reviewer_id = Column(String(64), nullable=True)
    reviewer_role = Column(SQLEnum(UserRole), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    risk_assessment = relationship("RiskAssessment", back_populates="review_case")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    audit_id = Column(String(64), primary_key=True, index=True)
    assessment_id = Column(String(64), ForeignKey("risk_assessments.assessment_id"), nullable=False, index=True)
    event_type = Column(SQLEnum(EventType), nullable=False)
    actor_type = Column(SQLEnum(ActorType), nullable=False)
    actor_id = Column(String(64), nullable=False)
    model_version = Column(String(64), nullable=True)
    policy_version = Column(String(64), nullable=True)
    decision = Column(String(64), nullable=False)
    reason = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    payload_json = Column(Text, nullable=False)
    previous_event_hash = Column(String(64), nullable=False)
    event_hash = Column(String(64), nullable=False)

    risk_assessment = relationship("RiskAssessment", back_populates="audit_events")
