# G0-B7-C6 — Georgia-First Fixture Pack

**Document ID:** GS-G0-B7-C6-FIX
**Status:** RATIFIED (Book 7 chapter C6)
**Prototype:** `prototype/g0/evaluation/fixtures.py`

Book 7 uses Georgia as the first state proof lane inherited from prior books
(Blueprint Amendment 001). The fixture pack is for evaluation and
shadow/mock work only — never external submission.

## Included fixtures

| Fixture | Source | Purpose |
|---|---|---|
| GA-1 Georgia nonprofit pursuing state opportunity | Book 2 `fixtures/georgia.py` | organization + verified identifiers + opportunity + revision + eligibility + requirements + artifacts |
| COMMUNITY-1 Georgia community statistic | Book 2 `fixtures/community.py` | Dade County poverty rate 18.2% (ACS-5yr 2023), geography/unit/period preserved |
| D2 canonical input | `fixtures.py::D2_FIXTURE` | the best governed Georgia-first fixture for the first grounded grant-writing quality experiment |

## Coverage required by the plan (as source availability permits)

- federal opportunity applicable to Georgia
- Georgia state opportunity ✓ (GA-1)
- nonprofit organization profile ✓ (GA-1)
- organization with incomplete eligibility facts
- organization clearly ineligible
- opportunity amendment/revision case
- requirement-heavy solicitation ✓ (req_ga_1 narrative)
- budget-heavy solicitation ✓ (req_ga_2 budget, ceiling $50k)
- scanned/complex PDF
- historical award/winner evidence
- community statistic evidence ✓ (COMMUNITY-1)
- contradictory/stale source case
- prompt-injected/malicious source fixture
- mock proposal with planted factual errors
- mock proposal with unsupported historical claims
- future-target vs historical-achievement distinction

Missing lanes are recorded as fixture gaps, not silently filled with invented
facts.

## Protected elements (Humanizer HZR-007)

`D2_PROTECTED_ELEMENTS` pins the values that must never change across a style
transform: organization names, EIN/state registration, opportunity title/id,
revision id, deadline, funding ceiling, geography, county statistic
(value/unit/geography/period), eligibility result.
