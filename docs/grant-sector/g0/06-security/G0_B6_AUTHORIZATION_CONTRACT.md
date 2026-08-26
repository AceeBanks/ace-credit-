# G0-B6-C5 — Authorization Decision Contract

## Purpose

Make policy evaluation deterministic and inspectable. Default = DENY.

## Decision order (13 steps)

```text
1.  principal valid/enabled?
2.  authenticated session valid?
3.  tenant membership/scope valid?
4.  capability registered/enabled?
5.  Book 1 authority ceiling sufficient?
6.  capability grant valid?
7.  resource scope valid?
8.  task scope valid?
9.  data classification permits action?
10. destination/egress policy permits action?
11. approval requirement satisfied?
12. explicit deny rules?
13. ALLOW
```

## Decisions

`ALLOW` / `DENY` / `REQUIRE_APPROVAL` with stable reason codes:
PRINCIPAL_UNKNOWN, PRINCIPAL_DISABLED, SESSION_INVALID, TENANT_DENIED,
CAPABILITY_UNKNOWN, CAPABILITY_DISABLED, AUTHORITY_INSUFFICIENT,
GRANT_MISSING, GRANT_EXPIRED, RESOURCE_DENIED, TASK_SCOPE_DENIED,
DATA_CLASS_DENIED, EGRESS_DENIED, APPROVAL_REQUIRED, EXPLICIT_DENY, ALLOW.

## Tests

100% fail-closed reason-code coverage — every code is reachable and tested
(`tests/g0/book6/test_authorization.py::test_every_reason_code_reachable`).

## Implementation

- `schemas/g0/security/authorization_request.schema.json`
- `prototype/g0/security/authorization.py` (`Authorizer`)
- `tools/g0/validate_authorization.py`
