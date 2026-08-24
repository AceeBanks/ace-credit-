# R0 Grant-Domain Data & Source Connectivity Deep Hunt

**Document ID:** GS-R0-DATA-001  
**Version:** 0.1  
**Status:** DEEP-HUNT COMPLETE / G0 INPUT  
**Date:** 2026-08-24

---

## 0. Executive conclusion

The Grant platform does **not** have a data scarcity problem. It has a **source-normalization, authority, freshness, and coverage problem**.

A strong first production system can be built primarily on free/open U.S. government sources for federal opportunities, awards, subawards, nonprofit identity/filings, audit history, and community-need statistics. Private-foundation/corporate opportunity coverage is the major area where a paid source such as Candid or a governed crawler network materially improves coverage.

The strongest new discovery is **CommonGrants**, an HHS-backed open standard for opportunities, applications, and awards. We should not invent an incompatible external grant schema. Our richer internal domain model should map to/from CommonGrants wherever practical.

The data fabric should therefore be four lanes:

```text
LANE A — OFFICIAL OPPORTUNITIES
Grants.gov / Simpler.Grants.gov / SAM Assistance Listings / state portals

LANE B — HISTORICAL AWARDS & WINNERS
USAspending / SAM subawards / agency award systems / Candid grants

LANE C — ORGANIZATION & CAPACITY INTELLIGENCE
IRS TEOS / 990 XML / EO BMF / ProPublica / FAC / Candid

LANE D — COMMUNITY NEED / IMPACT EVIDENCE
Census / SAIPE / CDC PLACES / SVI / USDA / BLS / BEA / NCES / HUD / topic sources
```

No lane alone is authoritative for everything. Each source is authoritative only for the facts it actually owns.

---

# 1. Source authority tiers

## Tier A — Primary official source

Examples:

- Grants.gov opportunity record and official attached solicitation;
- issuing-agency solicitation page;
- SAM Assistance Listing;
- USAspending award record;
- IRS filing or tax-exempt status dataset;
- FAC audit filing;
- Census/CDC/BLS/BEA official statistics.

Use: hard eligibility, deadline, funding ceiling, award history, legal/compliance facts, cited need statements.

## Tier B — Official secondary/derived source

Examples:

- agency-specific award systems such as HHS TAGGS;
- state centralized portals;
- NCES derived education data;
- CDC/ATSDR indices derived from Census and other inputs;
- USDA derived food-access indicators.

Use: domain enrichment, winner patterns, community evidence.

## Tier C — Curated commercial/third-party source

Examples:

- Candid Grants API;
- Candid Open Grant Opportunities API;
- ProPublica Nonprofit Explorer.

Use: enrichment, private-philanthropy coverage, convenience, historical research. Never override a conflicting current Tier A source without explicit reconciliation.

## Tier D — Web-discovered source

Examples:

- corporate foundation pages;
- local foundations;
- community foundations;
- issuer newsletters;
- local/state agency pages without APIs.

Use: discovery and evidence only after page/document snapshotting and authority verification.

---

# 2. Federal opportunity discovery — P0

## 2.1 Grants.gov REST API

**Decision:** ADOPT as primary federal opportunity adapter.

Confirmed capabilities:

- public `search2` endpoint;
- public `fetchOpportunity` endpoint;
- search by keyword, opportunity number/status, eligibility, agency, Assistance Listing number, funding category/instrument;
- production and staging environments;
- additional applicant/grantor APIs with keys where required.

Important: basic opportunity search/fetch can operate without authentication. This makes it ideal for the first vertical slice.

### Adapter output

Normalize into our internal `GrantOpportunity`, preserve:

- Grants.gov opportunity ID;
- opportunity number;
- title;
- agency;
- Assistance Listing numbers;
- status;
- open/close dates;
- eligibility categories;
- funding instruments/categories;
- source URL;
- raw payload hash;
- fetch timestamp;
- revision/version state.

