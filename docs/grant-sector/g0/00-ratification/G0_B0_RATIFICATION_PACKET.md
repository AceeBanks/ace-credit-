# G0 Book 0 — Ratification Packet

**Book:** G0-B0 (R0 Ratification & Reality Lock)
**Branch:** `grant-sector-r0-salvage`
**Status:** BOOK_COMPLETE_AWAITING_REVIEW — implementation agent does NOT self-ratify.
**Machine-readable lock:** `G0_B0_REALITY_LOCK.json` (generated, not hand-edited)

## Contents of this package

| Artifact | Purpose | Validator |
|---|---|---|
| `artifact_manifest.yaml` + doc | Content-pinned inventory of 23 pre-ratification artifacts with supersession graph | `validate_artifact_manifest.py` |
| `decision_register.yaml` + doc | 43 decisions across all 16 required categories, each with one primary status and resolvable lineage | `validate_decision_register.py` |
| `contradiction_ledger.yaml` + doc | 11 contradictions/drift entries; all ten mandated probes; zero open P0 | `validate_contradictions.py` |
| `non_goals.yaml` + doc | 15 frozen non-goals across all three kinds | `validate_freeze_registers.py` |
| `prototype_candidates.yaml` + doc | 10 bake-off candidates with metrics/kill criteria/licenses; none adopted at Book 0 | `validate_freeze_registers.py` |
| `G0_B0_REALITY_LOCK.json` | Computed readiness gate | `build_book0_reality_lock.py` |

## Reality Lock result (evidence-derived)

```
status: PASS
artifact_manifest_complete: true
all_major_decisions_classified: true
p0_open: 0
prototype_candidates_bounded: true
non_goals_frozen: true
supersession_cycles: 0
stale_authority_detected: false
book0_tests_all_pass: true (50/50)
ready_for_book1_ratification: true
```

`ready_for_book1_ratification` is the conjunction of every predicate above,
computed by `build_book0_reality_lock.py`; a not-run test suite blocks readiness.

## What was ratified (summary)

- Dual-Hermes split, four-plane architecture, selective transplant (no wholesale merges).
- Hermes operates; platform owns truth. Typed capability/policy engine dominates all tooling.
- Postgres authoritative; Redis transport-only; executable source precedence with immutable snapshots.
- Deterministic eligibility kernel; relational-first Evidence Graph; Semantica = mandatory P0 bake-off.
- Georgia-first state proof; D0/D1/D2 drafting milestones; automated submission REJECTED for Phase 1.
- Treg pattern adopted via independent implementation; code embedding blocked on license.

## Review request

Independent review should inspect commit range from `4fbbf186`
(G0-B01-BOOT) through the `G0-B0-BOOK` checkpoint against the Book 0 master plan
(`docs/grant-sector/BOOK_0_CONTINUOUS_EXECUTION_MASTER_PROMPT_v1.0.md`).
