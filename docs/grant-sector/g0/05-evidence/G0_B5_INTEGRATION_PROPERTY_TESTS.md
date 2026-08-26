# G0-B5-C25 — Integration & Property Tests

## Mandatory invariants (all asserted in `test_integration_properties.py`)

1. Every material operational claim is evidence-linked or explicitly
   qualified.
2. Generated text cannot self-authorize as evidence.
3. SourceSnapshot lineage survives normalization.
4. Claim promotion is explicit.
5. Contradictory evidence is retained.
6. Decisions pin exact input revisions.
7. Historical replay never substitutes current state silently.
8. Dependency invalidation is selective and traceable.
9. Retrieval rank is not authority.
10. Vector indexes are disposable/rebuildable.
11. Graph projections are disposable/rebuildable.
12. Internal canonical IDs survive all projections.
13. Cross-tenant graph/vector access is denied.
14. Explanation packets match decision evidence.
15. Claim ledger survives drafting/QA/humanization transformations.
16. Research findings preserve evidence and limitations.
17. Audit events link to decisions/evidence/output.
18. Eval cases retain lineage.
19. Optional Semantica failure does not destroy canonical operation.
20. Provenance-integrity failure blocks consequential promotion/finalization.

## Property tests

- deterministic derived facts replay exactly (`derived_fact_replay`);
- dependency invalidation is idempotent (same affected set on re-run);
- DecisionRecord serialization round-trip preserves semantics;
- corroboration requires independent upstreams;
- projection rebuild is exercised by the Semantica bake-off (W7) and the
  visibility rebuild contract.

Run: `python -m pytest tests/g0/book5/test_integration_properties.py -q`
(22 passed; Semantica-dependent property tests skip when the scoped
`.bakeoff/` dependency is not on the path).
