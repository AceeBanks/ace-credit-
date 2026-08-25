# G0 Book 8 — Production-Shaped Georgia Grant Vertical Slice Master Implementation Plan

**Document ID:** GS-G0-B8-PLAN-001  
**Version:** 1.0  
**Status:** READY FOR CONTINUOUS EXECUTION AFTER BOOK 7 RATIFICATION  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-25  
**Receives from:** Books 0–7 + Amendments 001–002  
**Hands off to:** Book 9 Runtime Substrate ADR, Clean Production Repository Seed & G1 Handoff

---

# 0. Book Mission

Book 8 is the first full-system proof that the architecture designed in Books 0–7 can operate as one coherent Grant Intelligence and Application Production machine.

The book does not add a new architectural philosophy. It **integrates and attacks the existing one**.

The governing question is:

> **Can one realistic Georgia-centered client journey move from conversational intent to a grounded, explainable, high-quality, submission-ready mock grant package through the exact constitutional, domain, source, agent, evidence, security and evaluation contracts already frozen—without architectural exceptions, hidden manual patches, context pollution, fabricated evidence, or unsafe authority?**

Book 8 is not a demo designed to look impressive.

It is a production-shaped proving ground designed to expose weak seams before the clean G1 production repository is seeded.

The vertical slice must prove that the following work together:

```text
CLIENT / ORGANIZATION
        ↓
PERSONAL HERMES
        ↓
IntentContract
        ↓
CEO HERMES
        ↓
Organization / Project State
        ↓
Grant Discovery
        ↓
SourceRegistry / SourceSnapshots
        ↓
Eligibility Normalization + Deterministic Evaluation
        ↓
Opportunity Ranking / Match Explanation
        ↓
Funder / Winner / Community Research
        ↓
Evidence / Provenance / Decision Records
        ↓
ApplicationProject
        ↓
Requirement Decomposition
        ↓
TaskPlan / Bounded Workers
        ↓
Drafting / Budget / Artifact Production
        ↓
Claim Ledger / QA / Eval Suites
        ↓
Human Review
        ↓
Submission-Ready MOCK Package
        ↓
OutcomeArtifact / ExplanationPacket
        ↓
PERSONAL HERMES
        ↓
CLIENT
```

External submission remains disabled.

---

# 1. Book 8 Is an Integration Book, Not a Redesign Book

Books 0–7 have already established the machine's governing contracts.

Book 8 must **consume** them.

It may expose gaps. If a gap exists, the correct response is:

```text
integration failure
        ↓
trace to responsible Book contract
        ↓
issue amendment/repair
        ↓
re-run affected tests
```

The incorrect response is:

```text
integration failure
        ↓
add a one-off shortcut
        ↓
vertical slice “works”
```

No hidden shortcuts.

No special Georgia-only alternate ontology.

No custom “demo mode” bypassing policy.

No bespoke prompt that carries raw source truth outside Book 3/5 contracts.

No temporary direct DB access for Hermes.

No fake citations.

No manual outcome marked automated unless explicitly represented as human action.

---

# 2. Book Theme

## Intent → Discover → Qualify → Research → Ground → Draft → Validate → Review → Explain → Reconstruct

```text
REALISTIC CLIENT INTENT
        ↓
INTENT PRESERVATION
        ↓
REAL OPPORTUNITY DATA
        ↓
DETERMINISTIC QUALIFICATION
        ↓
RESEARCH & EVIDENCE
        ↓
APPLICATION BLUEPRINT
        ↓
BOUNDED DOCUMENT PRODUCTION
        ↓
FACTUALITY / NUMERIC / REQUIREMENT QA
        ↓
HUMAN REVIEW
        ↓
CLIENT EXPLANATION
        ↓
RESTART / AMENDMENT / FAILURE TESTS
```

---

# 3. North-Star Vertical Slice Scenario

The canonical Book 8 scenario should use a Georgia-centered applicant and at least one real federal or Georgia opportunity.

The exact opportunity may change based on current availability at execution time, but the fixture must satisfy the architectural needs of the test.

## Canonical client profile archetype

A Georgia-based nonprofit or mission-driven organization with enough complexity to exercise the system.

Suggested archetype:

```text
Organization type:
Georgia nonprofit / community organization

Mission domain:
youth workforce development / education / community economic mobility

Geography:
Georgia, with service in one or more counties/communities

Program concept:
after-school / workforce readiness / career exposure / skills development

Funding need:
program expansion, staffing, equipment, participant support, community programming

Evidence needs:
organization identity
program history
community need
population statistics
budget assumptions
partnership/support evidence
```

This is a test archetype, not a hard-coded product niche.

## Opportunity lanes

Book 8 should exercise at least:

### Lane A — Federal / national structured source

Examples:

- Grants.gov/Simpler opportunity applicable to Georgia;
- associated Assistance Listing where relevant;
- USAspending historical award research.

### Lane B — Georgia state or agency source

Examples:

- Georgia OPB/Grants Portal;
- DCA;
- GEMA/HS;
- EPD;
- another registered Georgia agency source appropriate to the archetype.

Lane B may be a full parallel opportunity or a secondary proof of source normalization if no suitable open opportunity exists at execution time.

### Optional Lane C — Private/foundation source

Use one registered private/foundation webpage only if it materially tests Crawl4AI/non-API source ingestion and does not distract from the primary slice.

Agent-Reach remains optional secondary research only.

---

# 4. Success Definition

Book 8 passes only if the slice proves:

