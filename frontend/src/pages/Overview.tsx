import React from 'react';
import {
  ShieldAlert,
  UserCheck,
  IndianRupee,
  Activity,
  ArrowRight,
  AlertTriangle,
} from 'lucide-react';
import { RiskAssessmentResponse, ReviewCaseResponse } from '../types/api';
import { StatCard } from '../components/data-display/StatCard';
import { Badge } from '../components/data-display/Badge';
import { formatCurrency, formatPercent, formatDate } from '../lib/formatters';

interface OverviewProps {
  assessments: RiskAssessmentResponse[];
  reviews: ReviewCaseResponse[];
  onSelectAssessment: (assmt: RiskAssessmentResponse) => void;
  onNavigateTo: (route: any) => void;
  currency: 'INR' | 'USD';
  isLoading: boolean;
}

export const Overview: React.FC<OverviewProps> = ({
  assessments,
  reviews,
  onSelectAssessment,
  onNavigateTo,
  currency,
  isLoading,
}) => {
  // Aggregate real statistics
  const totalCases = assessments.length;
  const highRiskCases = assessments.filter((a) => a.risk_level === 'HIGH');
  const pendingReviews = reviews.filter((r) => r.status === 'PENDING_REVIEW');
  const totalExpectedLoss = assessments.reduce((acc, a) => acc + a.expected_loss, 0);

  const lowCount = assessments.filter((a) => a.risk_level === 'LOW').length;
  const medCount = assessments.filter((a) => a.risk_level === 'MEDIUM').length;
  const highCount = highRiskCases.length;

  if (isLoading && assessments.length === 0) {
    return (
      <div className="p-8 text-center text-surface-500 font-mono text-xs">
        Loading real-time risk exposure data...
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Disclaimer Banner */}
      <div className="p-3 bg-surface-50 border border-surface-200 rounded flex items-center justify-between text-xs font-mono text-surface-600">
        <span className="flex items-center">
          <AlertTriangle className="w-4 h-4 mr-2 text-amber-600" />
          SYNTHETIC SIMULATION ENVIRONMENT — ACTIVE MODEL: return-risk-hgb-v1
        </span>
        <span className="text-[11px] text-surface-400">Point-in-Time Features: 23</span>
      </div>

      {/* Primary KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Current Exposure"
          value={formatCurrency(totalExpectedLoss, currency)}
          subtitle="Aggregate expected loss across active return pool"
          icon={IndianRupee}
          accentValue
        />
        <StatCard
          title="Pending Review Queue"
          value={pendingReviews.length}
          subtitle="Flagged cases awaiting human risk analyst action"
          icon={UserCheck}
          badge={pendingReviews.length > 0 ? 'Action Required' : 'All Clear'}
        />
        <StatCard
          title="High Risk Propensity"
          value={highCount}
          subtitle={`${totalCases > 0 ? ((highCount / totalCases) * 100).toFixed(1) : 0}% of evaluated volume`}
          icon={ShieldAlert}
        />
        <StatCard
          title="Evaluated Pool"
          value={totalCases}
          subtitle="Point-in-time transactions scored"
          icon={Activity}
        />
      </div>

      {/* Two-Column Middle Section: Risk Distribution & Review Backlog */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution Card */}
        <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700">
              Risk Tier Breakdown
            </h3>
            <span className="text-xs font-mono text-surface-400">{totalCases} Total</span>
          </div>

          <div className="space-y-3">
            {/* High */}
            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="font-semibold text-status-high">High Risk (Score &ge; 0.70)</span>
                <span className="font-bold">{highCount} ({totalCases > 0 ? Math.round((highCount / totalCases) * 100) : 0}%)</span>
              </div>
              <div className="w-full h-2 bg-surface-100 rounded overflow-hidden">
                <div
                  className="h-full bg-status-high"
                  style={{ width: `${totalCases > 0 ? (highCount / totalCases) * 100 : 0}%` }}
                />
              </div>
            </div>

            {/* Medium */}
            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="font-semibold text-status-medium">Medium Risk (0.30 - 0.70)</span>
                <span className="font-bold">{medCount} ({totalCases > 0 ? Math.round((medCount / totalCases) * 100) : 0}%)</span>
              </div>
              <div className="w-full h-2 bg-surface-100 rounded overflow-hidden">
                <div
                  className="h-full bg-status-medium"
                  style={{ width: `${totalCases > 0 ? (medCount / totalCases) * 100 : 0}%` }}
                />
              </div>
            </div>

            {/* Low */}
            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="font-semibold text-status-low">Low Risk (&lt; 0.30)</span>
                <span className="font-bold">{lowCount} ({totalCases > 0 ? Math.round((lowCount / totalCases) * 100) : 0}%)</span>
              </div>
              <div className="w-full h-2 bg-surface-100 rounded overflow-hidden">
                <div
                  className="h-full bg-status-low"
                  style={{ width: `${totalCases > 0 ? (lowCount / totalCases) * 100 : 0}%` }}
                />
              </div>
            </div>
          </div>

          <div className="p-3 bg-surface-50 border border-surface-200 rounded text-[11px] text-surface-600 space-y-1">
            <p className="font-bold text-surface-900">Deterministic Policy Rule:</p>
            <p>High risk routes to manual human review; medium risk requires verification photos; low risk receives standard policy recommendation.</p>
          </div>
        </div>

        {/* Priority Pending Reviews */}
        <div className="lg:col-span-2 bg-white border border-surface-200 rounded p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700">
                  Priority Review Queue
                </h3>
                <p className="text-xs text-surface-500">Unresolved cases requiring risk analyst review</p>
              </div>
              <button
                onClick={() => onNavigateTo('reviews')}
                className="text-xs text-accent font-semibold flex items-center hover:underline focus:outline-none focus:ring-1 focus:ring-accent"
              >
                View all queue ({pendingReviews.length})
                <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </button>
            </div>

            {pendingReviews.length === 0 ? (
              <div className="p-8 text-center text-surface-400 font-mono text-xs bg-surface-50 border border-surface-200 rounded">
                No pending return cases require review at this time.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-surface-200 text-surface-500 text-[10px] uppercase">
                      <th className="pb-2 font-medium">Return ID</th>
                      <th className="pb-2 font-medium">Risk Score</th>
                      <th className="pb-2 font-medium">Exposure</th>
                      <th className="pb-2 font-medium">Recommendation</th>
                      <th className="pb-2 font-medium text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-surface-100">
                    {pendingReviews.slice(0, 4).map((r) => (
                      <tr key={r.case_id} className="hover:bg-surface-50">
                        <td className="py-2.5 font-bold text-surface-900">{r.return_id}</td>
                        <td className="py-2.5 font-bold">{formatPercent(r.risk_probability)}</td>
                        <td className="py-2.5">{formatCurrency(r.expected_loss, currency)}</td>
                        <td className="py-2.5">
                          <Badge type="recommendation" value={r.model_recommendation} />
                        </td>
                        <td className="py-2.5 text-right">
                          <button
                            onClick={() => onNavigateTo('reviews')}
                            className="px-2 py-1 text-[11px] font-semibold text-accent border border-accent rounded hover:bg-accent hover:text-white transition-colors focus:outline-none focus:ring-1 focus:ring-accent"
                          >
                            Review
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-surface-100 flex items-center justify-between text-[11px] font-mono text-surface-500">
            <span>Role Requirement: RISK_ANALYST or RISK_ADMIN</span>
            <span>Mandatory Rationale Enforced</span>
          </div>
        </div>
      </div>

      {/* Recent Flagged Transactions Table */}
      <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700">
              Recent Flagged Return Requests
            </h3>
            <p className="text-xs text-surface-500">Click any row to inspect explainability factors and audit history</p>
          </div>
          <button
            onClick={() => onNavigateTo('risk-monitor')}
            className="text-xs text-accent font-semibold flex items-center hover:underline focus:outline-none focus:ring-1 focus:ring-accent"
          >
            Open Full Risk Monitor
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-surface-200 text-surface-500 text-[10px] uppercase">
                <th className="pb-2 font-medium">Return ID</th>
                <th className="pb-2 font-medium">Order ID</th>
                <th className="pb-2 font-medium">Customer Ref</th>
                <th className="pb-2 font-medium">Risk Score</th>
                <th className="pb-2 font-medium">Risk Tier</th>
                <th className="pb-2 font-medium">Expected Loss</th>
                <th className="pb-2 font-medium">Policy Recommendation</th>
                <th className="pb-2 font-medium">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-100">
              {assessments.slice(0, 6).map((assmt) => (
                <tr
                  key={assmt.assessment_id}
                  onClick={() => onSelectAssessment(assmt)}
                  className="hover:bg-surface-50 cursor-pointer transition-colors"
                >
                  <td className="py-2.5 font-bold text-accent">{assmt.return_id}</td>
                  <td className="py-2.5 text-surface-700">{assmt.order_id}</td>
                  <td className="py-2.5 text-surface-500">{assmt.customer_id.substring(0, 10)}...</td>
                  <td className="py-2.5 font-bold text-surface-900">{formatPercent(assmt.risk_probability)}</td>
                  <td className="py-2.5">
                    <Badge type="risk" value={assmt.risk_level} />
                  </td>
                  <td className="py-2.5 font-semibold text-surface-800">
                    {formatCurrency(assmt.expected_loss, currency)}
                  </td>
                  <td className="py-2.5">
                    <Badge type="recommendation" value={assmt.recommendation} />
                  </td>
                  <td className="py-2.5 text-surface-400 text-[11px]">{formatDate(assmt.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
