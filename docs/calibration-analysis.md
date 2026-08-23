# Probability Calibration & Ranking Quality Analysis

**Audit Date:** 2026-08-23  
**Evaluated Artifact:** [`ml/evaluation/results/calibration.json`](ml/evaluation/results/calibration.json)

---

## 1. Brier Score Benchmark Comparison

$$\text{Brier Score} = \frac{1}{N} \sum_{i=1}^N (P_i - Y_i)^2$$

* **Baseline Logistic Regression:** `0.0644` (Superior probabilistic accuracy)
* **Champion HistGradientBoosting:** `0.0671` (Slightly higher probabilistic loss)

> [!NOTE]
> **Honest Calibration Interpretation:** Lower Brier score indicates superior probabilistic accuracy under this evaluation. Logistic Regression demonstrates slightly better empirical probability alignment than the gradient-boosted tree model.

---

## 2. Ranking Power vs. Probability Calibration

* **PR-AUC (Ranking Power):** Measures how effectively a model ranks abusive claims above legitimate ones across all possible thresholds.
  * HGB (`0.7983`) outperforms Logistic Regression (`0.7890`) in global ranking.
* **Brier Score (Calibration Quality):** Measures how closely raw predicted probabilities match actual observed event frequencies.
  * Logistic Regression (`0.0644`) is slightly better calibrated than HGB (`0.0671`).
* **Calibration Method:** Both models apply Platt scaling (`CalibratedClassifierCV(method="sigmoid", cv="prefit")`) fitted on the validation set ($N=750$).
