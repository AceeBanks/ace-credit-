# G0-B3 — Promotion, Conflict & Source-Change Governance (C10-C12)

## Scope

Defines how candidate claims become usable evidence/canonical facts (B3.C10), how disagreement is resolved **without destroying evidence lineage** (B3.C11), and how changing source state is converted into explicit governed events with materiality classification (B3.C12).

## C10 — Evidence Confidence & Promotion Model

Config of truth: `config/g0/source/promotion_conflict.yaml` · Prototype: `prototype/g0/source/promotion.py`

Promotion states: `CANDIDATE`, `PROVISIONAL`, `VERIFIED`, `CONFLICTED`, `STALE`, `REJECTED`, `SUPERSEDED`.

Confidence is carried as named components (`source_authority`, `directness_of_support`, `extraction_quality`, `normalization_confidence`, `corroboration`, `freshness`, `contradiction_state`, `identity_resolution`, `geography_population_fit`, `temporal_applicability`). A total score may be computed for ranking, but the components and the decision reason remain on the `PromotionEvent`.

**Promotion policy** is fact-class aware and fail-closed:
- Critical facts (`opportunity_deadline`, `eligibility`, `award_ceiling/floor`, `required_attachments`, `legal_organization_name`, `tax_exempt_status`, `submission_instructions`) require an **official/direct source** (or an explicit governed exception) and adequate confidence — otherwise they stay `CONFLICTED`/`STALE`, never `VERIFIED`.
- Narrative/contextual facts may permit multiple credible institutional sources with citation/caveats.
- Client-controlled facts (`client_program_intent`, `user_preferences_intention`, `internal_project_goals`) are governed by **client approval**.

## C11 — Conflict Resolution Protocol

Config of truth: `config/g0/source/promotion_conflict.yaml` · Prototype: `prototype/g0/source/conflict.py`

Conflict types: `VALUE`, `TEMPORAL`, `IDENTITY`, `GEOGRAPHY`, `UNIT`, `SOURCE_VERSION`, `INTERPRETATION`, `USER_OFFICIAL`.

Resolution methods: `SOURCE_PRECEDENCE`, `EFFECTIVE_DATE`, `SOURCE_REFRESH`, `MERGE_COMPATIBLE`, `HUMAN_REVIEW`, `OFFICIAL_CLARIFICATION`, `UNRESOLVED_BLOCK`.

- A lower-authority stale value becomes **SUPERSEDED**, never deleted — evidence lineage is preserved.
- An equal-authority contradiction does not last-write-win: it becomes `CONFLICTED`.
- **Critical-use block:** an unresolved conflict touching `deadline`, `eligibility`, `amount`, `required attachments`, `legal identity`, or `submission method` makes readiness block or clearly degrade (`ConflictRegistry.readiness_allows` fails closed).
- Human resolution records the method, evidence/value ref, and resolver actor.

## C12 — Revision & Source Change Protocol

Config of truth: `config/g0/source/promotion_conflict.yaml` · Prototype: `prototype/g0/source/source_change.py`

`SourceChangeEvent` carries `old_snapshot_id`/`new_snapshot_id`, `change_class`, `materiality`, `affected_fields`, and a `semantic_diff_ref`. **Raw byte diff is not enough** — classification is driven by structured field/requirement signals.

Materiality classes:
- **P0 — application-critical:** eligibility/deadline/award-ceiling-floor/match/required-attachment/submission-path/geography change; opportunity cancelled; mandatory question changed.
- **P1 — significant strategy/research:** program description, scoring guidance, contact, explanatory guidance, historical award correction.
- **P2 — nonmaterial:** formatting, navigation, nonsemantic typo, irrelevant site chrome.

A **parser-output change with unchanged raw source is distinguished from a true source change** (`is_true_source_change` fails to false when the raw object is unchanged or the change class is `PARSER_OUTPUT_CHANGE`).

## Tests

`tests/g0/book3/test_promotion_conflict.py` — 18 tests covering:
- enum sets in config match the known enums; confidence is non-opaque;
- critical deadline requires official source (else CONFLICTED); official source validates to VERIFIED;
- client approval controls client-intent facts;
- narrative context allows multiple institutional sources;
- lower-authority stale value superseded (not deleted);
- equal-authority contradiction blocks critical use; resolution unblocks; human resolution references evidence + actor;
- deadline amendment → P0; formatting → P2; program-description change → P1; cancellation → P0;
- parser-output change with unchanged raw is NOT a true source change.

## Validation

- Validator CLI: `python tools/g0/validate_promotion_conflict.py` → **PASS**
- Book 3 suite: 80 passed (62 prior + 18 new)

## Commits

- `G0-B3-C10-C12` chapter band.

## Status

PASS — promotion, conflict resolution, and source-change governance are fail-closed and under test.