"""
Data Splitter for Train, Validation, and Held-Out Test Datasets.

Ensures strict temporal splitting to mimic real-world production deployment.
The held-out test split remains completely isolated from model tuning.
"""

import pandas as pd
from typing import Tuple, Dict


def temporal_split(
    df: pd.DataFrame,
    timestamp_col: str = "request_timestamp",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Performs chronological temporal partitioning.
    
    Returns:
        (train_df, val_df, test_df)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5, "Ratios must sum to 1.0"

    df_sorted = df.sort_values(by=timestamp_col).reset_index(drop=True)
    n = len(df_sorted)

    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_df = df_sorted.iloc[:train_end].copy().reset_index(drop=True)
    val_df = df_sorted.iloc[train_end:val_end].copy().reset_index(drop=True)
    test_df = df_sorted.iloc[val_end:].copy().reset_index(drop=True)

    return train_df, val_df, test_df


def compute_split_summary(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str = "return_abuse"
) -> Dict[str, Dict[str, float]]:
    """Computes sample sizes and target prevalence across splits."""
    return {
        "train": {
            "count": len(train_df),
            "target_count": int(train_df[target_col].sum()),
            "prevalence": float(train_df[target_col].mean()),
        },
        "val": {
            "count": len(val_df),
            "target_count": int(val_df[target_col].sum()),
            "prevalence": float(val_df[target_col].mean()),
        },
        "held_out_test": {
            "count": len(test_df),
            "target_count": int(test_df[target_col].sum()),
            "prevalence": float(test_df[target_col].mean()),
        },
    }
