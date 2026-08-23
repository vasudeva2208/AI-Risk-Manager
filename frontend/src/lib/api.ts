import {
  RiskAssessmentResponse,
  ReviewCaseResponse,
  HumanDecisionSubmission,
  AuditEventResponse,
  AuditChainVerificationResponse,
  ModelRegistryEntry,
  ModelComparisonData,
} from '../types/api';

const RAW_BASE = (import.meta.env?.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000';
const API_HOST = RAW_BASE.replace(/\/+$/, '');
const API_BASE = `${API_HOST}/api/v1`;

export const apiClient = {
  // Risk Assessments
  async listAssessments(riskLevel?: string): Promise<RiskAssessmentResponse[]> {
    const url = riskLevel ? `${API_BASE}/risk/assessments?risk_level=${riskLevel}` : `${API_BASE}/risk/assessments`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch assessments: ${res.statusText}`);
    return res.json();
  },

  async getAssessment(id: string): Promise<RiskAssessmentResponse> {
    const res = await fetch(`${API_BASE}/risk/${id}`);
    if (!res.ok) throw new Error(`Assessment ${id} not found.`);
    return res.json();
  },

  // Review Queue
  async listReviews(status?: string): Promise<ReviewCaseResponse[]> {
    const url = status ? `${API_BASE}/reviews?status=${status}` : `${API_BASE}/reviews`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch review cases: ${res.statusText}`);
    return res.json();
  },

  async getReviewCase(caseId: string): Promise<ReviewCaseResponse> {
    const res = await fetch(`${API_BASE}/reviews/${caseId}`);
    if (!res.ok) throw new Error(`Review case ${caseId} not found.`);
    return res.json();
  },

  async submitReviewDecision(caseId: string, submission: HumanDecisionSubmission): Promise<ReviewCaseResponse> {
    const res = await fetch(`${API_BASE}/reviews/${caseId}/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(submission),
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || `Failed to submit decision`);
    }
    return res.json();
  },

  // Audit Trail
  async listAuditEvents(limit = 100): Promise<AuditEventResponse[]> {
    const res = await fetch(`${API_BASE}/audit/events?limit=${limit}`);
    if (!res.ok) throw new Error(`Failed to fetch audit events.`);
    return res.json();
  },

  async getAssessmentAudit(assessmentId: string): Promise<AuditEventResponse[]> {
    const res = await fetch(`${API_BASE}/audit/${assessmentId}`);
    if (!res.ok) throw new Error(`Audit events for ${assessmentId} not found.`);
    return res.json();
  },

  async verifyAuditChain(assessmentId?: string): Promise<AuditChainVerificationResponse> {
    const url = assessmentId ? `${API_BASE}/audit/verify?assessment_id=${assessmentId}` : `${API_BASE}/audit/verify`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to verify audit chain.`);
    return res.json();
  },

  // Model Registry
  async listModels(): Promise<ModelRegistryEntry[]> {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error(`Failed to fetch models from registry.`);
    return res.json();
  },

  // Evaluation Artifacts (Static assets served by frontend)
  async getModelComparison(): Promise<ModelComparisonData> {
    const res = await fetch('/evaluation_artifacts/model_comparison.json');
    if (!res.ok) throw new Error(`Failed to load model comparison artifact.`);
    return res.json();
  },

  async getThresholdAnalysis(): Promise<{ logreg_thresholds: any[]; hgb_thresholds: any[] }> {
    const res = await fetch('/evaluation_artifacts/threshold_analysis.json');
    if (!res.ok) throw new Error(`Failed to load threshold analysis artifact.`);
    return res.json();
  },

  async getPrCurve(): Promise<{ recall: number; precision: number }[]> {
    const res = await fetch('/evaluation_artifacts/pr_curve.json');
    if (!res.ok) return [];
    return res.json();
  },

  async getCalibrationCurve(): Promise<{ predicted_prob: number; empirical_fraction: number }[]> {
    const res = await fetch('/evaluation_artifacts/calibration.json');
    if (!res.ok) return [];
    return res.json();
  },

  async getConfidenceIntervals(): Promise<Record<string, { estimate: number; lower_95: number; upper_95: number; std_error: number }>> {
    const res = await fetch('/evaluation_artifacts/confidence_intervals.json');
    if (!res.ok) return {};
    return res.json();
  },

  async getCostSensitivity(): Promise<{ scenarios: any[] }> {
    const res = await fetch('/evaluation_artifacts/cost_sensitivity.json');
    if (!res.ok) return { scenarios: [] };
    return res.json();
  },
};
