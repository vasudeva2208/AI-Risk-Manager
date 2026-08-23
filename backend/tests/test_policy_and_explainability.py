import pytest
import datetime
import pandas as pd
from backend.app.services.decision_engine import decision_engine_service
from backend.app.services.explainability import explainability_service
from backend.app.models.entities import RiskLevel, BoundedRecommendation
from backend.app.services.risk_scoring import risk_scoring_service
from backend.app.schemas.domain import CustomerBase, OrderBase, ReturnRequestBase, ProductCategory, PaymentMethod, ReturnReason, ItemCondition


def test_deterministic_bounded_policy_thresholds():
    # Low Risk (p < 0.30)
    rec_low, tier_low, reason_low = decision_engine_service.evaluate_policy(
        risk_probability=0.15, expected_loss=250.0, currency="INR"
    )
    assert rec_low == BoundedRecommendation.APPROVE
    assert tier_low == RiskLevel.LOW
    assert "recommendation: approve" in reason_low.lower()

    # Medium Risk (0.30 <= p < 0.70)
    rec_med, tier_med, reason_med = decision_engine_service.evaluate_policy(
        risk_probability=0.45, expected_loss=1200.0, currency="INR"
    )
    assert rec_med == BoundedRecommendation.REQUIRE_ADDITIONAL_VERIFICATION
    assert tier_med == RiskLevel.MEDIUM
    assert "friction" in reason_med.lower() or "verification" in reason_med.lower()

    # High Risk (p >= 0.70)
    rec_high, tier_high, reason_high = decision_engine_service.evaluate_policy(
        risk_probability=0.82, expected_loss=6500.0, currency="INR"
    )
    assert rec_high == BoundedRecommendation.MANUAL_REVIEW
    assert tier_high == RiskLevel.HIGH
    assert "review queue" in reason_high.lower()

    # Active dispute override
    rec_disp, tier_disp, reason_disp = decision_engine_service.evaluate_policy(
        risk_probability=0.20, expected_loss=400.0, has_active_dispute=True, currency="INR"
    )
    assert rec_disp == BoundedRecommendation.MANUAL_REVIEW


def test_exact_policy_boundary_values():
    # 1. Exact P = 0.0 -> APPROVE
    rec, tier, _ = decision_engine_service.evaluate_policy(risk_probability=0.0, expected_loss=0.0)
    assert rec == BoundedRecommendation.APPROVE
    assert tier == RiskLevel.LOW

    # 2. Exact P = 0.299999 -> APPROVE
    rec, tier, _ = decision_engine_service.evaluate_policy(risk_probability=0.299999, expected_loss=100.0)
    assert rec == BoundedRecommendation.APPROVE
    assert tier == RiskLevel.LOW

    # 3. Exact P = 0.30 -> REQUIRE_ADDITIONAL_VERIFICATION
    rec, tier, _ = decision_engine_service.evaluate_policy(risk_probability=0.30, expected_loss=300.0)
    assert rec == BoundedRecommendation.REQUIRE_ADDITIONAL_VERIFICATION
    assert tier == RiskLevel.MEDIUM

    # 4. Exact P = 0.699999 -> REQUIRE_ADDITIONAL_VERIFICATION
    rec, tier, _ = decision_engine_service.evaluate_policy(risk_probability=0.699999, expected_loss=700.0)
    assert rec == BoundedRecommendation.REQUIRE_ADDITIONAL_VERIFICATION
    assert tier == RiskLevel.MEDIUM

    # 5. Exact P = 0.70 -> MANUAL_REVIEW
    rec, tier, _ = decision_engine_service.evaluate_policy(risk_probability=0.70, expected_loss=800.0)
    assert rec == BoundedRecommendation.MANUAL_REVIEW
    assert tier == RiskLevel.HIGH

    # 6. Exact P = 1.0 -> MANUAL_REVIEW
    rec, tier, _ = decision_engine_service.evaluate_policy(risk_probability=1.0, expected_loss=1200.0)
    assert rec == BoundedRecommendation.MANUAL_REVIEW
    assert tier == RiskLevel.HIGH