## 2.2 Simpler.Grants.gov

**Decision:** ADOPT API/data-model learnings; track actively.

The HHS `simpler-grants-gov` project is the open-source modernization of Grants.gov. Its public repository contains API, frontend, infrastructure, architecture decisions and opportunity schemas. The public developer service currently supports API-key access for search and detailed opportunity retrieval, but does not support applying/posting through the API yet.

This repository is CC0/public-domain dedicated and is therefore an unusually useful source of domain semantics and tests.

### Important consequence

We should follow Simpler.Grants.gov development because it is likely to become increasingly important to future application interoperability.

## 2.3 CommonGrants protocol

**Decision:** **ADOPT as external interoperability target.**

HHS/CommonGrants defines an open standard for sharing:

- funding opportunities;
- applications;
- awards.

It already provides:

- technical specification;
- data models;
- OpenAPI docs;
- TypeSpec core library;
- TypeScript SDK/client;
- Python SDK/client;
- FastAPI template;
- custom-field catalog;
- planned forms and AI tooling.

### Architectural change

Our internal domain may be richer, but every core object should have an explicit CommonGrants compatibility mapping where sensible.

```text
Internal GrantOpportunity ──map──> CommonGrants Opportunity
Internal ApplicationProject ─map──> CommonGrants Application
Internal Award/Outcome ─────map──> CommonGrants Award
```

This significantly reduces long-run vendor lock-in and gives us a path toward future grant-system interoperability.

## 2.4 SAM.gov Assistance Listings API

**Decision:** P0/P1 enrichment adapter.

SAM Assistance Listings describe federal programs that provide grants, loans, scholarships, insurance and other assistance. GSA released a new Federal Assistance Listings API in 2026 for bulk consumption.

Use it to enrich opportunity records with durable program-level context rather than treating an individual solicitation as the entire history of a funding program.

Key identity: Assistance Listing Number (ALN; former CFDA number).

---

# 3. Federal award / winner intelligence — P0

## 3.1 USAspending API

**Decision:** ADOPT as primary federal award-history adapter.

USAspending provides comprehensive award data and does not currently require API authorization for standard endpoints. It supports:

- award search;
- recipient/geographic breakdowns;
- Assistance Listing references;
- assistance downloads;
- custom award downloads;
- subaward/transaction search;
- bulk database/download paths.

### Primary Grant use

For any federal opportunity/ALN:

```text
current opportunity
    ↓ ALN / agency / keywords
historical USAspending awards
    ↓
recipient cohort
amount distribution
geography
award frequency
award duration/transactions
known prior winners
```

This becomes the foundation of federal “winner research.”

### Data warning

An award record shows that funding was made; it does not prove a recipient's proposal text caused the award. The product must distinguish observed winner attributes from inferred success factors.

## 3.2 SAM.gov subaward API

**Decision:** P1.

SAM moved FSRS subaward reporting into SAM.gov in 2025 and advertises a public subaward API for bulk data.

Use for:

- prime→subrecipient relationships;
- local downstream funding patterns;
- identifying intermediary organizations;
- discovering organizations repeatedly receiving pass-through funds.

This gives the Evidence Graph a more complete funding network than prime-award data alone.

## 3.3 Agency award systems

### HHS TAGGS

**Decision:** P1 high-value specialized adapter.

TAGGS supports HHS grant award and recipient searches from FY2005 onward, including Assistance Listings, OPDIV, recipient, award title/number, state, dates and amounts, with CSV/XLSX exports.

Use when an opportunity belongs to HHS because TAGGS can provide richer HHS-specific context than a general federal source.

### NIH RePORTER

**Decision:** P2 specialized research/health adapter.

NIH RePORTER exposes a Project API with grant/project identifiers, activity codes, administering institutes and detailed project metadata.

Useful for scientific/health nonprofit applicants; unnecessary for general MVP.

### Other agency-specific systems

