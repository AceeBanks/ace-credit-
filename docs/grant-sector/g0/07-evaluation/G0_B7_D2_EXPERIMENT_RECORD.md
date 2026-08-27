# G0-B7-D2 — First Grounded Grant-Writing Quality Experiment (Record)

**Document ID:** GS-G0-B7-D2-001
**Status:** HARNESS COMPLETE — LIVE MODEL LANE BLOCKED (BLOCKED_MODEL_RUNTIME)
**Branch:** `grant-sector-r0-salvage`
**Artifacts:** `docs/grant-sector/g0/07-evaluation/d2/`

## What D2 is

The project's first serious grant-writing quality experiment — separate
from the D1 architectural contract test. It measures a grounded draft
against the Book 7 evaluation machinery: deterministic QA, Claim Ledger
factuality, requirement coverage, budget reconciliation, protected-claim
diff (HZR-007).

## Input (governed Georgia-first fixture)

- **Organization:** Community Youth Works, Inc. — Georgia nonprofit,
  founded 2012, Atlanta GA (Book 2 GA-1 fixture; EIN + GA SOS identifiers
  VERIFIED).
- **Opportunity:** Georgia Rural Community Impact Grant FY2026
  (`opp_ga_501`), exact revision `opp_rev_ga_501_1` (deadline 2026-10-15,
  ceiling $50,000).
- **Eligibility:** ELIGIBLE (deterministic, rule_ga_1 + rule_ga_2).
- **Community statistic:** Dade County poverty rate 18.2% (ACS-5yr 2023).
- **Missing facts:** none fabricated; anything absent stays UNKNOWN/ASSUMPTION/
  QUESTION per existing contracts.

## Generation

- **BASELINE GROUNDED DRAFT:** deterministic, evidence-anchored (every
  material value derives from the fixture — no model, nothing invented).
- **HUMANIZED GROUNDED DRAFT:** **BLOCKED_MODEL_RUNTIME** — no configured
  language model provider in this environment. No fabricated "AI
  generation" result is produced. The HZR-007 protected-claim diff and
  HZR-008 factuality revalidation contracts are fully implemented and
  exercised against the deterministic draft so the pipeline is live.

## Baseline results (measured, not invented)

- Deterministic QA gates: **8/8 passed** (sections, word limit, deadline,
  ceiling, revision identity, budget reconcile, fabrication absence,
  submission absence).
- Material claim support rate: **1.0** (4/4 supported, 0 unsupported).
- Requirement coverage: **1.0** (2/2 mandatory completed).
- Budget: **$50,000.00** = ceiling, reconciles exactly.
- Eligibility: ELIGIBLE.

## Humanized lane

Status: **BLOCKED_MODEL_RUNTIME**. Protected-claim diff validator is live:
identity transform passes; tampered amount ($750k) and deadline (Oct 16)
are detected (HZR-A/B blocked). Factuality revalidation (HZR-008) is
wired to run after any future live transform.

## Human review

**NOT_PERFORMED** — no human reviewer available; no human-review score is
invented (D2 rule).

## Disposition

- **Humanizer: DEFER (no live run).** D2 does NOT promote Humanizer; a
  baseline-vs-candidate comparison through the Book 7 promotion path is
  required first (HZR-014).
- D2 remains **MOCK / NON_SUBMISSION**; submission is structurally disabled.

## Statistical discipline (C28)

This is an initial quality experiment on one fixture (GA-1), not proof that
the system writes better grants universally. Sample size, fixture identity,
exact revision, source state and eval version are recorded in
`D2_REPRODUCTION_MANIFEST.json`. Book 8 expands coverage.
