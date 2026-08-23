import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Layers } from 'lucide-react';
import { ModelComparisonData } from '../types/api';
import { apiClient } from '../lib/api';
import { formatCurrency, formatPercent } from '../lib/formatters';

interface ModelPerformanceProps {
  currency: 'INR' | 'USD';
}

export const ModelPerformance: React.FC<ModelPerformanceProps> = ({ currency }) => {
  const [data, setData] = useState<ModelComparisonData | null>(null);
  const [ciData, setCiData] = useState<Record<string, { estimate: number; lower_95: number; upper_95: number; std_error: number }>>({});
  const [selectedModelKey, setSelectedModelKey] = useState<'candidate_hist_gradient_boosting' | 'baseline_logistic_regression'>('candidate_hist_gradient_boosting');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    Promise.all([
      apiClient.getModelComparison(),
      apiClient.getConfidenceIntervals(),
    ])
      .then(([resComp, resCi]) => {
        setData(resComp);
        setCiData(resCi || {});
      })
      .catch((err) => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading || !data) {
    return (
      <div className="p-8 text-center text-surface-500 font-mono text-xs">
        Loading validated held-out evaluation artifacts...
      </div>
    );
  }

  const modelData = data.models[selectedModelKey];
  const metrics = modelData.metrics_at_opt_threshold;
  const cm = metrics.confusion_matrix;
  const costs = modelData.costs_at_opt_threshold[currency.toLowerCase() as 'usd' | 'inr'];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-surface-900 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-accent" />
            Model Performance &amp; Evaluation Integrity
          </h2>
          <p className="text-xs text-surface-500 mt-0.5">
            Post-selection evaluation on an untouched held-out test partition ({data.split_summary.held_out_test.count} records, {formatPercent(data.split_summary.held_out_test.prevalence)} prevalence).
          </p>
        </div>

        {/* Model Switcher */}
        <div className="flex items-center space-x-1 border border-surface-200 rounded p-0.5 bg-surface-50 text-xs font-mono">
          <button
            onClick={() => setSelectedModelKey('candidate_hist_gradient_boosting')}
            className={`px-3 py-1.5 rounded transition-colors ${
              selectedModelKey === 'candidate_hist_gradient_boosting'
                ? 'bg-surface-900 text-white font-semibold'
                : 'text-surface-600 hover:text-surface-900'
            }`}
          >
            Champion (HistGradientBoosting)
          </button>
          <button
            onClick={() => setSelectedModelKey('baseline_logistic_regression')}
            className={`px-3 py-1.5 rounded transition-colors ${
              selectedModelKey === 'baseline_logistic_regression'
                ? 'bg-surface-900 text-white font-semibold'
                : 'text-surface-600 hover:text-surface-900'
            }`}
          >
            Baseline (Logistic Regression)
          </button>
        </div>
      </div>

      {/* Mandatory Disclaimer */}
      <div className="p-3 bg-surface-50 border border-surface-200 rounded flex items-center justify-between text-xs font-mono text-surface-700">
        <span className="flex items-center">
          <AlertTriangle className="w-4 h-4 mr-2 text-amber-600 shrink-0" />
          {data.disclaimer}
        </span>
        <span className="text-[11px] text-surface-500 shrink-0 ml-2">Operating Threshold: {modelData.optimal_threshold.toFixed(2)}</span>
      </div>

      {/* Key Metric Scorecards with 95% Confidence Intervals */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono">
        <div className="bg-white border border-surface-200 rounded p-3 text-center shadow-sm">
          <span className="text-[10px] text-surface-500 block uppercase">Precision</span>
          <span className="text-xl font-bold text-accent">{formatPercent(metrics.precision)}</span>
          {ciData.precision ? (
            <span className="text-[9px] text-surface-500 block mt-0.5 font-mono">
              95% CI: {formatPercent(ciData.precision.lower_95)}–{formatPercent(ciData.precision.upper_95)}
            </span>
          ) : (
            <span className="text-[10px] text-surface-400 block mt-0.5">TP / (TP + FP)</span>
          )}
        </div>

        <div className="bg-white border border-surface-200 rounded p-3 text-center shadow-sm">
          <span className="text-[10px] text-surface-500 block uppercase">Recall</span>
          <span className="text-xl font-bold text-accent">{formatPercent(metrics.recall)}</span>
          {ciData.recall ? (
            <span className="text-[9px] text-surface-500 block mt-0.5 font-mono">
              95% CI: {formatPercent(ciData.recall.lower_95)}–{formatPercent(ciData.recall.upper_95)}
            </span>
          ) : (
            <span className="text-[10px] text-surface-400 block mt-0.5">TP / (TP + FN)</span>
          )}
        </div>

        <div className="bg-white border border-surface-200 rounded p-3 text-center shadow-sm">
          <span className="text-[10px] text-surface-500 block uppercase">F1-Score</span>
          <span className="text-xl font-bold text-surface-900">{metrics.f1_score.toFixed(4)}</span>
          {ciData.f1_score ? (
            <span className="text-[9px] text-surface-500 block mt-0.5 font-mono">
              95% CI: {ciData.f1_score.lower_95.toFixed(3)}–{ciData.f1_score.upper_95.toFixed(3)}
            </span>
          ) : (
            <span className="text-[10px] text-surface-400 block mt-0.5">Harmonic Mean</span>
          )}
        </div>

        <div className="bg-white border border-surface-200 rounded p-3 text-center shadow-sm">
          <span className="text-[10px] text-surface-500 block uppercase">PR-AUC</span>
          <span className="text-xl font-bold text-surface-900">{metrics.pr_auc.toFixed(4)}</span>
          {ciData.pr_auc ? (
            <span className="text-[9px] text-surface-500 block mt-0.5 font-mono">
              95% CI: {ciData.pr_auc.lower_95.toFixed(3)}–{ciData.pr_auc.upper_95.toFixed(3)}
            </span>
          ) : (
            <span className="text-[10px] text-surface-400 block mt-0.5">Precision-Recall</span>
          )}
        </div>

        <div className="bg-white border border-surface-200 rounded p-3 text-center shadow-sm">
          <span className="text-[10px] text-surface-500 block uppercase">ROC-AUC</span>
          <span className="text-xl font-bold text-surface-900">{metrics.roc_auc.toFixed(4)}</span>
          {ciData.roc_auc ? (
            <span className="text-[9px] text-surface-500 block mt-0.5 font-mono">
              95% CI: {ciData.roc_auc.lower_95.toFixed(3)}–{ciData.roc_auc.upper_95.toFixed(3)}
            </span>
          ) : (
            <span className="text-[10px] text-surface-400 block mt-0.5">Ranking Power</span>
          )}
        </div>

        <div className="bg-white border border-surface-200 rounded p-3 text-center shadow-sm">
          <span className="text-[10px] text-surface-500 block uppercase">Brier Score</span>
          <span className="text-xl font-bold text-surface-900">{metrics.brier_score.toFixed(4)}</span>
          <span className="text-[10px] text-surface-400 block mt-0.5">Platt Calibrated</span>
        </div>
      </div>

      {/* Confusion Matrix & Economic Cost Simulation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix */}
        <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700">
              Held-Out Test Confusion Matrix (N={data.split_summary.held_out_test.count})
            </h3>
            <span className="text-xs font-mono text-surface-400">T = {modelData.optimal_threshold.toFixed(2)}</span>
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            {/* True Positive */}
            <div className="p-4 bg-green-50 border border-green-200 rounded">
              <span className="text-[10px] text-green-700 font-bold block uppercase">
                True Positives (Caught)
              </span>
              <span className="text-2xl font-bold text-green-900">{cm.true_positives}</span>
              <p className="text-[11px] text-green-700 font-sans mt-1">
                Abusive returns correctly flagged for merchant intervention.
              </p>
            </div>

            {/* False Positive */}
            <div className="p-4 bg-amber-50 border border-amber-200 rounded">
              <span className="text-[10px] text-amber-700 font-bold block uppercase">
                False Positives (Friction)
              </span>
              <span className="text-2xl font-bold text-amber-900">{cm.false_positives}</span>
              <p className="text-[11px] text-amber-700 font-sans mt-1">
                Legitimate customers incorrectly flagged for verification.
              </p>
            </div>

            {/* False Negative */}
            <div className="p-4 bg-red-50 border border-red-200 rounded">
              <span className="text-[10px] text-red-700 font-bold block uppercase">
                False Negatives (Missed)
              </span>
              <span className="text-2xl font-bold text-red-900">{cm.false_negatives}</span>
              <p className="text-[11px] text-red-700 font-sans mt-1">
                Abusive claims missed by model causing unmitigated inventory loss.
              </p>
            </div>

            {/* True Negative */}
            <div className="p-4 bg-surface-50 border border-surface-200 rounded">
              <span className="text-[10px] text-surface-600 font-bold block uppercase">
                True Negatives (Standard Policy Processing)
              </span>
              <span className="text-2xl font-bold text-surface-900">{cm.true_negatives}</span>
              <p className="text-[11px] text-surface-600 font-sans mt-1">
                Legitimate returns receiving standard policy recommendation with zero customer friction.
              </p>
            </div>
          </div>
        </div>

        {/* Economic Simulation */}
        <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700">
              Asymmetric Merchant Economic Impact
            </h3>
            <span className="text-xs font-mono text-status-low font-bold">
              Net Benefit: +{formatCurrency(costs.net_merchant_benefit, currency)}
            </span>
          </div>

          <div className="space-y-2 font-mono text-xs">
            <div className="flex justify-between p-2 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Baseline Unmitigated Loss (Do Nothing):</span>
              <span className="font-bold text-surface-900">{formatCurrency(costs.baseline_unmitigated_loss, currency)}</span>
            </div>

            <div className="flex justify-between p-2 bg-green-50 border border-green-200 rounded text-green-900">
              <span>Gross Abusive Loss Prevented:</span>
              <span className="font-bold">+{formatCurrency(costs.gross_loss_prevented, currency)}</span>
            </div>

            <div className="flex justify-between p-2 bg-surface-50 border border-surface-200 rounded text-surface-700">
              <span>False Positive Friction Expenditure:</span>
              <span className="font-bold text-red-700">-{formatCurrency(costs.false_positive_friction_cost, currency)}</span>
            </div>

            <div className="flex justify-between p-2 bg-surface-50 border border-surface-200 rounded text-surface-700">
              <span>Review Analyst Labor Cost ({modelData.costs_at_opt_threshold.review_count} reviews):</span>
              <span className="font-bold text-red-700">-{formatCurrency(costs.review_labor_expenditure, currency)}</span>
            </div>

            <div className="flex justify-between p-2 bg-surface-50 border border-surface-200 rounded text-surface-700">
              <span>Realized Missed Fraud (False Negatives):</span>
              <span className="font-bold text-red-700">-{formatCurrency(costs.false_negative_realized_loss, currency)}</span>
            </div>

            <div className="flex justify-between p-2.5 bg-surface-900 text-white rounded font-bold mt-2">
              <span>Net Merchant Economic Benefit:</span>
              <span className="text-accent">+{formatCurrency(costs.net_merchant_benefit, currency)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Model Governance */}
      <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-3 font-mono text-xs">
        <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700 flex items-center">
          <Layers className="w-3.5 h-3.5 mr-1.5 text-accent" />
          Model Metadata &amp; Governance
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-surface-50 border border-surface-200 rounded">
            <span className="text-[10px] text-surface-500 block">MODEL VERSION</span>
            <span className="font-bold text-surface-900">{modelData.version}</span>
          </div>
          <div className="p-3 bg-surface-50 border border-surface-200 rounded">
            <span className="text-[10px] text-surface-500 block">FEATURE PIPELINE</span>
            <span className="font-bold text-surface-900">v2_point_in_time_23f</span>
          </div>
          <div className="p-3 bg-surface-50 border border-surface-200 rounded">
            <span className="text-[10px] text-surface-500 block">CALIBRATION</span>
            <span className="font-bold text-surface-900">Platt Sigmoid</span>
          </div>
          <div className="p-3 bg-surface-50 border border-surface-200 rounded">
            <span className="text-[10px] text-surface-500 block">THRESHOLD TUNING</span>
            <span className="font-bold text-surface-900">Validation Set Only (N=750)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
