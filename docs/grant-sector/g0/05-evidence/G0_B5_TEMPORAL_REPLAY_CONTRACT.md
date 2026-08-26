# G0 Book 5 — Temporal Replay Contract

**Chapter:** B5.C8

## Replay modes (never conflated)

| Mode | Evidence | Evaluator/policy |
|---|---|---|
| HISTORICAL_EXACT | exact pinned inputs of the original decision | original |
| HISTORICAL_REEVALUATE | historical evidence | current |
| CURRENT_REEVALUATE | current evidence | current |

## Rules

- ReplayPacket = DecisionRecord + pinned input refs + configuration/policy
  refs + source snapshot refs + engine metadata.
- EVID-LAW-007: HISTORICAL_EXACT never substitutes current state; the guard
  rejects any current input that isn't in the pinned set.
- A missing historical dependency is a **P0 integrity failure** — nothing is
  fabricated in its place.
- Exact token-for-token LLM regeneration is not required; replay correctness
  means reconstructing the exact evidence/context/instruction/output
  artifacts and re-running validators/evaluators.

## Tests

`tests/g0/book5/test_temporal_replay.py` — 5 tests.
