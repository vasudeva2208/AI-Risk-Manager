import React, { useState, useEffect, useRef } from 'react';
import { X, CheckCircle, AlertTriangle, ArrowUpRight, ShieldCheck } from 'lucide-react';
import { ReviewCaseResponse, HumanDecisionType } from '../../types/api';
import { formatCurrency, formatPercent } from '../../lib/formatters';

interface ReviewModalProps {
  reviewCase: ReviewCaseResponse | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmitDecision: (caseId: string, decision: HumanDecisionType, reason: string) => Promise<void>;
  currency: 'INR' | 'USD';
}

export const ReviewModal: React.FC<ReviewModalProps> = ({
  reviewCase,
  isOpen,
  onClose,
  onSubmitDecision,
  currency,
}) => {
  const [selectedDecision, setSelectedDecision] = useState<HumanDecisionType>('APPROVE_RETURN');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      // Focus modal
      const firstInput = modalRef.current?.querySelector('button, textarea, input') as HTMLElement;
      firstInput?.focus();
    } else {
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isSubmitting) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isSubmitting, onClose]);

  if (!isOpen || !reviewCase) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (reason.trim().length < 5) {
      setErrorMsg('Mandatory rationale must be at least 5 characters long.');
      return;
    }
    setErrorMsg(null);
    setShowConfirm(true);
  };

  const handleConfirmFinal = async () => {
    try {
      setIsSubmitting(true);
      await onSubmitDecision(reviewCase.case_id, selectedDecision, reason);
      setSuccessMsg('Decision recorded and audit event created.');
      setTimeout(() => {
        setSuccessMsg(null);
        setShowConfirm(false);
        setReason('');
        onClose();
      }, 1000);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit decision.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-surface-900/60 p-4 backdrop-blur-none" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div ref={modalRef} className="bg-white border border-surface-200 rounded w-full max-w-lg shadow-lg overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-surface-200 flex items-center justify-between bg-surface-50">
          <div>
            <h3 id="modal-title" className="text-sm font-bold text-surface-900">
              {showConfirm ? 'Confirm Analyst Decision' : 'Merchant Human Review Decision'}
            </h3>
            <p className="text-xs font-mono text-surface-500">Case ID: {reviewCase.case_id}</p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="text-surface-400 hover:text-surface-600 p-1 rounded focus:outline-none focus:ring-2 focus:ring-accent"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        {!showConfirm ? (
          <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs font-sans">
            {/* Case Summary Pill */}
            <div className="p-3 bg-surface-50 border border-surface-200 rounded grid grid-cols-3 gap-2 font-mono text-center">
              <div>
                <span className="text-[10px] text-surface-500 block">RISK SCORE</span>
                <span className="font-bold text-surface-900">{formatPercent(reviewCase.risk_probability)}</span>
              </div>
              <div>
                <span className="text-[10px] text-surface-500 block">EXPOSURE</span>
                <span className="font-bold text-surface-900">{formatCurrency(reviewCase.expected_loss, currency)}</span>
              </div>
              <div>
                <span className="text-[10px] text-surface-500 block">MODEL RECOMMENDATION</span>
                <span className="font-bold text-accent">{reviewCase.model_recommendation}</span>
              </div>
            </div>

            {/* Decision Select */}
            <div>
              <label className="block text-xs font-semibold text-surface-800 mb-2">
                Select Analyst Decision:
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setSelectedDecision('APPROVE_RETURN')}
                  className={`p-2.5 text-center rounded border text-xs font-mono font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-accent ${
                    selectedDecision === 'APPROVE_RETURN'
                      ? 'bg-surface-900 text-white border-surface-900'
                      : 'bg-white text-surface-700 border-surface-300 hover:bg-surface-50'
                  }`}
                >
                  <CheckCircle className="w-3.5 h-3.5 mx-auto mb-1 text-green-500" />
                  Approve Return
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedDecision('REQUEST_ADDITIONAL_VERIFICATION')}
                  className={`p-2.5 text-center rounded border text-xs font-mono font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-accent ${
                    selectedDecision === 'REQUEST_ADDITIONAL_VERIFICATION'
                      ? 'bg-surface-900 text-white border-surface-900'
                      : 'bg-white text-surface-700 border-surface-300 hover:bg-surface-50'
                  }`}
                >
                  <AlertTriangle className="w-3.5 h-3.5 mx-auto mb-1 text-amber-500" />
                  Request Verify
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedDecision('ESCALATE')}
                  className={`p-2.5 text-center rounded border text-xs font-mono font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-accent ${
                    selectedDecision === 'ESCALATE'
                      ? 'bg-surface-900 text-white border-surface-900'
                      : 'bg-white text-surface-700 border-surface-300 hover:bg-surface-50'
                  }`}
                >
                  <ArrowUpRight className="w-3.5 h-3.5 mx-auto mb-1 text-red-500" />
                  Escalate
                </button>
              </div>
            </div>

            {/* Reason Field */}
            <div>
              <label htmlFor="reviewer-reason" className="block text-xs font-semibold text-surface-800 mb-1">
                Mandatory Reviewer Rationale:
              </label>
              <textarea
                id="reviewer-reason"
                rows={3}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Explain the evidence reviewed (e.g. verified packaging photos, customer purchase receipt, or hub drop-off required)..."
                className="w-full p-2.5 text-xs font-mono border border-surface-300 rounded focus:ring-1 focus:ring-accent focus:border-accent"
              />
              <span className="text-[10px] text-surface-500">Record the evidence reviewed and reason for your decision (minimum 5 characters).</span>
            </div>

            {errorMsg && (
              <p className="text-xs font-mono text-red-600 bg-red-50 p-2 border border-red-200 rounded" role="alert">
                {errorMsg}
              </p>
            )}

            {/* Action Buttons */}
            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 text-xs text-surface-700 bg-white border border-surface-300 rounded hover:bg-surface-50 focus:outline-none focus:ring-2 focus:ring-accent"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={reason.trim().length < 5}
                className="px-4 py-1.5 text-xs font-semibold text-white bg-accent hover:bg-accent-hover rounded disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-accent"
              >
                Review &amp; Confirm
              </button>
            </div>
          </form>
        ) : (
          /* Confirmation Screen */
          <div className="p-6 space-y-4 text-xs font-sans">
            <div className="p-4 bg-surface-50 border border-surface-200 rounded space-y-2 font-mono text-surface-800">
              <div className="flex justify-between">
                <span className="text-surface-500">Case ID:</span>
                <span className="font-bold">{reviewCase.case_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-surface-500">Model Recommendation:</span>
                <span className="font-semibold text-surface-700">{reviewCase.model_recommendation}</span>
              </div>
              <div className="flex justify-between border-t border-surface-200 pt-2">
                <span className="text-surface-900 font-bold">Your Analyst Decision:</span>
                <span className="font-bold text-accent">{selectedDecision}</span>
              </div>
              <div className="border-t border-surface-200 pt-2">
                <span className="text-surface-500 block mb-1">Reason Recorded:</span>
                <p className="text-surface-900 bg-white p-2 border border-surface-200 rounded text-[11px] whitespace-pre-wrap">
                  {reason}
                </p>
              </div>
            </div>

            {successMsg && (
              <p className="text-xs font-mono text-green-700 bg-green-50 p-2.5 border border-green-200 rounded flex items-center" role="status">
                <ShieldCheck className="w-4 h-4 mr-1.5 text-green-600 shrink-0" />
                {successMsg}
              </p>
            )}

            {errorMsg && (
              <p className="text-xs font-mono text-red-600 bg-red-50 p-2 border border-red-200 rounded" role="alert">
                {errorMsg}
              </p>
            )}

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setShowConfirm(false)}
                disabled={isSubmitting || !!successMsg}
                className="px-3 py-1.5 text-xs text-surface-700 bg-white border border-surface-300 rounded hover:bg-surface-50 focus:outline-none focus:ring-2 focus:ring-accent disabled:opacity-50"
              >
                Back
              </button>
              <button
                type="button"
                onClick={handleConfirmFinal}
                disabled={isSubmitting || !!successMsg}
                className="px-4 py-1.5 text-xs font-semibold text-white bg-surface-900 hover:bg-surface-800 rounded disabled:opacity-50 flex items-center focus:outline-none focus:ring-2 focus:ring-accent"
              >
                <ShieldCheck className="w-3.5 h-3.5 mr-1 text-green-400" />
                {isSubmitting ? 'Recording Decision...' : 'Record Decision'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
