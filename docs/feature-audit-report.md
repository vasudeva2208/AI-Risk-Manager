# Point-in-Time Feature Audit & Leakage Assessment

**Audit Date:** 2026-08-23  
**Feature Pipeline Version:** `v2_point_in_time_23f`  
**Total Features Audited:** 23  
**Prediction Point:** $T_{\text{request}}$ (Online return request initiation)

---

## 1. Feature Audit Summary Table

| Feature Name | Category | Available At | Lookback Window | Uses Future Data? | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_account_age_days` | Customer History | $T_{\text{request}}$ | Lifetime ($t \le T_{\text{request}}$) | No | **SAFE** |
| `customer_order_count_lifetime` | Customer History | $T_{\text{request}}$ | Lifetime ($t \le T_{\text{request}}$) | No | **SAFE** |
| `customer_return_count_lifetime` | Customer History | $T_{\text{request}}$ | Lifetime ($t \le T_{\text{request}}$) | No | **SAFE** |
| `historical_return_rate` | Customer History | $T_{\text{request}}$ | Lifetime ($t \le T_{\text{request}}$) | No | **SAFE** |
| `historical_refund_amount` | Customer History | $T_{\text{request}}$ | Lifetime ($t \le T_{\text{request}}$) | No | **SAFE** |
| `customer_dispute_count` | Customer History | $T_{\text{request}}$ | Lifetime ($t \le T_{\text{request}}$) | No | **SAFE** |
| `orders_last_7d` | Customer History | $T_{\text{request}}$ | 7 days ($T_{\text{request}} - 7\text{d}$) | No | **SAFE** |
| `orders_last_30d` | Customer History | $T_{\text{request}}$ | 30 days ($T_{\text{request}} - 30\text{d}$) | No | **SAFE** |
| `orders_last_90d` | Customer History | $T_{\text{request}}$ | 90 days ($T_{\text{request}} - 90\text{d}$) | No | **SAFE** |
| `returns_last_7d` | Return Behavior | $T_{\text{request}}$ | 7 days ($T_{\text{request}} - 7\text{d}$) | No | **SAFE** |
| `returns_last_30d` | Return Behavior | $T_{\text{request}}$ | 30 days ($T_{\text{request}} - 30\text{d}$) | No | **SAFE** |
| `returns_last_90d` | Return Behavior | $T_{\text{request}}$ | 90 days ($T_{\text{request}} - 90\text{d}$) | No | **SAFE** |
| `refund_to_spend_ratio` | Return Behavior | $T_{\text{request}}$ | Lifetime ($t \le T_{\text{request}}$) | No | **SAFE** |
| `order_amount` | Order Characteristics | $T_{\text{order}}$ | Transaction time | No | **SAFE** |
| `item_count` | Order Characteristics | $T_{\text{order}}$ | Transaction time | No | **SAFE** |
| `discount_amount` | Order Characteristics | $T_{\text{order}}$ | Transaction time | No | **SAFE** |
| `order_discount_ratio` | Order Characteristics | $T_{\text{order}}$ | Transaction time | No | **SAFE** |
| `order_vs_avg_spend_ratio` | Order Characteristics | $T_{\text{request}}$ | Historical average comparison | No | **SAFE** |
| `refund_vs_order_ratio` | Order Characteristics | $T_{\text{request}}$ | Request vs Order comparison | No | **SAFE** |
| `days_since_delivery` | Timing | $T_{\text{request}}$ | $T_{\text{request}} - T_{\text{delivery}}$ | No | **SAFE** |
| `product_category` | Transaction Context | $T_{\text{order}}$ | Transaction time | No | **SAFE** |
| `payment_method` | Transaction Context | $T_{\text{order}}$ | Transaction time | No | **SAFE** |
| `return_reason` | Transaction Context | $T_{\text{request}}$ | Claim initiation time | No | **SAFE** |

---

## 2. Leakage Categorization & Banned Features

The following features were evaluated and explicitly excluded from model inputs:
1. `warehouse_inspection_result` — **LEAKAGE (BANNED)**: Determined days after return request upon warehouse package intake.
2. `carrier_measured_return_weight` — **LEAKAGE (BANNED)**: Available only during carrier return transit.
3. `final_dispute_status` — **LEAKAGE (BANNED)**: Payment processor chargebacks filed weeks post-return.
4. `return_abuse_label` — **TARGET (BANNED FROM FEATURES)**: Ground truth outcome.

---

## 3. Conclusion
All 23 features in the active feature extraction pipeline (`ml/features/extractor.py`) are strictly point-in-time compliant and contain zero target or post-event leakage.
