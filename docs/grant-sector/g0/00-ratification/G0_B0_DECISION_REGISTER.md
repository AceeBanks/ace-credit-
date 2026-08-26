# G0 Book 0 — B0.C2 R0 Decision Register

**Chapter:** B0.C2 — Decision Register
**Status:** IMPLEMENTED
**Machine-readable source of truth:** `config/g0/ratification/decision_register.yaml`
**Validator:** `tools/g0/validate_decision_register.py`

## WHAT

Normalizes every major R0 conclusion into exactly one primary status, in one
place, with evidence lineage back to content-pinned artifacts.

## WHY

R0 conclusions currently live scattered across 8+ documents with varying
wording and confidence levels. Downstream books need a single normalized
baseline so Book 1+ inherits decisions, not archaeology.

## AUTHORITY

Book 0 master prompt §B0.C2. Statuses are normalized *from* the pinned source
artifacts; where the plan's "expected baseline" and source artifacts differ,
the source artifact wins and the difference is recorded here.

## STATUSES

`RATIFIED` · `RATIFIED_WITH_CONDITION` · `PROTOTYPE_REQUIRED` · `DEFERRED` ·
`REJECTED` · `UNRESOLVED`

## INVARIANTS (validator-enforced, fail-closed)

- unique decision IDs; known status enum; declared category only;
- every decision cites ≥1 artifact ID that **resolves to the pinned manifest**
  (phantom lineage is a hard failure);
- RATIFIED_WITH_CONDITION ⇒ non-empty conditions;
- supersession references consistent + acyclic;
- every one of the 16 required categories has ≥1 decision.

## DECISION SUMMARY

| Area | Decision | Status |
|---|---|---|
| Architecture | Dual-Hermes split | RATIFIED |
| Architecture | Relationship/Control/Work/Data planes via typed contracts | RATIFIED |
| Architecture | Clean-repo selective transplant (no wholesale merge) | RATIFIED |
| Hermes | Hermes operates; platform owns truth | RATIFIED |
| Hermes | OCE-Hermes filtered MCP facade | RATIFIED_WITH_CONDITION |
| Memory/context | Personal/CEO memory isolation | RATIFIED |
| Memory/context | Bounded/disposable workers + sidechain traces | RATIFIED |
| Memory/context | Compaction with preservation classes + provenance | RATIFIED_WITH_CONDITION |
| Control/governance | Typed capability/policy engine (regex = defense-in-depth) | RATIFIED |
| Control/governance | Self-heal runtime-only; policy changes governed | RATIFIED |
| Control/governance | Consensus/critics only at justified ambiguity | RATIFIED |
| Control/governance | Promptfoo + Eval Lab benchmark-before-promotion | RATIFIED_WITH_CONDITION |
| Control/governance | Guardrails — selected validators only | RATIFIED_WITH_CONDITION |
| Data/source | Postgres authoritative durable state | RATIFIED |
| Data/source | Redis non-authoritative transport/cache | RATIFIED |
| Data/source | Executable source precedence + immutable snapshots | RATIFIED |
| Data/source | Federal/state/community adapter architecture | RATIFIED_WITH_CONDITION |
| External repositories | CommonGrants interoperability mapping | RATIFIED_WITH_CONDITION |
| Data/source | Candid optional enrichment only | DEFERRED |
| Evidence | Deterministic eligibility kernel | RATIFIED |
| Evidence | Evidence confidence model; LLM self-confidence rejected | RATIFIED |
| Evidence | Relational Evidence Graph first; graph DB deferred | RATIFIED |
| Evidence | Semantica substrate | PROTOTYPE_REQUIRED (P0 bake-off) |
| Research | Research Mesh contracts ported, persistence rewritten | RATIFIED_WITH_CONDITION |
| Research | Crawl4AI governed extraction | PROTOTYPE_REQUIRED |
| Research | GPT Researcher bounded patterns | PROTOTYPE_REQUIRED |
| Parsing | Parser contract + wrapped engines; Unstructured bake-off | PROTOTYPE_REQUIRED |
| Parsing | PixelRAG visual fallback benchmark | PROTOTYPE_REQUIRED |
| Security | Zero secrets in memory/prompts/sidechains/logs/Git | RATIFIED |
| Security | Progressive skill disclosure | RATIFIED |
| Licensing | Treg-inspired pattern, independent implementation | RATIFIED_WITH_CONDITION |
| Licensing | Treg code embedding/forking | REJECTED (nonstandard license) |
| Licensing | Fresh license/security due diligence gate | RATIFIED |
| Submission boundary | Automated submission excluded from Phase 1 | REJECTED / NON-GOAL |
| Mock drafting milestones | D0 after Book 3 / D1 after Book 4 / D2 at Book 8 | RATIFIED_WITH_CONDITION ×3 |
| Georgia-first | Georgia replaces California as proof state | RATIFIED |
| Client Phase 1 | Single-client real-data vertical slice | RATIFIED |
| Reject ledger | Trading-domain exclusion binding | REJECTED (for this product) |
| Reject ledger | Anti-pattern ledger bindings | RATIFIED |

## FAILURE MODE

Validator exits non-zero on any defect. A decision without resolvable lineage,
a category with no decision, or a conditional ratification without conditions
blocks the Book 0 Reality Lock.

## TEST

`tests/g0/book0/test_decision_register.py` — live-register pass plus negative
fixtures: phantom lineage, unknown status, duplicate IDs, missing conditions,
supersession cycles, unknown supersession target, empty sources/statement,
and category coverage gaps.

## HANDOFF

Book 1 receives: typed authority model must implement DEC-GOV-001/002;
submission prohibition implements DEC-SUB-001; drafting milestones implement
DEC-DRAFT-001/002 authority distinctions.