1. Personal Hermes can translate client conversation into valid IntentContract.
2. CEO Hermes can plan work without inheriting raw conversational history.
3. organization/project canonical state is reconstructed from durable stores.
4. a real opportunity enters through Book 3 source contracts.
5. opportunity revisions and source lineage are preserved.
6. eligibility rules are normalized and evaluated deterministically.
7. ineligible/unknown conditions cannot be hidden by ranking.
8. matching produces inspectable reasons.
9. funder/winner/community research is evidence-backed.
10. all material research can be exposed to the client.
11. ApplicationProject points to exact OpportunityRevision.
12. opportunity requirements are normalized before drafting.
13. bounded workers receive only relevant context and tools.
14. proposal/business-plan/budget artifacts use canonical/evidence-backed state.
15. material claims enter the Claim Ledger.
16. numerical values reconcile deterministically.
17. QA uses Book 7 gates rather than generic LLM approval.
18. security/tenant/tool boundaries remain intact.
19. human review is explicit and attributable.
20. final state is SUBMISSION_READY_MOCK, not SUBMITTED.
21. ExplanationPacket accurately reflects evidence/decisions.
22. source amendment invalidates only affected downstream state.
23. restart/reconstruction succeeds without hidden chat history.
24. workflow/task accepted state survives runtime restart.
25. failures and optional-component outages degrade according to Books 3–6.
26. cost/latency/reliability telemetry exists.
27. full decision/evidence/audit lineage can be reconstructed.
28. Book 9 receives enough measured evidence to choose runtime substrate rationally.

---

# 5. Hard Inputs from Books 1–7

The slice may not weaken:

## From Book 1

- Personal Hermes initial authority ceiling L1;
- CEO Hermes initial ceiling L2;
- safe drafting is allowed at L2;
- submission/signing/certification remain disabled;
- unknown authority defaults deny;
- client-visible research is required;
- proposal and business plan remain distinct;
- dynamic grant alignment required;
- humanization cannot alter facts silently.

## From Book 2

- stable internal IDs;
- Program ≠ Opportunity ≠ OpportunityRevision;
- ApplicationProject targets exact OpportunityRevision;
- Requirement ≠ RequirementResponse;
- EvidenceClaim ≠ CanonicalFact;
- Artifact ≠ SourceSnapshot;
- proposal/business plan separate;
- deterministic money semantics;
- CommonGrants mappings remain interoperability surfaces.

## From Book 3

- registered sources only;
- immutable SourceSnapshots;
- freshness/precedence/conflict semantics;
- external identifiers namespaced;
- statistics preserve geography/time/methodology;
- material source revisions create SourceChangeEvents;
- Georgia-first source proof;
- hostile source content has no policy authority.

## From Book 4

- Personal/CEO context separation;
- IntentContract / ClarificationRequest / TaskPlan / TaskContract;
- bounded ContextBundle;
- WorkerResult + Sidechain;
- selective memory;
- cold reconstruction;
- no raw giant history propagation.

## From Book 5

- DecisionRecords;
- ProvenanceRefs;
- evidence/claim support;
- contradiction retention;
- selective invalidation;
- Claim Ledger;
- ResearchFinding;
- ExplanationPacket;
- graph/vector projection non-sovereignty.

## From Book 6

- authenticated principals;
- tenant/project/resource scoping;
- capability authorization;
- worker grants;
- tool gateway;
- server-side credentials;
- egress control;
- durable approvals;
- prompt-injection containment;
- audit linkage.

## From Book 7

- Georgia-first eval fixtures;
- grant quality rubric;
- factuality/evidence metrics;
- eligibility/match metrics;
- research metrics;
- Personal/CEO/worker evals;
- memory/context tests;
- security regression hard gates;
- cost/latency/reliability metrics;
- candidate/promotion system.

---

# 6. Required Artifact Set

```text
docs/grant-sector/g0/08-vertical-slice/
├── G0_B8_VERTICAL_SLICE_CHARTER.md
├── G0_B8_CANONICAL_CLIENT_FIXTURE.md
├── G0_B8_OPPORTUNITY_SELECTION_RECORD.md
├── G0_B8_END_TO_END_SEQUENCE.md
├── G0_B8_INTEGRATION_CONTRACT_MATRIX.md
├── G0_B8_SOURCE_INGESTION_REPORT.md
├── G0_B8_ELIGIBILITY_REPORT.md
├── G0_B8_MATCHING_REPORT.md
├── G0_B8_RESEARCH_REPORT.md
├── G0_B8_APPLICATION_BLUEPRINT.md
├── G0_B8_DRAFTING_REPORT.md
├── G0_B8_BUDGET_REPORT.md
├── G0_B8_QA_EVAL_REPORT.md
├── G0_B8_HUMAN_REVIEW_REPORT.md
├── G0_B8_EXPLANATION_PACKET.md
├── G0_B8_SOURCE_AMENDMENT_DRILL.md
├── G0_B8_RESTART_RECOVERY_DRILL.md
├── G0_B8_OPTIONAL_COMPONENT_FAILURE_DRILL.md
├── G0_B8_COST_LATENCY_RELIABILITY_REPORT.md
├── G0_B8_SECURITY_AUDIT_REPORT.md
├── G0_B8_RECONSTRUCTION_PACKET.md
├── G0_B8_GAP_AND_REPAIR_LEDGER.md
├── G0_B8_RUNTIME_EVIDENCE_FOR_BOOK9.md
├── G0_B8_ADVERSARIAL_TEST_REPORT.md
├── G0_B8_REALITY_LOCK_REPORT.md
└── G0_B8_HANDOFF_TO_BOOK9.md

schemas/g0/vertical_slice/
├── slice_run.schema.json
├── client_fixture.schema.json
├── integration_checkpoint.schema.json
├── slice_result.schema.json
├── human_review_packet.schema.json
└── runtime_measurement.schema.json

config/g0/vertical_slice/
├── canonical_scenario.yaml
├── checkpoint_gates.yaml
├── allowed_capabilities.yaml
├── failure_injections.yaml
└── measurement_policy.yaml

prototype/g0/vertical_slice/
├── runner.py
├── checkpoints.py
├── fixtures.py
├── orchestration.py
├── failure_injection.py
├── measurement.py
└── adapters/

tests/g0/book8/
├── test_intake_to_intent.py
├── test_opportunity_ingestion.py
├── test_eligibility_flow.py
├── test_matching_flow.py
├── test_research_flow.py
├── test_application_blueprint.py
├── test_worker_contexts.py
├── test_drafting_flow.py
├── test_budget_flow.py
├── test_claim_ledger.py
├── test_qa_eval.py
├── test_human_review.py
├── test_explanation.py
├── test_source_amendment.py
├── test_restart_recovery.py
├── test_component_degradation.py
├── test_security_boundaries.py
├── test_reconstruction.py
└── test_adversarial_slice.py
```

