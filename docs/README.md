# AI Risk Manager — Documentation Index

Welcome to the comprehensive technical documentation for the **AI Risk Manager** project.

---

## 1. Problem & Prediction Point
* [`problem-definition.md`](problem-definition.md) — Targeted financial loss problem: E-commerce return abuse and friendly return fraud.
* [`prediction-point.md`](prediction-point.md) — Prediction moment formalization ($T_{\text{request}}$) and strict anti-leakage boundaries.

## 2. Data & ML Pipeline
* [`data-schema.md`](data-schema.md) — Domain schemas for customers, orders, return requests, and assessments.
* [`feature-specification.md`](feature-specification.md) — Formal mathematical definitions of all 23 point-in-time features.
* [`feature-audit-report.md`](feature-audit-report.md) — Audit confirming 0 forward leakage across all features.
* [`synthetic-data-audit.md`](synthetic-data-audit.md) — Statistical realism and distribution audit of the 5,000-record dataset.
* [`evaluation-methodology.md`](evaluation-methodology.md) — Chronological 70/15/15 partitioning and validation-only threshold tuning.
* [`evaluation-manifest.md`](evaluation-manifest.md) — **Authoritative Evidence Chain** with held-out metrics, bootstrap CIs, and confusion matrix.
* [`model-selection.md`](model-selection.md) — Candidate evaluation comparing HistGradientBoosting vs Logistic Regression.
* [`statistical-confidence.md`](statistical-confidence.md) — 1,000 bootstrap resample confidence intervals.

## 3. Decision Engine & Governance
* [`defense-only-policy.md`](defense-only-policy.md) — Strict defense-only mandate prohibiting autonomous fund seizures or payment denials.
* [`decision-governance.md`](decision-governance.md) — Three-layer separation of concerns (Model Prediction vs Policy Recommendation vs Human Decision).
* [`risk-score-contract.md`](risk-score-contract.md) — Mathematical probability contract ($P \in [0, 1]$) and determinism.
* [`decision-thresholds.md`](decision-thresholds.md) — ML operating threshold ($T=0.30$) vs operational policy bands ($<0.30, 0.30\text{–}0.70, \ge 0.70$).
* [`explainability-method.md`](explainability-method.md) — Model-derived feature attribution methodology.
* [`audit-integrity.md`](audit-integrity.md) — Cryptographic SHA-256 chained audit ledger and verification endpoints.
* [`cost-sensitivity.md`](cost-sensitivity.md) — Asymmetric economic cost model and grid search validation.

## 4. Operations & Demo
* [`demo-runbook.md`](demo-runbook.md) — **3-Minute Judge Demonstration Runbook** with exact talking points and failure recovery.
* [`api.md`](api.md) — Complete REST API specification for all `/api/v1` endpoints.

## 5. Buildathon Submission
* [`track-requirement-mapping.md`](track-requirement-mapping.md) — Explicit mapping of every Buildathon track requirement to implementation evidence.
* [`submission-evidence.md`](submission-evidence.md) — Consolidated judge-friendly technical narrative.
* [`final-submission-checklist.md`](final-submission-checklist.md) — Pre-submission verification checklist.
