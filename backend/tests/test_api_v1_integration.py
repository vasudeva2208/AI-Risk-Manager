import pytest
import datetime
import uuid
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["currency"] == "INR"


def test_model_registry_endpoints(client):
    # List models
    res_list = client.get("/api/v1/models")
    assert res_list.status_code == 200
    models = res_list.json()
    assert len(models) >= 2
    versions = [m["model_version"] for m in models]
    assert "return-risk-hgb-v1" in versions
    assert "return-risk-logreg-v1" in versions

    # Get single model
    res_single = client.get("/api/v1/models/return-risk-hgb-v1")
    assert res_single.status_code == 200
    assert res_single.json()["model_version"] == "return-risk-hgb-v1"


def test_full_end_to_end_assessment_review_audit_flow(client):
    test_run_id = uuid.uuid4().hex[:8].upper()
    now = datetime.datetime.utcnow()
    request_payload = {
        "customer": {
            "customer_id": f"CUST_E2E_{test_run_id}",
            "account_age_days": 8,
            "total_order_count": 2,
            "historical_return_count": 2,
            "historical_return_rate": 1.0,
            "historical_refund_amount": 14000.0,
            "historical_dispute_count": 1,
            "orders_last_7d": 1,
            "orders_last_30d": 2,
            "orders_last_90d": 2,
            "returns_last_7d": 1,
            "returns_last_30d": 2,
            "returns_last_90d": 2,
            "customer_avg_order_value": 3000.0,
        },
        "order": {
            "order_id": f"ORD_E2E_{test_run_id}",
            "customer_id": f"CUST_E2E_{test_run_id}",
            "order_timestamp": (now - datetime.timedelta(days=10)).isoformat(),
            "order_amount": 12000.0,
            "item_count": 2,
            "product_category": "ELECTRONICS",
            "discount_amount": 500.0,
            "payment_method": "BUY_NOW_PAY_LATER",
            "delivery_region": "IN_NORTH",
            "fulfillment_method": "EXPRESS_AIR",
            "delivery_timestamp": (now - datetime.timedelta(days=8)).isoformat(),
        },
        "return_request": {
            "return_id": f"RET_E2E_{test_run_id}",
            "order_id": f"ORD_E2E_{test_run_id}",
            "request_timestamp": now.isoformat(),
            "return_reason": "DEFECTIVE",
            "item_condition_declared": "OPENED_UNUSED",
            "refund_amount_requested": 12000.0,
            "return_method": "MAIL_IN",
        },
        "idempotency_key": f"IDEM_E2E_KEY_{test_run_id}",
        "target_currency": "INR",
    }

    # 1. Submit Assessment
    res_assess = client.post("/api/v1/risk/assess", json=request_payload)
    assert res_assess.status_code == 201, res_assess.text
    assess_data = res_assess.json()
    assert assess_data["order_id"] == f"ORD_E2E_{test_run_id}"
    assert assess_data["currency"] == "INR"
    assert 0.0 <= assess_data["risk_probability"] <= 1.0
    assert len(assess_data["top_risk_factors"]) > 0
    assessment_id = assess_data["assessment_id"]

    # 2. Idempotent re-submission returns exact same assessment
    res_idempotent = client.post("/api/v1/risk/assess", json=request_payload)
    assert res_idempotent.status_code == 201
    assert res_idempotent.json()["assessment_id"] == assessment_id

    # 3. Retrieve assessment
    res_get_assess = client.get(f"/api/v1/risk/{assessment_id}")
    assert res_get_assess.status_code == 200
    assert res_get_assess.json()["assessment_id"] == assessment_id

    # 4. Check review queue
    res_reviews = client.get("/api/v1/reviews?status=PENDING_REVIEW")
    assert res_reviews.status_code == 200
    reviews = res_reviews.json()
    case = next((c for c in reviews if c["assessment_id"] == assessment_id), None)
    assert case is not None
    case_id = case["case_id"]

    # 5. Submit Human Review Decision
    decision_payload = {
        "decision": "REQUEST_ADDITIONAL_VERIFICATION",
        "reason": "High refund velocity and BNPL tender; requested unboxing video.",
        "reviewer_id": "ANALYST_007",
        "reviewer_role": "RISK_ANALYST",
    }
    res_decision = client.post(f"/api/v1/reviews/{case_id}/decision", json=decision_payload)
    assert res_decision.status_code == 200
    resolved_case = res_decision.json()
    assert resolved_case["status"] == "RESOLVED"
    assert resolved_case["human_decision"] == "REQUEST_ADDITIONAL_VERIFICATION"
    assert resolved_case["reviewer_id"] == "ANALYST_007"

    # 6. Verify Audit Trail for this Assessment
    res_audit = client.get(f"/api/v1/audit/{assessment_id}")
    assert res_audit.status_code == 200
    events = res_audit.json()
    assert len(events) >= 3

    # 7. Verify Audit Hash Chain Integrity
    res_verify = client.get(f"/api/v1/audit/verify?assessment_id={assessment_id}")
    assert res_verify.status_code == 200
    assert res_verify.json()["status"] == "VALID"
