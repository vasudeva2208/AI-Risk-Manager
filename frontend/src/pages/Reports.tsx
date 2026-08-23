import React from 'react';
import { FileBarChart } from 'lucide-react';
import { RiskAssessmentResponse, ReviewCaseResponse } from '../types/api';
import { formatCurrency } from '../lib/formatters';

interface ReportsProps {
  assessments: RiskAssessmentResponse[];
  reviews: ReviewCaseResponse[];
  currency: 'INR' | 'USD';
}

export const Reports: React.FC<ReportsProps> = ({ assessments, reviews, currency }) => {
  const totalCases = assessments.length;
  const highRiskCases = assessments.filter((a) => a.risk_level === 'HIGH').length;
  const resolvedReviews = reviews.filter((r) => r.status === 'RESOLVED').length;
  const totalExposure = assessments.reduce((acc, a) => acc + a.expected_loss, 0);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-surface-900 flex items-center">
            <FileBarChart className="w-5 h-5 mr-2 text-accent" />
            Executive Risk &amp; Governance Reports
          </h2>
          <p className="text-xs text-surface-500 mt-0.5">
            Operational summary reports generated from live point-in-time assessment records.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk & Loss Summary */}
        <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700">
            Current Risk Volume &amp; Exposure Summary
          </h3>
          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between p-2.5 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Total Scored Returns:</span>
              <span className="font-bold text-surface-900">{totalCases}</span>
            </div>
            <div className="flex justify-between p-2.5 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">High Risk Propensity Cases:</span>
              <span className="font-bold text-status-high">{highRiskCases}</span>
            </div>
            <div className="flex justify-between p-2.5 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Aggregate Estimated Exposure:</span>
              <span className="font-bold text-accent">{formatCurrency(totalExposure, currency)}</span>
            </div>
          </div>
        </div>

        {/* Human Governance Summary */}
        <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700">
            Review Governance &amp; Analyst Throughput
          </h3>
          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between p-2.5 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Total Cases Flagged for Review:</span>
              <span className="font-bold text-surface-900">{reviews.length}</span>
            </div>
            <div className="flex justify-between p-2.5 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Audited Analyst Decisions Made:</span>
              <span className="font-bold text-green-700">{resolvedReviews}</span>
            </div>
            <div className="flex justify-between p-2.5 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Pending Analyst Backlog:</span>
              <span className="font-bold text-amber-700">{reviews.length - resolvedReviews}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
