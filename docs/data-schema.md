# Domain Data Schema Specification

This document formalizes the domain entities and relational structures for the Return Risk Management system.

---

## 1. Customer (`customers`)
Represents an e-commerce account. PII (names, raw emails, phone numbers) is stripped/hashed to adhere to privacy principles.

| Field | Type | Description |
| :--- | :--- | :--- |
| `customer_id` | String (UUID / ID) | Unique customer pseudonymized identifier. |
| `account_age_days` | Integer | Number of days since account registration. |
| `total_order_count` | Integer | Lifetime total completed orders. |
| `historical_return_count`| Integer | Lifetime count of past return requests. |
| `historical_return_rate` | Float ($0.0 - 1.0$) | Lifetime returns divided by lifetime orders. |
| `historical_refund_amount`| Float | Total lifetime currency refunded. |
| `historical_dispute_count`| Integer | Past chargebacks / disputes filed. |
| `created_at` | DateTime (ISO 8601) | Account creation timestamp. |

---

## 2. Order (`orders`)
Represents a transaction placed by a customer.

| Field | Type | Description |
| :--- | :--- | :--- |
| `order_id` | String (UUID / ID) | Unique order identifier. |
| `customer_id` | String (Foreign Key) | Associated customer identifier. |
| `order_timestamp` | DateTime (ISO 8601) | Timestamp order was placed. |
| `order_amount` | Float | Total monetary value of order ($USD). |
| `item_count` | Integer | Total units in the order. |
| `product_category` | Enum | `APPAREL`, `ELECTRONICS`, `LUXURY_GOODS`, `BEAUTY`, `HOME_GARDEN`. |
| `discount_amount` | Float | Monetary discount applied to order. |
| `payment_method` | Enum | `CREDIT_CARD`, `DEBIT_CARD`, `BUY_NOW_PAY_LATER`, `STORE_CREDIT`. |
| `delivery_region` | String | Geographic delivery region code (e.g., `US_EAST`, `US_WEST`). |
| `fulfillment_method` | Enum | `STANDARD_GROUND`, `EXPRESS_AIR`, `SAME_DAY`. |
| `delivery_timestamp` | DateTime (ISO 8601) | Timestamp delivery was confirmed. |

---

## 3. Return Request (`return_requests`)
Represents an initiated request to return merchandise for refund or store credit.

| Field | Type | Description |
| :--- | :--- | :--- |
| `return_id` | String (UUID / ID) | Unique return request identifier. |
| `order_id` | String (Foreign Key) | Associated order identifier. |
| `request_timestamp` | DateTime (ISO 8601) | Timestamp return was requested. |
| `return_reason` | Enum | `DEFECTIVE`, `WRONG_SIZE`, `NOT_AS_DESCRIBED`, `CHANGED_MIND`, `ARRIVED_LATE`. |
| `item_condition_declared`| Enum | `UNOPENED`, `OPENED_UNUSED`, `WORN_OR_USED`, `DAMAGED`. |
| `refund_amount_requested`| Float | Monetary refund requested ($USD). |
| `return_method` | Enum | `MAIL_IN`, `IN_STORE_DROP`, `LOCKER_DROP`. |
| `return_abuse_label` | Integer ($0$ or $1$) | Ground truth outcome (available strictly post-inspection/audit). |

---

## 4. Risk Assessment (`risk_assessments`)
Output of the risk evaluation pipeline generated upon return request ingestion.

| Field | Type | Description |
| :--- | :--- | :--- |
| `assessment_id` | String (UUID) | Unique risk assessment identifier. |
| `return_id` | String (Foreign Key) | Associated return request. |
| `order_id` | String (Foreign Key) | Associated order. |
| `customer_id` | String (Foreign Key) | Associated customer. |
| `model_version` | String | Version identifier of model used (e.g. `v1_baseline_logistic`). |
| `policy_version` | String | Version identifier of bounded policy rules. |
| `risk_score` | Float ($0.0 - 1.0$) | Calibrated probability $P(\text{return\_abuse} = 1)$. |
| `risk_level` | Enum | `LOW`, `MEDIUM`, `HIGH`. |
| `expected_loss` | Float | Calculated monetary exposure in $USD. |
| `recommendation` | Enum | `APPROVE`, `REQUIRE_ADDITIONAL_VERIFICATION`, `MANUAL_REVIEW`. |
| `top_risk_factors` | JSON Array | Top contributing features and directional impacts. |
| `created_at` | DateTime (ISO 8601) | Timestamp assessment was created. |

---

## 5. Audit Event (`audit_events`)
Cryptographically chained event ledger recording every automated and human decision.

| Field | Type | Description |
| :--- | :--- | :--- |
| `audit_id` | String (UUID) | Unique audit event identifier. |
| `assessment_id` | String (Foreign Key) | Associated risk assessment. |
| `event_type` | Enum | `RISK_EVALUATED`, `HUMAN_REVIEW_OVERRIDE`, `POLICY_TRIGGERED`. |
| `actor_type` | Enum | `SYSTEM`, `MERCHANT_ANALYST`, `COMPLIANCE_OFFICER`. |
| `actor_id` | String | Identifier of the system engine or human reviewer. |
| `decision` | String | Operational outcome enforced. |
| `reason` | String | Human or rule-based rationale for the decision. |
| `timestamp` | DateTime (ISO 8601) | Exact timestamp of the event. |
| `payload_json` | String (JSON) | Canonical JSON serialization of event data. |
| `previous_event_hash` | String (SHA-256) | Hash of the predecessor audit event (Genesis is `'0'*64`). |
| `event_hash` | String (SHA-256) | $\text{SHA256}(\text{previous\_hash} + \text{payload\_json} + \text{timestamp})$. |
