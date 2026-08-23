# Evaluation Methodology & Honest Metrics Framework

## 1. Held-Out Data Splitting Standard

To ensure genuine generalization and prevent data snooping:
* **Strict Temporal Splitting:** Datasets are partitioned chronologically by `request_timestamp`:
  * **Train Set (70%):** Earliest time window. Used for feature scaler fitting and model training.
  * **Validation Set (15%):** Intermediate window. Used for threshold tuning, policy exploration, and model selection.
  * **Held-Out Test Set (15%):** Latest time window. Untouched until final performance benchmarking.
* **No Resampling of Test Set:** The test set retains the natural, un-resampled empirical class distribution.

---

## 2. Statistical & ML Evaluation Metrics

Because return abuse is an imbalanced classification problem ($~5\%$), standard accuracy is misleading. The evaluation pipeline computes:

1. **Precision at Operating Threshold ($T$):**
   $$\text{Precision} = \frac{TP}{TP + FP}$$
   Measures fraction of flagged returns that were genuinely abusive.
2. **Recall at Operating Threshold ($T$):**
   $$\text{Recall} = \frac{TP}{TP + FN}$$
   Measures fraction of all abusive returns successfully caught.
3. **F1-Score / $F_\beta$ Score:**
   $$\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
4. **Precision-Recall Area Under Curve (PR-AUC / Average Precision):**
   Primary metric for ranking quality under severe class imbalance.
5. **Receiver Operating Characteristic Area Under Curve (ROC-AUC):**
   Secondary metric for ranking separation across all thresholds.
6. **Brier Score / Calibration Error:**
   $$\text{Brier} = \frac{1}{N} \sum_{i=1}^{N} (p_i - y_i)^2$$
   Ensures predicted probabilities reflect true empirical risk.

---

## 3. Financial & Operational Cost Matrix

We explicitly model the asymmetric economic consequences of risk decisions:

### Cost Components
* **$C_{FN}$ (False Negative Cost):**
  $$\text{Loss}_{FN} = \text{Order Amount} + \text{Handling Cost (\$8.50)}$$
  (Direct inventory write-off, refund payout, and return shipping waste).
* **$C_{FP}$ (False Positive Cost):**
  $$\text{Cost}_{FP} = \text{Review Labor Cost (\$15.00)} + \text{Customer Friction Churn Cost (\$35.00)} = \$50.00$$
  (Manual investigation labor plus amortized lifetime value erosion caused by unnecessary friction).
* **$C_{TP}$ (True Positive Benefit):**
  $$\text{Savings}_{TP} = \text{Order Amount} - \text{Review Labor Cost (\$15.00)}$$
* **$C_{TN}$ (True Negative Baseline):**
  $$\text{Cost}_{TN} = \$0.00$$

### Total Economic Impact Formula
$$\text{Net Merchant Benefit} = \sum_{TP} (\text{Amount}_i - 15.00) - \sum_{FP} 50.00 - \sum_{FN} (\text{Amount}_i + 8.50)$$

A risk policy is only considered beneficial if $\text{Net Merchant Benefit} > 0$ relative to a naive baseline.