NSF, SBIR/STTR and other award systems should be added only when client/program mix justifies them. USAspending remains the cross-agency baseline.

---

# 4. Organization identity, legal status and financial intelligence — P0

## 4.1 IRS Tax Exempt Organization Search / bulk data

**Decision:** ADOPT as primary nonprofit legal/filing source.

IRS exposes public datasets for:

- Form 990/990-EZ/990-PF/990-T filings;
- Form 990-N;
- Publication 78 deductible-organization data;
- automatic revocation;
- determination letters;
- EO Business Master File extracts;
- 1023-EZ approval data.

IRS also publishes current Form 990-series e-file XML bulk downloads and annual/monthly index files.

### Internal organization intelligence

Use EIN as a major canonical identity key where applicable and derive:

- legal name/address;
- exempt status/subsection;
- ruling/status information;
- filing history;
- revenue/expenses/assets;
- grants paid by private foundations via 990-PF;
- officers/compensation where relevant and public;
- program/service descriptions where available;
- compliance/freshness indicators.

Do not expose every public filing field to every worker. Personal/business financial data still requires scoped access.

## 4.2 EO Business Master File

**Decision:** P0 organization registry/cache seed.

The EO BMF is cumulative, downloadable CSV by state/region, and updated from IRS records. It is useful for resolving EIN/name/location and basic exempt-organization identity without parsing full filings.

## 4.3 ProPublica Nonprofit Explorer API v2

**Decision:** P1 convenience/enrichment adapter.

The API exposes the database behind Nonprofit Explorer through REST/JSON and can be joined to raw IRS filings using EIN. The site includes millions of annual returns and links to machine-readable filing data and nonprofit audit documents.

Use it to accelerate research/UI, but IRS remains authoritative for legal filing facts.

## 4.4 Federal Audit Clearinghouse

**Decision:** **P0/P1 major capacity/risk intelligence source.**

FAC data is public-domain and available through search, CSV and API. It contains Single Audit packages for non-federal entities meeting the federal-assistance expenditure threshold, including financial statements, federal awards and sometimes audit findings.

This source can answer questions that ordinary grant tools miss:

- Has this organization managed significant federal assistance before?
- Which federal programs has it administered?
- Were material findings reported?
- What is its scale of federal-award management?

### Guardrail

Audit findings are context, not a simplistic risk score. They require date, severity, corrective-action and resolution context.

---

# 5. Private foundation / corporate opportunity and winner data

This is the major non-free/open gap.

## 5.1 Candid Grants API

**Decision:** HIGH-VALUE OPTIONAL PAID DATA LAYER.

Candid's Grants API covers funders, recipients and grant transactions and combines foundation direct reporting, IRS 990/990-PF information, foundation websites and other public sources. Candid states new grants are published to its API every business day.

Useful fields include funder/recipient identity, amount, fiscal year, descriptions, program areas, and paid taxonomy fields for subject/population/support strategy.

Current published starting price for Grants API is about **$6,000**; therefore it should be an optional enterprise-quality enrichment layer, not a dependency required for the MVP.

## 5.2 Candid Open Grant Opportunities API

**Decision:** evaluate before scaling private-grant discovery.

Candid now advertises an Open Grant Opportunities API able to surface live RFP opportunities and filter by subject, population served and geography. Pricing is inquiry-based.

This is likely the cleanest way to expand private philanthropic opportunity coverage if the client can fund it.

## 5.3 Candid nonprofit APIs

Essentials/Premier/Charity Check can reduce organization-verification and profile work, but prices are material. IRS + ProPublica can provide a strong free baseline; Candid becomes an optional quality/convenience upgrade.

## 5.4 Free/private alternative: governed crawl network

For MVP/private-foundation coverage:

```text
foundation registry / known URLs
      ↓
Crawl4AI
      ↓
source snapshot + hash
      ↓
RFP/opportunity extractor
      ↓
human/automated authority check
      ↓
normalized opportunity
```

