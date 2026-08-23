"""
Deterministic Feature Extraction Engine (Phase 2).

Computes point-in-time features strictly using data available before the return request.
"""

import pandas as pd
import numpy as np


NUMERICAL_FEATURE_NAMES = [
    "customer_account_age_days",
    "customer_order_count_lifetime",
    "customer_return_count_lifetime",
    "historical_return_rate",
    "customer_dispute_count",
    "orders_last_7d",
    "orders_last_30d",
    "orders_last_90d",
    "returns_last_7d",
    "returns_last_30d",
    "returns_last_90d",
    "customer_return_velocity",
    "refund_to_spend_ratio",
    "order_amount",
    "order_item_count",
    "order_discount_ratio",
    "order_vs_avg_spend_ratio",
    "days_since_delivery",
    "refund_requested_ratio",
]

CATEGORICAL_FEATURE_NAMES = [
    "product_category",
    "payment_method",
    "return_reason",
    "item_condition_declared",
]

ALL_FEATURE_COLUMNS = NUMERICAL_FEATURE_NAMES + CATEGORICAL_FEATURE_NAMES


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts deterministic risk features from transaction and return records.
    Assumes all required raw fields are present.
    """
    feats = pd.DataFrame(index=df.index)

    # 1. Customer lifetime & baseline behavioral metrics
    feats["customer_account_age_days"] = df["customer_account_age_days"].astype(float).fillna(0.0)
    feats["customer_order_count_lifetime"] = df["customer_order_count_lifetime"].astype(float).fillna(0.0)
    feats["customer_return_count_lifetime"] = df["customer_return_count_lifetime"].astype(float).fillna(0.0)
    feats["historical_return_rate"] = df["historical_return_rate"].astype(float).fillna(0.0).clip(0.0, 1.0)
    feats["customer_dispute_count"] = df["customer_dispute_count"].astype(float).fillna(0.0)

    # 2. Multi-window velocity metrics (7d, 30d, 90d)
    feats["orders_last_7d"] = df["orders_last_7d"].astype(float).fillna(0.0) if "orders_last_7d" in df.columns else np.zeros(len(df))
    feats["orders_last_30d"] = df["orders_last_30d"].astype(float).fillna(0.0)
    feats["orders_last_90d"] = df["orders_last_90d"].astype(float).fillna(0.0) if "orders_last_90d" in df.columns else feats["orders_last_30d"] * 2.5

    feats["returns_last_7d"] = df["returns_last_7d"].astype(float).fillna(0.0) if "returns_last_7d" in df.columns else np.zeros(len(df))
    feats["returns_last_30d"] = df["returns_last_30d"].astype(float).fillna(0.0)
    feats["returns_last_90d"] = df["returns_last_90d"].astype(float).fillna(0.0) if "returns_last_90d" in df.columns else feats["returns_last_30d"] * 2.0

    # Return velocity ratio
    feats["customer_return_velocity"] = (
        feats["returns_last_30d"] / np.maximum(1.0, feats["orders_last_30d"])
    ).clip(0.0, 5.0)

    # 3. Financial ratios
    total_spend = np.maximum(1.0, df["customer_order_count_lifetime"] * df["customer_avg_order_value"])
    feats["refund_to_spend_ratio"] = (df["historical_refund_amount"] / total_spend).clip(0.0, 5.0)

    # 4. Current order features
    feats["order_amount"] = df["order_amount"].astype(float)
    feats["order_item_count"] = df["item_count"].astype(float).fillna(1.0)
    
    gross_order = df["order_amount"] + df["discount_amount"]
    feats["order_discount_ratio"] = np.where(
        gross_order > 0,
        df["discount_amount"] / gross_order,
        0.0
    )

    feats["order_vs_avg_spend_ratio"] = (
        df["order_amount"] / np.maximum(1.0, df["customer_avg_order_value"])
    ).clip(0.0, 10.0)

    # 5. Temporal return request timing
    req_ts = pd.to_datetime(df["request_timestamp"])
    del_ts = pd.to_datetime(df["delivery_timestamp"])
    days_since_delivery = (req_ts - del_ts).dt.total_seconds() / (24 * 3600)
    feats["days_since_delivery"] = days_since_delivery.clip(0.0, 90.0).fillna(5.0)

    feats["refund_requested_ratio"] = np.where(
        df["order_amount"] > 0,
        (df["refund_amount_requested"] / df["order_amount"]).clip(0.0, 2.0),
        1.0
    )

    # 6. Categoricals
    for cat_col in CATEGORICAL_FEATURE_NAMES:
        feats[cat_col] = df[cat_col].astype(str).fillna("UNKNOWN")

    return feats
