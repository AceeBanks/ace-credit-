# G0-B3 — StatisticObservation Policy & Federal/Georgia Source Profiles (C15-C17)

## Scope

Makes quantitative community/impact evidence safe for grant writing (B3.C15), defines the first authoritative federal data lanes (B3.C16), and proves Georgia as the first state-level source fabric (B3.C17).

## C15 — StatisticObservation Data Policy

Config of truth: `config/g0/source/statistic_policy.yaml` · Prototype: `prototype/g0/source/statistics.py`

A statistic may be promoted only when every required dimension is present: metric code/label, value, unit, geography type/id/label, population scope, reference period start/end, dataset name and vintage, estimate type, margin of error, confidence interval, methodology ref, source snapshot ref, and quality state.

Geography is fail-closed: a statistic **never silently crosses geography levels** — a Fulton County statistic cannot be described as a City of Atlanta statistic, and a statewide statistic cannot be represented as a local-county fact. Population/denominator semantics are preserved (percent estimates require a denominator context), and time distinguishes **reference period** from **dataset release/vintage** from **retrieval time**.

Derived statistics carry an explicit formula plus parent observation refs and replay deterministically — only supported formulas (`sum`, `mean`, `rate`) are accepted; arbitrary expressions are rejected rather than evaluated. Client-facing narrative may not overstate precision beyond the source methodology: percent estimates without a margin of error are flagged by the validator.

Latest-vintage policy: an old dataset vintage (e.g. ACS 2019 when 2023 is released) is stale even if retrieved recently.

## C16 — Federal Source Profiles

Config of truth: `config/g0/source/federal_profiles.yaml` · Validator: `tools/g0/validate_source_profiles.py`

The five required federal lanes are declared: Grants.gov/Simpler (opportunities), SAM Assistance Listings (durable program context), USAspending (awards/recipients), IRS EO/BMF/990 (nonprofit legal/status/filings), Census ACS/SAIPE + BLS/BEA/CDC/USDA/NCES/HUD (community statistics). Each profile records role, priority facts, identifier namespaces, capture method, expected revision semantics, freshness policy, rate-limit/auth notes, fixture examples, caveats and fallbacks.

**Namespace discipline:** every profile identifier namespace must exist in the live Book 2 catalog (`config/g0/domain/identifier_namespaces.yaml` — `GRANTS_GOV_OPPORTUNITY`, `ALN`, `UEI`, `USA_SPENDING_AWARD`, `FAIN`, `EIN`, `FIPS`). A profile may never introduce an ungoverned namespace.

The federal domain fixtures (`prototype/g0/domain/fixtures/federal.py`, FED-1/AWARD-1) normalize into the Book 2 core — `GrantOpportunity`, `Program`, `Award` — never a federal-specific root.

## C17 — Georgia Source Profiles

Config of truth: `config/g0/source/georgia_profiles.yaml` · Validator: `tools/g0/validate_source_profiles.py`

Georgia lanes: OPB Grants Portal, OPB Active Grant Programs/Awarded Grants, DCA, GEMA/HS, and a heterogeneous domain agency (EPD). The design goal is proven: **Georgia source fields normalize into the same Book 2 core domain** — a Georgia opportunity is a standard `GrantOpportunity` + `OpportunityRevision`, and Georgia awards/recipients map to standard `Award`/`Organization`. No `GeorgiaGrant` root entity exists.

For sources without structured APIs the **crawled-state rule** applies: registered source → crawler capture → raw snapshot → parser/extractor → normalized candidate → validation/promotion. No crawling directly into `CanonicalFact`. Any portal-specific IDs are stored as namespaced external identifiers (`GA_PORTAL` from the Book 2 catalog).

## Tests

- `tests/g0/book3/test_statistics.py` — required dimensions, geography mismatch, missing reference period, denominator context, derived-stat replay (unsupported formulas fail), latest-vintage staleness;
- `tests/g0/book3/test_federal_fixtures.py` — required lanes, Book 2 namespace catalog, capture/freshness enums, fixture examples, core-type normalization;
- `tests/g0/book3/test_georgia_fixtures.py` — crawled-state rule, no GeorgiaGrant root, exact-revision eligibility anchor, changed webpage → new snapshot + P0 change event, crawler cannot outrank official solicitation.

## Validation

- `python tools/g0/validate_statistics.py` → **PASS**
- `python tools/g0/validate_source_profiles.py` → **PASS**

## Commits

- `G0-B3-C15-C17` chapter band.

## Status

PASS — statistics are geography/time/denominator-safe, and federal/Georgia source profiles are registered, namespaced and fixture-backed.
