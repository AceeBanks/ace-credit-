# G0-B6-C27 — Integration & Property Tests

## Mandatory invariants (all proven)

1. Authentication never implies authorization.
2. Unknown capability defaults deny.
3. Missing tenant defaults deny.
4. Workers never inherit broad parent authority.
5. Every credential use is server-side and scoped.
6. Agent prompts/memory/logs contain no raw secrets.
7. Tool execution maps to registered capability.
8. External side effects require separate capability.
9. MCP cannot bypass policy.
10. Direct DB access is unavailable to agents.
11. Egress destination validated independently of model output.
12. Prompt injection cannot create authority.
13. Tenant isolation covers DB, graph, vector, artifacts and audit.
14. Approval tokens are resource/version bound.
15. Submission remains disabled.
16. Third-party workflow executor is non-authoritative.
17. Revocation takes effect within defined bound.
18. Security audit redacts secrets.
19. Break-glass is explicit, temporary and audited.
20. Security-control outage fails closed.

## Property tests

- **Determinism** — authorization yields the same decision/reason for the
  same inputs and policy version.
- **Narrow delegation** — a delegated worker grant cannot exceed the parent
  ceiling.
- **Tenant-scope intersection** — membership in two tenants cannot expand
  privilege into cross-tenant reads.
- **Rotation** — credential rotation preserves capability semantics.
- **Registry rebuild** — tool registry rebuild preserves capability
  mapping.
- **Monotonic revocation** — revocations never un-revoke without explicit
  reissue.

## Verified

- Tests: `tests/g0/book6/test_security_integration_properties.py`
  (renamed from `test_integration_properties.py` to avoid a pytest
  basename collision with Book 5's integration suite)