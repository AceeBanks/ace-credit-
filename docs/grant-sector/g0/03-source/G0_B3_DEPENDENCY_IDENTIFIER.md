# G0-B3 — Dependency Invalidation & External Identifier Verification (C13-C14)

## Scope

Ensures stale upstream facts cannot masquerade as current downstream work (B3.C13), and operationalizes the Book 2 identifier model against external sources (B3.C14).

## C13 — Dependency Invalidation Protocol

Config of truth: `config/g0/source/dependency_identifier.yaml` · Prototype: `prototype/g0/source/dependency_invalidation.py`

Invalidation states: `CURRENT`, `STALE_RECOMPUTE_REQUIRED`, `STALE_REVIEW_REQUIRED`, `INVALID`, `SUPERSEDED`.

A `DependencyGraph` tracks edges from downstream artifacts to the upstream fact classes they depend on, enabling **selective invalidation** — a change only marks the affected nodes stale, never the entire world. P0/P1 signals map to specific target artifacts.

Declared dependencies (from the plan):

| downstream artifact | upstream facts |
|---|---|
| `eligibility_decision` | deadline, eligibility, filings, required attachments |
| `match_explanation` | deadline, eligibility, match/share, award ceiling |
| `requirement_set` | deadline, required attachments |
| `draft_context_bundle` | requirements, financial filings |
| `proposal_section` | requirements, community stats, historical award |
| `budget` | award ceiling/floor, match rules, project assumptions |
| `submission_package` | requirements, submission instructions |

Propagation: a deadline/eligibility amendment → new `SourceSnapshot` → `SourceChangeEvent` (P0) → new `OpportunityRevision` → downstream decisions set `STALE` and queued for runtime recompute/review. Selectivity means a deadline-only change does not invalidate unrelated historical-winner research, and a **nonmaterial P2 change invalidates nothing**.

## C14 — External Identifier Verification Protocol

Config of truth: `config/g0/source/dependency_identifier.yaml` · Prototype: `prototype/g0/source/identifier_verification.py`

Verification states: `UNVERIFIED`, `USER_ASSERTED`, `SOURCE_ASSERTED`, `VERIFIED_OFFICIAL`, `CONFLICTED`, `EXPIRED/SUPERSEDED`.

A `VerificationEvent` records the identifier namespace, value, entity, verifying source snapshot, method, effective period, and result.

**Hard rule: an external ID claimed in chat does not become verified automatically** (it is `UNVERIFIED`). Examples:
- Client-provided EIN → `USER_ASSERTED`; IRS record match → `VERIFIED_OFFICIAL`.
- UEI from SAM source → `VERIFIED_OFFICIAL`.
- FIPS via geography resolver → `VERIFIED_OFFICIAL/REFERENCE`.
- Georgia portal ID via issuer portal snapshot → `VERIFIED_OFFICIAL`.

**Conflicting verified IDs trigger an identity conflict.** The same value in different namespaces remains distinct (an EIN value is never conflated with a Georgia portal ID even if the literal string matches).

## Tests

`tests/g0/book3/test_dependency_identifier.py` — 12 tests covering:
- deadline-only change invalidates only deadline dependents (budget untouched);
- eligibility change invalidates eligibility + readiness;
- budget-ceiling change invalidates budget/match; P2 change invalidates nothing;
- recompute restores CURRENT; signal-based selective invalidation;
- chat-claimed ID stays UNVERIFIED;
- user-asserted → official-verified progression;
- conflicting verified IDs trigger identity conflict;
- same value in different namespaces stays distinct.

## Validation

- Validator CLI: `python tools/g0/validate_dependency_identifier.py` → **PASS**
- Book 3 suite: 92 passed (80 prior + 12 new)

## Commits

- `G0-B3-C13-C14` chapter band.

## Status

PASS — dependency invalidation and identifier verification are fail-closed and under test.