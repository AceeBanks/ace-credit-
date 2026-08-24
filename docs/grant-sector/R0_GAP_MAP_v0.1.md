# R0 Gap Map

**Document ID:** GS-R0-GAP-001  
**Version:** 0.2  
**Status:** R0 DATA/SOURCE DEEP-HUNT INCORPORATED  
**Date:** 2026-08-24

---

## 0. Purpose

This map identifies what remains unsolved after:

1. internal `larger-lab`/OCE/Hermes salvage;
2. external generic-infrastructure review;
3. deep grant-domain data/source connectivity research.

R0 has now resolved enough of the *where will the data come from?* question to enter G0. Remaining gaps are primarily canonical contracts, domain logic, production controls, source adapter implementation, and product UX.

---

# 1. Domain-Critical Gaps — Build Ourselves

These capabilities are the product moat and should remain platform-owned.

| Gap | Updated status | Recommended ownership |
|---|---|---|
| Canonical Organization Profile model | Still open; now informed by IRS EIN/EO BMF/990, UEI and FAC | **NEW BUILD** |
| Canonical Grant Opportunity model | Still open; now should map to CommonGrants Opportunity | **NEW BUILD + CommonGrants compatibility** |
| Grant eligibility DSL / normalized rule model | Open | **NEW BUILD** |
| Eligibility evaluator | Open; must consume normalized facts/snapshots | **NEW BUILD** |
| Explainable grant matching model | Open | **NEW BUILD** |
| Grant-specific evidence hierarchy | Source hierarchy now researched; formal rules remain open | **NEW BUILD** |
| Funder / award / past-winner domain model | Data sources now resolved for federal baseline | **NEW BUILD** |
| Grant Evidence Graph schema | Semantica candidate identified; ontology still ours | **NEW BUILD ontology + Semantica bake-off** |
| Application Project state machine | Open; should map to CommonGrants Application where useful | **NEW BUILD** |
| Application blueprint / section dependency graph | Open | **NEW BUILD** |
| Cross-document fact registry | Open | **NEW BUILD** |
| Budget / financial reconciliation engine | Univer candidate identified; canonical model still ours | **NEW BUILD backend + Univer evaluation** |
| Grant requirement coverage engine | Open | **NEW BUILD** |
| Human review / approval gates | Open | **NEW BUILD** |
| Outcome/award feedback model | Open; CommonGrants Award + USAspending/Candid inform schema | **NEW BUILD** |

---

# 2. Grant Data / Source Connectivity — RESOLVED AT ARCHITECTURE LEVEL

The question is no longer whether suitable data exists. It does.

## 2.1 Federal opportunities — resolved candidates

- **Grants.gov REST API** — primary federal opportunity source.
- **Simpler.Grants.gov** — modernization project/API/model source and future interoperability path.
- **CommonGrants protocol** — external open standard for opportunity/application/award interoperability.
- **SAM.gov Assistance Listings** — program-level enrichment via Assistance Listing Number.

### Remaining work

- implement adapters;
- pin schema/API versions;
- establish retry/rate-limit rules;
- build revision/amendment detection;
- define opportunity identity reconciliation;
- create gold-set tests.

## 2.2 Federal historical awards / winners — resolved candidates

- **USAspending API** — cross-agency federal award-history baseline.
- **SAM.gov subaward data/API** — prime→subrecipient relationships.
- **TAGGS** — HHS-specialist award enrichment.
- **NIH RePORTER / other agency systems** — add only when vertical/use case justifies.

### Remaining work

- recipient identity resolution;
- ALN/opportunity→award linkage;
- winner cohort logic;
- no-causal-overclaim guardrails;
- transaction/award timing semantics.

## 2.3 Organization identity / financial / compliance — resolved candidates

- **IRS EO BMF** — registry/basic exempt-organization identity.
- **IRS 990-series XML/bulk data** — official filing/financial source.
- **ProPublica Nonprofit Explorer** — convenience/enrichment API.
- **Federal Audit Clearinghouse** — federal assistance/audit/capacity intelligence.

### Remaining work

- EIN/UEI/entity resolution;
- filing version/freshness semantics;
- financial normalization;
- scoped PII/sensitive field policy;
- audit-context interpretation rules.

## 2.4 Private foundations / corporate opportunities — partially resolved

- **Candid Grants API/Open Grant Opportunities API** — strongest paid structured candidate.
- **Targeted Crawl4AI source network** — free/open MVP path for issuer RFP pages.

### Remaining work

