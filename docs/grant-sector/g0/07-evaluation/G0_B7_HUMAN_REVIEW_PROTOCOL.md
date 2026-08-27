# G0-B7-C23 — Human Review Protocol

**Document ID:** GS-G0-B7-C23-HR
**Status:** RATIFIED (Book 7 chapter C23)
**Engine:** `prototype/g0/evaluation/human_review.py`
**Schema:** `human_review.schema.json`

Human review is targeted, not ceremonial.

## Required when

- rubric dimension is materially subjective and high-impact
- candidate changes client-facing grant strategy significantly
- evaluation disagreement remains unresolved
- security/policy boundary changes
- production skill promotion risk exceeds threshold
- gold-label creation/adjudication requires expertise

## Reviewer record

```text
reviewer identity/role
case/candidate
rubric
scores/decision
comments/reason codes
conflicts of interest if relevant
timestamp
```

## Rules

- Every material human decision is attributable; no anonymous consequential
  review.
- The reviewer receives a structured review packet, not unbounded raw logs.
- Inter-reviewer disagreement is data, not something to hide.
- Do not invent a human-review score if no human reviewed it (D2 rule).
