# Validation vs. Held-Out Test Generalization Analysis

**Model:** `return-risk-hgb-v1`  
**Operating Threshold:** $0.30$ (Optimized strictly on Validation Data)

> [!WARNING]
> **SYNTHETIC SIMULATION — NOT PRODUCTION SAVINGS**  
> All performance metrics and economic estimates reflect simulation parameters on synthetic data distributions.

---

## 1. Metric Generalization Comparison Table

| Evaluation Metric | Validation Partition ($N=750$) | Held-Out Test Partition ($N=750$) | Generalization Delta ($\Delta$) |
| :--- | :--- | :--- | :--- |
| **Positive Cases (Prevalence)** | `90 (12.00%)` | `134 (17.87%)` | $+5.87\%$ (Temporal prevalence shift in the synthetic held-out period) |
| **Precision @ 0.30** | `59.29%` | `75.00%` | $+15.71\%$ |
| **Recall @ 0.30** | `74.44%` | `85.07%` | $+10.63\%$ |
| **F1-Score @ 0.30** | `0.6601` | `0.7972` | $+0.1371$ |
| **PR-AUC** | `0.6144` | `0.7983` | $+0.1839$ |
| **ROC-AUC** | `0.8429` | `0.9242` | $+0.0813$ |
| **Brier Score** | `0.0623` | `0.0671` | $+0.0048$ |
| **True Positives ($TP$)** | `67` | `114` | $+47$ |
| **False Positives ($FP$)** | `46` | `38` | $-8$ (Lower friction) |
| **False Negatives ($FN$)** | `23` | `20` | $-3$ |
| **True Negatives ($TN$)** | `614` | `578` | $-36$ |
| **Review Volume ($TP+FP$)** | `113` | `152` | $+39$ |
| **Net Benefit (INR)** | `+₹36,25,203.45` | `+₹57,87,447.24` | $+₹21,62,243.79$ |

---

## 2. Analysis of Generalization Behavior

1. **Temporal Shift in Synthetic Period:** The test set covers the final chronological partition of the dataset, exhibiting a natural temporal variation in positive incidence (prevalence shifted from 12.00% in validation to 17.87% in held-out test).
2. **Precision & PR-AUC Improvement:** In imbalanced detection, higher target prevalence mathematically shifts precision upward for a constant false positive rate ($\text{Precision} = \frac{\text{TPR} \times P}{\text{TPR} \times P + \text{FPR} \times (1-P)}$). The model adapted to the higher prevalence period without false-positive explosion.
3. **Brier Score Calibration Stability:** Brier score shifted minimally from $0.0623$ on validation to $0.0671$ on held-out test, confirming stable Platt scaling probability calibration across time.