Use targeted crawling, not uncontrolled internet-wide scraping.

Priority targets:

- community foundations;
- large corporate foundations;
- regional philanthropies;
- issuer RFP pages;
- client-nominated funders.

---

# 6. State/local opportunity connectivity

There is no single national state/local API equivalent to Grants.gov.

Therefore state/local discovery needs a **registry-of-adapters** model.

## 6.1 California — best reference implementation

California has a centralized Grants Portal, and its open-data dataset updates daily and exposes API/download access. The portal covers competitive/first-come grants and loans from California state agencies and includes applicant type/category/deadline information.

**Decision:** build California as the first state adapter after federal MVP because it gives us a clean API/open-data reference implementation.

## 6.2 Texas — crawl/HTML adapters by agency

Texas has multiple grant surfaces rather than one clean open API. Examples include Governor eGrants, HHS Grants Portal, and Texas Education Agency grant opportunities.

**Decision:** use source-specific Crawl4AI adapters with source snapshots and parsers.

## 6.3 Nationwide state strategy

Create `SourceRegistry` records:

```yaml
source_id: state_ca_grants
jurisdiction: US-CA
source_type: opportunity_portal
access_mode: API
refresh_policy: daily
parser_version: ...
authority_tier: A/B

source_id: state_tx_oog_egrants
jurisdiction: US-TX
source_type: opportunity_portal
access_mode: WEB
refresh_policy: daily
parser_version: ...
authority_tier: A
```

Then add states according to client geography and market demand rather than writing 50 adapters before launch.

---

# 7. Community-need / impact evidence fabric

This should become a reusable, typed statistics layer rather than letting research agents randomly Google numbers.

## 7.1 Census ACS 5-year

**Decision:** P0 default demographic source.

ACS covers social, economic, housing and demographic characteristics and provides 5-year estimates down to census tracts and block groups. Current API access requires a Census API key.

Use for:

- population;
- age;
- race/ethnicity where relevant and appropriate;
- household/family structure;
- income;
- poverty;
- unemployment;
- education;
- disability;
- language;
- internet access;
- housing burden;
- commuting;
- insurance and other community characteristics.

## 7.2 Census SAIPE

**Decision:** P0 for poverty claims.

SAIPE provides annual model-based income/poverty estimates for states, counties and school districts and explicitly supports federal-program administration and fund allocation.

Prefer SAIPE over improvised ACS calculations when the claim is specifically county/school-district poverty and a current SAIPE measure exists.

## 7.3 CDC PLACES

**Decision:** P1 health/community-need evidence.

PLACES provides model-based health estimates nationwide at county, place, census tract and ZCTA levels, and datasets are accessible through public Socrata/OData interfaces.

Use for health behaviors, outcomes, prevention/status and social-needs measures when they directly support a proposal.

## 7.4 CDC/ATSDR Social Vulnerability Index

**Decision:** P1 contextual vulnerability measure.

SVI provides tract-level social vulnerability based on Census variables and includes downloadable documented datasets. Use as a contextual index, not as a substitute for the underlying metrics.

Important temporal warning: CDC cautions against comparing percentile ranks across different database vintages as if they are directly comparable.

## 7.5 USDA ERS Food Access / Food Environment

**Decision:** P1 when food/nutrition/community access is relevant.

ERS provides machine-readable CSV/XLSX data and geospatial APIs/ArcGIS services for food-access datasets. Its 2026 Food Environment Atlas includes hundreds of county-level indicators.

## 7.6 BLS API

**Decision:** P1 labor/economic evidence.

BLS Public Data API v2 exposes time-series labor statistics through REST/JSON. Use for employment, unemployment, wages and labor-market context where geography/series support the requested claim.

## 7.7 BEA Regional API

**Decision:** P1 economic-development evidence.

BEA Regional data includes county/state/MSA income, product and employment estimates. Good for economic-development narratives and local economic context.

