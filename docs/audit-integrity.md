# Tamper-Evident SHA-256 Chained Audit Trail

---

## 1. Cryptographic Hash-Chaining Architecture

Every security-critical event in the return risk lifecycle is sealed into a tamper-evident hash chain.

$$\text{Current Hash } H_n = \text{SHA256}\left( H_{n-1} + \text{CanonicalSerialization}(\text{Event}_n) \right)$$

### Canonical Serialization String:
$$H_n = \text{SHA256}(H_{n-1} \parallel \text{assessment\_id} \parallel \text{event\_type} \parallel \text{actor\_id} \parallel \text{model\_version} \parallel \text{policy\_version} \parallel \text{decision} \parallel \text{reason} \parallel \text{payload\_json} \parallel \text{timestamp})$$

* **Genesis Event:** Initial event has $H_0 = \text{"GENESIS\_HASH\_00000000000000000000000000000000"}$.
* **Deterministic UTF-8 Encoding:** All fields are encoded in standard UTF-8 with canonical JSON dictionary key ordering.

---

## 2. Event Taxonomy

1. `RISK_ASSESSMENT_CREATED` — Generated upon initial risk scoring.
2. `MODEL_RECOMMENDATION_CREATED` — Generated when model probability is calculated.
3. `POLICY_EVALUATED` — Generated when bounded policy assigns action.
4. `REVIEW_STARTED` — Generated when analyst opens triage case.
5. `REVIEW_DECISION_MADE` — Generated when authorized analyst submits decision.
6. `AUDIT_RECORD_CREATED` — Internal chain sealing event.

---

## 3. Verification API (`GET /api/v1/audit/verify`)

Iterates through all chronological audit chains and recomputes the expected hash for every event.

### Response `200 OK` (Valid):
```json
{
  "status": "VALID",
  "total_events_checked": 97,
  "assessment_id": null,
  "corrupted_event_id": null,
  "message": "Audit chain verification passed. All 97 cryptographic hashes across 40 assessment chains verified."
}
```

### Response `200 OK` (Tampered):
```json
{
  "status": "INVALID",
  "total_events_checked": 97,
  "assessment_id": "ASSMT_A1B2C3D4",
  "corrupted_event_id": "AUD_EVT_102",
  "message": "Audit chain integrity failed at event AUD_EVT_102: computed hash does not match stored hash."
}
```
