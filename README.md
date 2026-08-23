
# AI Risk Manager

> **A defense-only, explainable AI risk management system for e-commerce return abuse and friendly return fraud prevention.**

[![Automated Tests](https://img.shields.io/badge/pytest-53%20passed-brightgreen.svg)]()
[![Model Version](https://img.shields.io/badge/champion%20model-return--risk--hgb--v1-blue.svg)]()
[![Precision @ Opt Threshold](https://img.shields.io/badge/held--out%20precision-75.00%25-informational.svg)]()
[![Recall @ Opt Threshold](https://img.shields.io/badge/held--out%20recall-85.07%25-informational.svg)]()
[![PR--AUC](https://img.shields.io/badge/held--out%20PR--AUC-0.7983-informational.svg)]()
[![Audit Log](https://img.shields.io/badge/audit%20ledger-SHA--256%20chained-success.svg)]()

## 🚀 Live Demo

- **Frontend:** https://ai-risk-manager-frontend-2ckd.onrender.com
- **Backend API:** https://ai-risk-manager-rzhv.onrender.com
- **API Documentation:** https://ai-risk-manager-rzhv.onrender.com/docs
- **Health Check:** https://ai-risk-manager-rzhv.onrender.com/health

> **Demo Notice:** This deployment uses synthetic simulation data for demonstration and evaluation. Economic benefit figures are not production savings.[![Automated Tests](https://img.shields.io/badge/pytest-47%20passed-brightgreen.svg)]()
[![Model Version](https://img.shields.io/badge/champion%20model-return--risk--hgb--v1-blue.svg)]()
[![Precision @ Opt Threshold](https://img.shields.io/badge/held--out%20precision-75.00%25-informational.svg)]()
[![Recall @ Opt Threshold](https://img.shields.io/badge/held--out%20recall-85.07%25-informational.svg)]()
[![PR--AUC](https://img.shields.io/badge/held--out%20PR--AUC-0.7983-informational.svg)]()
[![Audit Log](https://img.shields.io/badge/audit%20ledger-SHA--256%20chained-success.svg)]()

---

## 1. Product Overview

E-commerce return abuse and friendly return fraud (wardrobing, empty box claims, fraudulent return tags, claiming non-receipt after delivery, rapid refund velocity) quietly destroy merchant operating margins. Merchants face an asymmetric loss problem:
* **False Negatives:** Unmitigated refund loss + return shipping and handling overhead.
* **False Positives:** Legitimate customer friction, support labor, and lifetime churn.

**AI Risk Manager** bridges the gap between predictive ML risk scoring, economic loss modeling, deterministic policy bounding, authorized human review triage, and cryptographic auditability.

```
Point-in-Time Features (23)
            ↓
Calibrated ML Model (HistGradientBoosting)
            ↓
Expected Loss Engine (INR ₹ / USD $)
            ↓
Deterministic Bounded Policy (APPROVE | REQUIRE_ADDITIONAL_VERIFICATION | MANUAL_REVIEW)
            ↓
Human Review Queue (Analyst Triage with Mandatory Rationale)
            ↓
Tamper-Evident SHA-256 Audit Ledger
```

---

## 2. Machine Learning Methodology & Evaluation Integrity

* **Strict Temporal Split:** 5,000 transactions chronologically partitioned into:
  * **Train (70%, N=3,500):** Earliest transactions.
  * **Validation (15%, N=750):** Intermediate partition for Platt probability calibration and validation-only threshold optimization.
  * **Held-Out Test Set (15%, N=750):** Untouched partition evaluated **once** for reporting.
* **23 Point-in-Time Features:** Pre-event lifetime frequency, 7d/30d/90d velocity windows, financial drain ratios, timing, and categoricals (0 post-event target leakage).
* **Champion Model (`return-risk-hgb-v1`):** `HistGradientBoostingClassifier` with Platt sigmoid calibration.
* **Baseline Model (`return-risk-logreg-v1`):** Calibrated Logistic Regression preserved for side-by-side comparison.

### Held-Out Test Set Performance Benchmark ($N = 750$ records)

| Model | Operating Threshold | Precision | Recall | F1-Score | PR-AUC | ROC-AUC | Brier Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline LogReg** | 0.30 | 75.82% | 86.57% | 0.8084 | 0.7890 | 0.9329 | 0.0644 |
| **Champion HGB** | **0.30** | **75.00%** | **85.07%** | **0.7972** | **0.7983** | **0.9242** | **0.0671** |

### Held-Out Confusion Matrix ($T = 0.30$):
* **True Positives (Abusive returns caught):** $114$
* **False Positives (Legitimate customers challenged):** $38$
* **False Negatives (Abusive claims missed):** $20$
* **True Negatives (Legitimate returns under standard policy):** $578$

> [!WARNING]
> **SYNTHETIC SIMULATION — NOT PRODUCTION SAVINGS**  
> All performance metrics and financial estimates reflect simulation parameters on synthetic data distributions and do not represent realized merchant earnings.

---

## 3. Asymmetric Economic Cost Model

$$\text{Expected Loss} = P(\text{Abuse}) \times \left( \text{Refund Amount Requested} + \text{Return Handling Cost} \right)$$

* **Simulated Held-Out Test Net Benefit:**
  * **USD (\$):** `+$69,728.28` net benefit vs. unmitigated loss of \$77,659.82.
  * **INR (₹):** `+₹57,87,447.24` net benefit vs. unmitigated loss of ₹64,45,765.06.

---

## 4. Key Architectural Capabilities

1. **Defense-Only System Boundary:** The ML model predicts risk only. It does **not** directly deny transactions, freeze funds, or seize balances. Consequential actions route to soft verification friction or human review.
2. **Safe Merchant Explainability:** Real point-in-time feature contributions translated into merchant-facing risk reasons (e.g. multi-order return velocity spikes, dispute history, BNPL tender, basket deviation).
3. **Role-Based Review Governance:** Human reviewer decisions (`APPROVE_RETURN`, `REQUEST_ADDITIONAL_VERIFICATION`, `ESCALATE`) are restricted to authorized personas (`RISK_ANALYST`, `RISK_ADMIN`) and require mandatory non-empty rationale ($\ge 5$ characters).
4. **Decision Separation:** Automated model recommendations and human reviewer decisions are stored in distinct database fields and never overwrite each other.
5. **Tamper-Evident SHA-256 Audit Trail:** Every critical event is cryptographically chained. One-click verification (`/api/v1/audit/verify`) validates chain integrity or identifies corrupted records.

---

## 5. Quick Start Guide

### Prerequisites
* Python 3.11+
* Node.js 20+ / 22+

### 1. Install Dependencies
```bash
# Python Virtual Environment
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell (or source .venv/bin/activate on Linux/macOS)

pip install -r backend/requirements.txt
pip install -r ml/requirements.txt
npm --prefix frontend install
```

### 2. Run Pipeline & Seed Database
```bash
# Execute ML pipeline, calibration, validation optimization, and artifact generation
python scripts/generate_and_train.py

# Seed demo operational cases with triage history and verified SHA-256 audit chain
python scripts/seed_demo_data.py
```

### 3. Run Automated Tests
```bash
pytest -v
```
*Expected: 47 passed in < 10s.*

### 4. Start Backend & Frontend Services
```bash
# Terminal 1: Backend API Service (FastAPI)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend Dashboard (Vite + React)
npm --prefix frontend run dev
```

* **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
* **Backend API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Backend Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 6. Documentation Index

* [`docs/README.md`](docs/README.md) — Comprehensive documentation index.
* [`docs/evaluation-manifest.md`](docs/evaluation-manifest.md) — **Authoritative Evidence Chain** with held-out metrics, bootstrap CIs, and confusion matrix.
* [`docs/track-requirement-mapping.md`](docs/track-requirement-mapping.md) — Mapping of every Buildathon track requirement to implementation evidence.
* [`docs/submission-evidence.md`](docs/submission-evidence.md) — Consolidated judge-friendly technical narrative.
* [`docs/demo-runbook.md`](docs/demo-runbook.md) — **3-Minute Judge Demonstration Runbook** with exact talking points and failure recovery.
* [`docs/final-submission-checklist.md`](docs/final-submission-checklist.md) — Pre-submission verification checklist.
* [`docs/api.md`](docs/api.md) — Complete REST API specification for all `/api/v1` endpoints.

---

## 7. License & Governance

Built for the AI Risk Manager track. Strictly defense-only.
## 🛡️ Risk Governance

- Defense-only risk management
- No autonomous financial execution
- Bounded policy thresholds
- Human review for governed decisions
- Explainable risk factors
- Tamper-evident audit trail
- Audit-chain integrity verification
- PII minimization
- Separate validation and held-out test evaluation
- Baseline model preserved for auditability
## 🧰 Technology Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

### Machine Learning
- scikit-learn
- Pandas
- NumPy
- Joblib

### Deployment
- Render Static Site
- Render Web Service
- Render PostgreSQL
## 💻 Local Development

### Backend

```powershell
cd "AI Risk Manager"

.\.venv\Scripts\Activate.ps1

$env:PYTHONPATH = (Get-Location).Path

.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
## ☁️ Production Deployment

The production demo is deployed using Render:

| Component | Platform |
|---|---|
| Frontend | Render Static Site |
| Backend | Render Web Service |
| Database | Render PostgreSQL |

### Production URLs

- **Frontend:** https://ai-risk-manager-frontend-2ckd.onrender.com
- **Backend:** https://ai-risk-manager-rzhv.onrender.com
- **Swagger API:** https://ai-risk-manager-rzhv.onrender.com/docs
- **Health:** https://ai-risk-manager-rzhv.onrender.com/health

The frontend communicates with the backend through:

`VITE_API_BASE_URL`

Production secrets and database credentials are stored in Render environment variables and are not committed to Git.
