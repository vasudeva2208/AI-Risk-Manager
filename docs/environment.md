# AI Risk Manager — Environment & Dependency Specification

---

## 1. Supported Runtime Environments

* **Machine Learning & Backend Runtime:** Python **3.11.x** (Tested with Python 3.11.9)
  * *Note: Python 3.11 is the designated stable production runtime for `scikit-learn`, `joblib`, and `pydantic`. The ML pipeline does NOT require Python 3.14.*
* **Frontend Runtime:** Node.js **20.x** or **22.x** (with npm 10+ / 11+)
* **Operating Systems:** Windows 10/11, macOS, Linux (Ubuntu 22.04 LTS / Debian 12)

---

## 2. Python Dependencies

### Backend (`backend/requirements.txt`)
* `fastapi >= 0.110.0`
* `uvicorn[standard] >= 0.28.0`
* `pydantic >= 2.6.0`
* `sqlalchemy >= 2.0.28`
* `pandas >= 2.2.0`
* `numpy >= 1.26.0`
* `httpx >= 0.27.0`
* `pytest >= 8.0.0`
* `pytest-asyncio >= 0.23.0`

### Machine Learning (`ml/requirements.txt`)
* `scikit-learn >= 1.4.0`
* `joblib >= 1.3.2`
* `pandas >= 2.2.0`
* `numpy >= 1.26.0`
* `pytest >= 8.0.0`

---

## 3. Frontend Dependencies (`frontend/package.json`)

* `react >= 18.2.0`
* `react-dom >= 18.2.0`
* `lucide-react >= 0.344.0` (Strictly SVG icons; 0 emojis)
* `tailwindcss >= 3.4.1`
* `typescript >= 5.2.2`
* `vite >= 5.1.4`

---

## 4. Virtual Environment Verification

To verify that the active environment matches expected specifications:

```bash
# Check Python version
python --version
# Output: Python 3.11.x

# Check Node version
node --version
# Output: v20.x.x or v22.x.x

# Run automated tests
pytest -v
# Output: 22+ passed
```