---

# 7. Chapter B8.C1 — Vertical Slice Charter

Define exactly what the slice proves and what it does not.

## In scope

- realistic client intake;
- one real federal or Georgia grant opportunity as primary;
- optional secondary Georgia/private proof;
- source ingestion/snapshot/revision;
- deterministic eligibility;
- matching;
- funder/winner/community research;
- ApplicationProject;
- requirements;
- bounded agent workflow;
- proposal draft;
- distinct business plan where useful to client scope;
- budget/financial artifact where required;
- claim ledger;
- QA/evaluation;
- human review;
- submission-ready mock package;
- explanation;
- failure/restart/amendment drills.

## Explicitly out of scope

- external submission;
- legally binding certification;
- full 50-state coverage;
- universal private-foundation coverage;
- generalized CRM/outreach platform;
- generalized autonomous company operator;
- production self-modification;
- production multi-region cloud architecture;
- runtime choice by popularity.

Commit: `G0-B8-C1: freeze production-shaped vertical slice charter`

---

# 8. Chapter B8.C2 — Canonical Client Fixture

The fixture must be rich enough to exercise the product but precise enough to evaluate reproducibly.

## Fixture content

### Organization identity

- internal organization ID;
- legal/display name;
- entity type;
- Georgia location;
- EIN/UEI where appropriate or explicitly absent;
- tax/status claims;
- operating history.

### Relationship information

- primary founder/contact;
- user preferences relevant to grant process;
- communication preferences;
- review preferences.

### Program/project concept

- mission;
- problem addressed;
- target population;
- geographic service area;
- program activities;
- current capacity;
- expansion goal;
- requested funding use;
- measurable future outcomes;
- known historical outcomes;
- budget assumptions.

### Evidence status

Every material fixture value declares:

- VERIFIED_OFFICIAL;
- CLIENT_PROVIDED;
- DERIVED;
- INFERRED;
- UNKNOWN;
- CONFLICTED.

The fixture should intentionally contain some missing data to test clarification/unknown handling.

## No magical perfect client

A perfect complete profile would fail to test Personal Hermes clarification and eligibility UNKNOWN behavior.

---

# 9. Chapter B8.C3 — Conversational Intake & Intent Preservation

## Objective

Start the slice from natural client language, not prebuilt structured JSON.

Example intent:

> We want to expand our youth workforce program into two more Georgia counties next year. Find funding that makes sense and build the strongest package we can for the best opportunity.

## Personal Hermes responsibilities

- identify organization/project context;
- use known profile before asking repeated questions;
- distinguish exploration from execution request;
- ask only critical clarifications;
- formulate typed IntentContract;
- preserve desired outcome and constraints;
- avoid making grant-selection decisions itself.

## IntentContract should include

```text
client_goal
organization_ref
project/program_ref
jurisdiction/geography
funding-use intent
deadline urgency
artifact expectations
search scope
risk/approval constraints
unknowns requiring CEO/system resolution
```

## Tests

- no raw conversation dump to CEO;
- missing critical information captured as unknown;
- Personal does not fabricate eligibility facts;
- intent semantic meaning preserved.

---

# 10. Chapter B8.C4 — CEO Planning & Work Decomposition

CEO receives only governed IntentContract + assembled canonical context.

## Required TaskPlan stages

```text
1. verify organization/project state
2. discover opportunities
3. snapshot/normalize candidates
4. hard eligibility screen
5. rank eligible/conditional candidates
6. research top candidate(s)
7. choose primary target with DecisionRecord
8. create ApplicationProject
9. normalize requirements
10. identify evidence gaps
11. plan research/drafting/budget tasks
12. execute bounded workers
13. run QA/evals
14. request human review
15. synthesize result/explanation
```

## Planning quality

CEO must not launch expensive research/drafting before hard eligibility screening unless explicitly justified.

This creates a cost-efficient pipeline:

```text
cheap deterministic filters
        ↓
only qualified opportunities
        ↓
expensive research / drafting
```

---

# 11. Chapter B8.C5 — Real Opportunity Discovery & Selection

## Objective

Use current or archived-real registered sources rather than invented grant records.

## Discovery path

Primary:

- Grants.gov/Simpler and/or registered Georgia source.

Optional:

- private/foundation registered source.

## Candidate record

For each considered opportunity retain:

- canonical Opportunity ID;
- exact revision;
- source refs;
- funding amount/range;
- deadline;
- applicant eligibility summary;
- geography;
- program/funder;
- key requirements;
- freshness state.

## Selection DecisionRecord

Selection must record why opportunity became primary target and why alternatives were rejected/deferred.

Reasons should include hard eligibility before strategic fit.

## Tests

- no search snippet becomes canonical opportunity truth;
- source snapshot exists;
- current revision known;
- stale/conflicted candidates flagged;
- ineligible candidate cannot win ranking.

Commit: `G0-B8-C2-C5: establish canonical client intent planning and real opportunity selection`

---

# 12. Chapter B8.C6 — Program & Funder Enrichment

Enrich the primary opportunity with authoritative/secondary data appropriate to source.

Potential federal enrichment:

- Assistance Listing;
- agency/program context;
- official NOFO attachments;
- award ceiling/floor;
- cost sharing;
- application instructions.

Potential Georgia enrichment:

- agency program page;
- official application packet;
- historical award list;
- geographic/policy context.

Every enrichment enters through Book 3 source contracts.

