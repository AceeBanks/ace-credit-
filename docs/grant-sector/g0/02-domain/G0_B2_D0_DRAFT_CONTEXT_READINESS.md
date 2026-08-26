# G0 Book 2 — Chapter C19: D0 Shadow Draft Readiness Contract

## Decision

Book 2 does **not** build the drafting harness. It defines the minimum domain
bundle the D0 harness must consume after Book 3 — and proves that bundle is
representable without agent memory.

Machine-readable source of truth: `config/g0/domain/draft_context_policy.yaml`.
Executable form: `prototype/g0/domain/draft_context.py` +
`prototype/g0/domain/fixtures/draft_context.py`.

## DraftContextBundle

```
Organization
+ Organization/project CanonicalFacts
+ GrantOpportunity
+ exact OpportunityRevision
+ EligibilityDecision
+ normalized Requirements
+ Funder/Program context
+ EvidenceClaims / CanonicalFacts
+ StatisticObservations
+ Budget/financial assumptions
+ Research findings
+ Proposal template/profile
→ DraftContextBundle
```

A plain frozen dataclass — reconstructable from fields alone, no hidden agent
memory.

## D0 rules (all enforced fail-closed)

1. exact opportunity revision required
2. eligibility cannot be INELIGIBLE (unresolved mandatory eligibility marks the
   mock incomplete)
3. mandatory requirement list present (missing → incomplete)
4. unsupported facts flagged, never silently filled
5. mock proposal links each material factual assertion to evidence where
   practical
6. output Artifact state = DRAFT/MOCK
7. no submission state/capability in the bundle

## Readiness fixture

`GA_DRAFT_BUNDLE` — a schema-valid synthetic Georgia-first
DraftContextBundle (organization, PROMOTED fact with supporting claim, GA
opportunity + exact revision, ELIGIBLE decision, normalized requirement, GA
OPB program, community statistic, Decimal-only budget, proposal template,
DRAFT proposal + business plan artifacts) that Book 3 can later replace with
source-governed snapshots. Validates clean.

## Tests (10 in `test_draft_context.py`)

- Georgia-first bundle is ready
- bundle representable without agent memory (replace-roundtrip equality)
- missing opportunity revision fails
- mismatched eligibility revision fails
- INELIGIBLE decision fails
- missing mandatory requirement list → explicit incomplete
- unsupported organization fact flagged
- output state must be DRAFT/MOCK; submission artifact rejected
- proposal/business plan contexts distinguishable
- validator: missing D0 rule fails closed

Run: `python -m pytest tests/g0/book2/test_draft_context.py -q` — **10 passed**.
