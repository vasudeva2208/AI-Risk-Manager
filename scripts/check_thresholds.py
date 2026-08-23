import numpy as np
import pandas as pd
from ml.data.generator import generate_synthetic_return_dataset
from ml.data.splitter import temporal_split
from ml.models.tree_model import TreeRiskModel
from ml.evaluation.metrics import compute_honest_metrics, compute_business_cost_matrix

df = generate_synthetic_return_dataset(num_samples=5000, random_seed=42)
train_df, val_df, test_df = temporal_split(df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
hgb_model = TreeRiskModel.load(artifact_dir="ml/models/candidate", model_version="return-risk-hgb-v1")
y_val_prob = hgb_model.predict_proba(val_df)

for t in [0.20, 0.25, 0.30, 0.35, 0.40]:
    m = compute_honest_metrics(val_df["return_abuse"].values, y_val_prob, threshold=t)
    c = compute_business_cost_matrix(val_df, y_val_prob, threshold=t)
    print(f"Threshold {t:.2f}: Precision={m['precision']:.4f}, Recall={m['recall']:.4f}, FP={c['fp_count']}, FN={c['fn_count']}, Reviews={c['review_count']}, Net Benefit INR={c['inr']['net_merchant_benefit']:,.2f}, USD={c['usd']['net_merchant_benefit']:,.2f}")
