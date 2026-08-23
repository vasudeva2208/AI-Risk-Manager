# Statistical Confidence & Uncertainty Estimation

**Methodology:** Non-parametric Percentile Bootstrap Resampling ($B = 1,000$ iterations, Fixed Seed = 42)  
**Evaluation Set:** Held-Out Test Partition ($N = 750$)  
**Artifact:** [`ml/evaluation/results/confidence_intervals.json`](ml/evaluation/results/confidence_intervals.json)

---

## 1. 95% Bootstrap Confidence Intervals

| Evaluation Metric | Point Estimate | 95% Confidence Interval (Lower – Upper) | Standard Error ($\text{SE}$) |
| :--- | :--- | :--- | :--- |
| **Precision** | `75.00%` | **`68.07% – 81.53%`** | `0.0353` |
| **Recall** | `85.07%` | **`78.76% – 90.77%`** | `0.0304` |
| **F1-Score** | `0.7972` | **`0.7448 – 0.8457`** | `0.0259` |
| **PR-AUC** | `0.7983` | **`0.7156 – 0.8637`** | `0.0373` |
| **ROC-AUC** | `0.9242` | **`0.8918 – 0.9542`** | `0.0157` |

---

## 2. Interpretation & Methodological Safeguards

* **Uncertainty Bounds:** The 95% confidence intervals bound sampling variance on the held-out test distribution. For example, true population Precision at $T=0.30$ is bounded between $68.07\%$ and $81.53\%$ with 95% confidence.
* **Evaluation-Only Procedure:** Bootstrap resampling was conducted strictly on held-out test predictions without retraining models or tuning thresholds.
* **Edge Case Handling:** Samples with zero-variance labels or zero positive predictions were guarded against NaN contamination by computing fallback ratios.
