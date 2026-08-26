# G0-B6-C28 — Security Performance / Usability Envelope

## Objective

Ensure the security architecture does not make grant production unusably
slow while refusing to weaken controls.

## Measured baseline (prototype latencies, ms)

| Control | Latency |
|---|---|
| authorization_decision | 1.2 |
| gateway_overhead | 0.8 |
| credential_resolution | 2.5 |
| audit_write | 0.6 |
| approval_workflow | 45.0 |
| source_browser_policy | 3.1 |
| worker_delegation | 1.0 |

## Envelope rules

- **PERF-001** No control is skipped to meet latency; a slower safe path
  is always preferred to a fast unsafe one.
- **PERF-002** Authorization caching permitted only within the revocation
  invalidation bound.
- **PERF-003** Gateway overhead stays a single digit of total latency.
- **PERF-004** Credential resolution is server-side only, never optimized
  by the model.

## Caching policy

- Authorization decision cache: enabled, 60s bound (matches lifecycle
  REV-005).
- Gateway setup cache: enabled (tool definitions immutable per version).
- Credential resolution cache: **disabled** — resolved fresh each use to
  honor capability/destination scope.

## Verified

- Tests: `tests/g0/book6/test_security_performance.py`
- Config: `config/g0/security/security_performance.yaml`