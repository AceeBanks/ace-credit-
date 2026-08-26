# G0 Book 3 — Test Report

**Test command:** `python -m pytest tests/g0 -q`
**Result:** **682 passed, 0 failed** (full suite)
**Book 3 suite:** **243 passed** across 20 files (`python -m pytest tests/g0/book3 -q`)

## Full-suite breakdown

| Suite | Tests |
|---|---|
| Book 0 (`tests/g0/book0`) | 51 |
| Book 1 (`tests/g0/book1`) | 133 |
| Book 2 (`tests/g0/book2`) | 255 |
| Book 3 (`tests/g0/book3`) | 243 |
| **Total (`tests/g0`)** | **682** |

## Book 3 coverage by chapter

| File | Tests | Chapters |
|---|---|---|
| `test_data_constitution.py` | 8 | C1 — Data Constitution |
| `test_source_registry.py` | 11 | C2-C3 — Source classification + SourceRegistry |
| `test_onboarding_snapshot.py` | 16 | C4-C5 — Onboarding + immutable SourceSnapshot |
| `test_capture_extraction.py` | 15 | C6-C7 — Capture/replay + extraction/normalization |
| `test_precedence_freshness.py` | 12 | C8-C9 — Precedence + freshness |
| `test_promotion_conflict.py` | 18 | C10-C12 — Promotion + conflict + source change |
| `test_dependency_identifier.py` | 12 | C13-C14 — Dependency invalidation + identifier verification |
| `test_statistics.py` | 12 | C15 — StatisticObservation policy |
| `test_federal_fixtures.py` | 7 | C16 — Federal source profiles |
| `test_georgia_fixtures.py` | 9 | C17 — Georgia source profiles |
| `test_private_sources.py` | 9 | C18 — Private/foundation sources |
| `test_source_security.py` | 9 | C19 — Hostile-source security |
| `test_retention.py` | 11 | C20 — Retention/deletion classes |
| `test_provenance.py` | 8 | C21 — Provenance chain |
| `test_source_health.py` | 7 | C22 — Source health |
| `test_d0_packet.py` | 10 | C23 — D0 data packet |
| `test_d0_harness.py` | 5 | C24 — D0 harness specification |
| `test_adversarial_data.py` | 26 | C25 — Adversarial suite A1-A25 (+ validator) |
| `test_integration_property.py` | 28 | C26 — 22 invariants + 6 property tests |
| `test_book3_reality_lock.py` | 10 | C27 — Reality Lock derivation + freshness |
| **Total** | **243** | |

## Validator CLIs (all PASS at BOOK time)

```bash
python tools/g0/validate_data_constitution.py
python tools/g0/validate_source_registry.py
python tools/g0/validate_onboarding_snapshot.py
python tools/g0/validate_capture_extraction.py
python tools/g0/validate_precedence_freshness.py
python tools/g0/validate_promotion_conflict.py
python tools/g0/validate_dependency_identifier.py
python tools/g0/validate_statistics.py
python tools/g0/validate_source_profiles.py
python tools/g0/validate_private_source_security.py
python tools/g0/validate_retention_provenance.py
python tools/g0/validate_health_d0.py
python tools/g0/validate_adversarial.py
```

## Notes

- Book 3 tests are fail-closed: injected defects flip assertions to red; there
  is no happy-path-only coverage.
- The Reality Lock's inner derivation run records **242 passed + 1 skipped**
  (the lock-freshness self-test excludes itself via `G0_SKIP_LOCK_FRESHNESS=1`
  to avoid recursion).
- All counts are from real runs (`python -m pytest`), never hand-written.
