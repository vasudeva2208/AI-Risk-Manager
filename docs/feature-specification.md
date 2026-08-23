# AI Risk Manager — 23 Point-in-Time Features Formal Specification

**Pipeline Version:** `v2_point_in_time_23f`  
**Prediction Point:** $T_{\text{request}}$ (Time of online return claim creation)  
**Total Features:** 23 (18 numerical, 2 engineered ratios, 3 categorical)

---

## Group 1: Customer History (7 Features)

1. `customer_account_age_days` (Numeric, $\ge 0$)
   * **Definition:** Elapsed days between customer account creation and $T_{\text{request}}$.
   * **Domain Context:** New accounts (<30 days) historically exhibit higher chargeback and return abuse propensity.

2. `customer_order_count_lifetime` (Numeric, $\ge 0$)
   * **Definition:** Cumulative orders successfully completed by customer prior to current order.

3. `customer_return_count_lifetime` (Numeric, $\ge 0$)
   * **Definition:** Cumulative return requests initiated by customer prior to current request.

4. `historical_return_rate` (Numeric, $[0.0, 1.0]$)
   * **Definition:** $\frac{\text{customer\_return\_count\_lifetime}}{\max(1, \text{customer\_order\_count\_lifetime})}$.

5. `historical_refund_amount` (Numeric, $\ge 0.0$)
   * **Definition:** Cumulative lifetime currency amount refunded to customer.

6. `customer_dispute_count` (Numeric, $\ge 0$)
   * **Definition:** Total formal credit card chargebacks or payment disputes on record.

7. `orders_last_7d`, `orders_last_30d`, `orders_last_90d` (Numeric, $\ge 0$)
   * **Definition:** Rolling window order counts prior to $T_{\text{request}}$.

---

## Group 2: Return Behavior & Velocity (4 Features)

8. `returns_last_7d` (Numeric, $\ge 0$)
   * **Definition:** Return claims submitted in the trailing 7 days prior to $T_{\text{request}}$.

9. `returns_last_30d` (Numeric, $\ge 0$)
   * **Definition:** Return claims submitted in the trailing 30 days prior to $T_{\text{request}}$.

10. `returns_last_90d` (Numeric, $\ge 0$)
    * **Definition:** Return claims submitted in the trailing 90 days prior to $T_{\text{request}}$.

11. `refund_to_spend_ratio` (Numeric, $[0.0, \infty)$)
    * **Definition:** Cumulative historical refunds divided by total lifetime order gross spend. High ratios (>0.50) indicate negative customer lifetime value and financial extraction.

---

## Group 3: Order Characteristics (5 Features)

12. `order_amount` (Numeric, $> 0.0$)
    * **Definition:** Gross monetary value of the order.

13. `item_count` (Numeric, $\ge 1$)
    * **Definition:** Number of distinct items in the order.

14. `discount_amount` (Numeric, $\ge 0.0$)
    * **Definition:** Total coupon / promo code discount applied at checkout.

15. `order_discount_ratio` (Numeric, $[0.0, 1.0]$)
    * **Definition:** $\frac{\text{discount\_amount}}{\text{order\_amount} + \text{discount\_amount}}$.

16. `order_vs_avg_spend_ratio` (Numeric, $\ge 0.0$)
    * **Definition:** Current order amount relative to the customer's historical average order value ($\frac{\text{order\_amount}}{\max(10, \text{customer\_avg\_order\_value})}$).

---

## Group 4: Timing Dynamics (2 Features)

17. `days_since_delivery` (Numeric, $\ge 0$)
    * **Definition:** Elapsed days between order delivery timestamp and return request timestamp ($T_{\text{request}} - T_{\text{delivery}}$).
    * **Domain Context:** Abusive claims frequently occur either immediately (<1 day, claiming empty box) or at the outer edge of policy (25–30 days, wardrobing).

18. `refund_vs_order_ratio` (Numeric, $[0.0, 1.0]$)
    * **Definition:** Requested refund amount divided by original order gross amount.

---

## Group 5: Transaction Context & Categoricals (3 Features)

19. `product_category` (Categorical)
    * **Values:** `APPAREL`, `ELECTRONICS`, `LUXURY_GOODS`, `BEAUTY`, `HOME_GARDEN`.

20. `payment_method` (Categorical)
    * **Values:** `CREDIT_CARD`, `DEBIT_CARD`, `BUY_NOW_PAY_LATER`, `STORE_CREDIT`.

21. `return_reason` (Categorical)
    * **Values:** `DEFECTIVE`, `WRONG_SIZE`, `NOT_AS_DESCRIBED`, `CHANGED_MIND`, `ARRIVED_LATE`.
