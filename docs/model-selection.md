# Model Selection Framework & Rationale

**Audit Date:** 2026-08-23  
**Status:** Champion Selected on Validation Partition ($N=750$), Evaluated Once on Held-Out Test ($N=750$).

---

## 1. Three-Stage Evaluation & Selection Pipeline

The project enforces a strict chronological three-stage lifecycle:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. TRAINING (N=3,500)                                       │
│    - Train Logistic Regression baseline                     │
│    - Train HistGradientBoosting candidate                   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. VALIDATION (N=750)                                       │
│    - Fit Platt sigmoid probability calibration              │
│    - Evaluate validation ranking quality & model properties │
│    - Select Champion architecture (HGB)                     │
│    - Optimize operational threshold (T = 0.30)              │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. HELD-OUT TEST (N=750)                                    │
│    - Single-pass post-selection evaluation                  │
│    - Compute final benchmark metrics & confidence intervals │
│    - Zero model tuning or threshold adjustments             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Selection Criteria Hierarchy (Evaluated Prior to Test Set Access)

1. **Non-Linear Feature Interaction Modeling:** Ability of gradient-boosted trees to capture non-linear velocity spikes, tender type interactions (`BUY_NOW_PAY_LATER`), and elapsed return request delay without manual interaction terms.
2. **Ranking & Calibration Quality:** Validation ranking stability and probability calibration under Platt scaling.
3. **Operational Threshold Optimization:** Validation net economic benefit across candidate operating thresholds ($T \in [0.30, 0.80]$).

---

## 3. Post-Selection Held-Out Test Benchmark ($N=750$, Threshold = 0.30)

*Note: The metrics below are post-selection evaluation results on the untouched test partition, confirming that the validation-selected model and threshold generalize effectively.*

| Evaluation Metric | Baseline Logistic Regression (`return-risk-logreg-v1`) | Champion HistGradientBoosting (`return-risk-hgb-v1`) | Post-Selection Observation |
| :--- | :--- | :--- | :--- |
| **PR-AUC** | `0.7890` | **`0.7983`** | HGB demonstrates higher ranking power |
| **ROC-AUC** | **`0.9245`** | `0.9242` | Comparable discrimination |
| **Brier Score** | **`0.0644`** | `0.0671` | LogReg shows slightly better calibration |
| **Precision @ 0.30** | **`75.82%`** | `75.00%` | LogReg (+0.82%) |
| **Recall @ 0.30** | **`86.57%`** | `85.07%` | LogReg (+1.50%) |
| **F1-Score @ 0.30** | **`0.8084`** | `0.7972` | LogReg (+0.0112) |
| **True Positives ($TP$)** | `116` | `114` | LogReg |
| **False Positives ($FP$)** | `37` | `38` | LogReg |
| **False Negatives ($FN$)** | `18` | `20` | LogReg |
| **True Negatives ($TN$)** | `579` | `578` | LogReg |
| **Review Volume ($TP+FP$)** | `153` | `152` | Similar review burden |
| **Net Benefit (INR)** | `+₹58,69,637.24` | `+₹57,87,447.24` | Both deliver strong simulated savings |

---

## 4. Honest Evaluation & Baseline Preservation

* **Logistic Regression Baseline Retained:** At the operating point $T=0.30$, Logistic Regression achieved slightly higher precision, recall, and a lower Brier score.
* **Active Co-existence:** The baseline model is preserved, versioned (`return-risk-logreg-v1`), and actively accessible via API and dashboard for side-by-side verification.
