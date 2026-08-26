# G0 Book 4 — Reality Lock Report

**Lock file:** `docs/grant-sector/g0/00-ratification/G0_B4_REALITY_LOCK.json`
**Builder:** `tools/g0/build_book4_reality_lock.py`
**Status:** **PASS** — `ready_for_book5: true`

## How the lock is computed (never hand-written)

The builder loads all 16 agent-policy configs, runs every chapter validator
against the live configs, runs the real Book 4 pytest suite plus a dedicated
C26 adversarial suite run, and reads the shared contradiction ledger.
Readiness is a conjunction:

- `dual_hermes_boundary_ratified` — Personal/CEO/Worker separation, capability
  partitioning, deny-by-default (C1 validator);
- `personal_contract_complete` / `ceo_contract_complete` — role contracts with
  no canonical mutation, no silent CEO/personal role takeover (C2-C3);
- `intent_contract_tests_pass` / `clarification_protocol_pass` — schemas +
  policy validate; assertions stay ASSERTION; avoidable clarifications detected (C4-C5);
- `task_contract_tests_pass` — worker context policy: never-inject classes,
  bounded refs, L2-only authority (C6-C7);
- `sidechain_isolation_pass` — secret scan fail-closed, trace separation (C8-C9);
- `outcome_explanation_separation_pass` — explanation cannot mutate facts (C10-C11);
- `personal_memory_policy_pass` / `ceo_memory_policy_pass` — role class
  catalogs, TTL policy (C12-C13);
- `worker_stateless_default` / `promotion_supersession_tests_pass` — stateless
  workers, explicit promotion, supersession (C14-C16);
- `compaction_anchor_tests_pass` — anchor/fact preservation (C17-C18);
- `cold_reconstruction_pass`, `multi_project_isolation_pass`,
  `multi_tenant_memory_isolation_pass`, `secret_memory_tests_pass` — behavioral:
  require BOTH valid configs AND a green live test run (C19, C23-C25);
- `d1_mock_draft_ready` — MOCK / NON-SUBMISSION contract (C22);
- `adversarial_p0_pass` — a real run of the 30-test C26 adversarial suite plus
  catalog validator (never a hand-set claim);
- `p0_open == 0` — from the shared contradiction ledger.

## Evidence snapshot (BOOK time)

```json
"status": "PASS",
"ready_for_book5": true,
"d1_mock_draft_unlocked": true,
"adversarial_p0_pass": true,
"p0_open": 0,
"evidence": {
  "test_results": { "exit_code": 0, "passed": 275, "failed": 0,
    "scope": "tests/g0/book4 excluding G0_B4_REALITY_LOCK.json freshness self-test" },
  "adversarial_results": { "exit_code": 0, "passed": 30, "failed": 0,
    "scope": "tests/g0/book4/test_adversarial_context_pollution.py (A1-A25 + catalog guards)" },
  "config_count": 16
}
```

## Stale-lock defense

`tests/g0/book4/test_book4_reality_lock.py::test_committed_lock_matches_regeneration`
recomputes the lock from live repository evidence and asserts byte-equality
(modulo the pytest summary lines) with the committed JSON. Editing the lock by
hand, or letting the repository drift, turns the freshness test red. Defect
injection tests prove each predicate independently flips readiness to FAIL.

## Reproduction

```bash
python tools/g0/build_book4_reality_lock.py \
  --out docs/grant-sector/g0/00-ratification/G0_B4_REALITY_LOCK.json
```

Exit code 0 ⇔ PASS. Regeneration is deterministic given repository state.
