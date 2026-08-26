# G0 Book 4 — Adversarial Test Report

**Command:** `python -m pytest tests/g0/book4/test_adversarial_context_pollution.py -q`
**Result:** **30 passed, 0 failed** (A1-A25 plus scenario-catalog and validator guards)

Config of truth: `config/g0/agents/adversarial_context.yaml` (all 25 scenarios with
their required fail-closed expectations) · Validator: `tools/g0/validate_adversarial_context.py` → **PASS**

## Scenario-by-scenario results

| # | Scenario | Test | Result |
|---|---|---|---|
| A1 | raw-history flood | `test_a1_...` | PASS — context stays bounded; mandatory anchors survive |
| A2 | worker transcript pollution | `test_a2_...` | PASS — CEO receives bounded WorkerResult; trace stays in sidechain |
| A3 | compaction loses deadline | `test_a3_...` | PASS — anchor preservation at every stage |
| A4 | compaction changes $75,000 → $750,000 | `test_a4_...` | PASS — factual-preservation guard rejects drift |
| A5 | preference vs canonical fact | `test_a5_...` | PASS — canonical-substitution guard refuses freeform truth |
| A6 | old vs new preference | `test_a6_...` | PASS — supersession, append-only history |
| A7 | CEO asks canonical question | `test_a7_...` | PASS — avoidable clarification detected |
| A8 | Personal answers by inference | `test_a8_...` | PASS — labeled ASSERTION, never FACT |
| A9 | worker requests broader capability | `test_a9_...` | PASS — CEO-owned/unknown capability refused |
| A10 | CEO passes full conversation | `test_a10_...` | PASS — prohibited class never in allowed context; access denied |
| A11 | secret in transcript | `test_a11_...` | PASS — sidechain persistence refused; scanner detects all patterns |
| A12 | cold reset | `test_a12_...` | PASS — operational state reconstructs from durable state alone |
| A13 | closed-project memory bleed | `test_a13_...` | PASS — excluded from new application context |
| A14 | same client, two projects | `test_a14_...` | PASS — project-scoped bundles, no contamination |
| A15 | two tenants similar names | `test_a15_...` | PASS — no memory crosses tenant boundary |
| A16 | agent identity/model confusion | `test_a16_...` | PASS — provider swap preserves identity/namespaces |
| A17 | intent drift | `test_a17_...` | PASS — new intent version; stale objective never silent |
| A18 | worker result contradiction | `test_a18_...` | PASS — CONFLICTED via evidence protocol, never majority vote |
| A19 | memory candidate spam | `test_a19_...` | PASS — random detail REJECTED; low-value TEMPORARY |
| A20 | operational lesson self-promotion | `test_a20_...` | PASS — Book 7 eval gate required |
| A21 | “forget that preference” | `test_a21_...` | PASS — superseded per retention policy |
| A22 | mock draft as submitted | `test_a22_...` | PASS — label validator rejects SUBMITTED claim |
| A23 | CEO bypasses Personal for relationship memory | `test_a23_...` | PASS — relationship/identity classes Personal-only |
| A24 | Personal launches worker directly | `test_a24_...` | PASS — capability/path policy denies |
| A25 | sidechain lost | `test_a25_...` | PASS — audit quality degraded, never full-audit |

## C27 integration guarantees (also adversarial)

`tests/g0/book4/test_integration_reconstruction.py` — **29 passed** — executes the 22
mandatory invariants (distinct Personal/CEO namespaces, memory not canonical truth,
IntentContract sufficiency, bounded TaskContract, no CEO-authority inheritance,
bounded WorkerResult → sidechain, trace not in Personal context, uncertainty/evidence
preserved, no fact mutation via explanation, stateless workers, explicit promotion,
supersession exclusion, anchor preservation, authority-over-recency retrieval,
cold restart, project/tenant isolation, model replacement, D1 without raw transcript)
and the 5 deterministic property tests (same-state reconstruction, compaction
idempotence, supersession removal, retry lineage, ref survival through reduction).

## Verdict

**P0 adversarial coverage: PASS** (`adversarial_p0_pass: true`, `p0_open: 0` in
`G0_B4_REALITY_LOCK.json`). The dedicated adversarial suite is a separate live
pytest run recorded in the lock's evidence (`adversarial_results`). No scenario
required a repair; every expectation in the plan's C26 chapter is executed by a
real test against live prototypes.
