# System Architecture

## Overview
The AI Return-Risk Manager is an enterprise-grade defense platform designed to ingest return requests, compute temporal behavioral features, generate calibrated risk probabilities via interpretable ML models, calculate expected financial loss, enforce deterministic bounded action policies, and maintain tamper-evident audit trails.

## Architectural Layers

```
+-------------------------------------------------------------+
|                  Merchant Risk Dashboard                     |
|           (React 18 + Vite + TypeScript + Tailwind)         |
|   - Triage Queue  - Risk Inspector  - Model Performance     |
+-------------------------------------------------------------+
                              | REST / JSON
+-------------------------------------------------------------+
|                     FastAPI Backend                          |
|   - API Routers (/api/v1/assessments, /api/v1/orders)       |
|   - Deterministic Bounded Policy Engine                      |
|   - Audit Logging Service (SHA-256 Hash Chaining)           |
+-------------------------------------------------------------+
         |                                           |
+--------------------------+               +------------------+
|    ML Pipeline Module    |               |  PostgreSQL /    |
| - Feature Extraction     |               |  SQLAlchemy ORM  |
| - Preprocessing Pipeline |               |  - Customers     |
| - Calibrated Classifier  |               |  - Orders        |
| - Loss Estimator         |               |  - ReturnReqs    |
| - Evaluation Harness     |               |  - RiskAssmts    |
+--------------------------+               |  - AuditEvents   |
                                           +------------------+
```

## Core Subsystems

### 1. Data & Schema Layer
- **Customer Entity:** Tracks historical behavioral metrics (account age, historical return rate, dispute counts) without storing sensitive PII.
- **Order Entity:** Captures order amount, item count, discounts, delivery region, fulfillment method, and timestamps.
- **Return Request Entity:** Captures return reason, requested refund amount, item condition stated, and timestamps.

### 2. Feature Pipeline (`ml/features`)
- Computes deterministic historical aggregates strictly prior to the return request timestamp to prevent data leakage.
- Features include customer velocity ratios (7d, 30d, 90d), refund-to-spend ratios, price anomalies, and category baseline risk.

### 3. ML Scoring & Calibration (`ml/models`)
- **Baseline Model:** Calibrated Logistic Regression with standard scaling and one-hot encoding for categorical variables.
- Models produce an estimated posterior probability: $P(\text{return\_abuse} = 1 \mid \mathbf{x})$.

### 4. Bounded Policy Engine (`backend/app/policies`)
- Decouples ML predictions from operational actions.
- The model itself cannot authorize financial transactions or account bans.
- Policy maps $(P(\text{Abuse}), \text{Expected Loss})$ to bounded actions:
  - **LOW RISK ($p < 0.30$):** `APPROVE` (Standard Automated Return)
  - **MEDIUM RISK ($0.30 \le p < 0.70$):** `REQUIRE_ADDITIONAL_VERIFICATION` (Soft friction, photo verification, or physical drop-off)
  - **HIGH RISK ($p \ge 0.70$):** `MANUAL_REVIEW` (Flagged for human risk analyst evaluation)

### 5. Tamper-Evident Audit Service (`backend/app/services/audit.py`)
- Every assessment creates an audit record chained using cryptographic SHA-256 hashes ($H_n = \text{SHA256}(H_{n-1} + \text{Payload}_n)$).
- Any modification to historical records invalidates the hash verification check.
