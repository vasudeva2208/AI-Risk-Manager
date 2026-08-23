"""
Synthetic Return-Risk Dataset Generator (Phase 2).

Generates realistic e-commerce transactions, customer profiles, and return requests.
Includes subtle multi-factor behavioral anomalies without trivial formula leakage.
Class distribution reflects realistic imbalanced risk (~12-16% in targeted return claims).
Labeled explicitly as SYNTHETIC.
"""

import numpy as np
import pandas as pd
import datetime


def generate_synthetic_return_dataset(
    num_samples: int = 5000,
    random_seed: int = 42,
    base_start_date: str = "2025-01-01",
) -> pd.DataFrame:
    """
    Generates a synthetic dataset of return requests for model development and evaluation.
    
    Customer cohorts modeled:
    1. Legitimate loyal customers (frequent orders, rare returns, low friction).
    2. Occasional shoppers (low order count, occasional size mismatch).
    3. Bracketing shoppers (multiple sizes ordered, high legitimate return rate, low dispute).
    4. Abusive wardrobers / empty box claimants (velocity spikes, high price items, high refund-to-spend).
    5. Opportunistic first-time abusive claimants (new accounts, immediate high-value return).
    """
    np.random.seed(random_seed)
    start_dt = datetime.datetime.fromisoformat(base_start_date)

    records = []
    num_customers = max(500, num_samples // 3)
    customer_pool = [f"CUST_{i:05d}" for i in range(num_customers)]

    # Assign latent customer personas
    # 0: Standard Loyal (65%)
    # 1: Frequent / Bracketing (20%)
    # 2: Opportunistic / Wardrober (10%)
    # 3: Serial Abusive (5%)
    customer_personas = np.random.choice(
        [0, 1, 2, 3],
        size=num_customers,
        p=[0.65, 0.20, 0.10, 0.05]
    )
    customer_persona_map = dict(zip(customer_pool, customer_personas))

    categories = ["APPAREL", "ELECTRONICS", "LUXURY_GOODS", "BEAUTY", "HOME_GARDEN"]
    category_base_price = {
        "APPAREL": (40.0, 150.0),
        "ELECTRONICS": (80.0, 450.0),
        "LUXURY_GOODS": (200.0, 1200.0),
        "BEAUTY": (20.0, 80.0),
        "HOME_GARDEN": (30.0, 200.0),
    }

    reasons = ["DEFECTIVE", "WRONG_SIZE", "NOT_AS_DESCRIBED", "CHANGED_MIND", "ARRIVED_LATE"]
    conditions = ["UNOPENED", "OPENED_UNUSED", "WORN_OR_USED", "DAMAGED"]
    payment_methods = ["CREDIT_CARD", "DEBIT_CARD", "BUY_NOW_PAY_LATER", "STORE_CREDIT"]

    for i in range(num_samples):
        cust_id = np.random.choice(customer_pool)
        persona = customer_persona_map[cust_id]

        # Timestamp generation (spanning 180 days)
        day_offset = int(np.random.uniform(0, 180))
        order_time = start_dt + datetime.timedelta(
            days=day_offset,
            hours=int(np.random.uniform(0, 24)),
            minutes=int(np.random.uniform(0, 60))
        )
        delivery_days = int(np.random.choice([1, 2, 3, 5], p=[0.1, 0.4, 0.3, 0.2]))
        delivery_time = order_time + datetime.timedelta(days=delivery_days)
        
        # Days between delivery and return request
        if persona == 2:  # Wardrober (often returns right at 25-29 days limit after event use)
            days_to_return = int(np.random.choice([1, 2, 26, 27, 28, 29]))
        elif persona == 3: # Serial (immediate claim of empty box or after prolonged hold)
            days_to_return = int(np.random.choice([0, 1, 2, 28, 29]))
        else:
            days_to_return = int(np.random.exponential(scale=5.0)) + 1
            days_to_return = min(30, max(1, days_to_return))

        return_time = delivery_time + datetime.timedelta(days=days_to_return)

        # Behavioral and historical metrics based on persona
        if persona == 0:  # Standard Loyal
            account_age_days = int(np.random.uniform(90, 1200))
            order_count_lifetime = int(np.random.poisson(lam=12)) + 1
            return_count_lifetime = int(np.random.binomial(n=order_count_lifetime, p=0.08))
            dispute_count = int(np.random.binomial(n=1, p=0.01))
            orders_7d = int(np.random.poisson(lam=0.4))
            orders_30d = int(np.random.poisson(lam=1.5))
            orders_90d = orders_30d + int(np.random.poisson(lam=3.0))
            returns_7d = int(np.random.binomial(n=max(1, orders_7d), p=0.05))
            returns_30d = int(np.random.binomial(n=max(1, orders_30d), p=0.05))
            returns_90d = int(np.random.binomial(n=max(1, orders_90d), p=0.07))
            category = np.random.choice(categories, p=[0.4, 0.15, 0.05, 0.25, 0.15])
            p_low, p_high = category_base_price[category]
            order_amount = round(float(np.random.uniform(p_low, p_high)), 2)
            avg_order_value = round(order_amount * np.random.uniform(0.8, 1.2), 2)
            discounts = round(float(np.random.choice([0, 5, 10, 15, 25])), 2)
            pay_method = np.random.choice(payment_methods, p=[0.6, 0.3, 0.05, 0.05])
            reason = np.random.choice(reasons, p=[0.1, 0.6, 0.1, 0.15, 0.05])
            item_cond = np.random.choice(conditions, p=[0.4, 0.5, 0.08, 0.02])
            item_count = int(np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1]))

            # Latent abuse probability is very low
            abuse_latent = -3.8 + 0.5 * (dispute_count > 0) + 0.3 * (order_amount > 400)

        elif persona == 1:  # Frequent / Bracketing (Legitimate size sampler)
            account_age_days = int(np.random.uniform(60, 800))
            order_count_lifetime = int(np.random.poisson(lam=25)) + 5
            return_count_lifetime = int(np.random.binomial(n=order_count_lifetime, p=0.35))
            dispute_count = int(np.random.binomial(n=1, p=0.02))
            orders_7d = int(np.random.poisson(lam=1.2)) + 1
            orders_30d = int(np.random.poisson(lam=4)) + 1
            orders_90d = orders_30d + int(np.random.poisson(lam=8))
            returns_7d = int(np.random.binomial(n=orders_7d, p=0.35))
            returns_30d = int(np.random.binomial(n=orders_30d, p=0.35))
            returns_90d = int(np.random.binomial(n=orders_90d, p=0.35))
            category = np.random.choice(categories, p=[0.7, 0.05, 0.05, 0.1, 0.1])
            p_low, p_high = category_base_price[category]
            order_amount = round(float(np.random.uniform(p_low, p_high * 1.5)), 2)
            avg_order_value = round(order_amount * np.random.uniform(0.7, 1.3), 2)
            discounts = round(float(np.random.choice([0, 10, 20, 30])), 2)
            pay_method = np.random.choice(payment_methods, p=[0.5, 0.2, 0.25, 0.05])
            reason = "WRONG_SIZE" if np.random.rand() < 0.8 else np.random.choice(reasons)
            item_cond = np.random.choice(conditions, p=[0.3, 0.65, 0.04, 0.01])
            item_count = int(np.random.choice([2, 3, 4], p=[0.5, 0.3, 0.2]))

            # Legitimate bracketing is NOT abuse, despite high return rate
            abuse_latent = -3.2 + 0.4 * (dispute_count > 0)

        elif persona == 2:  # Opportunistic / Wardrober
            account_age_days = int(np.random.uniform(10, 300))
            order_count_lifetime = int(np.random.poisson(lam=4)) + 1
            return_count_lifetime = int(np.random.binomial(n=order_count_lifetime, p=0.55))
            dispute_count = int(np.random.binomial(n=2, p=0.15))
            orders_7d = int(np.random.poisson(lam=0.8))
            orders_30d = int(np.random.poisson(lam=1.8)) + 1
            orders_90d = orders_30d + int(np.random.poisson(lam=3))
            returns_7d = int(np.random.binomial(n=max(1, orders_7d + 1), p=0.6))
            returns_30d = int(np.random.binomial(n=orders_30d, p=0.6))
            returns_90d = int(np.random.binomial(n=orders_90d, p=0.6))
            category = np.random.choice(categories, p=[0.45, 0.25, 0.25, 0.03, 0.02])
            p_low, p_high = category_base_price[category]
            order_amount = round(float(np.random.uniform(p_low * 1.5, p_high * 1.8)), 2)
            avg_order_value = round(order_amount * 0.65, 2)  # High price spike vs history
            discounts = round(float(np.random.choice([0, 5])), 2)
            pay_method = np.random.choice(payment_methods, p=[0.3, 0.1, 0.55, 0.05])
            reason = np.random.choice(reasons, p=[0.3, 0.1, 0.4, 0.1, 0.1])
            item_cond = np.random.choice(conditions, p=[0.6, 0.1, 0.25, 0.05]) # Claims unopened but worn
            item_count = int(np.random.choice([1, 2], p=[0.8, 0.2]))

            # Elevated abuse probability
            abuse_latent = -0.5 + 0.8 * (pay_method == "BUY_NOW_PAY_LATER") + 0.7 * (dispute_count > 0) + 0.6 * (category in ["LUXURY_GOODS", "APPAREL"])

        else:  # Serial Abuser / Fraud Ring
            account_age_days = int(np.random.uniform(1, 60))
            order_count_lifetime = int(np.random.poisson(lam=2)) + 1
            return_count_lifetime = int(np.random.binomial(n=order_count_lifetime, p=0.85))
            dispute_count = int(np.random.poisson(lam=1.5))
            orders_7d = int(np.random.poisson(lam=1.2)) + 1
            orders_30d = int(np.random.poisson(lam=2.5)) + 1
            orders_90d = orders_30d + 1
            returns_7d = int(np.random.binomial(n=orders_7d, p=0.85))
            returns_30d = int(np.random.binomial(n=orders_30d, p=0.85))
            returns_90d = returns_30d
            category = np.random.choice(categories, p=[0.1, 0.45, 0.40, 0.03, 0.02])
            p_low, p_high = category_base_price[category]
            order_amount = round(float(np.random.uniform(p_high * 0.8, p_high * 2.2)), 2)
            avg_order_value = round(order_amount * 0.5, 2)
            discounts = 0.0
            pay_method = np.random.choice(payment_methods, p=[0.2, 0.05, 0.7, 0.05])
            reason = np.random.choice(["DEFECTIVE", "NOT_AS_DESCRIBED"], p=[0.5, 0.5])
            item_cond = np.random.choice(conditions, p=[0.7, 0.1, 0.1, 0.1])
            item_count = int(np.random.choice([1, 2], p=[0.85, 0.15]))

            abuse_latent = 1.2 + 0.9 * (category in ["ELECTRONICS", "LUXURY_GOODS"]) + 0.5 * (dispute_count > 1)

        # Sigmoid probability with stochastic noise to guarantee realistic overlap
        noise = np.random.normal(0, 0.4)
        prob_abuse = 1.0 / (1.0 + np.exp(-(abuse_latent + noise)))
        target_label = int(np.random.rand() < prob_abuse)

        historical_return_rate = round(return_count_lifetime / max(1, order_count_lifetime), 4)
        refund_amount = min(order_amount, round(order_amount * np.random.choice([1.0, 0.5, 0.33]), 2))
        historical_refund_amount = round(return_count_lifetime * avg_order_value * 0.9, 2)

        records.append({
            "return_id": f"RET_{i:06d}",
            "order_id": f"ORD_{i:06d}",
            "customer_id": cust_id,
            "order_timestamp": order_time.isoformat(),
            "delivery_timestamp": delivery_time.isoformat(),
            "request_timestamp": return_time.isoformat(),
            "order_amount": order_amount,
            "item_count": item_count,
            "product_category": category,
            "discount_amount": discounts,
            "payment_method": pay_method,
            "delivery_region": np.random.choice(["US_EAST", "US_WEST", "US_CENTRAL", "US_SOUTH"]),
            "fulfillment_method": np.random.choice(["STANDARD_GROUND", "EXPRESS_AIR", "SAME_DAY"]),
            "return_reason": reason,
            "item_condition_declared": item_cond,
            "refund_amount_requested": refund_amount,
            "return_method": np.random.choice(["MAIL_IN", "IN_STORE_DROP", "LOCKER_DROP"], p=[0.7, 0.2, 0.1]),
            # Customer state at return timestamp
            "customer_account_age_days": account_age_days,
            "customer_order_count_lifetime": order_count_lifetime,
            "customer_return_count_lifetime": return_count_lifetime,
            "historical_return_rate": historical_return_rate,
            "historical_refund_amount": historical_refund_amount,
            "customer_dispute_count": dispute_count,
            "orders_last_7d": orders_7d,
            "orders_last_30d": orders_30d,
            "orders_last_90d": orders_90d,
            "returns_last_7d": returns_7d,
            "returns_last_30d": returns_30d,
            "returns_last_90d": returns_90d,
            "customer_avg_order_value": avg_order_value,
            # Ground truth label
            "return_abuse": target_label,
            "dataset_type": "SYNTHETIC",
        })

    df = pd.DataFrame(records)
    # Sort chronologically by request timestamp
    df = df.sort_values(by="request_timestamp").reset_index(drop=True)
    return df
