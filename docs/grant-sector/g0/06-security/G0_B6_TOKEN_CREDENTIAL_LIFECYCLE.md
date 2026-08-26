# G0-B6-C20 — Session, Token & Credential Lifecycle

## Objective

Prevent zombie authorization. Nothing that was once valid stays valid by
default.

## Lifecycle states

```text
ISSUED → ACTIVE → EXPIRING → EXPIRED
   └──────────→ REVOKED
   └──────────→ ROTATED
   └──────────→ COMPROMISED
```

## Rules (LIF-001..007)

- **LIF-001** Session/service tokens are short-lived (≤1h, default 5m);
  refresh requires a valid principal.
- **LIF-002** Capability grants are independently expirable from sessions.
- **LIF-003** Credential rotation is transparent to agents; old and new
  secrets never enter agent context (`rotate_credential` returns a
  reference, never material).
- **LIF-004** Compromise of a credential triggers dependent revocation of
  tokens bound to it.
- **LIF-005** Cached authorization decisions have a bounded TTL and are
  invalidated on revocation.
- **LIF-006** Revoked membership invalidates new decisions immediately.
- **LIF-007** A compromised credential is blocked even while technically
  valid.

## Verified

- Validator: `python tools/g0/validate_lifecycle_security.py`
- Tests: `tests/g0/book6/test_lifecycle_security.py` (C20 section)
- Config: `config/g0/security/lifecycle_policy.yaml`
