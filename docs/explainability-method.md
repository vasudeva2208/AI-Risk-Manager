# Model-Derived Feature Attribution & Safe Explainability

---

## 1. Attribution Methodology: Model-Derived Feature Attribution

The explainability engine (`backend/app/services/explainability.py`) translates complex high-dimensional risk signals into human-readable merchant reasons.

### Calculation Method:
1. **Feature Deviation:** Measure difference between observed feature value $x_j$ and reference population median $\mu_j$:
   $$\Delta_j = \frac{x_j - \mu_j}{\sigma_j + \epsilon}$$
2. **Model Weighting:** Scale deviation by model feature attribution weight $w_j$:
   $$\text{Attribution Contribution } C_j = \Delta_j \times w_j$$
3. **Top Factor Ranking:** Rank features by $|C_j|$ and select top 3–5 bounded factors.
4. **Contextual Translation:** Map top features to merchant-safe plain-language explanations.

---

## 2. Safe Explainability Safeguards

* **Defense-Only Context:** Explanations explain *why* a return was flagged (e.g. "Customer profile has 2 prior chargebacks on record").
* **Prohibited Adversarial Output:** The explanation API and UI strictly forbid:
  * Evasion instructions (e.g. "Reduce order by \$50 to bypass review").
  * Sensitivity gradients or threshold probing.
  * Counterfactual manipulation advice.
* **Bounded Output:** Top 3–5 factors displayed by default to prevent cognitive overload.
