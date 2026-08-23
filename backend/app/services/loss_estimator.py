"""
Expected Loss Estimation Service.

Calculates mathematically grounded financial loss exposure to the merchant:
Expected Loss = P(Abuse) * (Refund Requested Amount + Return Processing/Shipping Cost)

Supports transparent auditable calculation versions and currency handling (Default: INR ₹).
"""

import math
from typing import Dict, Any
from backend.app.schemas.domain import ExpectedLossDetail


DEFAULT_HANDLING_COST_USD = 8.50
DEFAULT_USD_TO_INR_RATE = 83.0
LOSS_CALCULATION_VERSION = "v1_asymmetric_linear"


class LossEstimatorService:
    def __init__(
        self,
        default_handling_cost_usd: float = DEFAULT_HANDLING_COST_USD,
        usd_to_inr_rate: float = DEFAULT_USD_TO_INR_RATE,
        version: str = LOSS_CALCULATION_VERSION,
    ):
        self.default_handling_cost_usd = default_handling_cost_usd
        self.usd_to_inr_rate = usd_to_inr_rate
        self.version = version

    def compute_expected_loss(
        self,
        risk_probability: float,
        refund_amount: float,
        currency: str = "INR",
        handling_cost_override: float = None,
    ) -> ExpectedLossDetail:
        """
        Calculates expected loss in the requested currency.
        Validates probability boundaries [0, 1] and non-negative currency amounts.
        """
        if not math.isfinite(risk_probability) or risk_probability < 0.0 or risk_probability > 1.0:
            raise ValueError(f"Invalid risk_probability: {risk_probability}. Must be finite number in [0.0, 1.0].")

        if not math.isfinite(refund_amount) or refund_amount < 0.0:
            raise ValueError(f"Invalid refund_amount: {refund_amount}. Must be a non-negative finite number.")

        if currency not in ["INR", "USD"]:
            raise ValueError(f"Unsupported currency: {currency}. Supported currencies are 'INR' and 'USD'.")

        # Determine handling cost in specified currency
        if handling_cost_override is not None:
            if not math.isfinite(handling_cost_override) or handling_cost_override < 0.0:
                raise ValueError("handling_cost_override must be non-negative finite number.")
            handling_cost = handling_cost_override
        elif currency == "INR":
            handling_cost = round(self.default_handling_cost_usd * self.usd_to_inr_rate, 2)
        else:
            handling_cost = self.default_handling_cost_usd

        # Total exposure if abuse is true
        estimated_loss_if_abuse = round(refund_amount + handling_cost, 2)

        # Expected value
        expected_loss = round(risk_probability * estimated_loss_if_abuse, 2)

        return ExpectedLossDetail(
            risk_probability=risk_probability,
            estimated_loss_if_abuse=estimated_loss_if_abuse,
            expected_loss=expected_loss,
            currency=currency,
            calculation_version=self.version,
            cost_breakdown={
                "refund_amount_exposure": round(refund_amount, 2),
                "return_handling_and_shipping": handling_cost,
                "total_loss_if_abusive": estimated_loss_if_abuse,
                "expected_financial_loss": expected_loss,
            }
        )


loss_estimator_service = LossEstimatorService()
