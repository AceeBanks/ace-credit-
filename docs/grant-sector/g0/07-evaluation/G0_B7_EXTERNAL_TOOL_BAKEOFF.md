# G0-B7-C27 — External Evaluation Tool Bake-Off

**Document ID:** GS-G0-B7-C27-BAKE
**Status:** RATIFIED (Book 7 chapter C27)

Evaluate external tools only where they reduce real engineering burden.
They are subordinate adapters behind project-owned contracts
(EVAL-LAW-014).

## Candidate roles

| Candidate | Allowed role |
|---|---|
| Promptfoo | test/eval orchestration, red-team, model/prompt comparison helper |
| Guardrails | structured validation helper where contracts fit |
| Hermes archived Skill Eval Lab | reference/possible adapter |
| SkillClaw | candidate skill evolution (generation only) |
| Hermes Dojo | performance/weakness detection |
| Hermes Skill Factory | workflow→candidate skill pattern (license resolved first) |
| 42-evey plugins | selective telemetry/cost/delegation/session helpers |
| Compozy skill lifecycle | only if Compozy remains runtime candidate |

## The project owns

EvalCase, EvalCorpusVersion, EvalSuite, EvalRun, MetricBundle,
CandidateChange, PromotionDecision, ReleaseCandidate, RollbackEvent.
External tools adapt to those objects.

## Decision outcomes

ADOPT_BOUNDED | WRAP | REFERENCE | DEFER | REJECT.

No wholesale "self-evolution stack." Humanizer disposition: PROMOTE |
REVISE | REJECT | QUARANTINE | DEFER via Book 7 promotion rules (HZR-014).
