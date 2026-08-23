# Risk Score Contract Specification

---

## 1. Mathematical & Structural Contract

Every risk assessment produced by the scoring service conforms to the following formal contract:

1. **Range Boundary:**
   $$P(\text{Abuse}) \in [0.0000, 1.0000]$$
   The score is guaranteed to be finite, non-negative, and strictly bounded by $[0, 1]$.
2. **Determinism:** Identical point-in-time features + model version produce identical floating-point risk probabilities.
3. **Metadata Association:** Every score is explicitly persisted alongside:
   * `model_version`: e.g. `return-risk-hgb-v1`
   * `feature_version`: e.g. `v2_point_in_time_23f`
   * `policy_version`: e.g. `return-policy-v1`
   * `created_at`: ISO-8601 UTC timestamp
4. **Calibration Standard:** Probabilities reflect empirical frequencies calibrated via Platt sigmoid scaling on the validation partition ($N=750$).

---

## 2. Risk Level Mapping

| Risk Probability Range | Risk Level Category | Default Policy Action |
| :--- | :--- | :--- |
| $0.00 \le P < 0.30$ | `LOW` | `APPROVE` |
| $0.30 \le P < 0.70$ | `MEDIUM` | `REQUIRE_ADDITIONAL_VERIFICATION` |
| $0.70 \le P \le 1.00$ | `HIGH` | `MANUAL_REVIEW` |

---

## 3. System Limitations
* **Probabilistic Scoring Only:** A high risk score ($P \ge 0.70$) indicates elevated statistical risk patterns, not proof of fraudulent intent.
* **No Direct Gateway Execution:** The scoring contract provides risk intelligence only; fund captures and refunds remain managed by merchant payment systems.
