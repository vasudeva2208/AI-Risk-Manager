from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.app.models.entities import (
    ProductCategory,
    PaymentMethod,
    ReturnReason,
    ItemCondition,
    RiskLevel,
    BoundedRecommendation,
    ReviewStatus,
    HumanDecisionType,
    UserRole,
    EventType,
    ActorType,
)


class CustomerBase(BaseModel):
    customer_id: str
    account_age_days: int = Field(ge=0, default=0)
    total_order_count: int = Field(ge=0, default=0)
    historical_return_count: int = Field(ge=0, default=0)
    historical_return_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    historical_refund_amount: float = Field(ge=0.0, default=0.0)
    historical_dispute_count: int = Field(ge=0, default=0)
    orders_last_7d: int = Field(ge=0, default=0)
    orders_last_30d: int = Field(ge=0, default=0)
    orders_last_90d: int = Field(ge=0, default=0)
    returns_last_7d: int = Field(ge=0, default=0)
    returns_last_30d: int = Field(ge=0, default=0)
    returns_last_90d: int = Field(ge=0, default=0)
    customer_avg_order_value: float = Field(ge=0.0, default=100.0)

    model_config = ConfigDict(from_attributes=True)


class CustomerCreate(CustomerBase):
    pass


class OrderBase(BaseModel):
    order_id: str
    customer_id: str
    order_timestamp: datetime
    order_amount: float = Field(gt=0.0)
    item_count: int = Field(ge=1, default=1)
    product_category: ProductCategory
    discount_amount: float = Field(ge=0.0, default=0.0)
    payment_method: PaymentMethod
    delivery_region: str = "IN_NORTH"
    fulfillment_method: str = "STANDARD_GROUND"
    delivery_timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(OrderBase):
    pass


class ReturnRequestBase(BaseModel):
    return_id: str
    order_id: str
    request_timestamp: datetime
    return_reason: ReturnReason
    item_condition_declared: ItemCondition
    refund_amount_requested: float = Field(gt=0.0)
    return_method: str = "MAIL_IN"

    model_config = ConfigDict(from_attributes=True)


class ReturnRequestCreate(ReturnRequestBase):
    pass


# Full Assessment Ingestion Request
class RiskAssessmentRequest(BaseModel):
    customer: CustomerBase
    order: OrderBase
    return_request: ReturnRequestBase
    idempotency_key: Optional[str] = None
    target_currency: str = "INR"
    preferred_model_version: Optional[str] = None


class RiskFactorContribution(BaseModel):
    feature_name: str
    feature_value: float
    contribution: float
    direction: str = "INCREASES_RISK"
    human_readable_reason: str


class ExpectedLossDetail(BaseModel):
    risk_probability: float
    estimated_loss_if_abuse: float
    expected_loss: float
    currency: str
    calculation_version: str
    cost_breakdown: Dict[str, float]


class RiskAssessmentResponse(BaseModel):
    assessment_id: str
    return_id: str
    order_id: str
    customer_id: str
    risk_probability: float
    risk_level: RiskLevel
    threshold_applied: float
    expected_loss: float
    estimated_loss_if_abuse: float
    currency: str
    model_version: str
    feature_version: str
    policy_version: str
    recommendation: BoundedRecommendation
    top_risk_factors: List[RiskFactorContribution]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Review Queue Schemas
class HumanDecisionSubmission(BaseModel):
    decision: HumanDecisionType
    reason: str = Field(min_length=5, description="Mandatory non-empty rationale for the human review decision")
    reviewer_id: str = Field(min_length=2, description="Pseudonymized ID of the risk analyst")
    reviewer_role: UserRole = UserRole.RISK_ANALYST


class ReviewCaseResponse(BaseModel):
    case_id: str
    assessment_id: str
    return_id: str
    order_id: str
    customer_id: str
    status: ReviewStatus
    model_recommendation: BoundedRecommendation
    risk_probability: float
    risk_level: RiskLevel
    expected_loss: float
    currency: str
    top_risk_factors: List[RiskFactorContribution]
    human_decision: Optional[HumanDecisionType] = None
    decision_reason: Optional[str] = None
    reviewer_id: Optional[str] = None
    reviewer_role: Optional[UserRole] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Audit Schemas
class AuditEventResponse(BaseModel):
    audit_id: str
    assessment_id: str
    event_type: EventType
    actor_type: ActorType
    actor_id: str
    model_version: Optional[str]
    policy_version: Optional[str]
    decision: str
    reason: str
    timestamp: datetime
    payload_json: str
    previous_event_hash: str
    event_hash: str

    model_config = ConfigDict(from_attributes=True)


class AuditChainVerificationResponse(BaseModel):
    status: str  # "VALID" or "INVALID"
    total_events_checked: int
    assessment_id: Optional[str] = None
    corrupted_event_id: Optional[str] = None
    message: str


# Model Registry Schemas
class ModelRegistryEntry(BaseModel):
    model_version: str
    algorithm: str
    feature_version: str
    calibration_method: str
    selected_threshold: float
    status: str  # "ACTIVE" or "INACTIVE"
    trained_at: Optional[str]
    sample_count: Optional[int]
    description: str
