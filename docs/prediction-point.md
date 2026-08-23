# Formal Definition of Prediction Point & Information Availability

---

## 1. Core Principle

> **The return-abuse risk prediction is generated strictly at the return-request timestamp, using only information available at or before that timestamp.**

The ML model predicts the likelihood that a return request is abusive (e.g. wardrobing, empty box claim, fraudulent defect claim) before the merchant issues a return authorization label, refund, or warehouse inspection.

---

## 2. E-Commerce Return Lifecycle

```
┌───────────────┐
│     ORDER     │  (T_order: Customer places order, tender processed)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   DELIVERY    │  (T_delivery: Carrier delivers package to customer)
└───────┬───────┘
        │
        ▼
┌───────────────────┐
│  RETURN REQUEST   │  (T_request: Customer initiates return request online)
└─────────┬─────────┘
          │
          ▼
┌───────────────────────┐
│ ★ RISK PREDICTION ★  │  ◄── [PREDICTION POINT = T_request]
└─────────┬─────────────┘      (Only pre-event features available)
          │
          ▼
┌───────────────────────┐
│  BOUNDED POLICY /     │  (Policy maps risk score to Approve, Verify, or Review)
│  HUMAN TRIAGE         │
└─────────┬─────────────┘
          │
          ▼
┌───────────────────────┐
│ WAREHOUSE INSPECTION  │  (Item returned, inspected in warehouse)
└─────────┬─────────────┘
          │
          ▼
┌───────────────────────┐
│  FINAL RETURN OUTCOME │  (Abuse confirmed / Legitimate return / Dispute)
└───────────────────────┘
```

---

## 3. Information Availability Boundaries

### A. Strictly Available at Prediction Time ($t \le T_{\text{request}}$)
* **Customer Profile:** Historical account age, lifetime order count, lifetime return rate, historical dispute count, historical refund amount.
* **Velocity Windows:** Orders and returns in the last 7, 30, and 90 days computed strictly up to $T_{\text{request}}$.
* **Current Transaction Details:** Order timestamp, delivery timestamp, product category, payment method, order amount, discount amount, fulfillment method.
* **Return Request Metadata:** Reason selected by customer, declared item condition, refund amount requested, return method.

### B. Strictly BANNED / Unavailable at Prediction Time ($t > T_{\text{request}}$)
* **Warehouse Physical Inspection Result:** Item condition upon warehouse receipt, packaging intactness, missing item checks.
* **Carrier Physical Return Weigh-in:** Actual return parcel weight vs. expected shipping weight.
* **Post-Review Human Decision:** Analyst overrides or supervisor approvals.
* **Subsequent Chargebacks / Formal Disputes:** Bank chargebacks initiated days or weeks after return request.
* **Final Return Disposition / Label:** Ground truth label `return_abuse_label`.

---

## 4. Verification & Defense
All 23 features in `ml/features/extractor.py` enforce point-in-time calculation constraints. No feature directly or indirectly leaks future information.
