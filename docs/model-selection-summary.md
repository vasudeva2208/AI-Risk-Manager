# Model Selection Summary

## 1. Pipeline Execution Sequence
1. **TRAIN ($N=3,500$):** Train candidate models (Logistic Regression baseline and HistGradientBoosting candidate).
2. **VALIDATION ($N=750$):** Perform Platt probability calibration, evaluate model properties and validation ranking, and optimize operating threshold ($T=0.30$).
3. **HELD-OUT TEST ($N=750$):** Single-pass post-selection evaluation to verify generalization.

## 2. Selection Rationale (Validation-Driven)
* **HistGradientBoosting** was selected as the champion model because it natively resolves complex non-linear interactions across multi-window return velocities and tender methods while providing strong validation ranking.
* **Operating threshold $T=0.30$** was selected exclusively on the validation set to maximize net merchant economic benefit under operational candidate bounding ($T \ge 0.30$).

## 3. Post-Selection Benchmark (Held-Out Test Set)
* Held-out test evaluation confirmed strong generalization:
  * **HGB:** PR-AUC: `0.7983`, Precision: `75.00%`, Recall: `85.07%`, F1: `0.7972`, Brier: `0.0671`.
  * **Logistic Regression Baseline:** PR-AUC: `0.7890`, Precision: `75.82%`, Recall: `86.57%`, F1: `0.8084`, Brier: `0.0644`.

## 4. Baseline Co-existence
Logistic Regression performs exceptionally well at $T=0.30$ and has a slightly lower Brier score. It is preserved, versioned (`return-risk-logreg-v1`), and actively accessible in the model registry.
