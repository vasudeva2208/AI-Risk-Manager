import React from 'react';
import { Settings as SettingsIcon, Lock, Layers } from 'lucide-react';

export const Settings: React.FC = () => {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans">
      <div>
        <h2 className="text-base font-bold text-surface-900 flex items-center">
          <SettingsIcon className="w-5 h-5 mr-2 text-accent" />
          System Configuration &amp; Governance
        </h2>
        <p className="text-xs text-surface-500 mt-0.5">
          Production model registry, bounded policy parameters, and security boundaries.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Model Configuration */}
        <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700 flex items-center">
            <Layers className="w-4 h-4 mr-1.5 text-accent" />
            Model Registry Status
          </h3>
          <div className="space-y-2.5 font-mono text-xs">
            <div className="flex justify-between p-2 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Active Champion:</span>
              <span className="font-bold text-surface-900">return-risk-hgb-v1</span>
            </div>
            <div className="flex justify-between p-2 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Algorithm:</span>
              <span className="font-bold text-surface-900">HistGradientBoosting</span>
            </div>
            <div className="flex justify-between p-2 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Feature Version:</span>
              <span className="font-bold text-surface-900">v2_point_in_time_23f</span>
            </div>
            <div className="flex justify-between p-2 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Probability Calibration:</span>
              <span className="font-bold text-surface-900">Platt Scaling (Sigmoid)</span>
            </div>
            <div className="flex justify-between p-2 bg-surface-50 border border-surface-200 rounded">
              <span className="text-surface-600">Locked Operating Threshold:</span>
              <span className="font-bold text-accent">0.30 (Validation Optimized)</span>
            </div>
          </div>
        </div>

        {/* Security & Access Controls */}
        <div className="bg-white border border-surface-200 rounded p-5 shadow-sm space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-surface-700 flex items-center">
            <Lock className="w-4 h-4 mr-1.5 text-accent" />
            Security &amp; Authorization Boundaries
          </h3>
          <div className="space-y-2.5 font-mono text-xs">
            <div className="p-3 bg-surface-50 border border-surface-200 rounded space-y-1.5">
              <span className="font-bold text-surface-900 block">Defense-Only System Safeguard:</span>
              <p className="text-[11px] font-sans text-surface-600">
                The ML model predicts risk only and is strictly prohibited from executing automatic financial fund forfeitures or unilateral denial actions.
              </p>
            </div>
            <div className="p-3 bg-surface-50 border border-surface-200 rounded space-y-1.5">
              <span className="font-bold text-surface-900 block">Reviewer Authorization:</span>
              <p className="text-[11px] font-sans text-surface-600">
                Human review decisions require valid authentication under roles <code className="text-surface-900">RISK_ANALYST</code> or <code className="text-surface-900">RISK_ADMIN</code> with mandatory non-empty rationale.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
