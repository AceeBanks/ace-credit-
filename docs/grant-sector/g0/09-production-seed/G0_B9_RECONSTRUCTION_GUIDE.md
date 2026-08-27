# G0 Book 9 — Reconstruction Guide (G0 Final Reconstruction Test)

**Chapter:** B9.C30
**Date:** 2026-08-27
**Status:** PASS — every north-star question answered from repository
artifacts; no tribal knowledge required.

A new engineering team with only repository artifacts (no conversation
history) reads this guide plus the referenced files and knows the product,
the architecture, and the build order.

| Question | Answer (artifact location) |
|---|---|
| What product are we building? | A governed Grant-writing platform: from client intent to grounded, evaluated, submission-*mock* grant package. (`docs/grant-sector/G0_BOOK_08_MASTER_IMPLEMENTATION_PLAN_v1.0.md`, charter `G0_B8_CHARTER.md`) |
| What is Phase 1? | Georgia-first vertical slice: Community Youth Works fixture → Georgia Rural Community Impact Grant → grounded draft. (`G0_B8_CHARTER.md`, `prototype/g0/vslice/`) |
| Who is Personal Hermes? | Client-facing agent: intent capture, IntentContract, preference continuity, explanation. Never CEO work. (`G0_B7_PERSONAL_HERMES_EVAL.md`, `prototype/g0/agents/intent_builder.py`) |
| Who is CEO Hermes? | Operations agent: task decomposition, worker choice, synthesis, completion-state. (`G0_B7_CEO_HERMES_EVAL.md`, `prototype/g0/agents/task_builder.py`) |
| What can workers do? | Task-scoped drafting/research/budget/QA only — bounded ContextBundles, structured WorkerResults, no client contact unless permitted. (`G0_B7_WORKER_EVAL.md`) |
| Where is truth? | Postgres (canonical). `G0_B9_CANONICAL_STATE_OWNERSHIP.md` |
| How are grants represented? | Opportunity + append-only OpportunityRevision + ApplicationProject. (`prototype/g0/domain/revisions.py`) |
| How are sources trusted? | Immutable SourceSnapshots; source text is untrusted; revision watcher. (`G0_B9_API_CONTRACT_MAP.md`, Book 5) |
| How is eligibility determined? | Deterministic rule engine only; LLM narrative can never set ELIGIBLE; UNKNOWN stays UNKNOWN. (`prototype/g0/domain/eligibility.py`) |
| What counts as evidence? | EvidenceClaims → canonical facts with source precedence; material claims map to refs. (`G0_B7_FACTUALITY_EVIDENCE_RUBRIC.md`) |
| How are decisions replayed? | DecisionRecord: same inputs → same decision; supersede semantics. (`prototype/g0/evidence/decisions.py`) |
| How are model calls governed? | Governed Model Gateway: PDP ALLOW, provider profile, server-side credential, egress policy, audit. (`prototype/g0/model/gateway.py`, `G0_MODEL_RUNTIME.md`) |
| How are tools secured? | Independent ToolGateway requiring `capability_id` in the decision, bound to tool's declared capabilities. (`prototype/g0/security/tool_gateway.py`) |
| How are changes promoted? | Book 7: CandidateChange → evaluation (deterministic-first) → single PromotionDecision → shadow/canary → rollout. (`G0_B7_CHANGE_PROMOTION_PROTOCOL.md`) |
| What runtime won? | OCE_NATIVE (project-owned). `G0_B9_RUNTIME_SUBSTRATE_ADR.md` |
| What gets deployed? | Modular monolith containers + managed Postgres + object storage. `G0_B9_DEPLOYMENT_STRATEGY.md` |
| What do we build in G1? | G1.1–G1.10 epics with PROMOTE/HARDEN/REIMPLEMENT/NEW classification. `G0_B9_G1_IMPLEMENTATION_BACKLOG.md` |
| Why were alternatives rejected? | Compozy/QM failed hard gate 7 (framework-owned state); hybrid unproven. `G0_B9_RUNTIME_BAKEOFF_RESULTS.md` |

## Self-check

If a new engineer must ask any question whose answer is not in the
repository, G0 is not complete. This guide + the referenced artifacts
answer all 16 questions above.
