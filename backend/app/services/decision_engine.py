"""
Deterministic Decision & Policy Engine.

Translates continuous calibrated probability and expected monetary loss into
bounded operational policy recommendations with versioned policy rules.

Consequential actions are strictly bounded:
- Low risk: Policy recommendation: APPROVE (Standard processing recommended under policy)
- Medium risk: Policy recommendation: REQUIRE_ADDITIONAL_VERIFICATION (Soft friction: photo / in-store verification)
- High risk: Policy recommendation: MANUAL_REVIEW (Human analyst review queue)

The engine produces operational recommendations only; it does NOT autonomously execute financial refunds or fund seizures.
"""

from typing import Tuple
from backend.app.models.entities import RiskLevel, BoundedRecommendation
from backend.app.core.config import settings


POLICY_VERSION = "return-policy-v1"


class DecisionEngineService:
    def __init__(
        self,
        threshold_low: float = 0.30,
        threshold_high: float = 0.70,
        policy_version: str = POLICY_VERSION,
    ):
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.policy_version = policy_version

    def classify_risk_level(self, risk_probability: float) -> RiskLevel:
        """Categorizes continuous probability into auditable risk tiers."""
        if risk_probability < self.threshold_low:
            return RiskLevel.LOW
        elif risk_probability < self.threshold_high:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    def evaluate_policy(
        self,
        risk_probability: float,
        expected_loss: float,
        has_active_dispute: bool = False,
        currency: str = "INR",
    ) -> Tuple[BoundedRecommendation, RiskLevel, str]:
        """
        Determines the bounded policy recommendation.
        Consequential actions require human review or verification;
        never automated arbitrary fund denial.
        """
        risk_level = self.classify_risk_level(risk_probability)

        # High risk tier or active payment dispute forces manual human review
        if risk_level == RiskLevel.HIGH or has_active_dispute:
            curr_symbol = "₹" if currency == "INR" else "$"
            reason = (
                f"High risk score ({risk_probability:.2f}) with expected exposure of {curr_symbol}{expected_loss:.2f}. "
                f"Policy recommendation: MANUAL_REVIEW (Route case to authorized merchant risk review queue)."
            )
            return BoundedRecommendation.MANUAL_REVIEW, risk_level, reason

        elif risk_level == RiskLevel.MEDIUM:
            reason = (
                f"Moderate risk score ({risk_probability:.2f}). "
                f"Policy recommendation: REQUIRE_ADDITIONAL_VERIFICATION (Enforce soft friction: photo submission or physical drop-off)."
            )
            return BoundedRecommendation.REQUIRE_ADDITIONAL_VERIFICATION, risk_level, reason

        else:
            reason = (
                f"Low risk score ({risk_probability:.2f}). "
                f"Policy recommendation: APPROVE (Standard return processing recommended based on low risk score)."
            )
            return BoundedRecommendation.APPROVE, risk_level, reason


decision_engine_service = DecisionEngineService()
