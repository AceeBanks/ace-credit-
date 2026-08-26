# G0 Book 3 — Reality Lock Report

**Lock file:** `docs/grant-sector/g0/00-ratification/G0_B3_REALITY_LOCK.json`
**Builder:** `tools/g0/build_book3_reality_lock.py`
**Status:** **PASS** — `ready_for_d0: true`, `ready_for_book4: true`

## How the lock is computed (never hand-written)

The builder loads all 19 source-policy configs, runs every chapter validator
against the live configs, runs the real Book 3 pytest suite, and reads the
shared contradiction ledger. Readiness is a conjunction:

- `data_constitution_complete` — all 20 DATA-LAW entries validate;
- `enabled_sources_registered == 1.0` — every ENABLED source is governed
  (adapter version + terms/robots/rate-limit/health policy refs);
- `critical_facts_with_snapshot_lineage == 1.0` — all 7 critical fact classes
  have a fact-specific precedence chain in the matrix;
- 19 chapter predicates (`snapshot_immutability_tests_pass` …
  `private_source_fixture_tests_pass`) — each from a live validator run;
- `d0_data_packet_ready` and `d0_shadow_draft_allowed` — D0 packet + harness
  spec validate, adversarial suite green, zero open P0s;
- `adversarial_p0_pass` — real pytest exit code 0 with zero failures (a
  not-run suite reports `null` and blocks readiness);
- `p0_open == 0` — from the shared contradiction ledger.

## Evidence snapshot (BOOK time)

```json
"status": "PASS",
"ready_for_d0": true,
"ready_for_book4": true,
"adversarial_p0_pass": true,
"p0_open": 0,
"evidence": {
  "test_results": { "exit_code": 0, "passed": 242, "failed": 0,
    "scope": "tests/g0/book3 excluding G0_B3_REALITY_LOCK.json freshness self-test" },
  "config_count": 19,
  "enabled_source_count": 8,
  "critical_fact_class_count": 7
}
```

## Stale-lock defense

`tests/g0/book3/test_book3_reality_lock.py::test_committed_lock_matches_regeneration`
recomputes the lock from live repository evidence and asserts byte-equality
(modulo the pytest summary line) with the committed JSON. Editing the lock by
hand, or letting the repository drift, turns the freshness test red. Defect
injection tests prove each predicate independently flips readiness to FAIL.

## Reproduction

```bash
python tools/g0/build_book3_reality_lock.py \
  --out docs/grant-sector/g0/00-ratification/G0_B3_REALITY_LOCK.json
```

Exit code 0 ⇔ PASS. Regeneration is deterministic given repository state.
