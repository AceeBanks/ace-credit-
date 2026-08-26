# G0 Book 0 — Internal Adversarial Review Record

**Scope:** full Book 0 ratification package (C1–C6), reviewed as an attacker
before the `G0-B0-BOOK` checkpoint. This review is NOT external ratification.

## Attack probes and results

| # | Attack | Result | Disposition |
|---|--------|--------|-------------|
| 1 | **Stale-lock attack** — hand-edit `G0_B0_REALITY_LOCK.json` to PASS; nothing previously proved the committed file matches honest regeneration | DEFECT — closed by REPAIR-01: freshness test regenerates the lock from live registers + live test run and requires exact equality (duration string normalized) with the committed artifact | FIXED |
| 2 | **Commit-message drift** — `G0-B0-C2` message says "38 decisions"; actual register holds 43 | Cosmetic history defect; branch is unpushed but history rewrite after checkpoint commits is forbidden by push discipline, so it stands corrected here and in this ledger. Machine-readable count (`decision_count: 43`) in the Reality Lock is authoritative | RECORDED |
| 3 | **Stray artifacts** — `__pycache__`, `.pyc`, temp files committed | CLEAN — `git ls-files` verified | none |
| 4 | **Hardcoded PASS** — grep for literal readiness assertions in validators/lock builder | CLEAN — every predicate is computed from validator reports or test exit codes; `test_tests_not_run_blocks_readiness` proves null blocks readiness | none |
| 5 | **Count drift** — docs claim counts that differ from registers | One defect found and fixed pre-C6-commit (per-suite test counts corrected in the test report). Freshness test now also pins total counts via lock equality | FIXED |
| 6 | **Unresolved P0** — ledger re-derived at lock build time | CLEAN — `p0_open == 0` derived from live ledger, not asserted | none |
| 7 | **Adopted-at-Book-0 candidate smuggling** | CLEAN — validator rejects `adopted_with_evidence` status at Book 0; adversarial test covers it | none |

## Repairs

- **G0-B0-REPAIR-01** — freshness equality test between committed
  `G0_B0_REALITY_LOCK.json` and live regeneration
  (`tests/g0/book0/test_reality_lock.py::test_committed_lock_matches_regeneration`,
  backed by `build_live_lock()`).

## Standing limitation (accepted, non-P0)

`G0_B0_REALITY_LOCK.json` must be regenerated whenever Book 0 tests are added;
the freshness test enforces this loudly rather than silently.