- quantify free-source recall gap;
- Candid commercial/license/business-case decision;
- create private-source registry;
- source-specific crawl policies and change detection.

## 2.5 State/local — architecture resolved, coverage intentionally incremental

- **California Grants Portal/open data** — first clean state API/open-data adapter candidate.
- **Texas and similar states** — source-specific portal crawlers/parsers.

### Remaining work

- adapter registry;
- jurisdiction-driven rollout order;
- coverage metrics;
- state source health/freshness monitoring.

## 2.6 Community need / impact — resolved candidate fabric

Baseline sources:

- Census ACS 5-year;
- Census SAIPE;
- CDC PLACES;
- CDC/ATSDR SVI;
- USDA ERS;
- BLS;
- BEA;
- NCES;
- HUD;
- topic-specific adapters as grant categories demand.

### Remaining work

- typed `StatisticObservation` contract;
- geography/FIPS normalization;
- dataset-vintage semantics;
- margin-of-error handling;
- source-methodology metadata;
- permitted interpretation guidance.

---

# 3. New P0 Data Contracts Identified by Deep Hunt

These are now mandatory G0/G1 contracts.

## 3.1 `SourceRegistry`

Required fields/concepts:

- canonical source ID;
- publisher/authority;
- jurisdiction;
- domain/source class;
- API/BULK/WEB/MANUAL access mode;
- credential requirements;
- terms/license notes;
- refresh policy;
- parser/adapter version;
- expected freshness;
- health/degradation state.

## 3.2 `SourceSnapshot`

Immutable evidence record:

- registry/source identity;
- canonical URL/request;
- retrieved/requested timestamps;
- raw payload/object-store pointer;
- cryptographic content hash;
- HTTP/API metadata;
- effective/published date;
- parser/adapter version;
- prior/revision relationship.

## 3.3 `ExternalIdentifier`

Normalize at least:

- EIN;
- UEI;
- Assistance Listing Number;
- Grants.gov opportunity ID/number;
- federal award ID/FAIN/agency award number;
- state source IDs;
- Candid IDs where licensed;
- FIPS/geographic IDs.

## 3.4 `StatisticObservation`

Must bind a statistic to:

- metric/variable;
- value/unit;
- geography/FIPS;
- cohort/population;
- reference period;
- estimate/MOE where applicable;
- methodology/dataset vintage;
- exact source snapshot;
- interpretation constraints.

---

# 4. CommonGrants Interoperability Gap — NEW G0 PRIORITY

The HHS CommonGrants project defines an open standard for funding opportunities, applications and awards and publishes SDKs/clients/templates.

We should not let our richer internal model become an incompatible island.

G0 must define:

```text
Internal GrantOpportunity ↔ CommonGrants Opportunity
Internal ApplicationProject ↔ CommonGrants Application
Internal Award/Outcome ↔ CommonGrants Award
```

Questions to resolve:

- which CommonGrants fields are canonical vs mirrored;
- how custom/internal fields are namespaced;
- versioning/migration strategy;
- validation/conformance tests;
- whether our public API eventually exposes CommonGrants-compatible endpoints.

---

# 5. Source Trust / Freshness / Conflict — NOW A FIRST-CLASS GAP

Source connectivity without truth discipline would still produce unreliable applications.

G0 needs an executable source precedence model, e.g.:

```text
current official solicitation/amendment
  > current issuing-agency source
  > official federal/state data derivative
  > curated third-party database
  > verified issuer webpage snapshot
  > aggregator/search result
  > user recollection/unverified statement
```

This is only a starting model; precedence must be fact-specific.

Required conflict handling:

- current vs superseded solicitation;
- revised deadlines;
- conflicting award totals due to transaction timing;
- nonprofit name changes with stable EIN;
- Census/statistical vintages;
- third-party vs official source disagreements.

No silent merge. Resolve deterministically when policy allows; otherwise escalate.

---

# 6. Source Change Detection — P0

New architecture requirement from the deep hunt:

Grant opportunities are mutable until close. Therefore source ingestion must model revisions, not just snapshots.

Need:

- hash/content change detection;
- structured field diffs;
- amendment relationships;
- deadline-change alerts;
- eligibility/requirement-change alerts;
- invalidation of dependent Match/Application decisions when material fields change;
- replay/re-evaluation against the new snapshot.

This should feed CEO Hermes as a structured event, not raw webpage text.

---

# 7. External Generic Infrastructure Gaps — Updated

Prior external review substantially reduced these gaps.

