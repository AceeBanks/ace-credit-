# G0 Book 2 — Chapter C20: Adversarial Domain Test Suite

## Decision

Attack the ontology before Book 3/data adapters depend on it. Scenarios
A1-A20 all fail closed: no silent merges, no fabricated facts, no invented
entities, no lost loss.

Tests: `tests/g0/book2/test_adversarial_domain.py` — **21 passed**.

## Scenario outcomes

| # | Attack | Outcome |
|---|---|---|
| A1 | Same name, different organization | near-identical names + different verified EINs → DISTINCT_CONFIRMED, never merged |
| A2 | Rename, same organization | same internal id + shared verified EIN → same Organization |
| A3 | Source disagreement on name/address | claims coexist (VERIFIED + CONFLICTED); identity intact |
| A4 | Amendment after drafting | new OpportunityRevision; old draft keeps old revision; dependency stale |
| A5 | Reissued opportunity number | explicit resolution rule (SAME vs REISSUED); never merged |
| A6 | Historical award, no opportunity | Award representable with `opportunity_id=None` |
| A7 | Recipient also funder elsewhere | same Organization, different OrganizationRoles |
| A8 | Requirement vs proposal section | separate objects, linked via satisfaction response |
| A9 | User claim as verified fact | requires explicit promotion with supporting claim |
| A10 | County statistic as city statistic | geography mismatch detectable |
| A11 | Proposal/business plan collapse | distinct ArtifactTypes |
| A12 | Synthetic testimonial | only source-backed VERIFIED claims support testimonial facts |
| A13 | CommonGrants lossy round trip | explicit loss report (`loss_notes`), never silent truncation |
| A14 | Provider ID collision | same string in two namespaces → distinct identifiers |
| A15 | Cross-tenant relationship | rejected when tenant mismatches an endpoint |
| A16 | Floating money | rejected by `validate_amounts` (Decimal-only) |
| A17 | Impossible state jump | IDEA→SUBMISSION_READY rejected by transition validator |
| A18 | Stale eligibility | rev-1 decision + rev-2 target → stale/incompatible |
| A19 | Artifact uses superseded fact | flagged, traceable, QA-detectable |
| A20 | Agent invents root entity | `GrantWinnerCompany` / `OpportunityObject` rejected by known-type guard |

Plus: identifier normalization is idempotent (property guard).
