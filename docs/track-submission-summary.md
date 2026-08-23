# AI Risk Manager Track — Submission Summary

---

## 1. One-Line Pitch
**AI Risk Manager** is a defense-only, explainable risk management platform that helps e-commerce merchants detect and mitigate return abuse and friendly return fraud through calibrated ML, asymmetric financial loss modeling, deterministic bounded policies, human analyst triage, and a tamper-evident SHA-256 audit ledger.

---

## 2. Problem Statement
E-commerce return abuse and "friendly return fraud" (e.g., wardrobing, claiming non-receipt after delivery, returning empty boxes, refund velocity spikes) quietly erode merchant operating margins. Merchants face an asymmetric loss problem:
* **False Negatives (Missed Abuse):** Result in full loss of order value plus return shipping and restocking costs.
* **False Positives (Mistaken Flags):** Cause customer friction, support labor overhead, and lifetime customer churn.

---

## 3. Solution Overview
The system establishes a trustworthy operational pipeline:
$$\text{Point-in-Time Features} \longrightarrow \text{Calibrated ML Probability} \longrightarrow \text{Expected Loss} \longrightarrow \text{Deterministic Bounded Policy} \longrightarrow \text{Human Review Queue} \longrightarrow \text{Tamper-Evident Audit Ledger}$$

* **Defense-Only System Boundary:** The ML model predicts risk only. It does **not** unilaterally deny transactions or freeze funds. Consequential actions route to soft verification friction or human review.
* **No Adversarial Exploitation:** Explanations and APIs are merchant-facing only, providing contextual risk reasons while omitting internal thresholds, gradients, or evasion instructions.

---

## 4. Machine Learning & Evaluation Integrity

* **Dataset:** 5,000 synthetic transactions structured across 180-day chronological progression.
* **Strict Temporal Partitioning:**
  * **Training Set:** Earliest 70% ($N = 3,500$ records)
  * **Validation Set:** Middle 15% ($N = 750$ records) — used exclusively for Platt probability calibration and threshold optimization.
  * **Held-Out Test Set:** Latest 15% ($N = 750$ records, 17.87% prevalence) — touched **exactly once** for final reporting.
* **23 Point-in-Time Features:** Lifetime history, 7d/30d/90d velocity windows, financial drain ratios, timing, and categoricals. All features audited to strictly precede return request timestamps (0 target leakage).
* **Champion Model (`return-risk-hgb-v1`):** `HistGradientBoostingClassifier` with Platt sigmoid calibration.
* **Baseline Model (`return-risk-logreg-v1`):** Calibrated L2-regularized Logistic Regression preserved for side-by-side comparison.

---

## 5. Held-Out Test Set Performance Benchmark ($N = 750$)

| Metric | Baseline (Logistic Regression) | Champion (HistGradientBoosting) |
| :--- | :--- | :--- |
| **Operating Threshold** | 0.30 (Val Optimized) | **0.30 (Val Optimized)** |
| **Precision** | 75.82% | **75.00%** |
| **Recall** | 86.57% | **85.07%** |
| **F1-Score** | 0.8084 | **0.7972** |
| **PR-AUC** | 0.7890 | **0.7983** |
| **ROC-AUC** | 0.9245 | **0.9242** |
| **Brier Score** | 0.0644 | **0.0671** |
| **True Positives (Caught)** | 116 | **114** |
| **False Positives (Friction)** | 37 | **38** |
| **False Negatives (Missed)** | 18 | **20** |
| **True Negatives (Auto-Approved)** | 579 | **578** |

*(Explicitly labelled: SYNTHETIC DATA — NOT PRODUCTION PERFORMANCE).*

---

## 6. Asymmetric Economic Loss Model

* **Formula:** $\text{Expected Loss} = P(\text{Abuse}) \times \left( \text{Refund Amount Requested} + \text{Return Handling \& Shipping Cost} \right)$
* **Cost Parameters:**
  * False Positive Cost: \$50.00 / ₹4,150 (Review Labor + Customer Friction)
  * False Negative Cost: Order Value + \$8.50 / ₹705.50 Handling
  * Review Labor: \$15.00 / ₹1,245 per flagged case
* **Simulated Held-Out Test Net Benefit:**
  * **USD (\$):** `+$69,728.28` net benefit vs. unmitigated loss of \$77,659.82.
  * **INR (₹):** `+₹57,87,447.24` net benefit vs. unmitigated loss of ₹64,45,765.06.
  * *(Label: "SYNTHETIC SIMULATION — NOT PRODUCTION SAVINGS")*.

---

## 7. Explainability & Human Governance

* **Safe Explainability:** Top point-in-time feature contributions translated into merchant-facing risk reasons (e.g. multi-order return velocity spikes, dispute history, BNPL tender, basket deviation).
* **Role-Based Authorization:** Human review decisions (`APPROVE_RETURN`, `REQUEST_ADDITIONAL_VERIFICATION`, `ESCALATE`) are restricted to authorized personas (`RISK_ANALYST`, `RISK_ADMIN`) and require mandatory non-empty rationale ($\ge 5$ characters).
* **Decision Separation:** Automated model recommendations and human reviewer decisions are stored in distinct database fields and never overwrite each other.

---

## 8. Tamper-Evident Auditability

* Every critical event (`RISK_ASSESSMENT_CREATED`, `POLICY_EVALUATED`, `REVIEW_STARTED`, `REVIEW_DECISION_MADE`) is cryptographically chained using SHA-256 hashes.
* One-click verification (`GET /api/v1/audit/verify`) confirms ledger integrity across all records or pinpoints the exact corrupted event if tampering occurs.

---

## 9. Genuine System Limitations

1. **Synthetic Data Distribution:** Evaluation results reflect synthetic data generation rules. Real-world deployment requires training on labeled merchant historical return and chargeback records.
2. **Covariate & Behavioral Shift:** Return abuse patterns evolve seasonally (e.g. holiday peaks); continuous model monitoring is required.
3. **No Direct Gateway Authorization:** System provides decision intelligence and triage routing; payment gateway refund execution is delegated to merchant ERP systems.