def test_explainability_feature_attribution_safety():
    now = datetime.datetime.utcnow()
    cust = CustomerBase(
        customer_id="CUST_EXPLAIN_01",
        account_age_days=5,
        total_order_count=1,
        historical_return_count=1,
        historical_return_rate=1.0,
        historical_refund_amount=9000.0,
        historical_dispute_count=2,
        orders_last_7d=1,
        orders_last_30d=1,
        orders_last_90d=1,
        returns_last_7d=1,
        returns_last_30d=1,
        returns_last_90d=1,
        customer_avg_order_value=1200.0,
    )
    order = OrderBase(
        order_id="ORD_EXPLAIN_01",
        customer_id="CUST_EXPLAIN_01",
        order_timestamp=now - datetime.timedelta(days=29),
        order_amount=9500.0,
        item_count=1,
        product_category=ProductCategory.LUXURY_GOODS,
        discount_amount=0.0,
        payment_method=PaymentMethod.BUY_NOW_PAY_LATER,
        delivery_region="IN_WEST",
        fulfillment_method="EXPRESS_AIR",
        delivery_timestamp=now - datetime.timedelta(days=28),
    )
    ret_req = ReturnRequestBase(
        return_id="RET_EXPLAIN_01",
        order_id="ORD_EXPLAIN_01",
        request_timestamp=now,
        return_reason=ReturnReason.DEFECTIVE,
        item_condition_declared=ItemCondition.UNOPENED,
        refund_amount_requested=9500.0,
        return_method="MAIL_IN",
    )

    score_res = risk_scoring_service.score_transaction(cust, order, ret_req)
    explanations = explainability_service.explain_prediction(
        model_instance=score_res["model_instance"],
        df_row=score_res["df_row"],
        top_k=4
    )

    assert len(explanations) > 0
    # Verify safety: no evasion advice, strictly merchant-facing
    for exp in explanations:
        assert exp.feature_name != ""
        assert exp.direction in ["INCREASES_RISK", "DECREASES_RISK"]
        reason_text = exp.human_readable_reason.lower()
        assert "how to avoid" not in reason_text
        assert "bypass" not in reason_text
        assert "cheat" not in reason_text
        assert "reduce your score" not in reason_text


def test_explainability_determinism():
    now = datetime.datetime.utcnow()
    cust = CustomerBase(
        customer_id="CUST_DET_01",
        account_age_days=120,
        total_order_count=10,
        historical_return_count=3,
        historical_return_rate=0.30,
        historical_refund_amount=3000.0,
        historical_dispute_count=0,
        orders_last_7d=1,
        orders_last_30d=2,
        orders_last_90d=5,
        returns_last_7d=0,
        returns_last_30d=1,
        returns_last_90d=2,
        customer_avg_order_value=1500.0,
    )
    order = OrderBase(
        order_id="ORD_DET_01",
        customer_id="CUST_DET_01",
        order_timestamp=now - datetime.timedelta(days=5),
        order_amount=2500.0,
        item_count=2,
        product_category=ProductCategory.APPAREL,
        discount_amount=250.0,
        payment_method=PaymentMethod.CREDIT_CARD,
        delivery_region="IN_NORTH",
        fulfillment_method="STANDARD_GROUND",
        delivery_timestamp=now - datetime.timedelta(days=3),
    )
    ret_req = ReturnRequestBase(
        return_id="RET_DET_01",
        order_id="ORD_DET_01",
        request_timestamp=now,
        return_reason=ReturnReason.WRONG_SIZE,
        item_condition_declared=ItemCondition.OPENED_UNUSED,
        refund_amount_requested=2500.0,
        return_method="MAIL_IN",
    )

    res1 = risk_scoring_service.score_transaction(cust, order, ret_req)
    exp1 = explainability_service.explain_prediction(res1["model_instance"], res1["df_row"], top_k=3)

    res2 = risk_scoring_service.score_transaction(cust, order, ret_req)
    exp2 = explainability_service.explain_prediction(res2["model_instance"], res2["df_row"], top_k=3)

    assert res1["risk_probability"] == res2["risk_probability"]
    assert len(exp1) == len(exp2)
    for e1, e2 in zip(exp1, exp2):
        assert e1.feature_name == e2.feature_name
        assert e1.contribution == e2.contribution
        assert e1.direction == e2.direction


def test_defense_only_prohibitions():
    # Assert policy engine never provides fund seizure or autonomous gateway denial
    assert not hasattr(decision_engine_service, "deny_payment")
    assert not hasattr(decision_engine_service, "freeze_funds")
    assert not hasattr(decision_engine_service, "confiscate")
