"""
Honest Evaluation, Calibration, and Business Cost Matrix Framework (Phase 2).

Computes precision, recall, F1, PR-AUC, ROC-AUC, Brier score, confusion matrix,
calibration curve bins, PR curve points, ROC curve points, and asymmetric
financial cost metrics strictly on evaluation sets.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
)
from sklearn.calibration import calibration_curve


def compute_honest_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.50,
) -> Dict[str, Any]:
    """
    Computes statistical and classification metrics on un-resampled evaluation data.
    """
    y_pred = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.0
    pr_auc = float(average_precision_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.0
    brier = float(brier_score_loss(y_true, y_prob))

    fpr = float(fp / max(1, fp + tn))
    fnr = float(fn / max(1, fn + tp))

    return {
        "operating_threshold": round(threshold, 4),
        "sample_count": int(len(y_true)),
        "positive_count": int(np.sum(y_true)),
        "prevalence": float(np.mean(y_true)),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
    }


def compute_business_cost_matrix(
    df: pd.DataFrame,
    y_prob: np.ndarray,
    threshold: float = 0.50,
    cost_review_friction: float = 15.00,
    cost_fp_churn: float = 35.00,
    cost_return_shipping: float = 8.50,
    currency_symbol: str = "₹",
    currency_rate_to_inr: float = 83.0,
    target_col: str = "return_abuse",
    amount_col: str = "order_amount",
) -> Dict[str, Any]:
    """
    Computes asymmetric merchant economic impact:
    - True Positives (Abuse caught): Prevented loss = Order Amount - Review Friction
    - False Positives (Legitimate customer flagged): Cost = Review Labor + Customer Friction
    - False Negatives (Abuse missed): Loss = Order Amount + Return Shipping
    - True Negatives: $0 cost
    """
    y_true = df[target_col].values
    order_amounts = df[amount_col].values
    y_pred = (y_prob >= threshold).astype(int)

    tp_mask = (y_true == 1) & (y_pred == 1)
    fp_mask = (y_true == 0) & (y_pred == 1)
    fn_mask = (y_true == 1) & (y_pred == 0)
    tn_mask = (y_true == 0) & (y_pred == 0)

    tp_count = int(np.sum(tp_mask))
    fp_count = int(np.sum(fp_mask))
    fn_count = int(np.sum(fn_mask))
    tn_count = int(np.sum(tn_mask))
    review_count = tp_count + fp_count

    # Unit costs
    fp_unit_cost = cost_review_friction + cost_fp_churn
    total_fp_cost_usd = float(fp_count * fp_unit_cost)
    total_fn_loss_usd = float(np.sum(order_amounts[fn_mask] + cost_return_shipping))
    tp_review_costs_usd = float(tp_count * cost_review_friction)
    gross_loss_prevented_usd = float(np.sum(order_amounts[tp_mask]))

    # Total cost = (FP * FP_COST) + (FN * FN_COST) + (REVIEW_COUNT * REVIEW_COST)
    total_operational_cost_usd = total_fp_cost_usd + total_fn_loss_usd + tp_review_costs_usd

    # Baseline cost if NO model was used (all returns accepted without check)
    baseline_unmitigated_loss_usd = float(np.sum(order_amounts[y_true == 1] + cost_return_shipping))

    # Net merchant benefit compared to doing nothing
    net_economic_benefit_usd = baseline_unmitigated_loss_usd - total_operational_cost_usd

    # Currency conversion for presentation
    return {
        "disclaimer": "SYNTHETIC SIMULATION — NOT PRODUCTION SAVINGS",
        "operating_threshold": round(threshold, 4),
        "currency_symbol": currency_symbol,
        "tp_count": tp_count,
        "fp_count": fp_count,
        "fn_count": fn_count,
        "tn_count": tn_count,
        "review_count": review_count,
        "usd": {
            "baseline_unmitigated_loss": round(baseline_unmitigated_loss_usd, 2),
            "gross_loss_prevented": round(gross_loss_prevented_usd, 2),
            "false_positive_friction_cost": round(total_fp_cost_usd, 2),
            "false_negative_realized_loss": round(total_fn_loss_usd, 2),
            "review_labor_expenditure": round(tp_review_costs_usd, 2),
            "total_estimated_cost": round(total_operational_cost_usd, 2),
            "net_merchant_benefit": round(net_economic_benefit_usd, 2),
        },
        "inr": {
            "baseline_unmitigated_loss": round(baseline_unmitigated_loss_usd * currency_rate_to_inr, 2),
            "gross_loss_prevented": round(gross_loss_prevented_usd * currency_rate_to_inr, 2),
            "false_positive_friction_cost": round(total_fp_cost_usd * currency_rate_to_inr, 2),
            "false_negative_realized_loss": round(total_fn_loss_usd * currency_rate_to_inr, 2),
            "review_labor_expenditure": round(tp_review_costs_usd * currency_rate_to_inr, 2),
            "total_estimated_cost": round(total_operational_cost_usd * currency_rate_to_inr, 2),
            "net_merchant_benefit": round(net_economic_benefit_usd * currency_rate_to_inr, 2),
        }
    }


def optimize_threshold_on_validation(
    val_df: pd.DataFrame,
    y_val_prob: np.ndarray,
    candidate_thresholds: List[float] = None,
    target_col: str = "return_abuse",
    cost_review_friction: float = 15.00,
    cost_fp_churn: float = 35.00,
    cost_return_shipping: float = 8.50,
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Evaluates candidate thresholds on the VALIDATION SET ONLY to select optimal operating threshold.
    Selection criteria: Maximizes Net Merchant Economic Benefit on validation data.
    """
    if candidate_thresholds is None:
        candidate_thresholds = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]

    y_val_true = val_df[target_col].values
    results = []
    best_threshold = 0.50
    max_net_benefit = -float("inf")

    for t in candidate_thresholds:
        metrics = compute_honest_metrics(y_val_true, y_val_prob, threshold=t)
        costs = compute_business_cost_matrix(
            df=val_df,
            y_prob=y_val_prob,
            threshold=t,
            cost_review_friction=cost_review_friction,
            cost_fp_churn=cost_fp_churn,
            cost_return_shipping=cost_return_shipping,
        )

        row = {
            "threshold": round(t, 2),
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1_score": metrics["f1_score"],
            "fp_count": costs["fp_count"],
            "fn_count": costs["fn_count"],
            "review_count": costs["review_count"],
            "total_cost_usd": costs["usd"]["total_estimated_cost"],
            "net_benefit_usd": costs["usd"]["net_merchant_benefit"],
            "net_benefit_inr": costs["inr"]["net_merchant_benefit"],
        }
        results.append(row)

        if costs["usd"]["net_merchant_benefit"] > max_net_benefit:
            max_net_benefit = costs["usd"]["net_merchant_benefit"]
            best_threshold = t

    return best_threshold, results


def generate_curve_artifacts(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> Dict[str, Any]:
    """
    Generates exact data points for PR curve, ROC curve, and calibration reliability diagrams.
    """
    # 1. Precision-Recall curve
    precisions, recalls, pr_thresholds = precision_recall_curve(y_true, y_prob)
    # Downsample points for efficient serialization
    step = max(1, len(precisions) // 50)
    pr_points = [
        {"recall": round(float(r), 4), "precision": round(float(p), 4)}
        for p, r in zip(precisions[::step], recalls[::step])
    ]

    # 2. ROC curve
    fprs, tprs, roc_thresholds = roc_curve(y_true, y_prob)
    step_roc = max(1, len(fprs) // 50)
    roc_points = [
        {"fpr": round(float(f), 4), "tpr": round(float(t), 4)}
        for f, t in zip(fprs[::step_roc], tprs[::step_roc])
    ]

    # 3. Calibration curve (reliability diagram)
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins, strategy="uniform")
    calib_points = [
        {"predicted_prob": round(float(p), 4), "empirical_fraction": round(float(t), 4)}
        for p, t in zip(prob_pred, prob_true)
    ]

    return {
        "pr_curve": pr_points,
        "roc_curve": roc_points,
        "calibration_curve": calib_points,
    }
