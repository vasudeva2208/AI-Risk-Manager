# AI Risk Manager — Reproducibility & Pipeline Guide

This document defines the deterministic procedure for reproducing the complete ML training pipeline, held-out evaluation benchmarks, database seeding, backend server, and frontend dashboard from a clean environment.

---

## 1. Environment Requirements

* **Python:** 3.11.x (or 3.10+)
* **Node.js:** 20.x or 22+
* **Package Managers:** `pip`, `npm`

---

## 2. Setup & Virtual Environment

```bash
# 1. Clone repository and navigate to root
cd "AI Risk Manager"

# 2. Create Python virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# 4. Install backend and ML dependencies
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt

# 5. Install frontend dependencies
npm --prefix frontend install
```

---

## 3. End-to-End ML Pipeline Execution

To deterministically generate the 5,000-sample synthetic dataset, apply the 70/15/15 chronological split, compute the 23 point-in-time features, train and calibrate both baseline and champion models, optimize thresholds strictly on validation data, evaluate against the untouched held-out test set ($N=750$), and export machine-readable JSON artifacts:

```bash
# Execute single-command pipeline
python scripts/generate_and_train.py
```

### Deterministic Artifact Verification
The pipeline generates:
* `ml/models/candidate/return-risk-hgb-v1.joblib`
* `ml/models/candidate/return-risk-hgb-v1_calibrated.joblib`
* `ml/models/baseline/return-risk-logreg-v1.joblib`
* `ml/models/baseline/return-risk-logreg-v1_calibrated.joblib`
* `ml/evaluation/results/model_comparison.json`
* `frontend/public/evaluation_artifacts/model_comparison.json`

Held-out evaluation metrics match deterministically:
* **Champion Model:** `return-risk-hgb-v1`
* **Operating Threshold:** `0.30` (Validation Optimized)
* **Precision:** `75.00%`
* **Recall:** `85.07%`
* **F1-Score:** `0.7972`
* **PR-AUC:** `0.7983`
* **ROC-AUC:** `0.9242`
* **Brier Score:** `0.0671`
* **Confusion Matrix:** $TP=114, FP=38, FN=20, TN=578$

---

## 4. Database Initialization & Demo Seeding

```bash
# Seed 40 isolated operational demo cases with review triage and SHA-256 audit chaining
python scripts/seed_demo_data.py
```

*Note: Demo data ($N=40$) is strictly isolated from the ML evaluation benchmark dataset ($N=5,000$).*

---

## 5. Automated Test Suite Execution

Run the complete 22-test automated regression and integration test suite:

```bash
# Run pytest with detailed verbose output
pytest -v
```

Expected result: `22 passed in < 10s`.

---

## 6. Running Backend & Frontend Services

### Backend Service (FastAPI)
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* Interactive Swagger Docs: `http://127.0.0.1:8000/docs`
* Health Check: `http://127.0.0.1:8000/health`

### Frontend Application (Vite + React)
```bash
npm --prefix frontend run dev
```
* Frontend Dashboard: `http://localhost:5173`

### Frontend Production Build
```bash
npm --prefix frontend run build
```
