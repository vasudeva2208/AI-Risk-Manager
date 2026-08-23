import React from 'react';
import { RiskLevel, BoundedRecommendation, ReviewStatus, HumanDecisionType } from '../../types/api';

interface BadgeProps {
  type: 'risk' | 'recommendation' | 'status' | 'decision';
  value: RiskLevel | BoundedRecommendation | ReviewStatus | HumanDecisionType | string;
}

export const Badge: React.FC<BadgeProps> = ({ type, value }) => {
  if (type === 'risk') {
    if (value === 'LOW') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-green-50 text-green-700 border border-green-200">LOW</span>;
    }
    if (value === 'MEDIUM') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-amber-50 text-amber-700 border border-amber-200">MEDIUM</span>;
    }
    return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-red-50 text-red-700 border border-red-200">HIGH</span>;
  }

  if (type === 'recommendation') {
    if (value === 'APPROVE') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-green-50 text-green-700 border border-green-200">APPROVE</span>;
    }
    if (value === 'REQUIRE_ADDITIONAL_VERIFICATION') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-amber-50 text-amber-700 border border-amber-200">VERIFY</span>;
    }
    return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-red-50 text-red-700 border border-red-200">MANUAL REVIEW</span>;
  }

  if (type === 'status') {
    if (value === 'PENDING_REVIEW') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-amber-50 text-amber-700 border border-amber-200">PENDING</span>;
    }
    if (value === 'UNDER_REVIEW') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-blue-50 text-blue-700 border border-blue-200">UNDER REVIEW</span>;
    }
    return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-surface-100 text-surface-700 border border-surface-200">RESOLVED</span>;
  }

  if (type === 'decision') {
    if (value === 'APPROVE_RETURN') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-green-50 text-green-700 border border-green-200">APPROVED</span>;
    }
    if (value === 'REQUEST_ADDITIONAL_VERIFICATION') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-amber-50 text-amber-700 border border-amber-200">VERIFY REQ</span>;
    }
    return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-red-50 text-red-700 border border-red-200">ESCALATED</span>;
  }

  return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-surface-100 text-surface-700 border border-surface-200">{value}</span>;
};
