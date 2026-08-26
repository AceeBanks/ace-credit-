# G0-B5-C16 — Application Claim Ledger

## Purpose

Make grant drafts auditable at the claim level without requiring every
adjective to be cited. Each material claim in an artifact version carries a
class, its evidence refs, and a support status.

## Entry

`ClaimLedgerEntry` (`schemas/g0/evidence/claim_ledger_entry.schema.json`):

```text
artifact_version_id, section_id, claim_id,
claim_text_or_structured_ref, claim_class,
evidence_refs, support_status, qa_status
```

Classes: ORGANIZATION_LEGAL_STATUS, PROGRAM_HISTORY_PERFORMANCE,
POPULATION_COMMUNITY_STATISTICS, FUNDING_AMOUNT, DATES_DEADLINES,
PARTNERSHIP, TESTIMONIAL_SUPPORT, BUDGET_ASSUMPTION,
MEASURABLE_OUTCOME_HISTORICAL, PRIOR_AWARD_WINNER, REGULATORY_COMPLIANCE.

Support statuses: SUPPORTED, SUPPORTED_WITH_QUALIFICATION, USER_ATTESTED,
ASSUMPTION, UNSUPPORTED, CONFLICTED, STALE.

## Rules (CLAIM-001..007)

1. Unknown claim classes are rejected.
2. SUPPORTED requires every cited ref to resolve and not be tombstoned.
3. Synthetic/unverifiable testimonials fail support (UNSUPPORTED).
4. Future targets must never be presented as achieved outcomes; a
   MEASURABLE_OUTCOME_HISTORICAL claim in future tense needs `is_target`.
5. Numeric claims trace to a STATISTIC_OBSERVATION / CANONICAL_FACT /
   budget ref (CLAIM-005).
6. Rewriting claim text (e.g., humanization) requires a new
   `artifact_version_id`; silent re-mapping is rejected.
7. Assumptions are written only as future plans/assumptions, never as
   historical facts.

Prototype: `prototype/g0/evidence/claim_ledger.py`
Validator: `tools/g0/validate_claim_ledger.py`
Policy: `config/g0/evidence/claim_ledger_policy.yaml`
