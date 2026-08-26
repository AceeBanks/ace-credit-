# G0 Book 2 — Handoff to Book 3

**From:** Book 2 — domain entities & relationships (`G0_BOOK_02_MASTER_IMPLEMENTATION_PLAN_v1.0.md`)
**To:** Book 3 — source governance / provenance (`G0_BOOK_03_MASTER_IMPLEMENTATION_PLAN_v1.0.md`)
**Precondition met:** `ready_for_book3: true` (computed, see `G0_B2_REALITY_LOCK.json`)

## Invariants Book 3 may assume (all executable in `tests/g0/book2/`)

1. **Root entities have stable internal identity** — every entity carries a
   semantic identity prefix (`org_`, `opp_`, `app_`, `fact_`, `claim_`,
   `stat_`, …); external provider IDs are namespaced references and NEVER
   replace internal identity (B2.C4/C5, invariant 01-03).
2. **Opportunity revisions are immutable** — stable root + immutable revision;
   material changes (deadline, eligibility, funding, match, geography,
   attachments, narrative, submission method, cancellation, scoring) invalidate
   dependent decisions; non-material changes do not (B2.C8).
3. **Eligibility decisions anchor to the exact OpportunityRevision** — and
   eligibility evaluation is deterministic: validated rule + canonical facts →
   result; missing evidence is UNKNOWN (aggregate CONDITIONAL), never fabricated;
   LLM narrative can never directly set ELIGIBLE (B2.C10).
4. **Facts require support; claims never auto-promote** — a claim becomes a
   CanonicalFact only through explicit governed promotion with ≥1 supporting
   claim ref; conflicting claims coexist; statistics keep geography/population/
   reference-period context (B2.C9).
5. **Money is Decimal-only** with explicit currency/period and deterministic
   totals; float money is rejected by schema and validator (B2.C12).
6. **State transitions are enumerated and validated** — submission stays
   unreachable in Phase 1; submission-ready never implies submitted (B2.C7,
   invariant 17-18).
7. **Proposal and business plan are distinct artifacts**; Requirement and
   RequirementResponse are distinct and evidence-linked; Artifact and
   SourceSnapshot are distinct semantic types (B2.C11/C13, invariants 12-14).
8. **Historical Awards exist without internal ApplicationProject** (B2.C14).
9. **Georgia is the first-source proof priority** — GA-1/FED-1/AWARD-1/
   COMMUNITY-1 fixtures validate against the same core ontology (B2.C17).
10. **D0 DraftContextBundle is the minimum domain bundle** for the shadow-draft
    harness: exact revision required, eligibility not INELIGIBLE, unsupported
    facts flagged, output state DRAFT/MOCK, no submission capability (B2.C19).
11. **CommonGrants mapping is MECHANISM-only until schemas are vendored** —
    `common_grants_schema_version` is `unpinned` and fails closed; the mapping
    rows must be re-verified against the vendored schemas before production
    compatibility claims (B2.C15). Book 3's source governance should treat the
    vendor step as an explicit checkpoint.
12. **Cross-tenant relationships are rejected**; provider additions never
    change core identity semantics; invented root entity types are rejected
    (B2.C16/C20).

## What Book 3 adds (out of Book 2 scope)

- SourceRegistry / SourceSnapshot governance and source freshness policy
  (Book 2 defines semantic meaning of temporal fields only).
- Eligibility/requirement source extraction pipelines.
- D0 harness consuming `DraftContextBundle` for mock grants.
- CommonGrants schema vendor + mapping row verification.
