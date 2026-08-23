# AI Risk Manager — Comprehensive Submission Evidence

---

## 1. Problem Definition
Merchants lose billions annually to e-commerce return abuse (e.g. wardrobing, empty box claims, fraudulent return tags, serial chargebacks). AI Risk Manager helps merchants detect and triage elevated-risk return claims before refund processing, balancing fraud prevention against legitimate customer friction.

---

## 2. Prediction Point ($T_{\text{request}}$)
The ML model predicts return abuse probability at the exact moment the customer requests a return ($T_{\text{request}}$).
* **Strict Anti-Leakage Rule:** Zero post-request data (warehouse receipts, carrier weigh-ins, post-dispute chargeback outcomes) is ingested by the feature pipeline.

---

## 3. Data Integrity
* Generated via a realistic, non-trivial synthetic generator ($N=5,000$, seed 42) with overlapping distributions, legitimate return variance, and realistic merchant dynamics.
* Temporal ordering is preserved across Train ($70\%$), Validation ($15\%$), and Held-Out Test ($15\%$).

---

## 4. Feature Construction (23 Point-in-Time Features)
1. **Behavioral & Account History:** `customer_account_age_days`, `customer_total_orders`, `customer_historical_return_count`, `customer_historical_return_rate`, `customer_lifetime_refund_amount`, `customer_dispute_count`, `customer_avg_order_value`.
2. **Velocity Windows:** `orders_last_7d`, `orders_last_30d`, `orders_last_90d`, `returns_last_7d`, `returns_last_30d`, `returns_last_90d`.
3. **Current Order Context:** `order_amount`, `item_count`, `discount_amount`, `payment_method_BNPL`, `payment_method_CREDIT_CARD`, `category_ELECTRONICS`, `category_LUXURY_GOODS`.
4. **Return Request Signals:** `refund_to_order_ratio`, `refund_to_spend_ratio`, `delivery_to_return_days`.

---

## 5. Model Selection & Rationale
* **Champion:** `return-risk-hgb-v1` (`HistGradientBoostingClassifier` with Platt Sigmoid calibration).
* **Baseline:** `return-risk-logreg-v1` (`LogisticRegression` with StandardScaler and Platt calibration).
* **Selection Criterion:** Selected on the validation set based on PR-AUC ($0.8407$).

---

## 6. Held-Out Evaluation Methodology
* The held-out test partition ($N=750$) was strictly untouched during training, calibration, and operating threshold tuning.
* Operating threshold $T=0.30$ was selected on the validation set by maximizing net merchant economic benefit.

---

## 7. Genuine Held-Out Results ($N=750$)
* **Precision:** **75.00%** ($95\%\text{ CI: } [68.07\%, 81.53\%]$)
* **Recall:** **85.07%** ($95\%\text{ CI: } [78.76\%, 90.77\%]$)
* **F1-Score:** **0.7972** ($95\%\text{ CI: } [0.7448, 0.8457]$)
* **PR-AUC:** **0.7983** ($95\%\text{ CI: } [0.7156, 0.8637]$)
* **ROC-AUC:** **0.9242** ($95\%\text{ CI: } [0.8872, 0.9570]$)
* **Brier Score:** **0.0671**
* **Confusion Matrix:** $\text{TP}=114, \text{FP}=38, \text{FN}=20, \text{TN}=578$.

---

## 8. False-Positive Economics
Customer friction is non-free: falsely challenging loyal customers causes churn.
> **SYNTHETIC SIMULATION — NOT PRODUCTION SAVINGS**
* Every FP incurs modeled friction cost $C_{\text{FP}} = \$50.00$ ($\text{₹}4,150.00$).
* Threshold $T=0.30$ optimally balances catching abuse against minimizing customer friction, yielding **$+\text{₹}57,87,447.24$ net economic benefit** ($+\$69,728.28$) on the held-out test partition.

---

## 9. Decision Governance Architecture
1. **Model Prediction:** Probabilistic propensity $P(\text{Abuse}) \in [0, 1]$.
2. **Policy Recommendation:** Bounded action (`APPROVE`, `REQUIRE_ADDITIONAL_VERIFICATION`, `MANUAL_REVIEW`). `APPROVE` represents a recommendation for standard processing; it never executes financial transactions.
3. **Human Decision:** Role-gated analyst review (`APPROVE_RETURN`, `REQUEST_ADDITIONAL_VERIFICATION`, `ESCALATE`) requiring mandatory rationale ($\ge 5$ chars).

---

## 10. Explainability
Model-derived feature attributions translate continuous gradient weights into the top 3–5 merchant factors explaining *why* a return was flagged. Evasion or threshold-probing guidance is strictly prohibited.

---

## 11. Tamper-Evident Audit Trail
Every assessment, policy evaluation, and reviewer resolution is sealed into a SHA-256 cryptographic hash chain verified via `/api/v1/audit/verify`.

---

## 12. Merchant Dashboard & UX
Production-ready React 18 / TypeScript / Tailwind CSS console providing real-time triage, inspection drawers, human review queues, audit verification, and model performance metrics.

---

## 13. Defense-Only Boundary
* The system does not autonomously seize funds, deny payment, freeze accounts, or execute financial forfeiture.
* No adversarial gradient, threshold probing, or evasion endpoints exist.

---

## 14. Real-World Limitations
* **Synthetic Data:** Real merchant deployments require streaming live order and return webhooks.
* **Cost Calibration:** Shipping ($\$8.50$), friction ($\$35.00$), and review labor ($\$15.00$) reflect baseline simulation models and must be calibrated to individual merchant carrier contracts.