No research worker may paste unregistered web content directly into canonical facts.

---

# 13. Chapter B8.C7 — Eligibility Normalization

## Objective

Convert opportunity eligibility language into validated structured rule set.

## Pipeline

```text
SourceSnapshot / Requirement text
        ↓
model-assisted candidate extraction
        ↓
schema validation
        ↓
normalization review/rules
        ↓
EligibilityRuleSet
        ↓
DecisionRecord
```

## Rule coverage

At minimum inspect:

- applicant type;
- nonprofit/business/government status;
- geography;
- program purpose;
- target population;
- registration/UEI/SAM where relevant;
- experience requirements;
- cost match;
- financial thresholds;
- funding-use restrictions;
- deadlines;
- required partnerships.

## No unknown collapse

Missing organization fact yields UNKNOWN/CONDITIONAL where applicable.

---

# 14. Chapter B8.C8 — Deterministic Eligibility Decision

Run validated rules against canonical organization/project facts.

## Output

Per-rule:

```text
PASS
FAIL
UNKNOWN
CONDITIONAL
```

Aggregate status:

```text
ELIGIBLE
INELIGIBLE
CONDITIONAL
UNKNOWN
```

## Required proof

Same rule/fact/revision inputs reproduce same result.

## Hard gate

If result is INELIGIBLE, drafting that opportunity as primary target stops.

If CONDITIONAL/UNKNOWN, CEO must surface unresolved facts and decide whether clarification/evidence collection can resolve them before expensive drafting.

---

# 15. Chapter B8.C9 — Match & Strategic Fit

Only eligible/conditional candidates enter strategic ranking.

## Match dimensions

- mission/program alignment;
- geography;
- target population;
- funding-use fit;
- funding amount fit;
- timing/deadline feasibility;
- organization maturity/capacity;
- evidence readiness;
- historical award pattern where relevant;
- competition/strategic considerations;
- application burden.

## Separate scores

Avoid one opaque “94% match.”

Represent:

```text
Eligibility status
Program alignment
Evidence readiness
Operational feasibility
Strategic attractiveness
Overall ranked recommendation
```

## Explanation

Match explanation cites decision inputs/evidence rather than model intuition.

Commit: `G0-B8-C6-C9: prove enrichment deterministic eligibility and explainable matching`

---

# 16. Chapter B8.C10 — Historical Award & Winner Research

## Objective

Use structured award data and issuer evidence to understand prior funding patterns without manufacturing causal claims.

Potential sources:

- USAspending;
- SAM subaward data where useful;
- agency-specific award databases;
- Georgia awarded-grant records;
- official program announcements;
- registered secondary research.

## ResearchFinding outputs

- typical award amount/range;
- recipient organization types;
- geographic distribution;
- repeated recipients where valid;
- program priorities visible in awards;
- project themes;
- limitations/sample size.

## Prohibited inference

Do not state that a descriptive historical characteristic caused winning unless evidence supports causal interpretation.

---

# 17. Chapter B8.C11 — Organization Verification & Capacity Research

Potential sources:

- IRS exempt-organization data;
- 990 data;
- FAC where applicable;
- SAM/entity registration;
- client uploads;
- official organization records.

## Goals

- verify legal identity/status;
- validate financial/capacity claims;
- identify federal award/audit experience;
- resolve conflicting names/addresses;
- avoid re-asking client for public official facts where appropriate.

Private/client claims remain clearly distinguished from verified official claims.

---

# 18. Chapter B8.C12 — Georgia Community Need & Impact Evidence

Use structured public data suitable to the program.

Potential sources:

- Census ACS;
- SAIPE;
- BLS;
- NCES;
- CDC;
- USDA;
- HUD;
- Georgia state/local public data where useful.

## StatisticObservation requirements

Every statistic retains:

```text
metric
value
unit
geography
population
reference period
dataset/version
MOE/confidence where applicable
methodology/source
```

## Program relevance

Do not add statistics merely to make proposal “look researched.”

Evidence must support actual need/impact claims relevant to the project.

## Geography test

County/city/state scopes may not be silently substituted.

---

# 19. Chapter B8.C13 — Research Synthesis

CEO or bounded research synthesis worker converts ResearchFindings into a grant-specific strategy packet.

## Strategy packet

```text
funder/program priorities
historical award observations
community need evidence
organization strengths
organization gaps
competitive considerations
specific alignment opportunities
risks / uncertainties
recommended narrative emphasis
claims not safe to make
```

This packet becomes visible to the client and is also consumed by drafting.

No hidden research-only reasoning required.

Commit: `G0-B8-C10-C13: build evidence-backed winner organization and Georgia impact research`

---

# 20. Chapter B8.C14 — ApplicationProject Creation

Create durable ApplicationProject only after primary opportunity is selected.

Must bind:

- tenant;
- organization;
- project/program concept;
- exact OpportunityRevision;
- EligibilityDecision;
- MatchDecision;
- primary source/evidence set;
- workflow state;
- assigned CEO/task lineage.

Initial lifecycle:

```text
QUALIFYING
→ RESEARCH
→ DRAFTING
→ QA
→ HUMAN_REVIEW
→ SUBMISSION_READY
```

No SUBMITTED transition in Book 8.

---

# 21. Chapter B8.C15 — Requirement Decomposition

## Objective

Normalize the actual solicitation/application instructions before writing.

Extract:

- narrative questions;
- forms;
- attachments;
- certifications;
- budget requirements;
- partnership letters;
- financial documents;
- formatting/word limits;
- scoring criteria;
- submission instructions;
- deadlines.

## Requirement map

Each requirement has:

```text
source locator
mandatory/optional
response type
constraints
required evidence
response artifact/section
completion state
```

## No template-first drafting

The client 18-section profile can enrich proposal structure, but solicitation requirements dominate required coverage.

---

# 22. Chapter B8.C16 — Application Blueprint

The blueprint is the plan before prose.

