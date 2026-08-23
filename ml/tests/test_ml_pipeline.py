import os
import json
import pytest
import numpy as np
import pandas as pd
from ml.data.generator import generate_synthetic_return_dataset
from ml.data.splitter import temporal_split, compute_split_summary
from ml.features.extractor import extract_features, NUMERICAL_FEATURE_NAMES, CATEGORICAL_FEATURE_NAMES
from ml.models.baseline import BaselineRiskModel
from ml.models.tree_model import TreeRiskModel
from ml.evaluation.metrics import (
    compute_honest_metrics,
    compute_business_cost_matrix,
    optimize_threshold_on_validation,
    generate_curve_artifacts,
)


def test_dataset_generation_and_properties():
    df = generate_synthetic_return_dataset(num_samples=300, random_seed=123)
    assert len(df) == 300
    assert "return_abuse" in df.columns
    assert set(df["return_abuse"].unique()).issubset({0, 1})
    assert df["order_amount"].min() > 0
    assert df["dataset_type"].iloc[0] == "SYNTHETIC"
    assert not df.isnull().any().any(), "Dataset should not contain NaN values"


def test_duplicate_detection_and_uniqueness():
    df = generate_synthetic_return_dataset(num_samples=250, random_seed=42)
    assert df["return_id"].nunique() == len(df), "All return_ids must be strictly unique"
    assert df["order_id"].nunique() == len(df), "All order_ids must be strictly unique"