## 7.8 NCES EDGE / CCD / ACS-ED

**Decision:** P1 education/youth evidence.

NCES provides public school/district characteristics, annual boundaries, demographics and custom ACS education estimates. This is particularly strong for after-school, youth-development and education applications.

## 7.9 HUD housing datasets

**Decision:** P1/P2 housing/community-development evidence.

HUD CHAS provides custom tabulations focused on housing needs and affordability. HUD Fair Market Rent and related datasets can support housing-cost and market context.

## 7.10 Topic adapters later

Possible additional adapters should be driven by actual grant categories rather than collected indiscriminately:

- FCC broadband;
- environmental data/EPA;
- crime/public safety;
- transportation;
- homelessness;
- maternal/child health;
- workforce certifications;
- local open-data portals.

---

# 8. New canonical data objects required

The deep hunt shows we need a dedicated source fabric independent from agents.

## `SourceRegistry`

Stores:

- source identity;
- publisher/authority;
- jurisdiction;
- domain;
- access mode API/BULK/WEB/MANUAL;
- credentials requirement;
- refresh cadence;
- terms/license notes;
- adapter/parser versions;
- health state;
- expected freshness.

## `SourceSnapshot`

Stores immutable fetch evidence:

- source registry ID;
- canonical URL/request;
- requested_at/retrieved_at;
- raw payload/object-store URI;
- payload hash;
- HTTP/API metadata;
- published/effective date where known;
- parser version;
- content identity;
- previous snapshot relationship.

## `ExternalIdentifier`

Must normalize identifiers such as:

- EIN;
- UEI;
- Assistance Listing Number;
- Grants.gov Opportunity ID/Number;
- award ID;
- FAIN;
- agency award number;
- state source ID;
- Candid IDs;
- FIPS geography IDs.

## `StatisticObservation`

For community evidence:

- metric/variable;
- value/unit;
- geography + FIPS;
- population cohort;
- reference period;
- estimate/margin-of-error;
- source snapshot;
- methodology/version;
- allowed interpretation notes.

This prevents generated proposals from detaching statistics from geography, date, source or margin of error.

---

# 9. Grant Intelligence Data Fabric architecture

```text
                    SOURCE REGISTRY
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
      API              BULK DATA           WEB
 Grants.gov            IRS XML/CSV        foundations
 USAspending           FAC CSV            state/local
 SAM                    Census            corporate RFPs
 Candid optional        USDA etc.         agency pages
        │                 │                 │
        └──────────────┬──┴─────────────────┘
                       ▼
                 FETCH / SNAPSHOT
                       │
                 immutable raw data
                       ▼
                 NORMALIZATION
                       │
        CommonGrants-compatible mappings
                       │
        ┌──────────────┼───────────────┐
        ▼              ▼               ▼
 Opportunities       Awards        Organizations
        │              │               │
        └──────────────┼───────────────┘
                       ▼
                   SEMANTICA
            provenance / conflicts
               temporal lineage
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
 ELIGIBILITY / MATCHING       RESEARCH / EVIDENCE
          │                         │
          └────────────┬────────────┘
                       ▼
                APPLICATION FACTORY
```

Semantica is evaluated as the graph/provenance substrate, but canonical operational truth still lives in our product datastore and object snapshots.

---

# 10. Source refresh strategy

Different data needs different cadence.

### Near-real-time / daily

- Grants.gov opportunities;
- state portals with live deadlines;
- Candid open opportunities if licensed;
- targeted corporate/foundation RFP pages.

### Daily/weekly

- award updates for active opportunity research;
- Candid transaction enrichment;
- source page change detection.

### Monthly

- IRS EO BMF;
- organization compliance refresh where appropriate.

### Filing/event driven

- IRS 990 filings;
- FAC audits;
- determination/revocation state.

### Dataset-vintage driven

- ACS;
- SAIPE;
- PLACES;
- SVI;
- USDA;
- NCES;
- BEA/BLS time series.

