# G0 Book 0 — B0.C4 Non-Goal Freeze & B0.C5 Prototype Candidate Register

**Chapters:** B0.C4 — Non-Goal Freeze; B0.C5 — Prototype / Bake-Off Candidates
**Status:** IMPLEMENTED
**Machine-readable sources:** `config/g0/ratification/non_goals.yaml`, `config/g0/ratification/prototype_candidates.yaml`
**Validator:** `tools/g0/validate_freeze_registers.py`

## WHAT (C4)

Fifteen frozen non-goals for G0/G1 first vertical-slice scope, each classified as
`explicitly_rejected` | `intentionally_deferred` | `future_extension_point`,
with rationale and lineage to pinned artifacts and decisions.

Highlights: autonomous submission and L4/L5 enablement are **explicitly rejected**;
50-state coverage, foundation universe, Candid are **deferred**; Kubernetes, graph DB
remain **extension points** architectured but not built.

## WHAT (C5)

Ten prototype/bake-off candidates that require evidence before adoption — never
architectural assumption: Semantica vs **relational baseline** (paired bake-off),
parser stack vs Unstructured, PixelRAG fallback, Crawl4AI, GPT Researcher patterns,
Eval Lab (Promptfoo integration), Guardrails validators, Univer workspace,
Activepieces fabric.

Each candidate carries hypothesis, baseline, success metrics, kill criteria,
license status, security notes, responsible book.

## WHY

R0 enthusiasm must not silently become architecture. Adoption happens only through
the responsible book's evidence gate.

## INVARIANTS (validator-enforced, fail-closed)

- unique IDs; known kinds/statuses; all three non-goal kinds represented;
- all ten mandated candidate IDs present;
- lineage resolves against the artifact manifest and decision register;
- **gate:** no candidate may be `adopted_with_evidence` at Book 0.

## FAILURE MODE

A missing mandated candidate, phantom lineage, or premature ADOPTED status exits
non-zero and blocks the Book 0 Reality Lock (`prototype_candidates_bounded`).

## TEST

`tests/g0/book0/test_freeze_registers.py` — live pass plus negatives: missing
kind coverage, unknown kind/status, phantom lineage, premature adoption gate,
missing mandated candidate.

## HANDOFF

Books 2+ inherit the obligation to run these bake-offs under their gates;
Book 5 owns the Semantica-vs-relational verdict.
