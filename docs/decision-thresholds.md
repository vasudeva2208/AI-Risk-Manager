# Decision Thresholds: ML Operating Point vs. Operational Policy Bands

---

## 1. Distinction Between ML Threshold and Policy Bands

The system strictly distinguishes between the **ML Operating Threshold** and **Operational Policy Bands**:

### A. ML Operating Threshold ($T = 0.30$)
* **Purpose:** Binary classification cut-off for statistical evaluation and economic loss optimization.
* **Optimization Source:** Validation set ($N=750$) cost curve search maximizing net merchant economic benefit under operational bounding ($T \ge 0.30$).
* **Mathematical Role:** Flags transactions with $P(\text{Abuse}) \ge 0.30$ as requiring active merchant risk management.

### B. Operational Policy Bands (`return-policy-v1`)
* **Purpose:** Bounded operational escalation tiers designed to minimize customer friction while protecting merchant capital.

| Probability Range | Policy Recommendation | Operational Mechanism |
| :--- | :--- | :--- |
| **$P < 0.30$** | `APPROVE` | Automatic instant return authorization label issued. Zero customer friction. |
| **$0.30 \le P < 0.70$** | `REQUIRE_ADDITIONAL_VERIFICATION` | Soft friction (request unboxing photo, serial number scan, or physical drop-off). No human review needed. |
| **$P \ge 0.70$** | `MANUAL_REVIEW` | Routed to human analyst triage queue with explainability insights. |
| **Active Dispute** | `MANUAL_REVIEW` | Any claim with open payment disputes routes directly to human review regardless of score. |

---

## 2. Deterministic Boundary Specifications

* $P = 0.000000 \implies \text{APPROVE}$
* $P = 0.299999 \implies \text{APPROVE}$
* $P = 0.300000 \implies \text{REQUIRE\_ADDITIONAL\_VERIFICATION}$
* $P = 0.699999 \implies \text{REQUIRE\_ADDITIONAL\_VERIFICATION}$
* $P = 0.700000 \implies \text{MANUAL\_REVIEW}$
* $P = 1.000000 \implies \text{MANUAL\_REVIEW}$