| Area | Leading candidate | Remaining decision |
|---|---|---|
| Web extraction | Crawl4AI | benchmark + security hardening |
| Deep research | GPT Researcher patterns | bounded worker integration |
| Document parsing | existing parsers + Unstructured | bake-off |
| Visual parsing | PixelRAG | fallback benchmark |
| Evidence/provenance | Semantica | P0 bake-off |
| Agent regression/red-team | Promptfoo + Hermes Eval Lab | integration/promotion policy |
| Structured validation | Guardrails | select validators only |
| Spreadsheet workspace | Univer | free/Pro feature boundary |
| Connector execution | Activepieces | bounded-use architecture |
| Tool credential proxy | Treg-inspired pattern | independent implementation/license decision |
| Signature/forms | Documenso/DocuSeal | defer/licensing |

No more broad generic-agent framework hunting is required before G0.

---

# 8. Production Infrastructure Gaps Still Open

## 8.1 Multi-tenant identity/auth

Still unresolved implementation choice:

- users/orgs/memberships;
- RBAC/ABAC/relation policy;
- service identities;
- invitations/recovery;
- tenant isolation proof.

## 8.2 Object/artifact storage

Need exact implementation for:

- source snapshots;
- uploads;
- sidechains/traces;
- proposal/deck/XLSX/DOCX/PDF artifacts;
- version/diff lineage;
- encryption/backup/retention.

## 8.3 Observability

Need exact stack for:

- distributed traces;
- tool/model costs;
- source adapter health;
- workflow SLIs;
- evaluation metrics;
- error aggregation;
- security events.

## 8.4 Production document compiler

Still not solved by the external batch. Need deterministic/versioned DOCX/PDF compilation independent of LLM generation.

---

# 9. Evaluation Gaps — Expanded by Data Hunt

## 9.1 Source Adapter Gold Set

Every adapter must prove:

- discovery recall;
- normalized field accuracy;
- deadline accuracy;
- stable identity;
- revision detection;
- source snapshot reproducibility;
- schema-drift behavior;
- duplicate handling;
- retry/failure behavior.

## 9.2 Winner Research Gold Set

Must prove:

- correct opportunity/program/ALN linkage;
- recipient identity resolution;
- amount/date/geography correctness;
- no unsupported causal claims from winner metadata.

## 9.3 Community Evidence Gold Set

Every promoted statistic must carry:

- variable;
- geography;
- reference period;
- unit;
- source;
- margin of error where relevant;
- methodology/vintage;
- valid interpretation.

## 9.4 Source Conflict Corpus

Include deliberate conflicts between:

- current vs old solicitation;
- aggregator vs issuer deadline;
- changed nonprofit names;
- award values at different transaction cutoffs;
- statistical vintages;
- third-party vs official source.

---

# 10. R0 Gap Priority — Updated

## P0 — G0/G1

- canonical grant/org/award/application schemas;
- CommonGrants mapping policy;
- `SourceRegistry`;
- immutable `SourceSnapshot`;
- canonical `ExternalIdentifier` model;
- `StatisticObservation`;
- source authority/freshness/conflict policy;
- revision/change-detection semantics;
- deterministic eligibility contract;
- Dual-Hermes contracts and authority;
- memory promotion/pruning;
- tenant/auth architecture;
- evidence/Semantica decision;
- threat model;
- adapter/eval doctrine.

## P1 — first real vertical slice

- Grants.gov/Simpler opportunity adapter;
- SAM Assistance Listing enrichment;
- USAspending award/winner adapter;
- IRS EO BMF/990 organization adapter;
- FAC adapter;
- ACS/SAIPE evidence adapter;
- California state adapter or one targeted Crawl4AI private source;
- explainable eligibility + matching;
- evidence graph;
- application blueprint/selected sections;
- QA;
- full Personal→CEO→worker→client path.

## P2 — expand after vertical slice proof

- Candid paid integration if ROI justifies;
- broader state/private source network;
- SAM subawards/TAGGS/agency-specialist data;
- CDC/USDA/NCES/HUD domain layers;
- full proposal/business-plan/deck/financial suite;
- outreach hooks;
- Phase 3 outcome/tracker loop.

---

# 11. R0 Closure Condition

R0 is now sufficient for G0.

Remaining work is no longer exploratory infrastructure hunting. It is constitutional/domain design and implementation validation.

The first production vertical slice should consume **real official data**, not mocked grant-domain records, so source authority, revisions, identifiers, evidence and winner research are tested from the beginning.