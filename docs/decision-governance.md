# AI Risk Manager — Decision Governance & Separation of Concerns

---

## 1. Core Governance Principle: Three Distinct Entities

The system strictly distinguishes three independent decision tiers:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. MODEL PREDICTION: P(Abuse) ∈ [0, 1]                      │
│    - Probabilistic risk score from point-in-time features.  │
│    - Probabilistic estimate, NEVER a factual proof of intent.│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. POLICY RECOMMENDATION                                    │
│    - Bounded deterministic operational action.              │
│    - APPROVE | REQUIRE_ADDITIONAL_VERIFICATION | REVIEW     │
│    - NEVER executes fund forfeiture or financial seizures.  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. HUMAN DECISION (When Triage Triggered)                   │
│    - Authorized analyst decision (RISK_ANALYST / RISK_ADMIN) │
│    - APPROVE_RETURN | REQUEST_ADDITIONAL_VERIFICATION | ESC │
│    - Requires mandatory non-empty rationale (≥ 5 chars).    │
│    - NEVER overwrites original model recommendation in DB.  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. TAMPER-EVIDENT AUDIT TRAIL                               │
│    - SHA-256 chained event sealing the entire workflow.     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Risk Semantics & Language Policy

* **Probabilistic Nature:** The model calculates statistical return-abuse propensity ($P \in [0, 1]$).
* **Banned Accusatory Language:** Terms like "confirmed fraud", "fraudster", "guaranteed abuse", "criminal intent" are prohibited across backend code, API responses, and UI labels.
* **Approved Neutral Terminology:**
  * *"Predicted return-abuse risk"*
  * *"Elevated risk signal"*
  * *"Risk assessment"*
  * *"Model recommendation"*
  * *"Historical behavior associated with elevated risk"*
  * *"Requires analyst review"*

---

## 3. Human Override Analytics Definition

An **override** occurs whenever the authorized human reviewer chooses a final resolution that differs from the automated model recommendation:
$$\text{Override Event} \iff \text{Human Action} \ne \text{Model Recommendation}$$

* Both fields (`model_recommendation` and `human_decision`) are stored as separate columns in the database and audit trail.
* Override analytics are computed directly from persisted records without modifying historical assessment state.
