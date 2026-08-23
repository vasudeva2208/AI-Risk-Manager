export type ProductCategory = "APPAREL" | "ELECTRONICS" | "LUXURY_GOODS" | "BEAUTY" | "HOME_GARDEN";
export type PaymentMethod = "CREDIT_CARD" | "DEBIT_CARD" | "BUY_NOW_PAY_LATER" | "STORE_CREDIT";
export type ReturnReason = "DEFECTIVE" | "WRONG_SIZE" | "NOT_AS_DESCRIBED" | "CHANGED_MIND" | "ARRIVED_LATE";
export type ItemCondition = "UNOPENED" | "OPENED_UNUSED" | "WORN_OR_USED" | "DAMAGED";
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";
export type BoundedRecommendation = "APPROVE" | "REQUIRE_ADDITIONAL_VERIFICATION" | "MANUAL_REVIEW";
export type ReviewStatus = "PENDING_REVIEW" | "UNDER_REVIEW" | "RESOLVED";
export type HumanDecisionType = "APPROVE_RETURN" | "REQUEST_ADDITIONAL_VERIFICATION" | "ESCALATE";
export type UserRole = "RISK_ANALYST" | "RISK_ADMIN" | "SYSTEM";
export type EventType = "RISK_ASSESSMENT_CREATED" | "MODEL_RECOMMENDATION_CREATED" | "REVIEW_STARTED" | "REVIEW_DECISION_MADE" | "POLICY_EVALUATED" | "AUDIT_RECORD_CREATED";
export type ActorType = "SYSTEM" | "MERCHANT_ANALYST" | "COMPLIANCE_OFFICER" | "RISK_ADMIN";

export interface RiskFactorContribution {
  feature_name: string;
  feature_value: number;
  contribution: number;
  direction: "INCREASES_RISK" | "DECREASES_RISK";
  human_readable_reason: string;
}

export interface RiskAssessmentResponse {
  assessment_id: string;
  return_id: string;
  order_id: string;
  customer_id: string;
  risk_probability: number;
  risk_level: RiskLevel;
  threshold_applied: number;
  expected_loss: number;
  estimated_loss_if_abuse: number;
  currency: string;
  model_version: string;
  feature_version: string;
  policy_version: string;
  recommendation: BoundedRecommendation;
  top_risk_factors: RiskFactorContribution[];
  created_at: string;
}

export interface ReviewCaseResponse {
  case_id: string;
  assessment_id: string;
  return_id: string;
  order_id: string;
  customer_id: string;
  status: ReviewStatus;
  model_recommendation: BoundedRecommendation;
  risk_probability: number;
  risk_level: RiskLevel;
  expected_loss: number;
  currency: string;
  top_risk_factors: RiskFactorContribution[];
  human_decision: HumanDecisionType | null;
  decision_reason: string | null;
  reviewer_id: string | null;
  reviewer_role: UserRole | null;
  created_at: string;
  resolved_at: string | null;
}

export interface HumanDecisionSubmission {
  decision: HumanDecisionType;
  reason: string;
  reviewer_id: string;
  reviewer_role: UserRole;
}

export interface AuditEventResponse {
  audit_id: string;
  assessment_id: string;
  event_type: EventType;
  actor_type: ActorType;
  actor_id: string;
  model_version: string | null;
  policy_version: string | null;
  decision: string;
  reason: string;
  timestamp: string;
  payload_json: string;
  previous_event_hash: string;
  event_hash: string;
}

export interface AuditChainVerificationResponse {
  status: "VALID" | "INVALID";
  total_events_checked: number;
  assessment_id: string | null;
  corrupted_event_id: string | null;
  message: string;
}

export interface ModelRegistryEntry {
  model_version: string;
  algorithm: string;
  feature_version: string;
  calibration_method: string;
  selected_threshold: number;
  status: "ACTIVE" | "INACTIVE";
  trained_at: string | null;
  sample_count: number | null;
  description: string;
}

export interface ModelComparisonData {
  disclaimer: string;
  selected_model: string;
  selection_rationale: string;
  split_summary: {
    train: { count: number; target_count: number; prevalence: number };
    val: { count: number; target_count: number; prevalence: number };
    held_out_test: { count: number; target_count: number; prevalence: number };
  };
  models: {
    baseline_logistic_regression: {
      version: string;
      optimal_threshold: number;
      metrics_at_opt_threshold: {
        precision: number;
        recall: number;
        f1_score: number;
        roc_auc: number;
        pr_auc: number;
        brier_score: number;
        false_positive_rate: number;
        false_negative_rate: number;
        confusion_matrix: {
          true_negatives: number;
          false_positives: number;
          false_negatives: number;
          true_positives: number;
        };
      };
      costs_at_opt_threshold: {
        tp_count: number;
        fp_count: number;
        fn_count: number;
        tn_count: number;
        review_count: number;
        usd: {
          baseline_unmitigated_loss: number;
          gross_loss_prevented: number;
          false_positive_friction_cost: number;
          false_negative_realized_loss: number;
          review_labor_expenditure: number;
          total_estimated_cost: number;
          net_merchant_benefit: number;
        };
        inr: {
          baseline_unmitigated_loss: number;
          gross_loss_prevented: number;
          false_positive_friction_cost: number;
          false_negative_realized_loss: number;
          review_labor_expenditure: number;
          total_estimated_cost: number;
          net_merchant_benefit: number;
        };
      };
    };
    candidate_hist_gradient_boosting: {
      version: string;
      optimal_threshold: number;
      metrics_at_opt_threshold: {
        precision: number;
        recall: number;
        f1_score: number;
        roc_auc: number;
        pr_auc: number;
        brier_score: number;
        false_positive_rate: number;
        false_negative_rate: number;
        confusion_matrix: {
          true_negatives: number;
          false_positives: number;
          false_negatives: number;
          true_positives: number;
        };
      };
      costs_at_opt_threshold: {
        tp_count: number;
        fp_count: number;
        fn_count: number;
        tn_count: number;
        review_count: number;
        usd: {
          baseline_unmitigated_loss: number;
          gross_loss_prevented: number;
          false_positive_friction_cost: number;
          false_negative_realized_loss: number;
          review_labor_expenditure: number;
          total_estimated_cost: number;
          net_merchant_benefit: number;
        };
        inr: {
          baseline_unmitigated_loss: number;
          gross_loss_prevented: number;
          false_positive_friction_cost: number;
          false_negative_realized_loss: number;
          review_labor_expenditure: number;
          total_estimated_cost: number;
          net_merchant_benefit: number;
        };
      };
    };
  };
}
