# G0-B6-C4 — RBAC + ABAC + Capability Grant Model

## Purpose

Layered authorization instead of one simplistic role table: RBAC role
defaults for humans, ABAC context attributes (tenant, project, resource
ownership, authority level, task assignment, data classification, phase,
time/expiry, approval state, destination risk), and explicit capability
grants.

## CapabilityGrant

```yaml
grant_id: principal_id: capability_id: tenant_id: project_id:
resource_constraints: authority_level: valid_from: expires_at:
approval_ref: issued_by: status:
```

## Rules (GRANT-001..006)

1. Only ACTIVE grants within `valid_from..expires_at` count; expired or
   revoked grants deny (SEC-LAW-010).
2. Worker grants must be narrower than/equal to the parent's delegable
   authority; exceeding the ceiling is rejected.
3. CEO may delegate only capabilities explicitly marked delegable.
4. Broad roles never bypass narrow resource scope; grant constraints always
   apply.
5. Phase-disabled capabilities (submission.execute, application.submit)
   cannot be enabled through a grant alone.
6. A grant revoked mid-task blocks the next protected action immediately.

## Implementation

- `config/g0/security/capability_grant_policy.yaml` (delegable /
  non-delegable / phase-disabled lists)
- `schemas/g0/security/capability_grant.schema.json`
- `prototype/g0/security/authorization.py` (`GrantRegistry`)
- `tools/g0/validate_authorization.py`
- `tests/g0/book6/test_authorization.py`
