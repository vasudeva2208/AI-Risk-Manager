# AI Risk Manager — Production Deployment Guide

> **SYNTHETIC SIMULATION — NOT PRODUCTION SAVINGS**  
> All model performance metrics and economic loss simulations reflect synthetic distributions and do not represent realized financial savings.

---

## 1. System Architecture & Component Decoupling

AI Risk Manager is designed as a decoupled, defense-only system comprising:
1. **FastAPI Backend Service (`backend/`):** REST API providing risk scoring, bounded policy recommendations, human review state transitions, and SHA-256 audit ledger verification.
2. **React/TypeScript Frontend SPA (`frontend/`):** Enterprise merchant console providing risk monitoring, review workflows, feature explainability inspection, audit log verification, and model performance metrics.
3. **ML Model Registry & Evaluation Assets (`ml/`, `frontend/public/evaluation_artifacts/`):** Versioned, reproducible serialized models (`return-risk-hgb-v1.joblib`, `return-risk-logreg-v1.joblib`) and evaluation benchmark JSONs.

---

## 2. Environment Variables Specification

### Backend Environment Variables (`.env`)

| Variable | Type | Default (Local) | Production Example | Description |
|---|---|---|---|---|
| `APP_NAME` | string | `"AI Return Risk Manager"` | `"AI Return Risk Manager"` | Service title in OpenAPI documentation |
| `APP_ENV` | string | `"development"` | `"production"` | Application runtime environment (`development` / `production`) |
| `DEBUG` | boolean | `True` | `False` | Enable debug logs and detailed traces |
| `API_V1_STR` | string | `"/api/v1"` | `"/api/v1"` | API v1 router prefix |
| `SECRET_KEY` | string | (dev default) | `<high-entropy-64-char-secret>` | Secret key for cryptographic utilities |
| `CORS_ORIGINS` | string | `http://localhost:3000,...` | `https://risk.merchantdomain.com` | Comma-separated list of allowed frontend origins |
| `DATABASE_URL` | string | `sqlite:///./risk_manager.db` | `postgresql://USER:PASSWORD@db:5432/risk_db` | Relational database connection string |
| `MODEL_DIR` | string | `ml/models/artifacts` | `ml/models/artifacts` | Directory containing serialized champion and baseline model files |
| `ACTIVE_MODEL_VERSION` | string | `return-risk-hgb-v1` | `return-risk-hgb-v1` | Active production champion model version |
| `POLICY_THRESHOLD_LOW` | float | `0.30` | `0.30` | Lower bounded policy threshold for `APPROVE` recommendation |
| `POLICY_THRESHOLD_HIGH` | float | `0.70` | `0.70` | Upper bounded policy threshold for `MANUAL_REVIEW` recommendation |

### Frontend Environment Variables (`frontend/.env`)

| Variable | Type | Default (Local) | Production Example | Description |
|---|---|---|---|---|
| `VITE_API_BASE_URL` | string | `http://127.0.0.1:8000` | `https://api-risk.merchantdomain.com` | Base URL of the deployed FastAPI backend service |

---

## 3. Local Development vs. Production Setup

### Local Development Setup
1. **Backend:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # or source .venv/bin/activate
   pip install -r backend/requirements.txt -r ml/requirements.txt
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *The frontend will automatically communicate with the backend at `http://127.0.0.1:8000` by default or via the Vite dev proxy.*

---

## 4. Production Deployment Procedures

### Backend Deployment (Docker / Cloud Container)
1. Ensure all model artifacts are present under `ml/models/` and `ml/models/artifacts/`.
2. Configure environment variables (`APP_ENV=production`, `CORS_ORIGINS=https://risk.merchantdomain.com`, `DATABASE_URL=...`).
3. Run using a production ASGI server (e.g. `uvicorn` with multiple workers or `gunicorn` with `uvicorn.workers.UvicornWorker`):
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Frontend Deployment (Static Hosting / CDN)
1. Set the build environment variable `VITE_API_BASE_URL` pointing to your deployed backend origin:
   ```bash
   export VITE_API_BASE_URL="https://api-risk.merchantdomain.com"
   ```
2. Build the production assets:
   ```bash
   npm --prefix frontend install
   npm --prefix frontend run build
   ```
3. Deploy the generated `frontend/dist/` directory to any modern static hosting provider (e.g. Cloudflare Pages, AWS S3 + CloudFront, Vercel, Netlify, NGINX).

---

## 5. Security & CORS Hardening

* **Wildcard Prevention:** When `APP_ENV=production`, the backend strictly disallows wildcard `*` in `CORS_ORIGINS` and will fail safely with a startup validation error if an unsafe wildcard origin is provided.
* **Defense-Only Guarantee:** The API exposes strictly bounded recommendations and does not execute payment gateway refunds, bank settlements, or customer fund freezing.
* **PII Minimization:** The backend hashes and pseudonymizes customer IDs; no raw payment credentials or credit card numbers are ever accepted or stored.

---

## 6. Health Check & Monitoring

* **Health Endpoint:** `GET /health`
  ```json
  {
    "status": "healthy",
    "app_name": "AI Return Risk Manager",
    "environment": "production",
    "active_model": "return-risk-hgb-v1",
    "currency": "INR",
    "policy_thresholds": {
      "low": 0.3,
      "high": 0.7
    }
  }
  ```
* **Audit Chain Integrity:** `GET /api/v1/audit/verify` (Returns `VALID` and verification count).