The product should never translate “last fetched” into “current” without understanding the dataset's own reference period.

---

# 11. MVP source set

The first production-quality source set should be intentionally small but powerful:

### Opportunity

- Grants.gov / Simpler API
- SAM Assistance Listings
- one state open-data source (California)
- targeted web source adapter using Crawl4AI

### Winner/history

- USAspending
- SAM subaward data
- HHS TAGGS only when applicable

### Organization

- IRS EO BMF
- IRS 990 XML
- ProPublica convenience adapter
- FAC

### Need/impact

- Census ACS
- Census SAIPE
- BLS
- BEA
- one domain layer selected by grant category (CDC/NCES/USDA/HUD)

### Optional paid accelerator

- Candid Grants + Open Opportunities

This gives meaningful national capability without requiring dozens of fragile connectors.

---

# 12. New evaluation suites

## Source Adapter Gold Set

For each adapter test:

- discovery recall;
- field accuracy;
- deadline accuracy;
- revision detection;
- stable identity;
- source snapshot reproducibility;
- failure/retry behavior;
- schema drift;
- duplicate detection.

## Winner Research Gold Set

Verify:

- correct opportunity/program → ALN mapping;
- correct historical awards;
- recipient identity resolution;
- no unsupported inference from winner metadata;
- amount/year/geography accuracy.

## Community Evidence Gold Set

Verify every statistic has:

- exact variable;
- geography;
- period;
- source;
- unit;
- margin of error where relevant;
- valid interpretation.

## Source Conflict Set

Deliberately create cases where:

- aggregator deadline differs from issuer;
- old solicitation conflicts with current amendment;
- nonprofit name changes but EIN stays same;
- award source values differ due to transaction timing;
- Census vintages differ.

System must apply source precedence or escalate rather than silently merge.

---

# 13. Cost posture

A surprisingly capable MVP can operate with mostly free/open sources.

### Free/open core

- Grants.gov;
- SAM.gov public data/APIs;
- USAspending;
- IRS;
- FAC;
- Census;
- CDC;
- USDA;
- BLS;
- BEA;
- NCES;
- California open data;
- targeted public web crawling.

### Paid optional

Candid is the main clearly valuable paid accelerator discovered. Current advertised starting prices include roughly $6,000 for Grants API, while its open-opportunity API requires a quote. Treat Candid as a coverage/quality upgrade after we quantify the free-source coverage gap.

---

# 14. R0 decision changes from this hunt

1. **CommonGrants is promoted into G0 as the external interoperability standard candidate.**
2. The source layer becomes a first-class platform subsystem, not a set of tools owned by research agents.
3. `SourceRegistry`, immutable `SourceSnapshot`, `ExternalIdentifier`, and `StatisticObservation` become core contracts.
4. USAspending + IRS + FAC now form a strong free federal winner/capacity intelligence layer.
5. Candid becomes optional paid enrichment, not MVP dependency.
6. State/local expansion becomes registry-driven and geography-prioritized rather than “build all 50 states.”
7. Community evidence becomes typed/statistical infrastructure rather than arbitrary agent web research.
8. Eligibility and matching must consume normalized source facts, never raw search snippets.
9. Source revision/change detection becomes P0 because grant deadlines and requirements can change.
10. The first vertical slice should use real Grants.gov + USAspending + IRS/FAC + Census data, not mocked domain data.

---

# 15. Handoff to G0

R0 internal salvage + external technology review + grant-domain source research is now sufficient to begin G0 constitutional design.

G0 should freeze:

- authority/source hierarchy;
- CommonGrants mapping policy;
- canonical identifiers;
- source registry/snapshot contracts;
- opportunity/award/organization/evidence schemas;
- freshness/revision semantics;
- deterministic eligibility contract;
- Dual-Hermes handoff contracts;
- data privacy and tenant scope;
- evaluation gates for source adapters and agent outputs.
