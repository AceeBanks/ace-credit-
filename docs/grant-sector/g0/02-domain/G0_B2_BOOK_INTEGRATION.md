# G0 Book 2 — Chapter C21: Book Integration & Property Tests

## Decision

Prove the 22 mandatory domain invariants against the live ontology, plus the
plan's property tests. Every invariant is an executable assertion, not prose.

Tests: `tests/g0/book2/test_domain_book_integration.py` — **27 passed** (22
invariants + 5 properties).

## The 22 mandatory invariants (all green)

1. Every root entity has stable internal identity (prefix scheme, `validate_internal_id`)
2. Every external identifier is namespaced
3. Provider IDs never replace internal primary identity
4. Funder/Recipient/Applicant are role semantics, not duplicate organizations
5. Opportunity revisions are immutable (frozen; append never mutates)
6. Eligibility decisions target the exact opportunity revision
7. ApplicationProject targets the exact opportunity revision
8. Material opportunity changes invalidate dependent decisions (`is_stale`)
9. EvidenceClaim cannot silently become CanonicalFact (explicit promotion + support)
10. Conflicting claims may coexist (CONFLICTED without deletion)
11. Statistics preserve geography/population/time context
12. Proposal and BusinessPlan are distinct artifacts
13. Requirement and RequirementResponse are distinct
14. Artifact and SourceSnapshot are distinct semantic types
15. Historical Award can exist without internal ApplicationProject
16. Money uses decimal/fixed-point semantics (float rejected)
17. State transitions are enumerated and validated (illegal jumps rejected)
18. Submission-ready does not imply submitted (no SUBMITTED artifact status)
19. CommonGrants mappings report loss explicitly (all LOSSY rows carry loss_notes)
20. Every Phase 1 client requirement is representable (C18 matrix all covered)
21. Georgia/federal fixtures validate against the same core ontology
22. D0 DraftContextBundle is representable without agent memory

## Property tests

- serialize → deserialize preserves semantic equality (`asdict` round trip)
- EXACT CommonGrants mapping round trip preserves equality (Award Decimal case)
- revision history append does not mutate the previous revision
- identifier normalization is idempotent (all four rules)
- deterministic state transition validator: same inputs → same verdict

Run: `python -m pytest tests/g0/book2/test_domain_book_integration.py -q`.
