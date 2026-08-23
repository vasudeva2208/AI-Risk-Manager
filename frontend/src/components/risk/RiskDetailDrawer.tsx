import React, { useState, useEffect } from 'react';
import { X, ShieldAlert, History, HelpCircle, UserCheck } from 'lucide-react';
import { RiskAssessmentResponse, AuditEventResponse } from '../../types/api';
import { Badge } from '../data-display/Badge';
import { formatCurrency, formatPercent, formatDate } from '../../lib/formatters';
import { apiClient } from '../../lib/api';

interface RiskDetailDrawerProps {
  assessment: RiskAssessmentResponse | null;
  isOpen: boolean;
  onClose: () => void;
  onOpenReviewModal?: (assessmentId: string) => void;
  currency: 'INR' | 'USD';
}

export const RiskDetailDrawer: React.FC<RiskDetailDrawerProps> = ({
  assessment,
  isOpen,
  onClose,
  onOpenReviewModal,
  currency,
}) => {
  const [showFormula, setShowFormula] = useState(false);
  const [auditEvents, setAuditEvents] = useState<AuditEventResponse[]>([]);
  const [isLoadingAudit, setIsLoadingAudit] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (assessment && isOpen) {
      setIsLoadingAudit(true);
      apiClient
        .getAssessmentAudit(assessment.assessment_id)
        .then((events) => setAuditEvents(events))
        .catch(() => setAuditEvents([]))
        .finally(() => setIsLoadingAudit(false));
    }
  }, [assessment, isOpen]);

  if (!isOpen || !assessment) return null;

  const scorePct = Math.round(assessment.risk_probability * 100);

  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-surface-900/40" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
      <div className="bg-white w-full max-w-xl h-full shadow-2xl flex flex-col border-l border-surface-200 overflow-hidden">
        {/* Drawer Header */}
        <div className="px-6 py-4 border-b border-surface-200 flex items-center justify-between bg-surface-50">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-accent" />
            <div>
              <h3 id="drawer-title" className="text-sm font-bold text-surface-900">Risk Assessment Inspector</h3>
              <p className="text-xs font-mono text-surface-500">ID: {assessment.assessment_id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close inspector"
            className="text-surface-400 hover:text-surface-600 p-1.5 rounded hover:bg-surface-200 focus:outline-none focus:ring-2 focus:ring-accent"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Drawer Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-xs font-sans">
          {/* Top Score Matrix */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="p-3 bg-surface-50 border border-surface-200 rounded">
              <span className="text-[10px] font-mono text-surface-500 block uppercase">Risk Score</span>
              <span className="text-xl font-mono font-bold text-surface-900">{scorePct} / 100</span>
              <span className="text-[10px] text-surface-400 block mt-0.5 font-mono">{formatPercent(assessment.risk_probability)} prob</span>
            </div>

            <div className="p-3 bg-surface-50 border border-surface-200 rounded">
              <span className="text-[10px] font-mono text-surface-500 block uppercase">Risk Level</span>
              <div className="mt-1">
                <Badge type="risk" value={assessment.risk_level} />
              </div>
            </div>

            <div className="p-3 bg-surface-50 border border-surface-200 rounded">
              <span className="text-[10px] font-mono text-surface-500 block uppercase">Expected Loss</span>
              <span className="text-base font-mono font-bold text-surface-900 mt-1 block">
                {formatCurrency(assessment.expected_loss, currency)}
              </span>
            </div>

            <div className="p-3 bg-surface-50 border border-surface-200 rounded">
              <span className="text-[10px] font-mono text-surface-500 block uppercase">Policy Recommendation</span>
              <div className="mt-1">
                <Badge type="recommendation" value={assessment.recommendation} />
              </div>
            </div>
          </div>

          {/* Probability Progress Bar */}
          <div className="p-4 bg-white border border-surface-200 rounded space-y-2">
            <div className="flex justify-between text-xs font-mono text-surface-700">
              <span className="font-semibold">Predicted Return-Abuse Probability:</span>
              <span className="font-bold">{formatPercent(assessment.risk_probability)}</span>
            </div>
            <div className="w-full h-2.5 bg-surface-100 rounded overflow-hidden border border-surface-200">
              <div
                className={`h-full ${
                  scorePct < 30 ? 'bg-status-low' : scorePct < 70 ? 'bg-status-medium' : 'bg-status-high'
                }`}
                style={{ width: `${scorePct}%` }}
              />
            </div>
            <p className="text-[11px] text-surface-500">
              Threshold applied: <span className="font-mono font-bold">{assessment.threshold_applied.toFixed(2)}</span> (Higher score = higher estimated return-abuse propensity)
            </p>
          </div>

          {/* Why was this flagged? (Feature Attributions) */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-surface-900 uppercase tracking-wider">
              Why was this flagged? (Top Risk Factors)
            </h4>
            <div className="space-y-2">
              {assessment.top_risk_factors.map((factor, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-surface-50 border border-surface-200 rounded flex flex-col space-y-1"
                >
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-surface-800">{factor.feature_name}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-surface-200 text-surface-700 font-semibold">
                      Value: {factor.feature_value}
                    </span>
                  </div>
                  <p className="text-xs text-surface-600 font-sans">
                    {factor.human_readable_reason}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Expected Loss Breakdown */}
          <div className="p-4 bg-surface-50 border border-surface-200 rounded space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-surface-900 uppercase tracking-wider">
                Expected Loss Quantification
              </h4>
              <button
                onClick={() => setShowFormula(!showFormula)}
                className="text-[11px] text-accent hover:underline flex items-center font-mono focus:outline-none focus:ring-1 focus:ring-accent"
              >
                <HelpCircle className="w-3.5 h-3.5 mr-1" />
                {showFormula ? 'Hide Formula' : 'How calculated?'}
              </button>
            </div>

            {showFormula && (
              <div className="p-3 bg-white border border-surface-200 rounded text-[11px] font-mono text-surface-700 space-y-1">
                <p className="font-bold text-surface-900">Transparent Economic Formula:</p>
                <p>Expected Loss = P(Abuse) × [Refund Requested + Return Shipping/Labor Cost]</p>
                <p className="text-surface-500">
                  = {formatPercent(assessment.risk_probability)} × {formatCurrency(assessment.estimated_loss_if_abuse, currency)} = {formatCurrency(assessment.expected_loss, currency)}
                </p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="p-2 bg-white border border-surface-200 rounded">
                <span className="text-[10px] text-surface-500 block">Total Exposure if Abusive:</span>
                <span className="font-bold text-surface-900">{formatCurrency(assessment.estimated_loss_if_abuse, currency)}</span>
              </div>
              <div className="p-2 bg-white border border-surface-200 rounded">
                <span className="text-[10px] text-surface-500 block">Expected Loss:</span>
                <span className="font-bold text-accent">{formatCurrency(assessment.expected_loss, currency)}</span>
              </div>
            </div>
          </div>

          {/* Audit History Timeline */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-surface-900 uppercase tracking-wider flex items-center">
                <History className="w-3.5 h-3.5 mr-1 text-surface-500" />
                Tamper-Evident Audit Timeline
              </h4>
              <span className="text-[10px] font-mono text-status-low font-semibold">SHA-256 Chained</span>
            </div>

            {isLoadingAudit ? (
              <p className="text-xs text-surface-500 font-mono">Loading audit trail...</p>
            ) : auditEvents.length === 0 ? (
              <p className="text-xs text-surface-500 font-mono">No audit records on file.</p>
            ) : (
              <div className="border-l-2 border-surface-200 pl-4 space-y-3">
                {auditEvents.map((evt) => (
                  <div key={evt.audit_id} className="relative space-y-0.5">
                    <div className="absolute -left-[21px] top-1.5 w-2 h-2 rounded-full bg-accent" />
                    <div className="flex items-center justify-between text-[11px] font-mono">
                      <span className="font-bold text-surface-800">{evt.event_type}</span>
                      <span className="text-surface-400">{formatDate(evt.timestamp)}</span>
                    </div>
                    <p className="text-xs text-surface-600 font-sans">{evt.reason}</p>
                    <p className="text-[10px] font-mono text-surface-400">
                      Actor: <span className="text-surface-600">{evt.actor_id}</span> ({evt.actor_type})
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-surface-200 bg-surface-50 flex items-center justify-between">
          <div className="text-[11px] font-mono text-surface-500">
            Model: <span className="font-bold text-surface-700">{assessment.model_version}</span>
          </div>
          {onOpenReviewModal && assessment.recommendation !== 'APPROVE' && (
            <button
              onClick={() => onOpenReviewModal(assessment.assessment_id)}
              className="btn-primary text-xs focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <UserCheck className="w-3.5 h-3.5 mr-1" />
              Open Human Review
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
