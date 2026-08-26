# G0-B6-C6/C7 — Authentication, Sessions & Service Identity

## Authentication strategy (C6)

Human auth minimums: secure session/token model, MFA-ready for privileged
roles, account recovery, session revocation, invitation/membership
acceptance, audit of privileged logins.

Session properties: short-lived access, refresh/re-auth policy, tenant
context bound server-side (client parameter tampering is ineffective,
AUTH-001), principal status checked each use, privilege elevation requires
full re-evaluation (AUTH-005).

## Rules (AUTH-001..005)

1. Tenant context is server-bound; client params cannot change it.
2. Revoked sessions are blocked immediately, including refresh.
3. Expired service tokens are blocked; rotation needs no prompt changes.
4. Service tokens authenticate services; they never impersonate human
   approval.
5. Privilege elevation re-evaluates the full authorization chain.

## Service identity (C7)

Six service identities (svc-source-grants-gov, svc-source-georgia-opb,
svc-evidence, svc-eligibility, svc-tool-gateway, svc-worker-runtime), each
with a minimum capability set (SVC-001), no shared omnipotent secret,
identity in audit, independent revocation (SVC-003), and source adapters
cannot call application-mutation capabilities (SVC-005).

## Implementation

- `config/g0/security/authn_session_policy.yaml`,
  `config/g0/security/service_identity_policy.yaml`
- `prototype/g0/security/authn.py` (`SessionManager`,
  `ServiceIdentityRegistry`)
- `tools/g0/validate_authn_credentials.py`
- `tests/g0/book6/test_authn_credentials.py`
