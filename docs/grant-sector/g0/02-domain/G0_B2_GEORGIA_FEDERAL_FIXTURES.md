# G0 Book 2 — Chapter C17: Georgia + Federal Fixture Architecture

## Decision

Ground the ontology in realistic first-client data shapes before Book 3 builds
source governance. Fixtures are **semantic examples, not live adapters** — Book
3 governs SourceRegistry/Snapshot and G1 builds ingestion.

Sources: `prototype/g0/domain/fixtures/` (georgia.py, federal.py, community.py).

## Scenarios

| Scenario | Represents | Fixture |
|---|---|---|
| GA-1 | Georgia nonprofit → state opportunity: Organization, verified identifiers (IRS EIN + GA SOS), Georgia OPB opportunity/revision, eligibility rules + ELIGIBLE decision, requirements, ApplicationProject, proposal + business plan artifacts, PROMOTED canonical fact with supporting claim | `GA_1` |
| FED-1 | Federal opportunity with assistance listing: Program (ALN 93.569) → Opportunity → Revision, eligibility rule (no debarment), ApplicationProject | `FED_1` |
| AWARD-1 | Historical winner intelligence: funder/recipient Organizations, opportunity, Award with amount + USAspending external id | `AWARD_1` |
| COMMUNITY-1 | Georgia community statistic: county poverty rate with geography, population, reference period, dataset version, methodology — never flattened to a bare number | `COMMUNITY_1` |

Federal classes covered: Grants.gov/Simpler-style opportunity, SAM/Assistance
Listing (ALN), USAspending award, IRS/EIN identity. Georgia classes: GA OPB
opportunity, GA SOS identifier, GA-awarded record. Census/ACS/SAIPE context via
the ACS statistic fixture.

## Validation

Every scenario validates against the **derived domain schemas** (catalog is
the single source of truth; unset optionals are omitted) and
**relationship/state invariants**:

- ApplicationProject anchored to the EXACT OpportunityRevision used by the rule
  set and decision
- decision ELIGIBLE with per-rule results; facts PROMOTED with supporting
  claims (model invariant engaged)
- program → opportunity → revision chain intact
- award recipient/funder resolve to canonical Organizations; external ids never
  replace internal identity
- statistic context (geography/population/reference period) preserved

## Tests (12 in `test_fixtures.py`)

- all four scenarios present; each validates against schemas
- GA-1 / FED-1 / AWARD-1 / COMMUNITY-1 schema validity + invariants

Run: `python -m pytest tests/g0/book2/test_fixtures.py -q` — **12 passed**.