## Blueprint content

```text
Requirement → planned response
Requirement → evidence
Requirement → source/citation strategy
Requirement → responsible worker
Requirement → artifact/section
Requirement → budget linkage
Requirement → unresolved gap
```

Also include opportunity-specific narrative strategy:

- founder/organization story emphasis;
- mission alignment;
- need statement;
- program design;
- outcomes;
- community impact;
- sustainability;
- budget justification.

## Gate

Do not start full drafting until mandatory requirements are mapped or explicitly marked unresolved.

---

# 23. Chapter B8.C17 — Worker Task Decomposition

Create bounded TaskContracts for specialist work.

Possible workers:

- requirement analyst;
- funder research;
- winner research;
- community evidence;
- narrative drafter;
- budget builder;
- QA factuality;
- QA requirement coverage;
- artifact formatter.

## Worker context rule

Each worker gets only:

- task instructions;
- relevant application/project facts;
- relevant requirements;
- relevant evidence;
- relevant style/profile constraints;
- permitted capabilities/tools.

No worker gets full client chat history.

No worker receives unrelated application data.

---

# 24. Chapter B8.C18 — Grant Proposal Drafting

## Objective

Produce a realistic, grant-specific proposal artifact from governed context.

The draft must be dynamic to the opportunity, not a generic client template with swapped funder name.

## Required behavior

- directly answer solicitation requirements;
- use evidence-backed community need;
- use organization facts accurately;
- distinguish historical facts from future targets;
- align mission/program with funder priorities;
- use measurable outcomes;
- coordinate with budget;
- preserve uncertainty/unknown gaps;
- avoid fabricated partnerships/testimonials;
- preserve Claim Ledger mappings.

## Proposal profile

The client-requested richer multi-section proposal structure may be used as a production profile where compatible, but funder-required fields/questions remain authoritative.

---

# 25. Chapter B8.C19 — Business Plan / Supporting Artifact Production

Because the client vision includes a distinct business plan/supporting package, the slice should produce at least one supporting artifact beyond the proposal where it adds meaningful coverage.

Possible outputs:

- business plan;
- pitch deck outline;
- goal sheet;
- partnership-letter checklist;
- financial package.

## Hard rule

Supporting artifact uses shared canonical facts but has its own semantic purpose.

Do not duplicate the proposal with a different title.

---

# 26. Chapter B8.C20 — Budget & Financial Package

## Objective

Prove narrative and numbers reconcile.

Budget should include realistic line items appropriate to scenario.

Requirements:

- decimal monetary values;
- currency explicit;
- totals deterministic;
- requested amount respects opportunity ceiling/floor where relevant;
- match/cost-share handled where applicable;
- narrative references match budget values;
- assumptions explicit;
- unsupported historical numbers not invented.

## QA

A budget inconsistency blocks SUBMISSION_READY.

Commit: `G0-B8-C14-C20: build application project blueprint bounded drafting and budget package`

---

# 27. Chapter B8.C21 — Claim Ledger Completion

Every material factual claim in generated artifacts should be classified.

Support statuses:

- SUPPORTED;
- SUPPORTED_WITH_QUALIFICATION;
- USER_ATTESTED;
- ASSUMPTION;
- UNSUPPORTED;
- CONFLICTED;
- STALE.

## Material claims include

- legal/status claims;
- program history;
- participant history;
- partnerships;
- statistics;
- award history;
- dates;
- monetary values;
- budget assumptions;
- outcome history.

## Gate

Unsupported high-materiality claim blocks internal approval.

---

# 28. Chapter B8.C22 — Deterministic QA

Run deterministic checks before subjective evaluation.

Examples:

- all mandatory requirements mapped;
- word/character/page constraints where machine-checkable;
- deadline/revision consistent;
- citations resolve;
- claim ledger complete enough;
- budget reconciles;
- proposal/business-plan shared facts consistent;
- names/IDs consistent;
- target vs historical outcome language consistent;
- no prohibited submission state;
- required artifacts present.

---

# 29. Chapter B8.C23 — Book 7 Evaluation Suite

Apply ratified quality suites:

- grant-draft quality;
- factuality/evidence;
- eligibility/match;
- research quality;
- Personal Hermes behavior;
- CEO Hermes behavior;
- worker boundaries;
- memory/context;
- security regressions;
- cost/latency/reliability.

## No one-score pass

Use dimension bundle + hard gates.

A quality weakness may require repair while security/factuality failure is hard block.

---

# 30. Chapter B8.C24 — Human Review

A human reviewer receives structured review packet rather than unbounded raw logs.

Packet includes:

- opportunity/revision;
- eligibility summary;
- match rationale;
- research findings;
- draft artifacts;
- requirement coverage;
- claim ledger issues;
- budget validation;
- known uncertainties;
- QA/eval results;
- exact items requiring human confirmation.

## Human actions

- approve internal draft;
- request edits;
- confirm client-provided fact;
- reject unsupported claim;
- resolve non-automatable ambiguity.

## Audit

Every material human decision is attributable.

Commit: `G0-B8-C21-C24: complete claim ledger deterministic QA eval and human review`

---

# 31. Chapter B8.C25 — Submission-Ready Mock Package

The final package should be realistic enough to demonstrate client value but clearly not externally submitted.

## Package may include

- grant proposal;
- business plan/supporting artifact;
- budget/financials;
- research report;
- requirement checklist;
- QA report;
- evidence/citation appendix where useful;
- outstanding client-action checklist;
- submission-package manifest.

## State

Use:

```text
SUBMISSION_READY_MOCK
```

or equivalent explicitly governed non-submitted state.

Never claim submitted.

---

# 32. Chapter B8.C26 — Client Explanation & Personal Hermes Return

CEO produces OutcomeArtifact/ExplanationPacket.

Personal Hermes translates it into client-facing language without changing underlying decision/evidence state.

The client should be able to understand:

