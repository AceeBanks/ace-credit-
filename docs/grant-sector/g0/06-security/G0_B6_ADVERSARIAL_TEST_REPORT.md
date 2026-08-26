# G0-B6 — Adversarial Test Report

## Scope

The plan (C26) requires at least 50 adversarial scenarios plus a mandatory
set of P0 cross-tenant, secret-exposure and authority attacks. All are
implemented in `test_adversarial_security.py` and pass.

## Result

`python -m pytest tests/g0/book6/test_adversarial_security.py -q`
→ **50 passed**.
`tests/g0/book6/test_adversarial_security.py` +
`test_security_integration_properties.py` + `test_security_performance.py`
→ **81 passed** (the P0 suite the Reality Lock builder runs).

## P0 evidence

Every required P0 category carries explicit PASS evidence:

| P0 category | Scenarios proving it |
|---|---|
| Cross-tenant access | S4 (sibling project), S5 (guessed artifact id), S11 (OAuth wrong tenant) |
| Cross-project access | S4 |
| Personal Hermes → CEO capability | S1 |
| CEO → forbidden capability | S2, S32 |
| Worker exceeding task contract | S3, S45 |
| Capability escalation | S3, S23 |
| Fake capability ids | S36 |
| Unauthorized MCP / dynamic tool | S21 |
| Credential request from agent context | S8, S33 |
| Secret leakage | S29, S30, S33, S46 |
| Malicious PDF/web instructions | S8, S9, S10 |
| Prompt injection | S8, S9, S10, S12, S34 |
| Egress outside allowlist / SSRF | S14, S15, S16, S13 |
| Direct submission attempt | S50 |
| Approval bypass | S24, S25 |
| Stale/revoked approval | S24 |
| Replay / duplicate side effect | S41, S42 |
| Quota / rate-limit bypass | S48 |
| L5 feature-flag enable | S50 |

All **19 required P0 sub-scenarios** from the mission specification for
Book 6 are covered and pass.

## Real gaps surfaced and fixed by this suite

1. **L5 submission was a hard-coded `False` stub** in
   `ApprovalRegistry.l5_submission_stays_disabled()`. It is now **derived
   from policy** (`approval_audit_policy.submission_phase == DISABLED`) and
   proven un-flippable by any approval token or feature flag.
2. **Gateway failed to fail closed on a missing `authorization_decision`**
   — it raised an attribute error instead of a clean denial. Now any
   `None` decision is a hard TOOL-006 deny.

## New guards added

- `ToolGateway._assert_not_replayed` / **TOOL-012** (idempotent external
  side effects — replay/nonce).
- `QuotaEnforcer` / **QTA-001** (principal-bucket rate limits).
- Gateway fails closed on missing decision.