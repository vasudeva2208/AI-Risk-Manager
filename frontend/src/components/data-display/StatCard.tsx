import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badge?: string;
  trend?: string;
  accentValue?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  accentValue = false,
}) => {
  return (
    <div className="bg-white border border-surface-200 rounded p-5 shadow-sm">
      <div className="flex items-center justify-between text-surface-500 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-surface-600">{title}</span>
        <Icon className="w-4 h-4 text-surface-400" />
      </div>
      <div className="flex items-baseline space-x-2">
        <p className={`text-2xl font-mono font-bold ${accentValue ? 'text-accent' : 'text-surface-900'}`}>
          {value}
        </p>
        {badge && (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono bg-surface-100 text-surface-600 border border-surface-200">
            {badge}
          </span>
        )}
      </div>
      {subtitle && <p className="text-xs text-surface-500 mt-1.5">{subtitle}</p>}
    </div>
  );
};
