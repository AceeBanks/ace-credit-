# G0-B7 — Handoff to Book 8

| Field | Value |
|---|---|
| Status | INTERNAL REALITY LOCK PASS + EXTERNAL REVIEW REPAIR COMPLETE (awaiting external ratification) |
| Branch | `grant-sector-r0-salvage` |
| Lock | `G0_B7_REALITY_LOCK.json` — status PASS, `ready_for_book8_architecture: true`, `ready_for_book8_execution: false`, `p0_open: 0` |
| External review | `G0_B7_EXTERNAL_REVIEW_01.md` — P1-01/P1-02/P2-01 repaired by `G0-B7-REPAIR-01` |
| Full suite | `python -m pytest tests/g0 -q` → **1687 passed, 14 skipped** |
| Book 7 suite | 283 passed, 2 skipped (exclusive) |
| Reality Lock freshness | 15 tests (book7) + 18 tests (book6) = **33 passed** unguarded |
| Submission | `submission_enabled = false` (structural, un-grantable) |
| D2 live-model lane | `d2_live_model_run_complete = false` — **BLOCKED_MODEL_RUNTIME**, honestly reported |
| D2 harness | `d2_harness_complete = true` — deterministic baseline draft, claim ledger, protected-claim diff all green |

## What Book 8 receives

Book 7 built the complete evaluation + promotion + quality-governance
apparatus. Book 8 receives:

- **Evaluation constitution** (24 laws, validated) — deterministic truth wins
  over LLM judges; hard security/factuality failures are non-compensatory.
- **Quality taxonomy** (9 dimensions, 6 non-compensatory hard gates) —
  correctness, factuality, grant quality, agent quality, security,
  operations.
- **EvalCase / EvalCorpusVersion / EvalSuite / EvalRun / MetricBundle**
  contracts (JSON schemas + governed dataclasses, hash-bound lineage to
  Book 5 eval-lineage contracts).
- **Golden-set protocol** — human-gold flag enforced at construction;
  leakage-guard (model/privacy/tenancy) on every fixture.
- **Georgia-first fixture pack** — `Community Youth Works, Inc.` +
  `opp_ga_501` FY2026 opportunity + revision `opp_rev_ga_501_1` +
  deterministic eligibility + protected-element pins.
- **Evaluation engines** — grant quality rubric, factuality/claim support,
  eligibility/match, research quality, Personal/CEO Hermes, worker, memory,
  model routing, parser/retrieval, operations (cost/latency), statistics.
- **Security regression suite** — re-runs every Book 6 repair seam
  (authority ladder, capability/tenant/project/resource binding, approval
  registry, DecisionRegistry, replay, submission disablement) as a hard
  gate; any regression => REJECT.
- **Promotion governance** — CandidateChange → PromotionDecision
  (PROMOTE/REVISE/REJECT/QUARANTINE/DEFER), threshold config, no
  self-promotion; rollback events + shadow/canary; human review schema.
- **Adversarial suite** — 40 plan attacks + 10 Humanizer-specific attacks,
  all red-green provable, all blocked by defenses; integration/property
  suite.
- **D2 harness** — first grounded grant-writing quality experiment; honest
  `BLOCKED_MODEL_RUNTIME` for live generation lanes.

## Humanizer disposition (as repaired)

**CANDIDATE / DEFER_PENDING_LIVE_BAKEOFF** — per the mission's promotion law
and `NO FAKE GREEN` rule (G0_B7_EXTERNAL_REVIEW_01 P1-01 repair):

- Amendment 003 ratified (bounded STYLE_TRANSFORM candidate; protected
  claims, facts, citations, numbers, terminology cannot change).
- ArtifactVersion N → STYLE_TRANSFORM → N+1 diff contract implemented and
  tested; protected-claim diff + factuality revalidation implemented.
  Ledger Batch 07 corrected from `ADOPT_BOUNDED` — no adoption decision is
  justified without a live baseline-vs-humanized comparison.
- No authorized model runtime is configured for the governed G0 pipeline, so
  no real humanized draft exists. `D2_LIVE_MODEL_RUN_COMPLETE`,
  `D2_LIVE_HUMANIZER_RUN_COMPLETE` and `HUMANIZER_LIVE_BAKEOFF_COMPLETE` are
  honestly `false`; `ready_for_book8_execution = false`.
- Disposition derives from Book 7 promotion rules once a live run exists;
  the harness and guards are ready.

## Hard invariants preserved (unchanged from Book 6)

- Deny-by-default authority; tenant/project isolation; server-side secrets.
- Tool gateway requires a registry-issued, request-bound AuthorizationDecision
  (capability, tenant, project, resource, request id) — no bearer-token reuse.
- Evidence authority, source precedence, historical replay, submission
  disabled — all preserved. A better eval score never weakens a prior
  invariant.

## STOP POINT

Per the mission, **Book 8 is NOT begun**: `ready_for_book8_execution = false`
(live D2 quality gate not passed — no authorized model runtime). The next
step is external ratification of the repair: evaluation methodology,
Humanizer results, D2 draft, Claim Ledger, factuality metrics,
baseline-vs-candidate comparison, and Book 7 promotion decisions.

## External components

- **blader/humanizer** — BOUNDED STYLE_TRANSFORM CANDIDATE (Amendment 003,
  ratified; CANDIDATE / DEFER_PENDING_LIVE_BAKEOFF pending live-model run).
- **Promptfoo / Guardrails / other bake-off candidates** — subordinate
  adapters; `external_tool_bakeoff_complete` derives from the governed
  adapter contract, no wholesale self-evolution stack installed.
