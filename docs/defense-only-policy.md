# AI Risk Manager — Defense-Only Policy & Governance Specification

---

## 1. Primary Defense-Only Mandate

> **The AI Risk Manager is strictly a defense-only, explainable risk management platform.**
> **The system does not autonomously seize funds, deny payment, freeze accounts, or execute financial forfeiture.**

The ML model predicts the statistical likelihood of return abuse based on available point-in-time features, and the deterministic policy engine produces bounded operational recommendations. All consequential actions require authorized human review or merchant ERP integration.

---

## 2. Three-Layer Decision Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ 1. MODEL PREDICTION                                         │
│    - Probabilistic output: P(Abuse) ∈ [0, 1]                │
│    - Never represents a factual determination of intent.    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. POLICY RECOMMENDATION                                    │
│    - Deterministic bounded suggestion based on policy rules.│
│    - APPROVE | REQUIRE_ADDITIONAL_VERIFICATION | REVIEW     │
│    - APPROVE means: "Standard processing recommended".      │
│    - Never executes financial forfeiture or gateway denial. │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. HUMAN DECISION (When Triage Triggered)                   │
│    - Authorized analyst decision (RISK_ANALYST / RISK_ADMIN) │
│    - APPROVE_RETURN | REQUEST_ADDITIONAL_VERIFICATION | ESC │
│    - Requires mandatory non-empty rationale (≥ 5 chars).    │
│    - Stored independently from model recommendation.        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. TAMPER-EVIDENT SHA-256 AUDIT TRAIL                       │
│    - Cryptographic verification of every workflow event.    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Strict Prohibitions & Defense-Only Safeguards

1. **No Autonomous Financial Forfeiture:** The system contains zero functions or API routes to deny payment, freeze funds, or confiscate balances.
2. **No Adversarial Vulnerability / Probing Interfaces:** The platform does not provide gradient discovery, threshold probing, score optimization, or fraud-evasion instructions.
3. **Role-Gated Human Authority:** Review resolutions require authenticated human analysts (`RISK_ANALYST` or `RISK_ADMIN`). Automated system actors are blocked from submitting review decisions.
4. **Preserved Decision Separation:** Automated model recommendations and human reviewer decisions are persisted in distinct database columns and never overwrite each other.