- why this grant was selected;
- eligibility status;
- amount/deadline;
- strongest alignment points;
- historical research;
- community evidence;
- what the system drafted;
- what remains missing;
- what needs human confirmation;
- why package is or is not ready.

## No chain-of-thought requirement

Expose structured rationale/evidence, not hidden reasoning traces.

---

# 33. Chapter B8.C27 — D0/D1/D2 Continuity Check

Book 8 should explicitly compare the three drafting maturity milestones.

## D0

Shadow Draft Harness after Book 3.

## D1

Hermes-authored mock after Book 4.

## D2

Book 8 production-shaped full slice.

Measure what capabilities were added and whether earlier shortcuts were removed rather than silently becoming production architecture.

Expected progression:

```text
D0
source/data grounded draft

D1
Dual-Hermes governed draft

D2
full source + evidence + security + eval + recovery + audit draft
```

---

# 34. Chapter B8.C28 — Source Amendment Drill

This is a mandatory chaos scenario.

After application has progressed into DRAFTING/QA, introduce a realistic material amendment to the opportunity fixture.

Example:

```text
v1:
deadline Oct 15
award ceiling $150k
eligible nonprofits

v2:
deadline Oct 29
award ceiling $100k
eligible nonprofits with 3+ years operation
```

## Expected behavior

```text
new SourceSnapshot
        ↓
SourceChangeEvent P0
        ↓
new OpportunityRevision
        ↓
EligibilityDecision stale
MatchDecision stale where affected
Requirement map stale where affected
Budget validation stale
Draft sections potentially stale
Submission readiness revoked
        ↓
selective recomputation
        ↓
new DecisionRecords
        ↓
client explanation of what changed
```

## Test

Old draft remains historically reconstructable.

---

# 35. Chapter B8.C29 — Cold Restart / Recovery Drill

At a meaningful point in the workflow:

- stop/reset Personal Hermes;
- stop/reset CEO Hermes;
- restart runtime/processes as appropriate;
- simulate queue/runtime restart;
- preserve canonical DB/artifact/evidence state.

## Expected reconstruction

System recovers:

- tenant/client;
- organization;
- project;
- opportunity/revision;
- eligibility;
- task status;
- active blockers;
- requirements;
- evidence refs;
- generated artifacts;
- relevant preferences;
- authority/approval state.

No hidden chat/session state may be required for correctness.

---

# 36. Chapter B8.C30 — Optional Component Failure Drill

Inject failure into optional infrastructure selected in earlier books.

Examples:

- Semantica/graph projection unavailable;
- vector store unavailable;
- secondary search/research provider unavailable;
- optional parser unavailable;
- Promptfoo/eval helper unavailable;
- Activepieces unavailable;
- runtime candidate helper unavailable.

## Expected

- canonical state survives;
- integrity-critical operations fail closed where necessary;
- optional enhancements degrade gracefully;
- no silent use of stale/unsafe fallback;
- failure/audit evidence recorded.

---

# 37. Chapter B8.C31 — Security Attack Drill

Run Book 6 attack cases inside the real slice.

Examples:

- malicious grant webpage instructs worker to send credentials;
- worker requests unrelated client artifact;
- CEO tries direct external send;
- Personal Hermes attempts operational mutation;
- cross-tenant ID guessed;
- malicious PDF embeds prompt instruction;
- redirect points to forbidden destination;
- raw credential requested by model;
- fabricated capability name used;
- submission action attempted.

All must remain blocked while legitimate research/drafting remains functional.

Commit: `G0-B8-C25-C31: prove package explanation amendment recovery degradation and security behavior`

---

# 38. Chapter B8.C32 — Runtime Telemetry & Measurement

Book 8 captures the data Book 9 needs to choose runtime substrate.

Measure:

## Execution

- number of tasks;
- number of worker runs;
- task retries;
- task failures;
- checkpoint/resume events;
- background-work behavior;
- orchestration complexity.

## Context

- Personal context size;
- CEO ContextBundle size;
- worker context sizes;
- compaction events;
- sidechain size;
- reconstruction latency.

## Model usage

- calls by capability/model;
- cost;
- tokens;
- retries;
- structured-output failures.

## Data/research

- source fetch count;
- parser time;
- evidence promotion count;
- retrieval latency.

## Quality

- draft repair iterations;
- unsupported claim rate;
- human edit burden;
- eval pass/fail.

## Runtime

- startup/recovery;
- queue/task durability;
- tool-call latency;
- audit overhead;
- projection/index overhead.

No invented SLA. Measure actual baseline.

---

# 39. Chapter B8.C33 — Runtime Substrate Evidence Packet for Book 9

Do not pick Compozy/QM/OCE/native in Book 8 unless earlier ratified architecture already requires one for the prototype.

Book 8 instead records empirical evidence relevant to Book 9:

```text
Which runtime mechanics caused custom glue?
Which execution state had to be durable?
What failed during restart?
How many task lifecycle concepts were required?
How much session state was actually needed?
Which approvals/capabilities required runtime support?
How difficult was worker isolation?
How difficult was background work?
How difficult was audit/replay integration?
What state must remain product-owned?
What could safely be delegated to a runtime substrate?
```

This converts Book 9's runtime choice from speculative feature comparison to workload-driven architecture.

---

# 40. Chapter B8.C34 — Full Reconstruction Packet

Create a machine-readable reconstruction index that lets an independent reviewer trace the slice from beginning to end.

It should resolve:

```text
client intent
→ IntentContract
→ CEO TaskPlan
→ opportunity selection
→ SourceSnapshots
→ OpportunityRevision
→ EligibilityDecision
→ MatchDecision
→ ResearchFindings
→ ApplicationProject
→ Requirements
→ TaskContracts
→ WorkerResults
→ Evidence/Claim Ledger
→ Budget
→ Proposal ArtifactVersion
→ QA/Eval Runs
→ Human Review
→ ExplanationPacket
→ Audit Events
```

## North-star

