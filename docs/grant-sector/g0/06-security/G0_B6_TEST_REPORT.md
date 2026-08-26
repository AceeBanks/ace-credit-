# G0-B6 — Test Report

## Full suite

`python -m pytest tests/g0 -q` → **1388 passed, 3 skipped**.

## Per-book exclusive counts

| Book | Tests collected | Notes |
|---|---|---|
| Book 0 | 51 | |
| Book 1 | 133 | |
| Book 2 | 255 | |
| Book 3 | 243 | |
| Book 4 | 276 | C1-C28 + Reality Lock noexcept freshness |
| Book 5 | 231 | C1-C25 + Reality Lock freshness |
| Book 6 | 202 | C1-C28 + Reality Lock freshness |
| **Full** | **1391** | 1388 passed + 3 skipped |

## Book 6 suite breakdown

| Area | File | Tests |
|---|---|---|
| Security constitution | `test_security_constitution.py` | 3 |
| Identity / tenant / resource isolation | `test_identity_isolation.py` | 9 |
| Capability grants + authorization | `test_authorization.py` | 21 |
| Authn / sessions / credentials | `test_authn_credentials.py` | 13 |
| Tool registry + gateway + MCP | `test_tool_gateway.py` | 50 |
| Integration / egress / classification | `test_boundaries.py` | 16 |
| Prompt injection / files / approval / audit | `test_hostile_approval_audit.py` | 20 |
| Lifecycle / break-glass / revocation / obs / threat | `test_lifecycle_security.py` | 22 |
| Adversarial security (50 scenarios) | `test_adversarial_security.py` | 50 |
| Integration & property invariants | `test_security_integration_properties.py` | 26 |
| Security performance envelope | `test_security_performance.py` | 5 |
| Reality Lock freshness + defect injection | `test_book6_reality_lock.py` | 13 |
| **Total** | | **248 collected** (202 exclusive + 46 shared/lock) |

The 202-exclusive book6 count is what the Reality Lock builder records
(199 passed + 3 skipped under the freshness recursion guard).

## Validators (all exit 0)

- `python tools/g0/validate_security_constitution.py`
- `python tools/g0/validate_identity_isolation.py`
- `python tools/g0/validate_authorization.py`
- `python tools/g0/validate_authn_credentials.py`
- `python tools/g0/validate_tool_gateway.py`
- `python tools/g0/validate_boundaries.py`
- `python tools/g0/validate_hostile_approval_audit.py`
- `python tools/g0/validate_lifecycle_security.py`
- `python tools/g0/validate_attack_surface.py`
- `python tools/g0/validate_security_performance.py`