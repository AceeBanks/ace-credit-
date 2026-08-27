# G0-B7-D2-LIVE — First Governed Model-Generated Grant-Writing Experiment

Status: **COMPLETED** · MOCK / NON_SUBMISSION · submission structurally disabled.

## What happened

A real language model — through the governed Model Gateway (PDP-issued
ALLOW, server-side credential, egress/SSRF control, one-shot replay,
audit) — wrote a grounded Grant draft from the governed Georgia-first
fixture. The Book 7 evaluation chain then judged that draft
deterministically. No fabrication was injected; failures were recorded
honestly.

## Input (governed fixture)

- Organization: **Community Youth Works, Inc.** (Georgia nonprofit,
  founded 2012, Atlanta GA, EIN 58-2345671)
- Opportunity: **Georgia Rural Community Impact Grant FY2026** (opp_ga_501)
- OpportunityRevision: **opp_rev_ga_501_1**
- Deadline: **October 15, 2026**
- Ceiling: **$50,000**
- Eligibility: **ELIGIBLE**
- Community evidence: Dade County, GA poverty rate **18.2 percent** (2023,
  ACS 5-year estimate)
- Evidence refs: `ref:opp_rev_ga_501_1`, `ref:stat_ga_42`,
  `ref:snap-ga-1`, `ref:snap-ga-2`; canonical fact `fact_ga_1`
  (501(c)(3), PROMOTED)

## Model run

| Field | Value |
|---|---|
| provider | openrouter (governed profile `pp_openrouter_dev`) |
| model | `minimax/minimax-m3:free` (pinned, attributable) |
| prompt version | D2-LIVE-PROMPT-v1 (bounded drafting instructions) |
| temperature | 0.2 |
| input tokens | 721 |
| output tokens | 486 |
| latency | ~7s |
| cost | $0.00 (free tier; `cost_usd_if_known=null`) |
| label | MOCK_NON_SUBMISSION |

## Baseline evaluation (real model draft)

- **Deterministic QA: PASS** (sections, word limit, deadline, funding
  amount, revision identity, eligibility, no fabrication, no submission)
- **Claim support rate: 1.0** (4/4 supported, 0 unsupported, 0 conflicted)
- **Unsupported material claims: 0**
- **Protected elements missing from draft: 0**
- **Requirement coverage: 1.0** (2/2 mandatory)
- **Hard gate: PASS**

Honest run-variance observation: `minimax/m3:free` occasionally drops the
explicit eligibility statement or the poverty statistic across runs; the
hard gate caught every such instance and those runs were recorded, not
hidden. Prompt v1 explicitly required both, and the final canonical run
passed. This is real evidence that deterministic gates catch model
variance.

## Humanizer live bake-off (Amendment 003 bounded lane)

| Field | Value |
|---|---|
| pipeline | baseline ArtifactVersion N → governed style-transform call → candidate N+1 |
| model | `minimax/minimax-m3:free` (same governed gateway) |
| protected-claim diff (HZR-007) | **PASS** — no protected element changed or dropped |
| semantic preservation | **PASS** |
| word delta | +14 (style-expansion, facts unchanged) |
| hard gate | **PASS** |
| disposition | **REVISE** (C28: single fixture is weak evidence; no auto-PROMOTE; provisional only) |

Humanizer did not change: organization name, EIN, founding year, location,
opportunity/revision ids, deadline, ceiling, eligibility, or the 18.2%
statistic. It added no partnerships, testimonials, past performance,
staff counts, or outcomes. UNKNOWN statements were preserved.

## D2 fail conditions — checked

fabricated partnership / testimonial / past performance: **absent**
wrong deadline / funding amount / revision: **absent**
unsupported statistic / citation-does-not-support-claim: **absent**
requirement omitted: **absent** (coverage 1.0)
eligibility inconsistency: **absent**
tenant/project contamination: **absent** (single tenant, project-bound grant)
submission capability appears: **absent** (`submission_enabled=false`)

## Artifacts (docs/grant-sector/g0/07-evaluation/d2-live/)

- D2_LIVE_INPUT_MANIFEST.json
- D2_LIVE_BASELINE_DRAFT.md
- D2_LIVE_BASELINE_CLAIM_LEDGER.json
- D2_LIVE_BASELINE_EVAL.json
- D2_LIVE_BASELINE_MODEL_RUN.json
- D2_LIVE_HUMANIZED_DRAFT.md
- D2_LIVE_HUMANIZED_DIFF.json
- D2_LIVE_HUMANIZER_RUN.json
- D2_LIVE_HUMANIZER_DECISION.json
- D2_LIVE_REPRODUCTION_MANIFEST.json

## Limitations (C28 statistical discipline)

- Single fixture (GA-1); an initial quality experiment, not proof across
  grants.
- Free-tier model; paid models returned HTTP 402 (account credits absent).
- No human reviewer; `human_review_status=NOT_PERFORMED`, no invented score.
- Model variance observed; final canonical run passed all gates.

## Reproduction

```
python tools/g0/d2_live.py --model minimax/minimax-m3:free
python tools/g0/humanizer_live.py --model minimax/minimax-m3:free
```
