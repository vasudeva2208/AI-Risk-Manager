"""
Risk Scoring Service.

Loads approved model artifacts from disk, constructs point-in-time feature representations,
validates inputs, and calculates calibrated risk probabilities.
"""

import os
import datetime
import pandas as pd
from typing import Dict, Any, Tuple
from backend.app.schemas.domain import CustomerBase, OrderBase, ReturnRequestBase
from backend.app.services.model_registry import model_registry, CHAMPION_MODEL_VERSION, BASELINE_MODEL_VERSION
from ml.models.tree_model import TreeRiskModel
from ml.models.baseline import BaselineRiskModel


class RiskScoringService:
    def __init__(self, base_artifacts_dir: str = "ml/models"):
        self.base_artifacts_dir = base_artifacts_dir
        self._loaded_models: Dict[str, Any] = {}

    def get_or_load_model(self, model_version: str = None) -> Tuple[Any, float]:
        """Loads and caches the requested or active model version along with its operating threshold."""
        if not model_version:
            model_version = model_registry.active_version

        if model_version in self._loaded_models:
            return self._loaded_models[model_version]

        if model_version == CHAMPION_MODEL_VERSION:
            artifact_dir = os.path.join(self.base_artifacts_dir, "candidate")
            model = TreeRiskModel.load(artifact_dir=artifact_dir, model_version=model_version)
            threshold = model.selected_threshold_
        elif model_version == BASELINE_MODEL_VERSION:
            artifact_dir = os.path.join(self.base_artifacts_dir, "baseline")
            model = BaselineRiskModel.load(artifact_dir=artifact_dir, model_version=model_version)
            threshold = model.selected_threshold_
        else:
            raise ValueError(f"Unknown or unsupported model version: {model_version}")

        self._loaded_models[model_version] = (model, threshold)
        return model, threshold

    def score_transaction(
        self,
        customer: CustomerBase,
        order: OrderBase,
        return_req: ReturnRequestBase,
        model_version: str = None,
    ) -> Dict[str, Any]:
        """
        Computes the point-in-time calibrated risk score for a single return request.
        """
        if not model_version:
            model_version = model_registry.active_version

        model, threshold = self.get_or_load_model(model_version)

        # Build single-row DataFrame matching the exact raw schema expected by extractor
        delivery_ts_str = order.delivery_timestamp.isoformat() if order.delivery_timestamp else order.order_timestamp.isoformat()
        
        row_dict = {
            "return_id": return_req.return_id,
            "order_id": order.order_id,
            "customer_id": customer.customer_id,
            "order_timestamp": order.order_timestamp.isoformat(),
            "delivery_timestamp": delivery_ts_str,
            "request_timestamp": return_req.request_timestamp.isoformat(),
            "order_amount": float(order.order_amount),
            "item_count": int(order.item_count),
            "product_category": order.product_category.value if hasattr(order.product_category, "value") else str(order.product_category),
            "discount_amount": float(order.discount_amount),
            "payment_method": order.payment_method.value if hasattr(order.payment_method, "value") else str(order.payment_method),
            "delivery_region": order.delivery_region,
            "fulfillment_method": order.fulfillment_method,
            "return_reason": return_req.return_reason.value if hasattr(return_req.return_reason, "value") else str(return_req.return_reason),
            "item_condition_declared": return_req.item_condition_declared.value if hasattr(return_req.item_condition_declared, "value") else str(return_req.item_condition_declared),
            "refund_amount_requested": float(return_req.refund_amount_requested),
            "return_method": return_req.return_method,
            # Point-in-time customer behavioral features
            "customer_account_age_days": float(customer.account_age_days),
            "customer_order_count_lifetime": float(customer.total_order_count),
            "customer_return_count_lifetime": float(customer.historical_return_count),
            "historical_return_rate": float(customer.historical_return_rate),
            "historical_refund_amount": float(customer.historical_refund_amount),
            "customer_dispute_count": float(customer.historical_dispute_count),
            "orders_last_7d": float(customer.orders_last_7d),
            "orders_last_30d": float(customer.orders_last_30d),
            "orders_last_90d": float(customer.orders_last_90d),
            "returns_last_7d": float(customer.returns_last_7d),
            "returns_last_30d": float(customer.returns_last_30d),
            "returns_last_90d": float(customer.returns_last_90d),
            "customer_avg_order_value": float(customer.customer_avg_order_value),
        }

        df_row = pd.DataFrame([row_dict])
        prob_arr = model.predict_proba(df_row)
        risk_probability = round(float(prob_arr[0]), 4)

        return {
            "model_version": model_version,
            "feature_version": "v2_point_in_time_23f",
            "risk_probability": risk_probability,
            "threshold_applied": threshold,
            "prediction_timestamp": datetime.datetime.utcnow().isoformat(),
            "df_row": df_row,
            "model_instance": model,
        }


risk_scoring_service = RiskScoringService()
