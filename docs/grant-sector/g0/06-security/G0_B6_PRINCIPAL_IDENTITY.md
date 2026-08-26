# G0-B6-C2 — Principal & Identity Model

## Purpose

Define authenticated identity for humans, Hermes agents, workers and
services. Model/provider/session IDs never equal principal identity.

## Principal types

HUMAN_USER, HUMAN_ADMIN, HERMES_PERSONAL, HERMES_CEO, WORKER_AGENT,
DETERMINISTIC_SERVICE, SOURCE_ADAPTER, POLICY_SERVICE, TOOL_GATEWAY,
INTEGRATION_SERVICE, SYSTEM_JOB.

## Rules (IDN-001..005)

1. Principal identity is logical and stable: replacing the model/provider
   behind a Hermes role does not create a new principal.
2. Disabled/deactivated principals cannot authorize.
3. Duplicate principal ids are rejected.
4. Worker instance identity binds to its parent task and carries no
   inherited authority.
5. Human principals store the least personal data required.

## Implementation

- `config/g0/security/principal_policy.yaml`
- `schemas/g0/security/principal.schema.json`
- `prototype/g0/security/models.py`, `prototype/g0/security/identity.py`
  (`PrincipalRegistry`)
- `tools/g0/validate_identity_isolation.py`
- `tests/g0/book6/test_identity_isolation.py`

## Tenant & resource scope (C3)

Tenant is the primary isolation boundary. Product roles OWNER/ADMIN/MEMBER/
REVIEWER/READ_ONLY (not Book 1 authority levels). Resource hierarchy:
Tenant → Organization → ApplicationProject → Task/Artifact/Evidence/Audit.
`ScopeEvaluator` enforces: no cross-tenant reads by guessed ID, public
sources reusable while private annotations stay tenant-bound, project-scoped
workers cannot cross projects, and membership expiry is enforced.