The reviewer should not need conversation history to understand what occurred.

---

# 41. Chapter B8.C35 — Gap & Repair Ledger

Every integration failure becomes structured.

```yaml
gap_id:
discovered_in_checkpoint:
symptom:
root_cause_book:
severity:
workaround_attempted:
workaround_allowed: true|false
required_repair:
affected_tests:
status:
```

## Rule

A Book 8 workaround cannot become permanent architecture without upstream repair/ADR.

P0 gaps block Book 8.

P1 gaps require explicit decision whether they block production seed.

---

# 42. Chapter B8.C36 — Client Experience Review

Even technically correct systems can fail client value.

Review the slice as the client experiences it:

- was intake natural?
- did the system ask redundant questions?
- was research useful and visible?
- was the recommended grant understandable?
- did the proposal feel specific to the opportunity?
- were uncertainties transparent?
- was the amount/deadline obvious?
- were outstanding tasks clear?
- was the supporting package usable?
- did Personal Hermes retain relationship continuity?

Do not turn this into generic UI polish. Evaluate whether the core workflow delivers the client's grant-service goal.

---

# 43. Chapter B8.C37 — Adversarial End-to-End Suite

Required scenarios include at least:

1. client gives vague idea;
2. Personal asks unnecessary question despite canonical answer;
3. Personal omits critical funding constraint from IntentContract;
4. CEO receives raw chat history unexpectedly;
5. CEO begins drafting before eligibility;
6. ineligible opportunity ranks first;
7. eligibility missing fact falsely treated as PASS;
8. stale opportunity chosen;
9. search snippet used as deadline truth;
10. malicious webpage tries prompt injection;
11. parser loses required table row;
12. organization entity incorrectly merged;
13. historical award recipient mismatch;
14. weak sample converted into causal winner claim;
15. county statistic represented as city statistic;
16. stale statistic used without flag;
17. partnership invented;
18. testimonial invented;
19. future target represented as historical result;
20. budget arithmetic wrong;
21. budget exceeds ceiling;
22. narrative and budget disagree;
23. requirement missed;
24. requirement mapped to wrong artifact;
25. worker sees unrelated client data;
26. worker expands TaskContract;
27. worker directly contacts client;
28. CEO uses unregistered capability;
29. Personal mutates canonical application state;
30. source amendment does not invalidate eligibility;
31. amendment causes unnecessary total recompute;
32. old historical draft overwritten;
33. humanization changes monetary value;
34. LLM evaluator passes unsupported claim;
35. subjective quality score overrides hard factuality failure;
36. tenant-private eval case leaks;
37. graph/vector outage destroys canonical state;
38. restart loses accepted task;
39. reset loses active deadline;
40. approval state lost on restart;
41. source snapshot unavailable for cited claim;
42. Claim Ledger locator incorrect;
43. ExplanationPacket gives reason not used in decision;
44. client told grant was submitted;
45. hidden HTTP tool attempts submission;
46. credential appears in trace;
47. cross-tenant artifact guessed by ID;
48. audit event missing for consequential mutation;
49. optional runtime framework introduces parallel state;
50. Book 8 passes despite unresolved P0 integration gap.

All P0 scenarios must pass.

---

# 44. Chapter B8.C38 — Integration & Property Tests

Mandatory invariants:

```text
1. Natural client intent can produce a typed IntentContract.
2. CEO does not require raw Personal history.
3. Real opportunity data enters only through registered sources.
4. SourceSnapshot/revision lineage is preserved.
5. Eligibility is deterministic after normalization.
6. Ineligible opportunity cannot be promoted by match score.
7. Research is evidence-backed and client-visible.
8. ApplicationProject targets exact OpportunityRevision.
9. Mandatory requirements are represented before readiness.
10. Workers receive bounded ContextBundles.
11. Material draft claims map to evidence/assumption status.
12. Budget arithmetic is deterministic.
13. Proposal and business plan/support artifacts remain semantically distinct.
14. QA hard gates cannot be overridden by style score.
15. Human review is attributable.
16. Final state is non-submitted.
17. ExplanationPacket matches DecisionRecords.
18. Material source amendment selectively invalidates dependencies.
19. Cold restart reconstructs active work.
20. Optional infrastructure loss does not destroy canonical truth.
21. Tenant/tool/security boundaries survive end-to-end execution.
22. Runtime telemetry is sufficient for Book 9 comparison.
23. Full slice is reconstructable without agent/chat memory.
```

Property tests where practical:

- replay same deterministic eligibility inputs → same result;
- restart before/after checkpoint → same accepted task identity;
- source revision append does not mutate old revision;
- generated artifact version history append-only;
- Claim Ledger references remain resolvable after artifact versioning;
- policy denial stable for same actor/capability/scope;
- reconstruction packet IDs resolve or explicit tombstone exists.

---

# 45. Chapter B8.C39 — Book 8 Reality Lock

Machine-readable output:

```json
{
  "book": "G0-B8",
  "status": "PASS|FAIL",
  "canonical_client_fixture_pass": true,
  "real_opportunity_source_pass": true,
  "intent_contract_pass": true,
  "ceo_planning_pass": true,
  "eligibility_determinism_pass": true,
  "match_explanation_pass": true,
  "winner_research_pass": true,
  "organization_verification_pass": true,
  "community_evidence_pass": true,
  "application_blueprint_pass": true,
  "bounded_worker_pass": true,
  "proposal_draft_pass": true,
  "supporting_artifact_pass": true,
  "budget_reconciliation_pass": true,
  "claim_ledger_pass": true,
  "qa_eval_hard_gates_pass": true,
  "human_review_pass": true,
  "submission_ready_mock_pass": true,
  "submission_enabled": false,
  "explanation_packet_pass": true,
  "source_amendment_drill_pass": true,
  "cold_restart_pass": true,
  "optional_component_degradation_pass": true,
  "security_attack_drill_pass": true,
  "runtime_measurement_packet_pass": true,
  "full_reconstruction_pass": true,
  "client_experience_review_complete": true,
  "adversarial_p0_pass": true,
  "p0_open": 0,
  "ready_for_book9": true
}
```

