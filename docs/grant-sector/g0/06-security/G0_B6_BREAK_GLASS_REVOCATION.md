# G0-B6-C21/C22 — Break-Glass & Revocation / Incident Recovery

## C21 — Break-Glass (BG-001..006)

Recovery exists **without** a hidden superuser.

- **BG-001** Explicit break-glass principal/flow only; no implicit
  invocation — a normal admin token can never act as break-glass.
- **BG-002** A reason is mandatory (≥8 chars, real).
- **BG-003** Every break-glass action generates an A4 elevated audit
  event; `authorize()` fails closed if the audit write is unavailable.
- **BG-004** Grants are short-lived and expire automatically.
- **BG-005** No silent use — all uses are visible in the security report.
- **BG-006** Cannot bypass immutable legal/client restrictions without a
  separate process.

Allowed purposes: tenant lockout recovery, security incident containment,
service restoration, corrupted authorization state repair.

## C22 — Revocation & Incident Recovery (REV-001..005)

Revocable objects: principal, membership, capability grant, service
identity, credential, tool version, integration, approval token,
model/provider route.

- **REV-001** Disabling a tool blocks all subsequent use.
- **REV-002** Credential compromise never requires resetting Hermes memory.
- **REV-003** A revoked worker grant stops the task safely (fail-closed on
  next authorization).
- **REV-004** Incident handling preserves decision/audit evidence;
  `PRESERVE_EVIDENCE` and `ASSESS_AFFECTED_TENANTS_RESOURCES` precede any
  repair in the canonical sequence:
  `DETECT → CONTAIN → REVOKE → PRESERVE_EVIDENCE → ASSESS → ROTATE/REPAIR → REVALIDATE → RESTORE → POSTMORTEM`
- **REV-005** Revocation takes effect within a defined bound (60s);
  cached allows cannot outlive the bound.

## Verified

- Validator: `python tools/g0/validate_lifecycle_security.py`
- Tests: `tests/g0/book6/test_lifecycle_security.py` (C21/C22 sections)
- Config: `config/g0/security/lifecycle_policy.yaml`
