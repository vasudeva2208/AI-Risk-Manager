import React, { useState } from 'react';
import { UserCheck, ShieldCheck, Clock, CheckCircle2 } from 'lucide-react';
import { ReviewCaseResponse } from '../types/api';
import { Badge } from '../components/data-display/Badge';
import { formatCurrency, formatPercent } from '../lib/formatters';

interface ReviewsProps {
  reviews: ReviewCaseResponse[];
  onOpenReviewModal: (caseItem: ReviewCaseResponse) => void;
  currency: 'INR' | 'USD';
  isLoading: boolean;
}

export const Reviews: React.FC<ReviewsProps> = ({
  reviews,
  onOpenReviewModal,
  currency,
  isLoading,
}) => {
  const [activeTab, setActiveTab] = useState<'PENDING_REVIEW' | 'RESOLVED' | 'ALL'>('PENDING_REVIEW');

  const filteredReviews = reviews.filter((r) => {
    if (activeTab === 'ALL') return true;
    return r.status === activeTab;
  });

  const pendingCount = reviews.filter((r) => r.status === 'PENDING_REVIEW').length;
  const resolvedCount = reviews.filter((r) => r.status === 'RESOLVED').length;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-surface-900 flex items-center">
            <UserCheck className="w-5 h-5 mr-2 text-accent" />
            Human Review Queue &amp; Governance
          </h2>
          <p className="text-xs text-surface-500 mt-0.5">
            Authorize, verify, or escalate flagged return requests with mandatory evidence rationale.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="px-2.5 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded font-semibold flex items-center">
            <Clock className="w-3.5 h-3.5 mr-1 text-amber-600" />
            {pendingCount} Pending Triage
          </span>
          <span className="px-2.5 py-1 bg-green-50 text-green-800 border border-green-200 rounded font-semibold flex items-center">
            <ShieldCheck className="w-3.5 h-3.5 mr-1 text-green-600" />
            {resolvedCount} Audited Decisions
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-surface-200 flex space-x-4 text-xs font-mono">
        <button
          onClick={() => setActiveTab('PENDING_REVIEW')}
          className={`pb-2.5 font-semibold transition-colors border-b-2 ${
            activeTab === 'PENDING_REVIEW'
              ? 'border-accent text-accent'
              : 'border-transparent text-surface-500 hover:text-surface-800'
          }`}
        >
          Pending Review ({pendingCount})
        </button>
        <button
          onClick={() => setActiveTab('RESOLVED')}
          className={`pb-2.5 font-semibold transition-colors border-b-2 ${
            activeTab === 'RESOLVED'
              ? 'border-accent text-accent'
              : 'border-transparent text-surface-500 hover:text-surface-800'
          }`}
        >
          Resolved Cases ({resolvedCount})
        </button>
        <button
          onClick={() => setActiveTab('ALL')}
          className={`pb-2.5 font-semibold transition-colors border-b-2 ${
            activeTab === 'ALL'
              ? 'border-accent text-accent'
              : 'border-transparent text-surface-500 hover:text-surface-800'
          }`}
        >
          All Cases ({reviews.length})
        </button>
      </div>

      {/* Table */}
      <div className="bg-white border border-surface-200 rounded shadow-sm overflow-hidden">
        {isLoading && reviews.length === 0 ? (
          <div className="p-8 text-center text-surface-500 font-mono text-xs">Loading review queue...</div>
        ) : filteredReviews.length === 0 ? (
          <div className="p-12 text-center text-surface-400 font-mono text-xs">
            No review cases in this view.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-surface-50 border-b border-surface-200 text-surface-600 text-[10px] uppercase">
                <tr>
                  <th className="py-3 px-4 font-semibold">Case ID</th>
                  <th className="py-3 px-4 font-semibold">Return ID</th>
                  <th className="py-3 px-4 font-semibold">Risk Propensity</th>
                  <th className="py-3 px-4 font-semibold">Expected Exposure</th>
                  <th className="py-3 px-4 font-semibold">Model Recommendation</th>
                  <th className="py-3 px-4 font-semibold">Status</th>
                  <th className="py-3 px-4 font-semibold">Human Decision &amp; Reason</th>
                  <th className="py-3 px-4 text-right font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100">
                {filteredReviews.map((caseItem) => (
                  <tr key={caseItem.case_id} className="hover:bg-surface-50">
                    <td className="py-3 px-4 font-bold text-surface-900">{caseItem.case_id}</td>
                    <td className="py-3 px-4 text-accent font-semibold">{caseItem.return_id}</td>
                    <td className="py-3 px-4 font-bold">
                      {formatPercent(caseItem.risk_probability)}
                    </td>
                    <td className="py-3 px-4 font-bold text-surface-800">
                      {formatCurrency(caseItem.expected_loss, currency)}
                    </td>
                    <td className="py-3 px-4">
                      <Badge type="recommendation" value={caseItem.model_recommendation} />
                    </td>
                    <td className="py-3 px-4">
                      <Badge type="status" value={caseItem.status} />
                    </td>
                    <td className="py-3 px-4 max-w-xs">
                      {caseItem.status === 'RESOLVED' ? (
                        <div className="space-y-0.5">
                          <div className="flex items-center space-x-1.5">
                            <Badge type="decision" value={caseItem.human_decision || ''} />
                            <span className="text-[10px] text-surface-400">by {caseItem.reviewer_id}</span>
                          </div>
                          <p className="text-[11px] text-surface-600 font-sans truncate" title={caseItem.decision_reason || ''}>
                            {caseItem.decision_reason}
                          </p>
                        </div>
                      ) : (
                        <span className="text-surface-400 italic">Awaiting Analyst Triage</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {caseItem.status === 'PENDING_REVIEW' ? (
                        <button
                          onClick={() => onOpenReviewModal(caseItem)}
                          className="px-3 py-1.5 text-xs font-semibold text-white bg-accent hover:bg-accent-hover rounded shadow-sm transition-colors"
                        >
                          Review
                        </button>
                      ) : (
                        <span className="inline-flex items-center text-[11px] text-surface-400 font-semibold">
                          <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-green-500" />
                          Resolved
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
