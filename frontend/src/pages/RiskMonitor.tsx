import React, { useState, useMemo } from 'react';
import { Search, Filter, ShieldAlert, ArrowUpDown, ChevronRight } from 'lucide-react';
import { RiskAssessmentResponse } from '../types/api';
import { Badge } from '../components/data-display/Badge';
import { formatCurrency, formatPercent, formatDate } from '../lib/formatters';

interface RiskMonitorProps {
  assessments: RiskAssessmentResponse[];
  onSelectAssessment: (assmt: RiskAssessmentResponse) => void;
  currency: 'INR' | 'USD';
  isLoading: boolean;
}

export const RiskMonitor: React.FC<RiskMonitorProps> = ({
  assessments,
  onSelectAssessment,
  currency,
  isLoading,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<string>('ALL');
  const [selectedRecommendation, setSelectedRecommendation] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<'score' | 'loss' | 'date'>('score');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const filteredAssessments = useMemo(() => {
    return assessments.filter((a) => {
      const matchesSearch =
        a.return_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.order_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.customer_id.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesLevel = selectedRiskLevel === 'ALL' || a.risk_level === selectedRiskLevel;
      const matchesRec = selectedRecommendation === 'ALL' || a.recommendation === selectedRecommendation;

      return matchesSearch && matchesLevel && matchesRec;
    }).sort((a, b) => {
      let valA = 0;
      let valB = 0;
      if (sortBy === 'score') {
        valA = a.risk_probability;
        valB = b.risk_probability;
      } else if (sortBy === 'loss') {
        valA = a.expected_loss;
        valB = b.expected_loss;
      } else {
        valA = new Date(a.created_at).getTime();
        valB = new Date(b.created_at).getTime();
      }
      return sortOrder === 'desc' ? valB - valA : valA - valB;
    });
  }, [assessments, searchTerm, selectedRiskLevel, selectedRecommendation, sortBy, sortOrder]);

  const toggleSort = (field: 'score' | 'loss' | 'date') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-surface-900 flex items-center">
            <ShieldAlert className="w-5 h-5 mr-2 text-accent" />
            Operational Risk Monitor
          </h2>
          <p className="text-xs text-surface-500 mt-0.5">
            Investigate return requests, review calculated risk propensity, and inspect feature attributions.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono text-surface-600 bg-surface-50 p-2 border border-surface-200 rounded">
          <span>Active Cases: <strong className="text-surface-900">{filteredAssessments.length}</strong></span>
          <span>•</span>
          <span>High Priority: <strong className="text-status-high">{filteredAssessments.filter(a => a.risk_level === 'HIGH').length}</strong></span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white border border-surface-200 rounded p-4 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        {/* Search */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-surface-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search return ID, order ID, customer ref..."
            className="w-full pl-9 pr-3 py-1.5 text-xs font-mono border border-surface-300 rounded focus:ring-1 focus:ring-accent focus:border-accent"
          />
        </div>

        {/* Dropdowns */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <div className="flex items-center space-x-1 text-xs">
            <Filter className="w-3.5 h-3.5 text-surface-400" />
            <span className="text-surface-500 font-mono text-[11px]">Level:</span>
            <select
              value={selectedRiskLevel}
              onChange={(e) => setSelectedRiskLevel(e.target.value)}
              className="text-xs font-mono border border-surface-300 rounded px-2 py-1 bg-white text-surface-800"
            >
              <option value="ALL">All Tiers</option>
              <option value="HIGH">High Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="LOW">Low Risk</option>
            </select>
          </div>

          <div className="flex items-center space-x-1 text-xs">
            <span className="text-surface-500 font-mono text-[11px]">Action:</span>
            <select
              value={selectedRecommendation}
              onChange={(e) => setSelectedRecommendation(e.target.value)}
              className="text-xs font-mono border border-surface-300 rounded px-2 py-1 bg-white text-surface-800"
            >
              <option value="ALL">All Actions</option>
              <option value="MANUAL_REVIEW">Manual Review</option>
              <option value="REQUIRE_ADDITIONAL_VERIFICATION">Require Verification</option>
              <option value="APPROVE">Approve</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white border border-surface-200 rounded shadow-sm overflow-hidden">
        {isLoading && assessments.length === 0 ? (
          <div className="p-8 text-center text-surface-500 font-mono text-xs">Loading operational risk pool...</div>
        ) : filteredAssessments.length === 0 ? (
          <div className="p-12 text-center text-surface-400 font-mono text-xs">
            No return transactions match the active filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-surface-50 border-b border-surface-200 text-surface-600 text-[10px] uppercase">
                <tr>
                  <th className="py-3 px-4 font-semibold">Return ID</th>
                  <th className="py-3 px-4 font-semibold">Order Ref</th>
                  <th className="py-3 px-4 font-semibold">Customer Hash</th>
                  <th
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-surface-900"
                    onClick={() => toggleSort('score')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Risk Score</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3 px-4 font-semibold">Risk Level</th>
                  <th
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-surface-900"
                    onClick={() => toggleSort('loss')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Expected Loss</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3 px-4 font-semibold">Policy Recommendation</th>
                  <th
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-surface-900"
                    onClick={() => toggleSort('date')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Timestamp</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3 px-4 text-right font-semibold">Inspector</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100">
                {filteredAssessments.map((assmt) => (
                  <tr
                    key={assmt.assessment_id}
                    onClick={() => onSelectAssessment(assmt)}
                    className="hover:bg-surface-50 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 font-bold text-accent">{assmt.return_id}</td>
                    <td className="py-3 px-4 text-surface-700">{assmt.order_id}</td>
                    <td className="py-3 px-4 text-surface-500">{assmt.customer_id.substring(0, 12)}...</td>
                    <td className="py-3 px-4 font-bold text-surface-900">
                      {formatPercent(assmt.risk_probability)}
                    </td>
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
                    <td className="py-3 px-4 text-right text-surface-400">
                      <ChevronRight className="w-4 h-4 inline-block text-surface-400" />
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
