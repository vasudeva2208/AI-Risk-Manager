import React from 'react';
import {
  LayoutDashboard,
  ShieldAlert,
  CreditCard,
  UserCheck,
  PieChart,
  Activity,
  History,
  FileBarChart,
  Settings,
  Lock
} from 'lucide-react';

export type NavRoute = 
  | 'overview' 
  | 'risk-monitor' 
  | 'transactions' 
  | 'reviews' 
  | 'risk-analysis' 
  | 'model-performance' 
  | 'audit-log' 
  | 'reports' 
  | 'settings';

interface SidebarProps {
  currentRoute: NavRoute;
  onRouteChange: (route: NavRoute) => void;
  pendingReviewCount: number;
}

interface NavGroup {
  title: string;
  items: { id: NavRoute; label: string; icon: React.FC<{ className?: string }>; count?: number }[];
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentRoute,
  onRouteChange,
  pendingReviewCount,
}) => {
  const navGroups: NavGroup[] = [
    {
      title: 'Operations',
      items: [
        { id: 'overview', label: 'Overview', icon: LayoutDashboard },
        { id: 'risk-monitor', label: 'Risk Monitor', icon: ShieldAlert },
        { id: 'transactions', label: 'Transactions', icon: CreditCard },
        { id: 'reviews', label: 'Reviews', icon: UserCheck, count: pendingReviewCount },
      ],
    },
    {
      title: 'Analysis',
      items: [
        { id: 'risk-analysis', label: 'Risk Analysis', icon: PieChart },
        { id: 'model-performance', label: 'Model Performance', icon: Activity },
        { id: 'reports', label: 'Reports', icon: FileBarChart },
      ],
    },
    {
      title: 'Governance',
      items: [
        { id: 'audit-log', label: 'Audit Log', icon: History },
        { id: 'settings', label: 'Settings', icon: Settings },
      ],
    },
  ];

  return (
    <aside className="w-64 bg-surface-900 text-white flex flex-col shrink-0 border-r border-surface-800 select-none">
      {/* Brand Header */}
      <div className="px-5 py-4 border-b border-surface-800 flex items-center space-x-3">
        <div className="p-1.5 bg-accent text-white rounded">
          <ShieldAlert className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight text-white">AI Risk Manager</h1>
          <p className="text-[11px] font-mono text-surface-400">Defense &amp; Governance</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-4 space-y-4 overflow-y-auto" aria-label="Main Navigation">
        {navGroups.map((group) => (
          <div key={group.title} className="space-y-1">
            <span className="px-3 text-[10px] font-mono font-bold uppercase tracking-wider text-surface-500 block mb-1">
              {group.title}
            </span>
            {group.items.map((item) => {
              const Icon = item.icon;
              const isActive = currentRoute === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => onRouteChange(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 text-xs font-medium rounded transition-colors focus:outline-none focus:ring-1 focus:ring-accent ${
                    isActive
                      ? 'bg-accent text-white font-semibold'
                      : 'text-surface-300 hover:bg-surface-800 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-surface-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.count !== undefined && item.count > 0 && (
                    <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono font-bold ${
                      isActive ? 'bg-white text-accent' : 'bg-surface-800 text-surface-200'
                    }`}>
                      {item.count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer / System Status */}
      <div className="p-3 border-t border-surface-800 bg-surface-900/80">
        <div className="flex items-center justify-between text-[11px] font-mono text-surface-400">
          <span className="flex items-center">
            <Lock className="w-3 h-3 mr-1 text-surface-500" />
            Defense-Only
          </span>
          <span className="text-status-low font-bold">return-policy-v1</span>
        </div>
      </div>
    </aside>
  );
};
