# Validation-Driven Threshold Selection & Operational Bounding

**Authoritative Operating Threshold:** $T = 0.30$  
**Optimization Scope:** Validation Partition ($N=750$) ONLY.

---

## 1. Candidate Search Space & Operational Bounding

1. **Candidate Range Definition:** The operational candidate search grid is configured as:
   $$\mathcal{T}_{\text{candidate}} = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]$$
2. **Operational Minimum Bound ($T \ge 0.30$):** Thresholds below $0.30$ (such as $0.20$ and $0.25$) are bounded out of the operational candidate pool to protect merchant customer experience and enforce a minimum operating precision floor.
3. **Validation Economics Across Candidate Range ($N=750$, FP Cost = ₹4,150):**
   * **$T = 0.20$ & $0.25$ (Bounded Out):** Net Benefit = `+₹36,36,257.39` (Friction on 46 legitimate accounts, 114 reviews). Identical benefit due to no validation predictions falling in $[0.20, 0.25)$.
   * **$T = 0.30$ (Uniquely Optimal within Candidate Grid):** Net Benefit = **`+₹36,25,203.45`** (\$43,677.15), capturing $74.44\%$ recall with $59.29\%$ precision and $113$ reviews.
   * **$T = 0.35$:** Net Benefit = `+₹35,55,455.23` (\$42,836.81, Recall drops to $72.22\%$).
   * **$T = 0.40$:** Net Benefit = `+₹35,27,758.96` (\$42,503.12, Recall drops to $68.89\%$).
   * **$T \ge 0.50$:** Net benefit declines steeply due to unmitigated false negative ($FN$) return fraud losses.

---

## 2. Test Set Isolation Protocol

* **Strict Three-Stage Pipeline:**
  1. **TRAINING ($N=3,500$):** Models fitted on early chronological orders.
  2. **VALIDATION ($N=750$):** Platt probability calibration and threshold selection ($T=0.30$).
  3. **HELD-OUT TEST ($N=750$):** Single-pass post-selection evaluation.
* **Test Isolation:** The held-out test partition ($N=750$) was never accessed during threshold search or probability calibration.
