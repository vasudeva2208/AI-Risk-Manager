from typing import Tuple
from backend.app.models.entities import RiskLevel, BoundedRecommendation
from backend.app.core.config import settings


POLICY_VERSION = "v1.0_deterministic_bounded"


class BoundedPolicyEngine:
    """
    Deterministic bounded risk policy engine.
    Decouples raw statistical risk probability from operational recommendations.
    Ensures safe, defense-only bounding with zero automated financial denial of customers.
    """

    def __init__(
        self,
        threshold_low: float = settings.POLICY_THRESHOLD_LOW,
        threshold_high: float = settings.POLICY_THRESHOLD_HIGH,
        policy_version: str = POLICY_VERSION,
    ):
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.policy_version = policy_version

    def evaluate_risk_level(self, risk_score: float) -> RiskLevel:
        """Determines the discrete risk tier from the continuous calibrated probability."""
        if risk_score < self.threshold_low:
            return RiskLevel.LOW
        elif risk_score < self.threshold_high:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    def compute_expected_loss(
        self,
        risk_score: float,
        order_amount: float,
        handling_cost: float = settings.COST_RETURN_SHIPPING,
    ) -> float:
        """
        Calculates mathematical expected financial loss to the merchant:
        Expected Loss = P(Abuse) * (Order Amount + Return Handling Cost)
        """
        exposure = order_amount + handling_cost
        expected_loss = risk_score * exposure
        return round(expected_loss, 2)

    def determine_recommendation(
        self,
        risk_score: float,
        expected_loss: float,
        has_open_dispute: bool = False,
    ) -> Tuple[BoundedRecommendation, str]:
        """
        Determines the bounded operational recommendation.
        Consequential actions require human review or additional verification;
        never automated arbitrary customer fund denial.
        """
        risk_level = self.evaluate_risk_level(risk_score)

        # High risk or existing open dispute overrides to manual human review
        if risk_level == RiskLevel.HIGH or has_open_dispute:
            reason = (
                f"High risk score ({risk_score:.2f}) with expected loss of ${expected_loss:.2f}. "
                f"Routed to manual analyst triage queue for verification."
            )
            return BoundedRecommendation.MANUAL_REVIEW, reason

        elif risk_level == RiskLevel.MEDIUM:
            reason = (
                f"Moderate risk score ({risk_score:.2f}). "
                f"Requires additional verification (item condition photo or in-store drop-off)."
            )
            return BoundedRecommendation.REQUIRE_ADDITIONAL_VERIFICATION, reason

        else:
            reason = (
                f"Low risk score ({risk_score:.2f}). "
                f"Standard automated return authorization approved."
            )
            return BoundedRecommendation.APPROVE, reason
