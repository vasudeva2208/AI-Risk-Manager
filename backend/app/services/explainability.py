"""
Explainability Service.

Generates merchant-facing risk factor attributions and plain-language rationale
strictly derived from observed point-in-time feature values.
Adheres strictly to Defense-Only boundaries: never outputs evasion guidance or scoring bypass rules.
"""

import pandas as pd
from typing import List, Dict, Any
from backend.app.schemas.domain import RiskFactorContribution


class ExplainabilityService:
    def explain_prediction(
        self,
        model_instance: Any,
        df_row: pd.DataFrame,
        top_k: int = 4,
    ) -> List[RiskFactorContribution]:
        """
        Extracts top contributing risk factors and maps them to clear, merchant-facing explanations.
        """
        raw_explanations = model_instance.explain_instance(df_row, top_k=top_k)
        formatted_contributions: List[RiskFactorContribution] = []

        row_dict = df_row.iloc[0].to_dict()

        for item in raw_explanations:
            feat_name = item["feature_name"]
            val = float(item["feature_value"])
            contrib = float(item["contribution"])

            human_reason = self._generate_safe_merchant_reason(feat_name, val, row_dict)

            formatted_contributions.append(RiskFactorContribution(
                feature_name=feat_name,
                feature_value=round(val, 3),
                contribution=round(contrib, 4),
                direction="INCREASES_RISK" if contrib >= 0 else "DECREASES_RISK",
                human_readable_reason=human_reason,
            ))

        return formatted_contributions

    def _generate_safe_merchant_reason(
        self,
        feature_name: str,
        feature_value: float,
        context: Dict[str, Any]
    ) -> str:
        """Translates technical feature values into merchant risk team explanations."""
        if "dispute_count" in feature_name:
            count = int(context.get("customer_dispute_count", feature_value))
            return f"Customer profile has {count} prior formal payment dispute(s) or chargeback(s) on record."

        elif "returns_last_7d" in feature_name or "returns_last_30d" in feature_name:
            r30 = int(context.get("returns_last_30d", feature_value))
            return f"Abnormal return velocity: customer initiated {r30} return request(s) within the last 30 days."

        elif "days_since_delivery" in feature_name:
            days = int(context.get("days_since_delivery", feature_value))
            return f"Late return request submitted {days} days post-delivery (adjacent to 30-day policy limit)."

        elif "order_vs_avg_spend_ratio" in feature_name:
            ratio = float(context.get("order_vs_avg_spend_ratio", feature_value))
            return f"High basket deviation: order amount is {ratio:.1f}x higher than the customer's historical average order value."

        elif "refund_to_spend_ratio" in feature_name:
            ratio = float(context.get("refund_to_spend_ratio", feature_value))
            return f"Negative customer equity: historical refunds account for {(ratio * 100):.1f}% of total lifetime spend."

        elif "payment_method" in feature_name and "BUY_NOW_PAY_LATER" in str(context.get("payment_method", "")):
            return "High-risk payment method: transaction tendered via Buy-Now-Pay-Later (BNPL) credit."

        elif "customer_account_age_days" in feature_name:
            age = int(context.get("customer_account_age_days", feature_value))
            return f"Low account seasoning: account was created only {age} day(s) prior to high-value transaction."

        elif "order_discount_ratio" in feature_name:
            return "Promotional code stacking: heavy discount applied relative to gross order value."

        else:
            return f"Elevated behavioral signal detected on feature '{feature_name}' (value: {feature_value:.2f})."


explainability_service = ExplainabilityService()
