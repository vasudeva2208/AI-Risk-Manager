# Evaluation Manifest & Authoritative Evidence Chain

---

## 1. Dataset Integrity & Specifications

* **Dataset Version:** `return-abuse-synthetic-v1`
* **Total Instances:** $5,000$ synthetic return transactions
* **Positive (Abusive) Labels:** $673$ ($13.46\%$ overall prevalence)
* **Negative (Legitimate) Labels:** $4,327$ ($86.54\%$)
* **Deterministic Seed:** $42$
* **Forward Leakage / Lookahead Bias:** $0$ columns
* **Missing Values:** $0$ across all 23 extracted features
* **Feature Set:** `v2_point_in_time_23f` (23 strictly point-in-time behavioral, velocity, order, and refund attributes)

---

## 2. Prediction Point ($T_{\text{request}}$)

The prediction is generated at the exact timestamp $T_{\text{request}}$ when the customer submits a return request.
* **Included Information:** Historical account age, lifetime orders, 7d/30d/90d return counts, historical dispute count, current order amount, payment tender method, item condition declared, return reason declared, delivery-to-return elapsed days.
* **Prohibited Information:** Warehouse receipt condition, post-inspection triage, carrier transit weigh-in data, refund bank settlement outcome, post-resolution chargeback outcomes.

---

## 3. Temporal Partitioning

Chronological ordering is strictly preserved by sorting all records by $T_{\text{request}}$ before splitting:

| Partition | Record Count | Abuse Positives | Prevalence | Partition Role |
|---|---|---|---|---|
| **TRAIN** | $3,500$ ($70\%$) | $449$ | **$12.83\%$** | Feature learning, model parameter training |
| **VALIDATION** | $750$ ($15\%$) | $90$ | **$12.00\%$** | Hyperparameter tuning, probability calibration, threshold selection ($T=0.30$) |
| **HELD-OUT TEST** | $750$ ($15\%$) | $134$ | **$17.87\%$** | Untouched post-selection benchmark evaluation |

---

## 4. Model Architectures & Operating Threshold

* **Champion Model:** `return-risk-hgb-v1`
  * Algorithm: `HistGradientBoostingClassifier` with Platt Sigmoid Probability Calibration.
  * Selected on validation data based on PR-AUC dominance ($0.8407$).
* **Baseline Model:** `return-risk-logreg-v1`
  * Algorithm: `LogisticRegression` with StandardScaler and Platt Sigmoid Calibration.
* **Authoritative Operating Threshold:** $T = 0.30$
  * Selected strictly on the validation set by maximizing net merchant economic benefit (+₹36,25,203.45).
  * The held-out test partition was untouched during threshold tuning.

---

## 5. Authoritative Held-Out Test Evaluation ($N=750$)

| Metric | Champion (`return-risk-hgb-v1`) | 95% Confidence Interval (1,000 Bootstrap) | Baseline (`return-risk-logreg-v1`) |
|---|---|---|---|
| **Precision @ 0.30** | **75.00%** | $[68.07\%, 81.53\%]$ | 75.82% |
| **Recall @ 0.30** | **85.07%** | $[78.76\%, 90.77\%]$ | 86.57% |
| **F1-Score @ 0.30** | **0.7972** | $[0.7448, 0.8457]$ | 0.8084 |
| **PR-AUC** | **0.7983** | $[0.7156, 0.8637]$ | 0.7890 |
| **ROC-AUC** | **0.9242** | $[0.8872, 0.9570]$ | 0.9245 |
| **Brier Score** | **0.0671** | Platt Calibrated | 0.0644 |

### Held-Out Confusion Matrix ($N=750, T=0.30$)

| | Actual Abusive ($Y=1, N=134$) | Actual Legitimate ($Y=0, N=616$) |
|---|---|---|
| **Flagged as Risk ($\hat{Y}=1, N=152$)** | **True Positives (TP) = 114** | **False Positives (FP) = 38** |
| **Standard Policy ($\hat{Y}=0, N=598$)** | **False Negatives (FN) = 20** | **True Negatives (TN) = 578** |

* Mathematical Identity Checks:
  $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}} = \frac{114}{152} = 75.00\%$$
  $$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}} = \frac{114}{134} = 85.07\%$$

---

## 6. Asymmetric Economic Cost Model

> **SYNTHETIC SIMULATION — NOT PRODUCTION SAVINGS**

* **Cost Assumptions:**
  * Return Shipping & Processing Overhead ($C_{\text{ship}}$): $\$8.50$ ($\text{₹}705.50$)
  * Human Review Labor ($C_{\text{review}}$): $\$15.00$ ($\text{₹}1,245.00$)
  * False Positive Customer Friction / Churn ($C_{\text{FP}}$): $\$50.00$ ($\text{₹}4,150.00$)
  * Configured Simulation Conversion Rate: $\text{₹}83.00 / \text{USD}$

### Test Set Economic Impact Breakdown (INR)

* **Baseline Unmitigated Loss (Do Nothing):** $\text{₹}64,45,765.06$ ($\$77,659.82$)
* **Gross Abusive Loss Prevented:** $+\text{₹}60,06,650.24$ ($+\$72,369.28$)
* **False Positive Customer Friction Expenditure:** $-\text{₹}1,57,700.00$ ($-\$1,900.00$)
* **Review Labor Expenditure ($152$ Reviews):** $-\text{₹}1,41,930.00$ ($-\$1,710.00$)
* **Realized False Negative Loss ($20$ Missed Cases):** $-\text{₹}3,58,687.82$ ($-\$4,321.54$)
* **Net Merchant Economic Benefit:** **$+\text{₹}57,87,447.24$** ($+\$69,728.28$)
