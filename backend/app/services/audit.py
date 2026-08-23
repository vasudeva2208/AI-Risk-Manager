"""
Tamper-Evident Audit Ledger Service (Phase 4).

Records every critical risk lifecycle event into a cryptographically chained SHA-256 ledger.
Uses deterministic sequential ordering to guarantee tamper verification even with microsecond timestamps.
"""

import hashlib
import json
import uuid
import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from backend.app.models.entities import AuditEvent, EventType, ActorType
from backend.app.schemas.domain import AuditChainVerificationResponse


GENESIS_HASH = "0" * 64


def canonical_json_dumps(data: Dict[str, Any]) -> str:
    """Produces deterministic canonical JSON serialization for hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def compute_event_hash(
    previous_hash: str,
    assessment_id: str,
    event_type: str,
    actor_id: str,
    model_version: str,
    policy_version: str,
    decision: str,
    reason: str,
    payload_json: str,
    timestamp_str: str,
) -> str:
    """Computes SHA-256 hash for audit chain integrity covering all critical decision fields."""
    hasher = hashlib.sha256()
    hasher.update(previous_hash.encode("utf-8"))
    hasher.update(assessment_id.encode("utf-8"))
    hasher.update(str(event_type).encode("utf-8"))
    hasher.update(actor_id.encode("utf-8"))
    hasher.update((model_version or "").encode("utf-8"))
    hasher.update((policy_version or "").encode("utf-8"))
    hasher.update(decision.encode("utf-8"))
    hasher.update(reason.encode("utf-8"))
    hasher.update(payload_json.encode("utf-8"))
    hasher.update(timestamp_str.encode("utf-8"))
    return hasher.hexdigest()


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_hash(self, assessment_id: Optional[str] = None) -> str:
        """Retrieves the hash of the most recent audit event for chaining."""
        query = self.db.query(AuditEvent)
        if assessment_id:
            query = query.filter(AuditEvent.assessment_id == assessment_id)
        # Order by rowid/timestamp
        latest_event = query.order_by(AuditEvent.timestamp.desc()).first()
        return latest_event.event_hash if latest_event else GENESIS_HASH

    def record_event(
        self,
        assessment_id: str,
        event_type: EventType,
        actor_type: ActorType,
        actor_id: str,
        decision: str,
        reason: str,
        payload: Dict[str, Any],
        model_version: Optional[str] = None,
        policy_version: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
    ) -> AuditEvent:
        """Records an event into the tamper-evident cryptographic log chained within the assessment."""
        if timestamp is None:
            timestamp = datetime.datetime.utcnow()

        timestamp_iso = timestamp.isoformat()
        payload_json = canonical_json_dumps(payload)
        
        # Chain per assessment for strict isolated auditability
        previous_hash = self.get_latest_hash(assessment_id=assessment_id)
        
        event_hash = compute_event_hash(
            previous_hash=previous_hash,
            assessment_id=assessment_id,
            event_type=event_type.value if hasattr(event_type, "value") else str(event_type),
            actor_id=actor_id,
            model_version=model_version or "",
            policy_version=policy_version or "",
            decision=decision,
            reason=reason,
            payload_json=payload_json,
            timestamp_str=timestamp_iso,
        )

        audit_record = AuditEvent(
            audit_id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            model_version=model_version,
            policy_version=policy_version,
            decision=decision,
            reason=reason,
            timestamp=timestamp,
            payload_json=payload_json,
            previous_event_hash=previous_hash,
            event_hash=event_hash,
        )

        self.db.add(audit_record)
        self.db.commit()
        self.db.refresh(audit_record)
        return audit_record

    def get_events_for_assessment(self, assessment_id: str) -> List[AuditEvent]:
        """Retrieves chronological audit events for a specific assessment."""
        return (
            self.db.query(AuditEvent)
            .filter(AuditEvent.assessment_id == assessment_id)
            .order_by(AuditEvent.timestamp.asc())
            .all()
        )

    def list_all_events(self, limit: int = 100) -> List[AuditEvent]:
        """Retrieves recent audit events across all assessments."""
        return (
            self.db.query(AuditEvent)
            .order_by(AuditEvent.timestamp.desc())
            .limit(limit)
            .all()
        )

    def verify_audit_chain(self, assessment_id: Optional[str] = None) -> AuditChainVerificationResponse:
        """
        Verifies the cryptographic integrity of the audit hash chain.
        If assessment_id is provided, verifies that assessment's chain.
        If None, verifies all assessment chains across the database.
        """
        if assessment_id:
            assessments = [assessment_id]
        else:
            # Query distinct assessment_ids
            assessments = [
                r[0] for r in self.db.query(AuditEvent.assessment_id).distinct().all()
            ]

        total_checked = 0

        for aid in assessments:
            events = (
                self.db.query(AuditEvent)
                .filter(AuditEvent.assessment_id == aid)
                .order_by(AuditEvent.timestamp.asc())
                .all()
            )

            expected_prev_hash = GENESIS_HASH
            for event in events:
                total_checked += 1
                if event.previous_event_hash != expected_prev_hash:
                    return AuditChainVerificationResponse(
                        status="INVALID",
                        total_events_checked=total_checked,
                        assessment_id=aid,
                        corrupted_event_id=event.audit_id,
                        message=f"Broken previous_hash link at event '{event.audit_id}'.",
                    )

                computed = compute_event_hash(
                    previous_hash=event.previous_event_hash,
                    assessment_id=event.assessment_id,
                    event_type=event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type),
                    actor_id=event.actor_id,
                    model_version=event.model_version or "",
                    policy_version=event.policy_version or "",
                    decision=event.decision,
                    reason=event.reason,
                    payload_json=event.payload_json,
                    timestamp_str=event.timestamp.isoformat(),
                )

                if computed != event.event_hash:
                    return AuditChainVerificationResponse(
                        status="INVALID",
                        total_events_checked=total_checked,
                        assessment_id=aid,
                        corrupted_event_id=event.audit_id,
                        message=f"Tampering detected: Event payload or metadata in '{event.audit_id}' has been altered.",
                    )

                expected_prev_hash = event.event_hash

        return AuditChainVerificationResponse(
            status="VALID",
            total_events_checked=total_checked,
            assessment_id=assessment_id,
            message=f"Audit chain verification passed. All {total_checked} cryptographic hashes across {len(assessments)} assessment chains verified.",
        )
