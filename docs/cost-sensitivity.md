# Validation Cost Sensitivity Analysis

**Audit Date:** 2026-08-23  
**Analysis Scope:** Validation Partition ($N=750$) across 7 Customer-Friction Scenarios  
**Artifact:** [`ml/evaluation/results/cost_sensitivity.json`](ml/evaluation/results/cost_sensitivity.json)

---

## 1. Scenario Results Table

| False Positive Cost ($C_{FP}$) | Unconstrained Val Optimal | Candidate Grid Optimal ($T \ge 0.30$) | Validation Precision @ 0.30 | Validation Recall @ 0.30 | Validation Net Benefit @ 0.30 (INR) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **₹1,000.00 (\$12.05)** | `0.20` | `0.30` | `59.29%` | `74.44%` | `+₹37,60,003.45` |
| **₹2,000.00 (\$24.10)** | `0.20` | `0.30` | `59.29%` | `74.44%` | `+₹37,24,103.45` |
| **₹3,000.00 (\$36.14)** | `0.20` | `0.30` | `59.29%` | `74.44%` | `+₹36,78,103.45` |
| **₹4,150.00 (\$50.00)** | `0.20` | **`0.30`** | `59.29%` | `74.44%` | **`+₹36,25,203.45`** |
| **₹5,000.00 (\$60.24)** | `0.20` | `0.30` | `59.29%` | `74.44%` | `+₹35,86,103.45` |
| **₹7,500.00 (\$90.36)** | `0.20` | `0.30` | `59.29%` | `74.44%` | `+₹34,71,103.45` |
| **₹10,000.00 (\$120.48)** | `0.20` | `0.30` | `59.29%` | `74.44%` | `+₹33,56,103.45` |

---

## 2. Key Findings & Operational Bounding

1. **Unconstrained vs. Bounded Optimal:** In unconstrained optimization across $T \in [0.20, 0.80]$, $T=0.20$ and $T=0.25$ yield identical net benefit (+₹36,36,257.39 at FP cost ₹4,150) because no validation observations fall within $[0.20, 0.25)$.
2. **Operational Floor ($T=0.30$):** To prevent low-threshold customer friction escalation, the operational policy grid enforces $T \ge 0.30$, where $T=0.30$ is **uniquely optimal** (+₹36,25,203.45 / \$43,677.15) with $74.44\%$ recall and $59.29\%$ precision.
3. **Threshold Stability:** Across the entire range from ₹1,000 to ₹10,000 FP cost, $T=0.30$ remains the most robust operating point within the operational search grid.
