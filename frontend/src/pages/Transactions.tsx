import React, { useState } from 'react';
import { CreditCard, Search } from 'lucide-react';
import { RiskAssessmentResponse } from '../types/api';
import { Badge } from '../components/data-display/Badge';
import { formatCurrency, formatPercent, formatDate } from '../lib/formatters';

interface TransactionsProps {
  assessments: RiskAssessmentResponse[];
  onSelectAssessment: (assmt: RiskAssessmentResponse) => void;
  currency: 'INR' | 'USD';
  isLoading: boolean;
}

export const Transactions: React.FC<TransactionsProps> = ({
  assessments,
  onSelectAssessment,
  currency,
  isLoading,
}) => {
  const [search, setSearch] = useState('');

  const filtered = assessments.filter((a) =>
    a.return_id.toLowerCase().includes(search.toLowerCase()) ||
    a.order_id.toLowerCase().includes(search.toLowerCase()) ||
    a.customer_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-surface-900 flex items-center">
            <CreditCard className="w-5 h-5 mr-2 text-accent" />
            Transaction Ledger &amp; Scoring History
          </h2>
          <p className="text-xs text-surface-500 mt-0.5">
            Full ledger of point-in-time transactions with customer pseudonym masks.
          </p>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-surface-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search transactions..."
            className="w-full pl-9 pr-3 py-1.5 text-xs font-mono border border-surface-300 rounded focus:ring-1 focus:ring-accent"
          />
        </div>
      </div>

      <div className="bg-white border border-surface-200 rounded shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-surface-500 font-mono text-xs">Loading ledger...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-surface-50 border-b border-surface-200 text-surface-600 text-[10px] uppercase">
                <tr>
                  <th className="py-3 px-4 font-semibold">Return ID</th>
                  <th className="py-3 px-4 font-semibold">Order ID</th>
                  <th className="py-3 px-4 font-semibold">Customer Hash</th>
                  <th className="py-3 px-4 font-semibold">Risk Propensity</th>
                  <th className="py-3 px-4 font-semibold">Risk Tier</th>
                  <th className="py-3 px-4 font-semibold">Expected Loss</th>
                  <th className="py-3 px-4 font-semibold">Policy Recommendation</th>
                  <th className="py-3 px-4 font-semibold">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100">
                {filtered.map((assmt) => (
                  <tr
                    key={assmt.assessment_id}
                    onClick={() => onSelectAssessment(assmt)}
                    className="hover:bg-surface-50 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 font-bold text-accent">{assmt.return_id}</td>
                    <td className="py-3 px-4 text-surface-700">{assmt.order_id}</td>
                    <td className="py-3 px-4 text-surface-500">{assmt.customer_id.substring(0, 10)}...</td>
                    <td className="py-3 px-4 font-bold text-surface-900">{formatPercent(assmt.risk_probability)}</td>
                    <td className="py-3 px-4">
                      <Badge type="risk" value={assmt.risk_level} />
                    </td>
                    <td className="py-3 px-4 font-bold text-surface-800">
                      {formatCurrency(assmt.expected_loss, currency)}
                    </td>
                    <td className="py-3 px-4">
                      <Badge type="recommendation" value={assmt.recommendation} />
                    </td>
                    <td className="py-3 px-4 text-surface-500 text-[11px]">{formatDate(assmt.created_at)}</td>
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
