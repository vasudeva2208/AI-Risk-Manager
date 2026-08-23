import pytest
import datetime
from backend.app.schemas.domain import CustomerBase, OrderBase, ReturnRequestBase, ProductCategory, PaymentMethod, ReturnReason, ItemCondition
from backend.app.services.risk_scoring import risk_scoring_service
from backend.app.services.loss_estimator import loss_estimator_service
from backend.app.services.model_registry import model_registry, CHAMPION_MODEL_VERSION, BASELINE_MODEL_VERSION


@pytest.fixture
def sample_payload():
    now = datetime.datetime.utcnow()
    cust = CustomerBase(
        customer_id="CUST_TEST_001",
        account_age_days=12,
        total_order_count=2,
        historical_return_count=1,
        historical_return_rate=0.50,
        historical_refund_amount=4500.0,
        historical_dispute_count=1,
        orders_last_7d=1,
        orders_last_30d=2,
        orders_last_90d=2,
        returns_last_7d=1,
        returns_last_30d=1,
        returns_last_90d=1,
        customer_avg_order_value=2500.0,
    )
    order = OrderBase(
        order_id="ORD_TEST_001",
        customer_id="CUST_TEST_001",
        order_timestamp=now - datetime.timedelta(days=15),
        order_amount=8500.0,
        item_count=2,
        product_category=ProductCategory.ELECTRONICS,
        discount_amount=0.0,
        payment_method=PaymentMethod.BUY_NOW_PAY_LATER,
        delivery_region="IN_NORTH",
        fulfillment_method="EXPRESS_AIR",
        delivery_timestamp=now - datetime.timedelta(days=12),
    )
    ret_req = ReturnRequestBase(
        return_id="RET_TEST_001",
        order_id="ORD_TEST_001",
        request_timestamp=now,
        return_reason=ReturnReason.NOT_AS_DESCRIBED,
        item_condition_declared=ItemCondition.OPENED_UNUSED,
        refund_amount_requested=8500.0,
        return_method="MAIL_IN",
    )
    return cust, order, ret_req


def test_model_registry_and_active_champion():
    models = model_registry.list_models()
    assert len(models) >= 2
    versions = [m.model_version for m in models]
    assert CHAMPION_MODEL_VERSION in versions
    assert BASELINE_MODEL_VERSION in versions

    active = model_registry.get_active_model_entry()
    assert active.model_version == CHAMPION_MODEL_VERSION
    assert active.status == "ACTIVE"


def test_risk_scoring_champion_and_baseline(sample_payload):
    cust, order, ret_req = sample_payload

    # 1. Score with champion
    res_champion = risk_scoring_service.score_transaction(cust, order, ret_req, model_version=CHAMPION_MODEL_VERSION)
    assert res_champion["model_version"] == CHAMPION_MODEL_VERSION
    assert 0.0 <= res_champion["risk_probability"] <= 1.0
    assert res_champion["threshold_applied"] == 0.30

    # 2. Score with baseline
    res_baseline = risk_scoring_service.score_transaction(cust, order, ret_req, model_version=BASELINE_MODEL_VERSION)
    assert res_baseline["model_version"] == BASELINE_MODEL_VERSION
    assert 0.0 <= res_baseline["risk_probability"] <= 1.0


def test_expected_loss_calculation():
    # Test INR calculation
    loss_inr = loss_estimator_service.compute_expected_loss(
        risk_probability=0.75,
        refund_amount=10000.0,
        currency="INR"
    )
    assert loss_inr.currency == "INR"
    assert loss_inr.estimated_loss_if_abuse == 10705.50
    assert loss_inr.expected_loss == 8029.12

    # Test USD calculation
    loss_usd = loss_estimator_service.compute_expected_loss(
        risk_probability=0.50,
        refund_amount=100.0,
        currency="USD"
    )
    assert loss_usd.currency == "USD"
    assert loss_usd.estimated_loss_if_abuse == 108.50
    assert loss_usd.expected_loss == 54.25


def test_expected_loss_deterministic_example():
    # Probability: 0.70, Refund: 1000, Handling: 200 => Exposure: 1200, Expected Loss: 840
    res = loss_estimator_service.compute_expected_loss(
        risk_probability=0.70,
        refund_amount=1000.0,
        currency="INR",
        handling_cost_override=200.0
    )
    assert res.estimated_loss_if_abuse == 1200.0
    assert res.expected_loss == 840.0


def test_expected_loss_edge_cases():
    # Probability = 0.0
    loss_zero_p = loss_estimator_service.compute_expected_loss(
        risk_probability=0.0,
        refund_amount=500.0,
        currency="INR"
    )
    assert loss_zero_p.expected_loss == 0.0
    assert loss_zero_p.estimated_loss_if_abuse > 0.0

    # Probability = 1.0
    loss_one_p = loss_estimator_service.compute_expected_loss(
        risk_probability=1.0,
        refund_amount=500.0,
        currency="USD",
        handling_cost_override=10.0
    )
    assert loss_one_p.expected_loss == 510.0
    assert loss_one_p.estimated_loss_if_abuse == 510.0

    # Zero refund
    loss_zero_ref = loss_estimator_service.compute_expected_loss(
        risk_probability=0.5,
        refund_amount=0.0,
        currency="USD",
        handling_cost_override=8.50
    )
    assert loss_zero_ref.expected_loss == 4.25


def test_expected_loss_invalid_inputs_rejection():
    # Invalid probability > 1.0
    with pytest.raises(ValueError):
        loss_estimator_service.compute_expected_loss(risk_probability=1.2, refund_amount=100.0)

    # Invalid probability < 0.0
    with pytest.raises(ValueError):
        loss_estimator_service.compute_expected_loss(risk_probability=-0.1, refund_amount=100.0)

    # Negative refund amount
    with pytest.raises(ValueError):
        loss_estimator_service.compute_expected_loss(risk_probability=0.5, refund_amount=-50.0)

    # Unsupported currency
    with pytest.raises(ValueError):
        loss_estimator_service.compute_expected_loss(risk_probability=0.5, refund_amount=100.0, currency="EUR")