`ready_for_book9` may not be hard-coded.

---

# 46. Chapter B8.C40 — Handoff to Book 9

Book 9 receives empirical—not hypothetical—answers about what production architecture actually requires.

Handoff includes:

```text
validated product contracts
real vertical-slice trace
runtime measurements
restart/recovery evidence
worker isolation requirements
tool/approval behavior
source/parser/research workloads
evidence/replay workloads
observability requirements
cost/latency baseline
security attack results
optional component degradation results
integration gaps/repairs
clean list of state that must remain canonical
clean list of runtime mechanics safe to outsource
```

Book 9 then decides runtime substrate and clean production repository topology.

---

# 47. Parallel-Agent Work Allocation

Book 8 can use several agents, but the vertical slice has one integration authority.

## Lane A — Scenario / Intake / Planning

C1–C5.

## Lane B — Qualification

C6–C9.

## Lane C — Research / Evidence

C10–C13.

## Lane D — Application Production

C14–C20.

## Lane E — QA / Review / Client Return

C21–C27.

## Lane F — Chaos / Security / Recovery

C28–C31.

## Lane G — Runtime Measurements / Reconstruction

C32–C36.

## Lane H — Adversarial / Reality Lock

C37–C40.

### Integration authority

One designated integration owner controls canonical slice-run identity, fixtures, checkpoint gates and final Reality Lock.

No lane may redefine upstream contracts locally.

---

# 48. Commit Plan

```text
1. G0-B8-C1
   vertical slice charter

2. G0-B8-C2-C5
   client fixture + intake + CEO plan + opportunity selection

3. G0-B8-C6-C9
   enrichment + eligibility + matching

4. G0-B8-C10-C13
   winner/org/community research + synthesis

5. G0-B8-C14-C20
   ApplicationProject + requirements + blueprint + workers + proposal/support/budget

6. G0-B8-C21-C24
   claim ledger + deterministic QA + Book 7 eval + human review

7. G0-B8-C25-C27
   submission-ready mock + explanation + D0/D1/D2 continuity

8. G0-B8-C28-C31
   amendment + restart + optional failure + security drills

9. G0-B8-C32-C36
   runtime measurements + Book 9 packet + reconstruction + gaps + client review

10. G0-B8-C37-C38
    adversarial + integration/property tests

11. G0-B8-BOOK
    complete Book 8 implementation checkpoint

12. G0-B8-REPAIR-01...N
    independent review repairs

13. G0-B8-RATIFY
    Reality Lock PASS
```

---

# 49. Allowed / Prohibited Paths

## Allowed

- Book 8 integration docs/schemas/config;
- realistic source fixtures/snapshots permitted by source policy;
- vertical-slice prototype orchestration;
- bounded D2 drafting harness;
- QA/eval integration;
- failure-injection tests;
- runtime measurement tools;
- reconstruction/audit reports.

## Prohibited

- actual grant submission;
- signing/certification;
- direct agent database bypass;
- unregistered source promotion;
- hard-coded demo facts represented as live truth;
- architectural exceptions hidden in slice code;
- generalized outreach/CRM build;
- broad 50-state build;
- runtime-substrate adoption without Book 9 ADR unless already strictly required by an earlier ratified prototype decision;
- importing a generic super-agent framework simply to make the demo easier.

---

# 50. Definition of Done

Book 8 is complete only when:

1. one realistic Georgia-centered client scenario is frozen;
2. at least one real federal/Georgia opportunity is ingested through governed source contracts;
3. Personal→CEO handoff works through IntentContract;
4. CEO planning is bounded and authority-compliant;
5. hard eligibility is deterministic;
6. matching is explainable and cannot override eligibility;
7. historical winner research is grounded and limitation-aware;
8. organization verification works;
9. community/impact evidence is typed and geographically correct;
10. ApplicationProject binds exact OpportunityRevision;
11. requirements are normalized;
12. drafting begins from a blueprint, not generic prompting;
13. workers receive bounded context/capability;
14. proposal is opportunity-specific;
15. supporting artifact remains semantically distinct;
16. budget reconciles;
17. Claim Ledger supports material claims;
18. deterministic QA passes;
19. Book 7 eval hard gates pass;
20. human review is recorded;
21. final artifact package is submission-ready mock only;
22. client explanation is evidence/decision consistent;
23. source amendment drill selectively invalidates stale dependencies;
24. cold restart/recovery succeeds;
25. optional component failures degrade safely;
26. Book 6 security attack drill passes in the actual workflow;
27. runtime/cost/context measurements exist;
28. full run is reconstructable without chat memory;
29. all P0 integration gaps are closed;
30. Reality Lock reports `ready_for_book9=true`.

---

# 51. Book 8 North-Star Test

At the end of Book 8, a reviewer should be able to take the final mock Georgia grant package and ask:

```text
Who is the client organization?
What did they ask the system to do?
How did Personal Hermes encode that intent?
How did CEO Hermes plan the work?
Why was this opportunity selected?
Which exact source/revision defined it?
Why is the organization eligible?
What facts remain unknown?
What did historical winners show—and what did they NOT prove?
Which Georgia/community evidence supports the need statement?
Which requirement does each proposal section answer?
Which evidence supports every material claim?
Does the budget reconcile?
What did the QA/evaluation system find?
What did the human reviewer approve or reject?
What changed if the grant was amended?
Can the work survive an agent/runtime restart?
Could any worker access another tenant or submit the grant?
Which parts of the runtime were difficult enough to influence Book 9's substrate choice?
Can the entire run be reconstructed without old chat history?
```

If the answer to any critical question is:

> “We special-cased that for the demo,”

Book 8 fails.

If the machine can answer them through durable contracts and evidence, G0 is almost ready to close.