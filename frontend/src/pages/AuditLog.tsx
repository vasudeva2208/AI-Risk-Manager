import React, { useState, useEffect } from 'react';
import { History, ShieldCheck, AlertOctagon, RefreshCw, Key } from 'lucide-react';
import { AuditEventResponse, AuditChainVerificationResponse } from '../types/api';
import { apiClient } from '../lib/api';
import { formatDate } from '../lib/formatters';

export const AuditLog: React.FC = () => {
  const [events, setEvents] = useState<AuditEventResponse[]>([]);
  const [verification, setVerification] = useState<AuditChainVerificationResponse | null>(null);
  const [lastVerifiedAt, setLastVerifiedAt] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);

  const loadAuditData = async () => {
    setIsLoading(true);
    try {
      const [evts, ver] = await Promise.all([
        apiClient.listAuditEvents(100),
        apiClient.verifyAuditChain(),
      ]);
      setEvents(evts);
      setVerification(ver);
      setLastVerifiedAt(new Date().toISOString());
    } catch (err) {
      console.error('Failed to load audit trail:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAuditData();
  }, []);

  const handleVerifyChain = async () => {
    setIsVerifying(true);
    try {
      const ver = await apiClient.verifyAuditChain();
      setVerification(ver);
      setLastVerifiedAt(new Date().toISOString());
    } catch (err) {
      console.error(err);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-surface-900 flex items-center">
            <History className="w-5 h-5 mr-2 text-accent" />
            Tamper-Evident Audit Ledger
          </h2>
          <p className="text-xs text-surface-500 mt-0.5">
            Cryptographically chained SHA-256 event trail recording every model assessment, policy evaluation, and reviewer decision.
          </p>
        </div>

        <button
          onClick={handleVerifyChain}
          disabled={isVerifying}
          className="btn-primary text-xs flex items-center focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isVerifying ? 'animate-spin' : ''}`} />
          {isVerifying ? 'Verifying Hashes...' : 'Re-verify Hash Chain'}
        </button>
      </div>

      {/* Verification Status Card */}
      {verification && (
        <div
          className={`p-4 rounded border flex flex-col sm:flex-row sm:items-center justify-between font-mono text-xs gap-3 ${
            verification.status === 'VALID'
              ? 'bg-green-50 border-green-200 text-green-900'
              : 'bg-red-50 border-red-200 text-red-900'
          }`}
          role="status"
        >
          <div className="flex items-center space-x-3">
            {verification.status === 'VALID' ? (
              <ShieldCheck className="w-6 h-6 text-green-600 shrink-0" />
            ) : (
              <AlertOctagon className="w-6 h-6 text-red-600 shrink-0" />
            )}
            <div>
              <p className="font-bold">
                {verification.status === 'VALID'
                  ? 'Tamper-Evident Audit Chain Verified'
                  : 'Audit Integrity Failure Detected'}
              </p>
              <p className="text-[11px] opacity-90 font-sans mt-0.5">{verification.message}</p>
              {verification.corrupted_event_id && (
                <p className="text-[11px] font-bold text-red-700 mt-1">
                  Corrupted Event ID: {verification.corrupted_event_id}
                </p>
              )}
            </div>
          </div>
          <div className="flex sm:flex-col justify-between sm:text-right shrink-0 border-t sm:border-t-0 border-surface-200 pt-2 sm:pt-0">
            <div>
              <span className="text-[10px] block opacity-75">CHAIN STATUS</span>
              <span className="font-bold text-sm">{verification.status}</span>
            </div>
            {lastVerifiedAt && (
              <span className="text-[10px] text-surface-500 font-mono mt-1 block">
                Events checked: {verification.total_events_checked}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Events Table */}
      <div className="bg-white border border-surface-200 rounded shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-surface-500 font-mono text-xs">Loading audit ledger...</div>
        ) : events.length === 0 ? (
          <div className="p-8 text-center text-surface-400 font-mono text-xs">No audit events recorded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-surface-50 border-b border-surface-200 text-surface-600 text-[10px] uppercase">
                <tr>
                  <th className="py-3 px-4 font-semibold">Timestamp</th>
                  <th className="py-3 px-4 font-semibold">Event Type</th>
                  <th className="py-3 px-4 font-semibold">Assessment ID</th>
                  <th className="py-3 px-4 font-semibold">Actor</th>
                  <th className="py-3 px-4 font-semibold">Outcome / Decision</th>
                  <th className="py-3 px-4 font-semibold">Rationale</th>
                  <th className="py-3 px-4 font-semibold">SHA-256 Hash</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100">
                {events.map((evt) => (
                  <tr key={evt.audit_id} className="hover:bg-surface-50">
                    <td className="py-3 px-4 text-surface-500 text-[11px] whitespace-nowrap">
                      {formatDate(evt.timestamp)}
                    </td>
                    <td className="py-3 px-4 font-bold text-surface-900">{evt.event_type}</td>
                    <td className="py-3 px-4 text-accent font-semibold">{evt.assessment_id}</td>
                    <td className="py-3 px-4 text-surface-700">
                      {evt.actor_id} <span className="text-[10px] text-surface-400">({evt.actor_type})</span>
                    </td>
                    <td className="py-3 px-4 font-bold">{evt.decision}</td>
                    <td className="py-3 px-4 max-w-xs font-sans text-surface-600 truncate" title={evt.reason}>
                      {evt.reason}
                    </td>
                    <td className="py-3 px-4 text-[10px] text-surface-400 font-mono flex items-center space-x-1" title={evt.event_hash}>
                      <Key className="w-3 h-3 text-surface-400 shrink-0" />
                      <span>{evt.event_hash.substring(0, 12)}...</span>
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
