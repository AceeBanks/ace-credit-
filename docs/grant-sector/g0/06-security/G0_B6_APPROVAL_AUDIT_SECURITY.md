# G0-B6-C18/C19 — Approval Enforcement & Audit Security

## C18 — Approval enforcement (APPR-001..006)

Approvals are durable, scoped evidence — never vibes.

- **APPR-001** An approval binds to a specific action/resource/version via
  `request_hash`; it never applies to "anything related to this application
  forever."
- **APPR-002** An old approval cannot authorize a changed document version
  (hash mismatch → denied).
- **APPR-003** An approval from the wrong tenant is denied.
- **APPR-004** A revoked approval is denied.
- **APPR-005** A chat phrase like "looks good" does not become an approval
  unless captured through an approved UX/action. Approval is durable
  evidence (SEC-LAW-013).
- **APPR-006** Generating a draft needs no pre-approval; accepting
  protected canonical changes requires approval per policy; **L5
  submission stays disabled regardless of approval tokens** (mission law
  20).

## C19 — Audit security (AUD-001..005)

- **AUD-001** Denied actions are logged where policy requires.
- **AUD-002** Secret values are absent from audit records; only references
  are recorded.
- **AUD-003** Audit events link to the AuthorizationDecision and
  DecisionRecord where applicable.
- **AUD-004** Audit access is tenant-filtered.
- **AUD-005** Audit storage is append-oriented with an integrity hash
  chain; mutation is restricted; retention class is recorded.

## Verified

- Validator: `python tools/g0/validate_hostile_approval_audit.py`
- Tests: `tests/g0/book6/test_hostile_approval_audit.py` (C18/C19 section)
- Config: `config/g0/security/approval_audit_policy.yaml`
