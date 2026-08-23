import React from 'react';
import { PieChart, AlertCircle, CheckCircle } from 'lucide-react';
import { RiskAssessmentResponse } from '../types/api';
import { formatCurrency } from '../lib/formatters';

interface RiskAnalysisProps {
  assessments: RiskAssessmentResponse[];
  currency: 'INR' | 'USD';
}

export const RiskAnalysis: React.FC<RiskAnalysisProps> = ({ assessments, currency }) => {
  const highRisk = assessments.filter((a) => a.risk_level === 'HIGH');
  const medRisk = assessments.filter((a) => a.risk_level === 'MEDIUM');
  const lowRisk = assessments.filter((a) => a.risk_level === 'LOW');

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div>
        <h2 className="text-base font-bold text-surface-900 flex items-center">
          <PieChart className="w-5 h-5 mr-2 text-accent" />
          Risk Factor &amp; Exposure Analysis
        </h2>
        <p className="text-xs text-surface-500 mt-0.5">
          Detailed analysis of behavioral risk patterns, tender method exposure, and velocity signals.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* High Risk Profile */}
        <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-3">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="font-bold text-status-high">HIGH RISK POOL</span>
            <span className="px-2 py-0.5 rounded bg-red-50 text-red-700 font-bold">
              {highRisk.length} cases
            </span>
          </div>
          <p className="text-xs text-surface-600">
            Primary driver: High recent return velocity (&gt;2 returns in 30d) coupled with BNPL tender and dispute histories.
          </p>
          <div className="p-3 bg-surface-50 border border-surface-200 rounded text-xs font-mono">
            <span className="text-surface-500 block text-[10px]">AVG EXPECTED EXPOSURE</span>
            <span className="text-lg font-bold text-surface-900">
              {formatCurrency(
                highRisk.length > 0
                  ? highRisk.reduce((acc, a) => acc + a.expected_loss, 0) / highRisk.length
                  : 0,
                currency
              )}
            </span>
          </div>
        </div>

        {/* Medium Risk Profile */}
        <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-3">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="font-bold text-status-medium">MEDIUM RISK POOL</span>
            <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 font-bold">
              {medRisk.length} cases
            </span>
          </div>
          <p className="text-xs text-surface-600">
            Primary driver: Elevated order-to-average spend ratios and late return requests submitted near policy boundaries.
          </p>
          <div className="p-3 bg-surface-50 border border-surface-200 rounded text-xs font-mono">
            <span className="text-surface-500 block text-[10px]">AVG EXPECTED EXPOSURE</span>
            <span className="text-lg font-bold text-surface-900">
              {formatCurrency(
                medRisk.length > 0
                  ? medRisk.reduce((acc, a) => acc + a.expected_loss, 0) / medRisk.length
                  : 0,
                currency
              )}
            </span>
          </div>
        </div>

        {/* Low Risk Profile */}
        <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-3">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="font-bold text-status-low">LOW RISK POOL</span>
            <span className="px-2 py-0.5 rounded bg-green-50 text-green-700 font-bold">
              {lowRisk.length} cases
            </span>
          </div>
          <p className="text-xs text-surface-600">
            Primary driver: Established customer accounts (&gt;180 days), low historical refund ratios, and standard credit card tenders.
          </p>
          <div className="p-3 bg-surface-50 border border-surface-200 rounded text-xs font-mono">
            <span className="text-surface-500 block text-[10px]">AVG EXPECTED EXPOSURE</span>
            <span className="text-lg font-bold text-surface-900">
              {formatCurrency(
                lowRisk.length > 0
                  ? lowRisk.reduce((acc, a) => acc + a.expected_loss, 0) / lowRisk.length
                  : 0,
                currency
              )}
            </span>
          </div>
        </div>
      </div>

      {/* Governance & Policy Matrix */}
      <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700">
          Point-in-Time Behavioral Signal Contributions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-3 bg-surface-50 border border-surface-200 rounded space-y-2">
            <span className="font-bold text-surface-900 flex items-center">
              <AlertCircle className="w-3.5 h-3.5 mr-1 text-red-500" />
              Top Risk Accelerators
            </span>
            <ul className="list-disc list-inside text-surface-600 space-y-1 text-[11px]">
              <li>Short-term return velocity spikes (<code className="text-surface-800">returns_last_7d</code> &amp; <code className="text-surface-800">returns_last_30d</code>)</li>
              <li>Lifetime dispute and chargeback frequency (<code className="text-surface-800">customer_dispute_count</code>)</li>
              <li>High refund-to-spend ratio (<code className="text-surface-800">refund_to_spend_ratio &gt; 0.50</code>)</li>
              <li>BNPL tender with fast delivery-to-return claim (&lt; 2 days)</li>
            </ul>
          </div>

          <div className="p-3 bg-surface-50 border border-surface-200 rounded space-y-2">
            <span className="font-bold text-surface-900 flex items-center">
              <CheckCircle className="w-3.5 h-3.5 mr-1 text-green-500" />
              Top Risk Dampeners
            </span>
            <ul className="list-disc list-inside text-surface-600 space-y-1 text-[11px]">
              <li>Seasoned customer account age (<code className="text-surface-800">customer_account_age_days &gt; 180</code>)</li>
              <li>High lifetime retained spend with low return rate (&lt; 5%)</li>
              <li>Zero prior chargeback disputes across customer tenure</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
