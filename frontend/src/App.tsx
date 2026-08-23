import { useState, useEffect, useCallback } from 'react';
import { Sidebar, NavRoute } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { Overview } from './pages/Overview';
import { RiskMonitor } from './pages/RiskMonitor';
import { Transactions } from './pages/Transactions';
import { Reviews } from './pages/Reviews';
import { RiskAnalysis } from './pages/RiskAnalysis';
import { ModelPerformance } from './pages/ModelPerformance';
import { AuditLog } from './pages/AuditLog';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';
import { RiskDetailDrawer } from './components/risk/RiskDetailDrawer';
import { ReviewModal } from './components/review/ReviewModal';
import { apiClient } from './lib/api';
import {
  RiskAssessmentResponse,
  ReviewCaseResponse,
  HumanDecisionType,
  UserRole,
} from './types/api';

export function App() {
  const [currentRoute, setCurrentRoute] = useState<NavRoute>('overview');
  const [currency, setCurrency] = useState<'INR' | 'USD'>('INR');
  const [assessments, setAssessments] = useState<RiskAssessmentResponse[]>([]);
  const [reviews, setReviews] = useState<ReviewCaseResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Inspector & Modal states
  const [selectedAssessment, setSelectedAssessment] = useState<RiskAssessmentResponse | null>(null);
  const [selectedReviewCase, setSelectedReviewCase] = useState<ReviewCaseResponse | null>(null);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [assmts, revs] = await Promise.all([
        apiClient.listAssessments(),
        apiClient.listReviews(),
      ]);
      setAssessments(assmts);
      setReviews(revs);
    } catch (err) {
      console.error('Failed to load risk manager data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleOpenReviewModalByAssessmentId = (assessmentId: string) => {
    const caseItem = reviews.find((r) => r.assessment_id === assessmentId);
    if (caseItem) {
      setSelectedReviewCase(caseItem);
      setIsReviewModalOpen(true);
    }
  };

  const handleOpenReviewModalForCase = (caseItem: ReviewCaseResponse) => {
    setSelectedReviewCase(caseItem);
    setIsReviewModalOpen(true);
  };

  const handleSubmitDecision = async (caseId: string, decision: HumanDecisionType, reason: string) => {
    await apiClient.submitReviewDecision(caseId, {
      decision,
      reason,
      reviewer_id: 'ANALYST_PRIYA',
      reviewer_role: 'RISK_ANALYST' as UserRole,
    });
    await fetchData();
  };

  const pendingCount = reviews.filter((r) => r.status === 'PENDING_REVIEW').length;

  const routeTitles: Record<NavRoute, { title: string; subtitle: string }> = {
    overview: {
      title: 'Merchant Risk Overview',
      subtitle: 'Monitor return risk, review workload, and merchant exposure.',
    },
    'risk-monitor': {
      title: 'Risk Monitor',
      subtitle: 'Investigate return requests requiring attention.',
    },
    transactions: {
      title: 'Transactions Ledger',
      subtitle: 'Point-in-time transactions with customer pseudonym masks.',
    },
    reviews: {
      title: 'Human Review Queue',
      subtitle: 'Authorize, verify, or escalate flagged return requests.',
    },
    'risk-analysis': {
      title: 'Risk Factor Analysis',
      subtitle: 'Behavioral risk patterns, tender method exposure, and velocity signals.',
    },
    'model-performance': {
      title: 'Model Performance & Benchmark',
      subtitle: 'Evaluate detection quality on an untouched held-out test set.',
    },
    'audit-log': {
      title: 'Tamper-Evident Audit Ledger',
      subtitle: 'Cryptographically chained SHA-256 event trail recording every risk decision.',
    },
    reports: {
      title: 'Executive Reports',
      subtitle: 'Operational risk and review throughput reports.',
    },
    settings: {
      title: 'System Settings & Governance',
      subtitle: 'Model registry status, policy thresholds, and defense-only boundaries.',
    },
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-surface-50 font-sans antialiased text-surface-900">
      {/* Left Sidebar */}
      <Sidebar
        currentRoute={currentRoute}
        onRouteChange={setCurrentRoute}
        pendingReviewCount={pendingCount}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          title={routeTitles[currentRoute].title}
          subtitle={routeTitles[currentRoute].subtitle}
          currency={currency}
          onCurrencyChange={setCurrency}
          onRefresh={fetchData}
          isLoading={isLoading}
        />

        <main className="flex-1 overflow-y-auto">
          {currentRoute === 'overview' && (
            <Overview
              assessments={assessments}
              reviews={reviews}
              onSelectAssessment={setSelectedAssessment}
              onNavigateTo={setCurrentRoute}
              currency={currency}
              isLoading={isLoading}
            />
          )}

          {currentRoute === 'risk-monitor' && (
            <RiskMonitor
              assessments={assessments}
              onSelectAssessment={setSelectedAssessment}
              currency={currency}
              isLoading={isLoading}
            />
          )}

          {currentRoute === 'transactions' && (
            <Transactions
              assessments={assessments}
              onSelectAssessment={setSelectedAssessment}
              currency={currency}
              isLoading={isLoading}
            />
          )}

          {currentRoute === 'reviews' && (
            <Reviews
              reviews={reviews}
              onOpenReviewModal={handleOpenReviewModalForCase}
              currency={currency}
              isLoading={isLoading}
            />
          )}

          {currentRoute === 'risk-analysis' && (
            <RiskAnalysis assessments={assessments} currency={currency} />
          )}

          {currentRoute === 'model-performance' && (
            <ModelPerformance currency={currency} />
          )}

          {currentRoute === 'audit-log' && <AuditLog />}

          {currentRoute === 'reports' && (
            <Reports assessments={assessments} reviews={reviews} currency={currency} />
          )}

          {currentRoute === 'settings' && <Settings />}
        </main>
      </div>

      {/* Inspector Drawer */}
      <RiskDetailDrawer
        assessment={selectedAssessment}
        isOpen={selectedAssessment !== null}
        onClose={() => setSelectedAssessment(null)}
        onOpenReviewModal={handleOpenReviewModalByAssessmentId}
        currency={currency}
      />

      {/* Human Review Modal */}
      <ReviewModal
        reviewCase={selectedReviewCase}
        isOpen={isReviewModalOpen}
        onClose={() => {
          setIsReviewModalOpen(false);
          setSelectedReviewCase(null);
        }}
        onSubmitDecision={handleSubmitDecision}
        currency={currency}
      />
    </div>
  );
}

export default App;
