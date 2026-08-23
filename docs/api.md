# AI Risk Manager — API v1 Reference Specification

Base URL: `/api/v1`

---

## 1. System Endpoints

### `GET /health`
* **Description:** Health check and environment telemetry.
* **Authentication/Authorization:** None (Public).
* **Response `200 OK`:**
```json
{
  "status": "healthy",
  "app_name": "AI Risk Manager",
  "environment": "production",
  "active_model": "return-risk-hgb-v1",
  "currency": "INR",
  "policy_thresholds": {
    "low": 0.30,
    "high": 0.70
  }
}
```

---

## 2. Risk Assessment Endpoints

### `POST /api/v1/risk/assess`
* **Description:** Ingests point-in-time order and customer history, calculates 23 behavioral features, generates calibrated risk probability, calculates expected monetary loss, enforces deterministic policy recommendations, chains an audit event, and routes to the human review queue if flagged.
* **Authentication/Authorization:** `SYSTEM` or authenticated merchant application.
* **Request Body (`application/json`):**
```json
{
  "customer": {
    "customer_id": "CUST_001",
    "account_age_days": 45,
    "total_order_count": 5,
    "historical_return_count": 1,
    "historical_return_rate": 0.20,
    "historical_refund_amount": 1200.0,
    "historical_dispute_count": 0,
    "orders_last_7d": 1,
    "orders_last_30d": 2,
    "orders_last_90d": 4,
    "returns_last_7d": 0,
    "returns_last_30d": 1,
    "returns_last_90d": 1,
    "customer_avg_order_value": 1500.0
  },
  "order": {
    "order_id": "ORD_001",
    "customer_id": "CUST_001",
    "order_timestamp": "2026-08-10T12:00:00Z",
    "order_amount": 3500.0,
    "item_count": 1,
    "product_category": "APPAREL",
    "discount_amount": 0.0,
    "payment_method": "CREDIT_CARD",
    "delivery_region": "IN_NORTH",
    "fulfillment_method": "STANDARD_GROUND",
    "delivery_timestamp": "2026-08-12T16:00:00Z"
  },
  "return_request": {
    "return_id": "RET_001",
    "order_id": "ORD_001",
    "request_timestamp": "2026-08-20T10:00:00Z",
    "return_reason": "WRONG_SIZE",
    "item_condition_declared": "OPENED_UNUSED",
    "refund_amount_requested": 3500.0,
    "return_method": "MAIL_IN"
  },
  "idempotency_key": "IDEM_REQ_001",
  "target_currency": "INR",
  "preferred_model_version": "return-risk-hgb-v1"
}
```
* **Response `201 Created`:**
```json
{
  "assessment_id": "ASSMT_A1B2C3D4E5F6",
  "return_id": "RET_001",
  "order_id": "ORD_001",
  "customer_id": "CUST_001",
  "risk_probability": 0.78,
  "risk_level": "HIGH",
  "threshold_applied": 0.30,
  "expected_loss": 3280.29,
  "estimated_loss_if_abuse": 4205.50,
  "currency": "INR",
  "model_version": "return-risk-hgb-v1",
  "feature_version": "v2_point_in_time_23f",
  "policy_version": "return-policy-v1",
  "recommendation": "MANUAL_REVIEW",
  "top_risk_factors": [
    {
      "feature_name": "customer_dispute_count",
      "feature_value": 1.0,
      "contribution": 0.18,
      "direction": "INCREASES_RISK",
      "human_readable_reason": "Customer profile has 1 prior formal payment dispute(s) or chargeback(s) on record."
    }
  ],
  "created_at": "2026-08-23T10:00:00Z"
}
```
* **Error Responses:** `400 Bad Request` (Malformed or missing required fields), `500 Internal Server Error`.

### `GET /api/v1/risk/assessments`
* **Description:** Lists evaluated risk assessments with optional filtering.
* **Query Parameters:**
  * `risk_level` (Optional: `LOW` | `MEDIUM` | `HIGH`)
  * `limit` (Optional integer, 1–500, default 100)
* **Response `200 OK`:** Array of `RiskAssessmentResponse`.

### `GET /api/v1/risk/{assessment_id}`
* **Description:** Retrieves full risk assessment details and top factor contributions by ID.
* **Response `200 OK`:** `RiskAssessmentResponse`.
* **Error Response:** `404 Not Found`.

---

## 3. Human Review Queue Endpoints

### `GET /api/v1/reviews`
* **Description:** Lists review queue items with triage details.
* **Query Parameters:**
  * `status` (Optional: `PENDING_REVIEW` | `UNDER_REVIEW` | `RESOLVED`)
* **Response `200 OK`:** Array of `ReviewCaseResponse`.

### `GET /api/v1/reviews/{case_id}`
* **Description:** Retrieves a specific review case with full risk factor breakdown and decision history.
* **Response `200 OK`:** `ReviewCaseResponse`.
* **Error Response:** `404 Not Found`.

### `POST /api/v1/reviews/{case_id}/decision`
* **Description:** Submits an authorized analyst decision with mandatory rationale. Stores human decision separately from the model recommendation and appends a SHA-256 audit record.
* **Authentication/Authorization:** Role must be `RISK_ANALYST` or `RISK_ADMIN`.
* **Request Body:**
```json
{
  "decision": "APPROVE_RETURN",
  "reason": "Customer provided authentic retail receipt and garment tag photos.",
  "reviewer_id": "ANALYST_PRIYA",
  "reviewer_role": "RISK_ANALYST"
}
```
* **Response `200 OK`:** Updated `ReviewCaseResponse` with `status: "RESOLVED"`.
* **Error Responses:** `400 Bad Request` (Duplicate submission or reason < 5 chars), `403 Forbidden` (Unauthorized role).

---

## 4. Tamper-Evident Audit Trail Endpoints

### `GET /api/v1/audit/events`
* **Description:** Lists chronological audit events across all assessments.
* **Query Parameters:** `limit` (Optional, default 100).
* **Response `200 OK`:** Array of `AuditEventResponse`.

### `GET /api/v1/audit/verify`
* **Description:** Verifies cryptographic SHA-256 hash chaining integrity. Returns `VALID` if untouched, or `INVALID` with the exact corrupted event ID.
* **Query Parameters:** `assessment_id` (Optional, filters verification to a single assessment chain).
* **Response `200 OK`:**
```json
{
  "status": "VALID",
  "total_events_checked": 97,
  "assessment_id": null,
  "corrupted_event_id": null,
  "message": "Audit chain verification passed. All 97 cryptographic hashes across 40 assessment chains verified."
}
```

### `GET /api/v1/audit/{assessment_id}`
* **Description:** Retrieves chronological audit events for a single assessment.
* **Response `200 OK`:** Array of `AuditEventResponse`.
* **Error Response:** `404 Not Found`.

---

## 5. Model Registry Endpoints

### `GET /api/v1/models`
* **Description:** Lists all registered models, their active/inactive status, and operating thresholds.
* **Response `200 OK`:** Array of `ModelRegistryEntry`.

### `GET /api/v1/models/{model_version}`
* **Description:** Retrieves metadata for a specific model version.
* **Response `200 OK`:** `ModelRegistryEntry`.
* **Error Response:** `404 Not Found`.