def test_temporal_split_isolation_and_ordering():
    df = generate_synthetic_return_dataset(num_samples=300, random_seed=42)
    train, val, test = temporal_split(df, timestamp_col="request_timestamp", train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    
    assert len(train) == 210
    assert len(val) == 45
    assert len(test) == 45

    # Check temporal ordering: max train timestamp <= min val timestamp <= min test timestamp
    max_train_ts = train["request_timestamp"].max()
    min_val_ts = val["request_timestamp"].min()
    max_val_ts = val["request_timestamp"].max()
    min_test_ts = test["request_timestamp"].min()

    assert max_train_ts <= min_val_ts, "Train dates must precede validation dates"
    assert max_val_ts <= min_test_ts, "Validation dates must precede test dates"


def test_feature_extraction_point_in_time_safety():
    df = generate_synthetic_return_dataset(num_samples=50, random_seed=99)
    feats = extract_features(df)

    # Verify no target or post-event columns are in features
    banned_columns = [
        "return_abuse",
        "return_abuse_label",
        "abuse_latent",
        "warehouse_inspection_note",
        "chargeback_final_disposition",
    ]
    for banned in banned_columns:
        assert banned not in feats.columns

    # Verify expected column counts
    for col in NUMERICAL_FEATURE_NAMES:
        assert col in feats.columns
    for col in CATEGORICAL_FEATURE_NAMES:
        assert col in feats.columns

    assert not feats.isnull().any().any(), "Engineered features must not contain NaNs"


def test_prediction_point_and_timing_integrity():
    df = generate_synthetic_return_dataset(num_samples=100, random_seed=42)
    req_ts = pd.to_datetime(df["request_timestamp"])
    order_ts = pd.to_datetime(df["order_timestamp"])
    del_ts = pd.to_datetime(df["delivery_timestamp"])

    assert (req_ts >= del_ts).all(), "Return request timestamp must be at or after delivery timestamp"
    assert (del_ts >= order_ts).all(), "Delivery timestamp must be at or after order timestamp"


def test_generator_determinism_and_variance():
    df1 = generate_synthetic_return_dataset(num_samples=100, random_seed=42)
    df2 = generate_synthetic_return_dataset(num_samples=100, random_seed=42)
    pd.testing.assert_frame_equal(df1, df2)

    df3 = generate_synthetic_return_dataset(num_samples=100, random_seed=999)
    assert not df1["order_amount"].equals(df3["order_amount"])


def test_legitimate_variance_not_all_abusive():
    df = generate_synthetic_return_dataset(num_samples=500, random_seed=42)
    high_order_legit = df[(df["order_amount"] > 300) & (df["return_abuse"] == 0)]
    assert len(high_order_legit) > 0

    high_ret_legit = df[(df["historical_return_rate"] > 0.25) & (df["return_abuse"] == 0)]
    assert len(high_ret_legit) > 0


def test_dataset_metadata_and_quality_artifact():
    quality_path = "ml/evaluation/results/dataset_quality.json"
    assert os.path.exists(quality_path)
    with open(quality_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["dataset_version"] == "return-abuse-synthetic-v1"
    assert meta["row_count"] == 5000
    assert meta["temporal_separation_verified"] is True
    assert meta["missing_values_count"] == 0


def test_model_selection_report_artifact():
    report_path = "ml/evaluation/results/model_selection_report.json"
    assert os.path.exists(report_path)
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    assert report["selected_model"] == "return-risk-hgb-v1"
    assert "selection_criterion" in report
    assert len(report["candidate_models"]) >= 2


def test_validation_vs_test_artifact():
    v_vs_t_path = "ml/evaluation/results/validation_vs_test.json"
    assert os.path.exists(v_vs_t_path)
    with open(v_vs_t_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation"]["sample_count"] == 750
    assert data["held_out_test"]["sample_count"] == 750
    assert "metrics" in data["validation"]
    assert "metrics" in data["held_out_test"]


def test_cost_sensitivity_artifact():
    sens_path = "ml/evaluation/results/cost_sensitivity.json"
    assert os.path.exists(sens_path)
    with open(sens_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "scenarios" in data
    assert len(data["scenarios"]) >= 5
    for sc in data["scenarios"]:
        assert sc["fp_cost_inr"] > 0
        assert 0.0 <= sc["optimal_validation_threshold"] <= 1.0


def test_confidence_intervals_artifact():
    ci_path = "ml/evaluation/results/confidence_intervals.json"
    assert os.path.exists(ci_path)
    with open(ci_path, "r", encoding="utf-8") as f:
        ci = json.load(f)
    for metric in ["precision", "recall", "f1_score", "pr_auc", "roc_auc"]:
        assert metric in ci
        assert ci[metric]["lower_95"] <= ci[metric]["estimate"] <= ci[metric]["upper_95"]


def test_evaluation_manifest_artifact():
    manifest_path = "ml/evaluation/results/evaluation_manifest.json"
    assert os.path.exists(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["champion_model_version"] == "return-risk-hgb-v1"
    assert manifest["baseline_model_version"] == "return-risk-logreg-v1"
    assert "artifacts" in manifest


def test_metric_honesty_confusion_matrix_identities():
    y_true = np.array([1, 1, 1, 0, 0, 0, 0, 1, 0, 1])
    y_prob = np.array([0.9, 0.8, 0.7, 0.6, 0.4, 0.3, 0.2, 0.1, 0.05, 0.85])
    m = compute_honest_metrics(y_true, y_prob, threshold=0.50)

    cm = m["confusion_matrix"]
    total_cm = cm["true_positives"] + cm["false_positives"] + cm["false_negatives"] + cm["true_negatives"]
    assert total_cm == len(y_true)

    calc_prec = cm["true_positives"] / (cm["true_positives"] + cm["false_positives"])
    calc_rec = cm["true_positives"] / (cm["true_positives"] + cm["false_negatives"])
    assert np.isclose(m["precision"], round(calc_prec, 4))
    assert np.isclose(m["recall"], round(calc_rec, 4))


def test_baseline_and_tree_model_reproducibility():
    df = generate_synthetic_return_dataset(num_samples=400, random_seed=42)
    train, val, test = temporal_split(df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)

    logreg = BaselineRiskModel(random_state=42)
    logreg.train(train, val_df=val)
    probs_logreg = logreg.predict_proba(test)
    assert len(probs_logreg) == len(test)
    assert np.all((probs_logreg >= 0.0) & (probs_logreg <= 1.0))

    hgb = TreeRiskModel(random_state=42)
    hgb.train(train, val_df=val)
    probs_hgb = hgb.predict_proba(test)
    assert len(probs_hgb) == len(test)
    assert np.all((probs_hgb >= 0.0) & (probs_hgb <= 1.0))


def test_threshold_selection_without_test_data():
    df = generate_synthetic_return_dataset(num_samples=400, random_seed=42)
    train, val, test = temporal_split(df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)

    hgb = TreeRiskModel(random_state=42)
    hgb.train(train, val_df=val)

    y_val_prob = hgb.predict_proba(val)
    best_thresh, grid = optimize_threshold_on_validation(val, y_val_prob)
    assert 0.30 <= best_thresh <= 0.80
    assert len(grid) == 11

    y_test_prob = hgb.predict_proba(test)
    metrics_test = compute_honest_metrics(test["return_abuse"].values, y_test_prob, threshold=best_thresh)
    assert 0.0 <= metrics_test["precision"] <= 1.0
    assert 0.0 <= metrics_test["recall"] <= 1.0


def test_curve_generation_and_calibration():
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0])
    y_prob = np.array([0.1, 0.2, 0.85, 0.75, 0.3, 0.9, 0.15, 0.4, 0.65, 0.25, 0.8, 0.1, 0.2, 0.95, 0.05])

    curves = generate_curve_artifacts(y_true, y_prob, n_bins=5)
    assert "pr_curve" in curves
    assert "roc_curve" in curves
    assert "calibration_curve" in curves
    assert len(curves["pr_curve"]) > 0
    assert len(curves["roc_curve"]) > 0


def test_asymmetric_cost_matrix_and_currency_support():
    test_df = pd.DataFrame({
        "return_abuse": [1, 1, 0, 0],
        "order_amount": [200.0, 150.0, 100.0, 80.0]
    })
    y_prob = np.array([0.8, 0.2, 0.7, 0.1])

    costs = compute_business_cost_matrix(
        df=test_df,
        y_prob=y_prob,
        threshold=0.50,
        currency_symbol="₹",
        currency_rate_to_inr=83.0,
    )
    assert costs["disclaimer"] == "SYNTHETIC SIMULATION — NOT PRODUCTION SAVINGS"
    assert costs["tp_count"] == 1
    assert costs["fn_count"] == 1
    assert costs["fp_count"] == 1
    assert costs["tn_count"] == 1
    assert "usd" in costs
    assert "inr" in costs
    assert costs["inr"]["gross_loss_prevented"] == round(costs["usd"]["gross_loss_prevented"] * 83.0, 2)
