# AI Risk Manager — 3-Minute Judge Demonstration Runbook

---

## Preparation (30 Seconds Before Demo)
1. **Start Backend:**
   ```bash
   # In terminal 1:
   .venv/Scripts/activate  # (or source .venv/bin/activate on Linux/Mac)
   python -m uvicorn backend.app.main:app --port 8000 --reload
   ```
2. **Start Frontend:**
   ```bash
   # In terminal 2:
   cd frontend
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.

---

## 3-Minute Live Demo Flow

### Step 1: Overview & Exposure (30s)
* **Screen:** [`Overview`](http://localhost:5173/)
* **Talking Point:** "AI Risk Manager provides e-commerce merchants with defense-only return abuse risk detection. Notice the clean operational dashboard: aggregate modeled loss exposure, active pending triage queue, and the synthetic simulation notice indicating active champion `return-risk-hgb-v1` evaluated on 23 point-in-time features."

### Step 2: Risk Monitor & Flagged Case (45s)
* **Screen:** [`Risk Monitor`](http://localhost:5173/)
* **Action:** Filter by **High Risk**. Click on case **`RET_E2E_99`** (`ASSMT_6F3B808BCD72`).
* **Talking Point:** "The Risk Monitor sorts return claims by risk probability and expected financial exposure. Let's inspect flagged return `RET_E2E_99`."

### Step 3: Inspector & Explainability (45s)
* **Screen:** [`Risk Assessment Inspector Drawer`](http://localhost:5173/)
* **Talking Points:**
  1. **Predicted Risk:** $80.0\%$ return-abuse risk propensity.
  2. **Top Risk Factors:** Explains *why* it was flagged—customer profile has 1 prior chargeback, 2 return requests in 30 days, BNPL tender, and low account age.
  3. **Expected Loss:** Modeled loss of $\text{₹}10,169.48$ based on $P(\text{Abuse}) \times (\text{Refund} + \text{Handling})$.
  4. **Policy Recommendation:** Deterministic bounded action `MANUAL_REVIEW`.

### Step 4: Human Review & Decision (30s)
* **Screen:** Click **"Open Human Review"**
* **Action:** Select Analyst Decision **`REQUEST_ADDITIONAL_VERIFICATION`**, enter rationale *"Customer has 2 returns in 30d; requested packaging photos and store receipt."*, click **Review & Confirm**, then **Record Decision**.
* **Talking Point:** "Notice the strict separation between automated model recommendations and human analyst decisions. Human resolutions require mandatory evidence rationale and role authentication."

### Step 5: Tamper-Evident Audit Ledger (30s)
* **Screen:** [`Audit Log`](http://localhost:5173/)
* **Action:** Click **"Re-verify Hash Chain"**.
* **Talking Point:** "Every assessment and review action is cryptographically sealed in a SHA-256 hash chain. The live verification endpoint confirms zero tampering across all ledger events."

### Step 6: Model Performance & Held-Out Honesty (30s)
* **Screen:** [`Model Performance`](http://localhost:5173/)
* **Talking Point:** "We report honest held-out test metrics on an untouched $N=750$ test partition. Precision: $75.00\%$, Recall: $85.07\%$, PR-AUC: $0.7983$, with full 95% bootstrap confidence intervals and transparent confusion matrix ($114/38/20/578$)."

---

## Demo Recovery Quick Reference

| Issue | Resolution Step |
|---|---|
| Backend port in use | Stop existing process or run `uvicorn backend.app.main:app --port 8001` |
| Database empty | Run `python -m ml.evaluation.evaluate_pipeline` to seed data |
| Frontend connection error | Verify backend is running on `http://localhost:8000/health` |
| Audit chain invalid | Run seed script to regenerate fresh clean genesis chain |
