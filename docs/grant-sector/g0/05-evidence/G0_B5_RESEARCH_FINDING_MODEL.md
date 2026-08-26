# G0-B5-C17 — Research Finding Model

## Purpose

Turn funder/winner/community research into durable, evidence-backed objects
instead of disposable prose. Findings are consumable by drafting context and
showable to the client, with limitations preserved.

## ResearchFinding

```text
finding_id, research_type, subject_refs, statement, evidence_refs,
quality, applicability, limitations, award_sample_size, created_at,
created_by
```

Types: FUNDER_PRIORITY, HISTORICAL_WINNER_PATTERN, AWARD_RANGE,
GEOGRAPHIC_PATTERN, PROGRAM_ALIGNMENT, COMMUNITY_NEED, COMPETITIVE_SIGNAL,
REQUIREMENT_INTERPRETATION, OTHER.

## Rules (FIND-001..005)

1. A finding without evidence refs is rejected.
2. Limitations are preserved wherever the finding is consumed (client view
   carries them).
3. Historical winner patterns are descriptive, not causal: forbidden
   language ("always", "never", "proves", "guarantees", "every winner") is
   rejected, and weak-sample patterns must carry a limitation.
4. AWARD_RANGE and HISTORICAL_WINNER_PATTERN findings must represent
   `award_sample_size`.
5. Findings declare applicability; they are never silently injected as
   established facts.

Prototype: `prototype/g0/evidence/research.py`
Validator: `tools/g0/validate_research_finding.py`
Policy: `config/g0/evidence/research_finding_policy.yaml`
