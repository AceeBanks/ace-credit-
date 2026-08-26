# G0 Book 2 — Test Report & Reality Lock Report

**Test command:** `python -m pytest tests/g0/book2 -q`
**Result:** **255 passed, 0 failed** (full suite; the Reality Lock's inner
derivation run records 254 passed + 1 self-excluded freshness test — see
`evidence.test_results.scope` in `G0_B2_REALITY_LOCK.json`)

## Coverage by chapter

| Suite | Tests | Proves |
|---|---|---|
| `test_domain_glossary.py` | 7 | B2.C1 ubiquitous language: 40+ terms, required fields, no duplicates/banned aliases, Book 1 capability resource types mapped |
| `test_entity_boundaries.py` | 27 | B2.C2-C3: ADR-B2-001..010 boundary scenarios + core entity catalog (21 entities), derived schemas current, money-as-string |
| `test_identity_semantics.py` + `test_external_identifiers.py` | 19 | B2.C4-C5: identity prefixes, resolution rules, opportunity identity, namespace validation |
| `test_relationships.py` | 9 | B2.C6: relationship catalog with cardinality/endpoint validation |
| `test_state_machines.py` | 14 | B2.C7: transition legality, submission unreachable, precondition gates, stale-revision blocks |
| `test_revision_semantics.py` | 15 | B2.C8: immutable revisions, material staleness, non-material no-op, version lineage |
| `test_fact_evidence.py` | 10 | B2.C9: explicit promotion, support requirement, conflict coexistence, statistic context |
| `test_eligibility.py` | 13 | B2.C10: deterministic evaluation, UNKNOWN semantics, supersession, narrative barrier |
| `test_requirements.py` | 8 | B2.C11: multi-artifact requirements, evidence-gated completion, dynamic sections |
| `test_budget.py` | 11 | B2.C12: Decimal-only, deterministic totals/ceiling/match, currency, narrative mismatch |
| `test_artifacts.py` | 8 | B2.C13: Phase 1 families, immutable versions, superseded/mock package exclusion |
| `test_outcomes.py` + `test_common_grants.py` | 20 | B2.C14-C15: evidence-only learning; CommonGrants round trips, extensions, loss, schema pin |
| `test_extension_portability.py` + `test_fixtures.py` | 20 | B2.C16-C17: provider portability; GA-1/FED-1/AWARD-1/COMMUNITY-1 schema-valid fixtures |
| `test_client_vision.py` + `test_draft_context.py` | 23 | B2.C18-C19: 31 client requirements covered; D0 bundle contract + readiness fixture |
| `test_adversarial_domain.py` + `test_domain_book_integration.py` | 48 | B2.C20-C21: A1-A20 attacks fail closed; 22 mandatory invariants + 5 properties |
| `test_book2_reality_lock.py` | 9 | B2.C22: lock is DERIVED — defect injection flips readiness; committed lock equals regeneration |

**Total: 255 tests across 20 suites.**

## Reality Lock reproduction

```bash
python tools/g0/build_book2_reality_lock.py \
  --out docs/grant-sector/g0/00-ratification/G0_B2_REALITY_LOCK.json
```

Exit code 0 ⇔ PASS. Regeneration is deterministic given repository state.

## Lock snapshot (2026-08-26)

| Predicate | Value |
|---|---|
| status | PASS |
| glossary_complete | true |
| entity_boundaries_ratified | true |
| root_entities_with_stable_identity | 1.0 |
| external_ids_namespaced | true |
| relationship_catalog_complete | true |
| state_machine_tests_pass | true |
| revision_replay_tests_pass | true |
| fact_claim_evidence_tests_pass | true |
| eligibility_determinism_contract_pass | true |
| application_document_model_pass | true |
| common_grants_exact_roundtrip_pass | true |
| common_grants_loss_reporting_pass | true |
| client_phase1_domain_coverage | 1.0 |
| georgia_federal_fixture_tests_pass | true |
| d0_draft_context_ready | true |
| adversarial_p0_pass | true |
| p0_open | 0 |
| **ready_for_book3** | **true** |
