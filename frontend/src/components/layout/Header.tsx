import React from 'react';
import { RefreshCw, CheckCircle2 } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  currency: 'INR' | 'USD';
  onCurrencyChange: (c: 'INR' | 'USD') => void;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  currency,
  onCurrencyChange,
  onRefresh,
  isLoading = false,
}) => {
  return (
    <header className="bg-white border-b border-surface-200 px-6 py-4 flex items-center justify-between shrink-0">
      <div>
        <h2 className="text-lg font-bold tracking-tight text-surface-900">{title}</h2>
        {subtitle && <p className="text-xs text-surface-500 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center space-x-3">
        {/* Currency Switcher */}
        <div className="flex items-center space-x-1 border border-surface-200 rounded p-0.5 bg-surface-50 text-xs font-mono">
          <button
            onClick={() => onCurrencyChange('INR')}
            className={`px-2 py-1 rounded transition-colors ${
              currency === 'INR'
                ? 'bg-surface-900 text-white font-semibold'
                : 'text-surface-600 hover:text-surface-900'
            }`}
          >
            INR (₹)
          </button>
          <button
            onClick={() => onCurrencyChange('USD')}
            className={`px-2 py-1 rounded transition-colors ${
              currency === 'USD'
                ? 'bg-surface-900 text-white font-semibold'
                : 'text-surface-600 hover:text-surface-900'
            }`}
          >
            USD ($)
          </button>
        </div>

        {/* Refresh Action */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-1.5 text-surface-600 hover:text-surface-900 border border-surface-200 rounded hover:bg-surface-50 transition-colors disabled:opacity-50"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        )}

        <span className="hidden sm:inline-flex items-center px-2 py-1 rounded text-xs font-mono bg-status-low-bg text-status-low border border-green-200">
          <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
          Production Champion
        </span>
      </div>
    </header>
  );
};
