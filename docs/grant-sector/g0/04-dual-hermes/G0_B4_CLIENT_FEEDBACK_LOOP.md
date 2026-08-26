# G0 Book 4 — Client Feedback & Co-Adaptation Loop

**Document ID:** GS-G0-B4-C20-C21-FEEDBACK-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C20-C21
**Policy:** `config/g0/agents/feedback_policy.yaml`
**Prototype:** `prototype/g0/agents/feedback.py`
**Validator:** `tools/g0/validate_feedback_loop.py`

---

## 1. Purpose

Make user corrections **first-class events** and allow the two Hermes roles
to improve their interface without merging contexts.

## 2. Feedback types

INTENT_MISUNDERSTOOD · FACTUAL_CORRECTION · PREFERENCE_CORRECTION ·
ARTIFACT_REVISION_REQUEST · PRIORITY_CHANGE · PROJECT_CANCELLATION_PAUSE ·
RESULT_DISAGREEMENT

## 3. Flow

```text
Client correction
  ↓
Personal Hermes
  ↓
classify feedback
  ↓
Intent amendment / Fact proposal / Memory supersession / Artifact revision request
  ↓
CEO notified if operational impact
  ↓
selective replan/recompute
```

## 4. Routing (frozen)

| Feedback | Route |
|---|---|
| INTENT_MISUNDERSTOOD | INTENT_AMENDMENT |
| FACTUAL_CORRECTION | FACT_PROPOSAL (never silent canonical mutation) |
| PREFERENCE_CORRECTION | MEMORY_SUPERSESSION |
| ARTIFACT_REVISION_REQUEST | ARTIFACT_REVISION_REQUEST |
| PRIORITY_CHANGE | INTENT_AMENDMENT |
| PROJECT_CANCELLATION_PAUSE | PROJECT_STATE_CHANGE |
| RESULT_DISAGREEMENT | EXPLANATION_REVIEW |

## 5. Rules (frozen)

| Rule | Content |
|---|---|
| FEEDBACK-001 | Client changing target geography invalidates the relevant grant search/match plan → selective replan. |
| FEEDBACK-002 | Tone feedback updates a preference/artifact request, never canonical grant facts. |
| FEEDBACK-003 | Factual corrections become proposals routed to governed promotion. |
| FEEDBACK-004 | No co-adaptation change promotes without Book 7 evaluation. |

## 6. Co-adaptation

The agents improve the **protocol**, not by sharing all memory. Metrics
(clarification rate, replanning rate, avoidable CEO questions, …) produce
`CM-LESSON-CANDIDATE`s that require Book 7 evaluation before becoming
operational doctrine.

## 7. Verified behaviors

- `test_geography_change_invalidates_match_plan`
- `test_tone_feedback_updates_preference_not_facts`
- `test_factual_correction_is_proposal_not_mutation`
- `test_repeated_clarification_produces_lesson_candidate`
- `test_coadaptation_lesson_cannot_promote_without_book7`
