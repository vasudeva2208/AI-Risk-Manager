# Synthetic Data Realism & Quality Audit Report

**Audit Date:** 2026-08-23  
**Dataset Version:** `return-abuse-synthetic-v1`  
**Evaluation Dataset Scope:** 5,000 Chronologically Progressed Transactions  
**Demo Dataset Scope:** 40 Isolated Demonstration Records (`DATASET_TYPE = "demo"`)

> [!WARNING]
> **SYNTHETIC DATASET NOTICE**  
> This project currently evaluates its ML pipeline using synthetic data designed for development and demonstration. The reported metrics do not represent production merchant performance. Production deployment would require appropriately labelled historical merchant data and validation against real-world distributions.

---

## 1. Class Distribution & Partition Prevalence

| Partition | Total Records | Positive (Abusive) | Negative (Legitimate) | Prevalence Rate |
| :--- | :--- | :--- | :--- | :--- |
| **Entire Dataset** | 5,000 | 673 | 4,327 | 13.46% |
| **Training Partition (70%)** | 3,500 | 449 | 3,051 | 12.83% |
| **Validation Partition (15%)** | 750 | 90 | 660 | 12.00% |
| **Held-Out Test Partition (15%)** | 750 | 134 | 616 | 17.87% |

*Note: The natural chronological shift reflects realistic seasonal holiday shopping trends simulated in the latter 30 days of the 180-day generation window.*

---

## 2. Feature-Target Overlap & Variance

The dataset explicitly avoids deterministic separation between classes by modeling heterogeneous customer cohorts and stochastic Gaussian logit noise:

### A. Legitimate Behavioral Variance (Negative Class)
* **Legitimate Frequent Shoppers (Bracketing Persona):** Order multiple sizes of apparel with high legitimate return frequency (35% return rate), but low chargeback disputes and high net retained spend.
* **Legitimate High-Value Buyers:** Luxury goods and electronics purchases with zero dispute history.
* **Legitimate BNPL Users:** Tendered via Buy-Now-Pay-Later credit without velocity anomalies.

### B. Heterogeneous Risk Profiles (Positive Class)
* **Serial Empty-Box Claimants:** Low account age, immediate return requests (<24h post-delivery), elevated dispute frequency.
* **Wardrobers:** Late return claims (26–29 days post-delivery) on high-value apparel.
* **Velocity Abuse:** Rapid burst of 3+ return claims within 7 days.

---

## 3. Data Integrity & Sanitization Metrics

* **Missing Values Count:** `0` (100% complete data, zero nulls).
* **Identifier Uniqueness:**
  * Duplicate Return IDs: `0`
  * Duplicate Order IDs: `0`
  * Unique Customers: `1,577` across 5,000 transactions.
* **Target Leakage Check:** **PASSED** (0 post-event observation fields or target labels present in the 23-feature extraction matrix).

---

## 4. Feature Summary & Target Correlation Diagnostics

| Feature Name | Min | Median | Mean | Max | Target Correlation ($r$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `historical_return_rate` | 0.00 | 0.125 | 0.219 | 1.00 | +0.5932 |
| `customer_dispute_count` | 0.00 | 0.000 | 0.126 | 5.00 | +0.4920 |
| `returns_last_7d` | 0.00 | 0.000 | 0.407 | 6.00 | +0.4303 |
| `returns_last_30d` | 0.00 | 0.000 | 0.714 | 8.00 | +0.4226 |
| `customer_account_age_days` | 1.00 | 488.00 | 521.64 | 1,199.00 | -0.4116 |
| `customer_order_count_lifetime` | 1.00 | 13.00 | 14.60 | 47.00 | -0.3775 |
| `order_vs_avg_spend_ratio` | 0.10 | 1.000 | 1.135 | 4.88 | +0.2854 |
| `customer_return_velocity` | 0.00 | 0.000 | 0.285 | 4.00 | +0.3340 |
| `days_since_delivery` | 0.00 | 5.000 | 7.912 | 30.00 | +0.1845 |
| `order_amount` | 20.04 | 136.68 | 247.93 | 2,384.50 | +0.2612 |

---

## 5. Highly Correlated Features & Modeling Rationale

* **`returns_last_7d` ($r=+0.43$) vs. `returns_last_30d` ($r=+0.42$):** Both are retained because gradient-boosted decision trees use 7-day velocity to detect sudden burst attacks while using 30-day velocity to detect sustained return wear.
* **`historical_return_rate` ($r=+0.59$) vs. `customer_return_velocity` ($r=+0.33$):** Historical rate reflects lifetime customer habit, whereas velocity captures acute behavioral deviation.
