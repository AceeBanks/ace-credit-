# G0-B6-C3 — Tenant, Organization Membership & Resource Scope

## Purpose

Define commercial multi-tenant boundaries. A tenant is the primary
isolation boundary for client-owned data/resources; Tenant == Organization
is NOT assumed (one tenant may manage multiple organizations/programs).

## Membership

```yaml
membership_id: tenant_id: principal_id: role_ids: status:
valid_from: valid_to:
```

Initial product roles: OWNER, ADMIN, MEMBER, REVIEWER, READ_ONLY — product
roles, not Book 1 authority levels.

## Resource scope hierarchy

```text
Tenant
 └── Organization(s)
      └── ApplicationProject(s)
           ├── Task(s)
           ├── Artifact(s)
           ├── Evidence
           └── Audit/Decision records
```

## Enforcement (`ScopeEvaluator`)

- Tenant A member cannot read Tenant B artifact by guessed ID;
- shared public sources remain reusable while tenant-private annotations
  stay isolated;
- a worker assigned Project A cannot access Project B by default;
- membership expiry (valid_to) is enforced at evaluation time.

## Implementation

- `config/g0/security/principal_policy.yaml` (membership roles/statuses,
  scope hierarchy)
- `schemas/g0/security/tenant_membership.schema.json`
- `prototype/g0/security/identity.py` (`ScopeEvaluator`)
- `tests/g0/book6/test_identity_isolation.py`
