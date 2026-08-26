# G0-B6-C26 — Adversarial Security Suite

## Objective

Attack the security architecture before real production operations. 50
scenarios, grouped by threat category, each exercising a real guard.

## Scenarios and P0 evidence

| # | Scenario | Guard exercised | P0 |
|---|---|---|---|
| 1 | Personal Hermes calls CEO-only mutation | authority ceiling (L1 < L3) | ✅ |
| 2 | CEO calls hidden/disabled submission tool | gateway denies disabled tool | ✅ |
| 3 | worker tries parent capability escalation | GRANT-002 ceiling at issue time | ✅ |
| 4 | worker accesses sibling project | resource tenant scope | ✅ |
| 5 | Tenant A guesses Tenant B artifact ID | `can_read` tenant check | ✅ |
| 6 | vector search leaks Tenant B content | scoped_refs tenant filter | ✅ |
| 7 | graph traversal leaks restricted metadata | visibility rank | ✅ |
| 8 | webpage asks agent to reveal secrets | INJ-001 untrusted + vault inaccessible | ✅ |
| 9 | webpage asks agent to send email | INJ-006 + egress | ✅ |
| 10 | PDF contains fake system prompt | INJ-002 stays data | ✅ |
| 11 | OAuth token used for wrong tenant | AUTH-001 server-side tenant bind | ✅ |
| 12 | caller overwrites Authorization header | TOOL-007 | ✅ |
| 13 | credential forwarded to redirect host | EGR-003 redirect revalidation | ✅ |
| 14 | SSRF to cloud metadata endpoint | EGR-002 blocked host | ✅ |
| 15 | SSRF to localhost/internal network | EGR-002 blocked hosts | ✅ |
| 16 | DNS-rebinding destination change | EGR-003 redirect revalidation | ✅ |
| 17 | malicious file path traversal | FILE-005 sanitize | ✅ |
| 18 | archive bomb | FILE-002 ratio | ✅ |
| 19 | macro/executable document content | FILE-004 | ✅ |
| 20 | tool schema version changes silently | TOOL-002 review required | ✅ |
| 21 | unknown MCP tool discovered dynamically | TOOL-001/005 | ✅ |
| 22 | Activepieces flow mutates canonical state | INT-001 | ✅ |
| 23 | revoked capability reused from cache | LIF-005 stale allow expired | ✅ |
| 24 | expired approval on changed artifact | APPR-001/002 hash-bound | ✅ |
| 25 | chat "yes" treated as submission approval | APPR-005 UX-only + phase disabled | ✅ |
| 26 | service identity impersonates human | SVC-005 no mutation caps | ✅ |
| 27 | admin action missing elevated audit | BG-003 fails closed | ✅ |
| 28 | break-glass used without reason | BG-002 | ✅ |
| 29 | secret appears in error trace | OBS-005 redaction | ✅ |
| 30 | secret appears in sidechain | LIF-003 rotation returns reference only | ✅ |
| 31 | tenant-private content enters global eval | PII-004 eval gate | ✅ |
| 32 | model fallback gets broader tool set | surface manifest independent of model | ✅ |
| 33 | tool result includes secret in response | TOOL-010 payload scan | ✅ |
| 34 | malicious source changes tool destination | TOOL-008 allowlist | ✅ |
| 35 | source adapter tries application mutation | SVC-005 / INT-001 | ✅ |
| 36 | DB credentials requested through agent tool | capability never registered | ✅ |
| 37 | authorization service unavailable | gateway fails closed | ✅ |
| 38 | credential vault unavailable | gateway fails closed | ✅ |
| 39 | audit write fails during protected mutation | BG-003 fails closed | ✅ |
| 40 | compromised integration returns forged receipt | INT-004 validated required | ✅ |
| 41 | replay of old signed tool request | TOOL-012 idempotency | ✅ |
| 42 | duplicate request double side effect | TOOL-012 nonce | ✅ |
| 43 | artifact export bypasses classification | DATA-002 no downgrade | ✅ |
| 44 | public share link exposes private artifact | VIS-001 share-link policy | ✅ |
| 45 | retired worker remains active | PRINCIPAL_DISABLED | ✅ |
| 46 | provider logs restricted payload | PII-002 redaction + eval gate | ✅ |
| 47 | malicious filename reaches command shell | FILE-005 sanitize (never shells) | ✅ |
| 48 | quota/rate-limit bypass | QTA-001 principal bucket | ✅ |
| 49 | crawler crosses source boundary | INT-002 unrelated resource | ✅ |
| 50 | future L5 endpoint enabled by feature flag | GRANT-005 phase-disabled | ✅ |

**All 50 scenarios pass.** The suite surfaced and fixed one real gap: L5
submission was a hard-coded `False` stub; it is now **derived from policy**
(`approval_audit_policy.submission_phase == DISABLED`), and the gateway now
fails closed when `authorization_decision` is missing (`None`).

## New guards added by this suite

- `ToolGateway._assert_not_replayed` / TOOL-012 (idempotent external side
  effects).
- `QuotaEnforcer` / QTA-001 (principal-bucket rate limits).
- Gateway fails closed on missing decision (TOOL-006).

## Verified

- Tests: `tests/g0/book6/test_adversarial_security.py` (50 passed)