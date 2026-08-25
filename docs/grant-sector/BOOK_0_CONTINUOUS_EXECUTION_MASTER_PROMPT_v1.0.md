# Book 0 Continuous Execution — Master Agent Prompt

**Document ID:** GS-G0-B0-PROMPT-001  
**Version:** 1.0  
**Target repository:** `dabiggestpoppa/larger-lab`  
**Target branch:** `grant-sector-r0-salvage`  
**Mission:** Build G0 Book 0 — R0 Ratification & Reality Lock completely, continuously, with evidence and checkpoint commits.

---

# MASTER PROMPT

You are the primary implementation agent for **Grant Sector G0 Book 0 — R0 Ratification & Reality Lock**.

You are not being asked to brainstorm the architecture from scratch. The architecture has already undergone a deep R0 salvage/research phase and a complete G0 master planning phase. Your role is to **execute the ratification book faithfully, test it aggressively, preserve lineage, commit coherent checkpoints, and stop only for genuinely non-resolvable P0 contradictions or explicit human/business decisions.**

Work continuously until the entire Book 0 implementation, evidence packet and book-complete checkpoint are finished.

Do **not** ask for approval between normal chapters.

Do **not** rush, summarize away deliverables, or substitute a high-level report for the actual artifacts/tests.

Do **not** move into Book 1 implementation except where Book 0 must reference the provisional Book 1 constitution as an R0/G0 artifact.

---

# 1. AUTHORITATIVE WORKSPACE

Repository:

`dabiggestpoppa/larger-lab`

Branch:

`grant-sector-r0-salvage`

Work only on this branch unless explicitly instructed otherwise.

Before changing anything:

1. fetch/pull the current branch state;
2. verify branch identity;
3. inspect the current Grant Sector docs tree;
4. record the starting HEAD SHA in the Book 0 evidence report;
5. do not assume prompt text is more current than repository artifacts if the repository contains a later explicit supersession/amendment.

---

# 2. REQUIRED AUTHORITATIVE INPUTS

You must read the relevant contents of these files before implementation:

## R0 foundation

- `docs/grant-sector/GRANT_SECTOR_DUAL_HERMES_CONTEXT_AND_R0_CHARTER_v0.1.md`
- `docs/grant-sector/R0_SALVAGE_MAP_v0.1.md`
- `docs/grant-sector/R0_BRANCH_ARCHAEOLOGY_NOTES_v0.1.md`
- `docs/grant-sector/R0_REJECT_DO_NOT_PORT_LEDGER_v0.1.md`
- `docs/grant-sector/R0_GAP_MAP_v0.1.md`
- `docs/grant-sector/R0_SEED_ARCHITECTURE_RECOMMENDATION_v0.1.md`
- `docs/grant-sector/R0_PROGRESS_CHECKPOINT_2026-08-24.md`
- `docs/grant-sector/R0_EXTERNAL_REPO_REVIEW_BATCH_01.md`
- `docs/grant-sector/R0_EXTERNAL_REPO_REVIEW_BATCH_02_SEMANTICA_TREG.md`
- `docs/grant-sector/R0_EXTERNAL_REPO_REVIEW_BATCH_03_AWESOME_AI_APPS.md`
- `docs/grant-sector/R0_GRANT_DOMAIN_DATA_SOURCE_DEEP_HUNT_v0.1.md` if present

## G0 plans

- `docs/grant-sector/G0_ENTRY_PLAN_v0.1.md`
- `docs/grant-sector/G0_BLOCK_00_TO_03_MASTER_IMPLEMENTATION_PLAN_v1.0.md`
- `docs/grant-sector/G0_FULL_MASTER_BUILD_BLUEPRINT_v1.0.md`
- `docs/grant-sector/G0_BOOK_01_PRODUCT_CONSTITUTION_DRAFT_v0.1.md`
- `docs/grant-sector/G0_BOOK_01_MASTER_IMPLEMENTATION_PLAN_v1.0.md`
- `docs/grant-sector/G0_BOOK_02_MASTER_IMPLEMENTATION_PLAN_v1.0.md`
- `docs/grant-sector/G0_BOOK_03_MASTER_IMPLEMENTATION_PLAN_v1.0.md` if present
- `docs/grant-sector/G0_BOOK_04_MASTER_IMPLEMENTATION_PLAN_v1.0.md` if present
- `docs/grant-sector/G0_BOOK_05_MASTER_IMPLEMENTATION_PLAN_v1.0.md`
- `docs/grant-sector/G0_BOOK_06_MASTER_IMPLEMENTATION_PLAN_v1.0.md`
- `docs/grant-sector/G0_BLUEPRINT_AMENDMENT_001_GEORGIA_FIRST_EARLY_DRAFTING.md`

## OCE/Hermes evidence as needed

Where R0 decisions cite OCE/Hermes architecture, inspect the referenced current/historical files rather than relying on summaries alone when validation is necessary.

Priority areas include:

- OCE constitutional/golden-system doctrine;
- `hermes-set-up/oce-hermes-telegram-operator/` architecture/contracts/tests;
- archived Hermes context-compaction/subagent/skill-eval artifacts;
- historical Research Mesh contracts from `master` when a ratification decision depends on them.

Do not re-run the entire R0 archaeology unless a contradiction genuinely requires it.

---

# 3. BOOK 0 MISSION

Book 0 exists to convert R0 exploratory research into a finite, authoritative, machine-checkable decision baseline.

The core question is:

> **What from R0 is now permitted to constrain or influence production architecture, what remains experimental, what is rejected, what is deferred, and where do contradictions remain?**

Book 0 must produce an evidence-backed ratification packet that Books 1–9 can rely upon without reinterpreting R0 every time.

---

# 4. REQUIRED BOOK 0 CHAPTERS

You must implement all chapters below.

## B0.C1 — R0 Artifact Manifest

Build a canonical inventory of all R0/G0-pre-ratification artifacts relevant to Grant Sector architecture.

For each artifact record:

```yaml
artifact_id:
path:
commit_sha_or_blob_sha:
version:
artifact_type:
authority_class:
status:
created_or_observed_at:
supersedes:
superseded_by:
notes:
```

Required authority classes should distinguish at least:

- binding candidate;
- architecture evidence;
- research evidence;
- prototype evidence;
- historical lineage;
- reject ledger;
- amendment;
- provisional downstream draft.

Deliverables:

- human-readable manifest;
- machine-readable JSON/YAML manifest;
- validator that checks paths/duplicates/supersession cycles.

Checkpoint commit:

`G0-B0-C1: build R0 artifact manifest and lineage validator`

---

## B0.C2 — Decision Register

Normalize every major R0 conclusion into exactly one primary status:

- `RATIFIED`
- `RATIFIED_WITH_CONDITION`
- `PROTOTYPE_REQUIRED`
- `DEFERRED`
- `REJECTED`
- `UNRESOLVED`

Each decision must include:

```yaml
decision_id:
title:
status:
category:
statement:
rationale:
source_artifact_ids:
conditions:
affected_books:
implementation_implications:
supersedes_decision_id:
```

At minimum cover decisions around:

- Dual-Hermes architecture;
- Relationship/Control/Work/Data planes;
- Hermes as operator, not sovereign product truth;
- Personal vs CEO memory isolation;
- workers bounded/disposable;
- Postgres/governed durable state as authoritative;
- Redis non-authoritative transport/cache;
- deterministic eligibility/numerical logic;
- evidence lineage/source snapshots;
- Research Mesh salvage posture;
- OCE-Hermes MCP facade posture;
- context compaction + sidechains;
- skill/eval salvage;
- parser architecture;
- Crawl4AI/GPT Researcher/Unstructured/Promptfoo/Guardrails/Univer/Activepieces/PixelRAG dispositions;
- Semantica prototype requirement;
- Treg architectural pattern vs embedding/license restriction;
- CommonGrants as interoperability surface;
- Grants.gov/Simpler/SAM/USAspending/IRS/FAC/Census source architecture;
- Georgia-first state proof;
- early drafting D0/D1/D2 milestones;
- automated submission excluded from Phase 1;
- all major reject-ledger anti-patterns.

Checkpoint commit:

`G0-B0-C2: normalize R0 architecture decisions`

---

## B0.C3 — Contradiction & Drift Sweep

Perform a deliberate contradiction scan across authoritative R0/G0 planning artifacts.

Do not rely only on keyword matching. Use semantic review plus deterministic checks where possible.

Classify contradictions:

- authority;
- storage/source-of-truth;
- tenant/security;
- memory/context;
- component disposition;
- licensing;
- source precedence;
- domain terminology;
- implementation timing;
- state/jurisdiction priority;
- drafting/submission authority;
- external integration authority.

Record each:

```yaml
contradiction_id:
claim_a:
claim_b:
source_a:
source_b:
severity: P0|P1|P2
resolution:
resolution_authority:
status:
affected_decisions:
```

Specific contradictions you must actively test for:

1. California-first vs Georgia-first state proof;
2. CEO L2 drafting allowed vs any language accidentally delaying all drafting until Book 8;
3. automated submission excluded vs any capability/plan implying Phase 1 auto-submit;
4. Semantica foundational enthusiasm vs explicit prototype/bake-off requirement;
5. Treg architecture use vs code embedding/licensing caution;
6. graph/evidence projection vs canonical database sovereignty;
7. Redis transport vs accepted-job truth;
8. Personal/CEO shared memory vs separate memory requirement;
9. full worker transcript in parent context vs sidechain isolation;
10. external framework as architecture authority vs bounded component rule.

Zero P0 contradictions may remain unresolved.

Checkpoint commit:

`G0-B0-C3: close R0 P0 contradictions and drift`

---

## B0.C4 — Non-Goal Freeze

Create the explicit non-goals for G0/G1 first vertical-slice scope.

At minimum include:

- autonomous grant submission;
- L4/L5 production enablement;
- all 50 state source integrations;
- complete private-foundation universe;
- generic autonomous agent OS replacement;
- worker autobiographical long-term memory;
- Kubernetes unless evidence later demands it;
- universal knowledge ontology;
- generic graph database as mandatory foundation;
- custom vector database;
- production self-modifying code/policy;
- direct Hermes database access;
- Candid as mandatory MVP dependency;
- broad trading/CEREBUS logic reuse;
- arbitrary third-party MCP/community tools auto-enabled.

Non-goals must distinguish:

- explicitly rejected;
- intentionally deferred;
- future extension point.

---

## B0.C5 — Prototype / Bake-Off Candidate Register

Freeze candidates that require evidence rather than architectural assumption.

At minimum:

- Semantica evidence substrate/projection;
- relational baseline evidence substrate;
- Unstructured vs salvaged parser stack;
- PixelRAG visual fallback;
- Crawl4AI extraction;
- GPT Researcher bounded research patterns;
- Promptfoo + internal Hermes Eval Lab;
- Guardrails selected validators;
- Univer budget/spreadsheet workspace;
- Activepieces bounded integration fabric.

Each candidate must include:

```yaml
candidate_id:
capability_gap:
hypothesis:
baseline:
success_metrics:
kill_criteria:
license_status:
security_notes:
responsible_book:
status:
```

Do not mark a candidate ADOPTED merely because R0 liked it.

Checkpoint commit:

`G0-B0-C4-C5: freeze non-goals and prototype register`

---

## B0.C6 — R0 Ratification Reality Lock

Implement a machine-readable reality lock.

Minimum output:

```json
{
  "book": "G0-B0",
  "status": "PASS|FAIL",
  "artifact_manifest_complete": true,
  "all_major_decisions_classified": true,
  "p0_open": 0,
  "prototype_candidates_bounded": true,
  "non_goals_frozen": true,
  "supersession_cycles": 0,
  "stale_authority_detected": false,
  "ready_for_book1_ratification": true
}
```

`ready_for_book1_ratification` must be computed, never hard-coded.

Book 0 may reference the already drafted Book 1 constitution as a provisional downstream artifact, but Book 0 does not ratify Book 1 itself.

---

# 5. REQUIRED OUTPUT TREE

Create a coherent Book 0 package, for example:

```text
docs/grant-sector/g0/00-ratification/
├── G0_B0_R0_ARTIFACT_MANIFEST.md
├── G0_B0_DECISION_REGISTER.md
├── G0_B0_CONTRADICTION_LEDGER.md
├── G0_B0_NON_GOALS.md
├── G0_B0_PROTOTYPE_CANDIDATE_REGISTER.md
├── G0_B0_RATIFICATION_PACKET.md
├── G0_B0_TEST_REPORT.md
├── G0_B0_REALITY_LOCK_REPORT.md
└── G0_B0_HANDOFF_TO_BOOK_1.md

config/g0/ratification/
├── artifact_manifest.yaml
├── decision_register.yaml
├── contradiction_ledger.yaml
├── non_goals.yaml
└── prototype_candidates.yaml

tools/g0/
├── validate_artifact_manifest.py
├── validate_decision_register.py
├── validate_contradictions.py
├── validate_ratification.py
└── build_book0_reality_lock.py

tests/g0/book0/
├── test_artifact_manifest.py
├── test_decision_register.py
├── test_contradictions.py
├── test_non_goals.py
├── test_prototype_register.py
└── test_reality_lock.py
```

Adapt path naming only if necessary for repository consistency. Do not omit artifact classes.

---

# 6. IMPLEMENTATION REQUIREMENTS

## 6.1 Machine-readable first-class artifacts

The Markdown docs are human-readable views. The decision/manifest/contradiction registers must also exist in machine-readable form.

## 6.2 Validation scripts must fail closed

A malformed/missing mandatory field must produce failure.

## 6.3 Do not hard-code PASS

Reality lock derives readiness from validations/test evidence.

## 6.4 Preserve historical lineage

Do not edit old R0 docs simply to remove contradictions. Resolve them in Book 0 with explicit supersession/decision records.

## 6.5 No secrets

If historical files contain credentials/secrets, do not copy values into Book 0 artifacts or logs. Record only the security finding and affected pattern.

## 6.6 No trading-domain expansion

Trading-specific material is out of scope except where R0 already identified generic infrastructure.

## 6.7 No premature implementation

Book 0 is ratification infrastructure. Do not build the actual grant product, source adapters, Hermes runtime, Semantica integration, auth system, etc.

---

# 7. REQUIRED TEST STRATEGY

At minimum implement:

## Structural tests

- all required files present;
- unique artifact IDs;
- unique decision IDs;
- unique contradiction IDs;
- valid statuses/enums;
- no supersession cycles;
- every decision references valid artifacts.

## Coverage tests

Every major R0 category has at least one explicit decision.

Required categories:

```text
architecture
Hermes
memory/context
control/governance
data/source
research
parsing
security
evidence
external repositories
licensing
Georgia-first
client Phase 1
mock drafting milestones
submission boundary
reject ledger
```

## Contradiction tests

Create fixtures containing known contradictions and verify validation/Reality Lock fails.

## Negative tests

Examples:

- decision without source;
- unresolved P0 contradiction;
- candidate marked adopted without disposition evidence;
- supersession loop;
- unknown status;
- missing non-goal category;
- Book 0 Reality Lock with missing artifact.

## Reality Lock test

Run clean package → PASS.

Inject P0 contradiction → FAIL.

Remove mandatory decision → FAIL.

Hard-code readiness independently of predicates → test should catch/design prevent.

---

# 8. EXPECTED DECISION BASELINE

Do not blindly copy this list; validate against source artifacts. But unless source evidence contradicts it, the expected high-level direction is:

```text
Dual-Hermes split                         RATIFIED
Hermes as operator, not canonical truth   RATIFIED
Personal/CEO separate memories            RATIFIED
Worker bounded/sidechain pattern          RATIFIED
Postgres/durable state authoritative      RATIFIED
Redis transport/cache non-authoritative   RATIFIED
Deterministic eligibility                 RATIFIED
Evidence/source lineage                   RATIFIED
Georgia-first state proof                 RATIFIED
D0 after Book 3                           RATIFIED_WITH_CONDITION
D1 Hermes draft after Book 4              RATIFIED_WITH_CONDITION
D2 production-shaped proof Book 8         RATIFIED_WITH_CONDITION
Auto-submission Phase 1                    REJECTED / NON-GOAL
Semantica                                  PROTOTYPE_REQUIRED
Crawl4AI                                  PROTOTYPE_REQUIRED
Unstructured                              PROTOTYPE_REQUIRED
PixelRAG                                  PROTOTYPE_REQUIRED
GPT Researcher patterns                   PROTOTYPE_REQUIRED
Promptfoo                                 RATIFIED_WITH_CONDITION / prototype integration
Guardrails                                RATIFIED_WITH_CONDITION / bounded validators
Univer                                    PROTOTYPE_REQUIRED
Activepieces                              PROTOTYPE_REQUIRED / bounded executor
Treg code embedding                       REJECTED/blocked pending license
Treg architectural pattern                RATIFIED_WITH_CONDITION
Candid mandatory MVP dependency           DEFERRED
Trading strategies                         REJECTED for this product
```

If repository source material indicates a more precise disposition, use the source and document why.

---

# 9. P0 STOP CONDITIONS

Stop continuous execution and report immediately only if you discover a genuinely non-resolvable issue such as:

1. two authoritative user/client requirements directly conflict and no supersession exists;
2. the branch does not contain the required source artifacts and they cannot be recovered from known refs;
3. a legal/license fact materially changes a planned component disposition and cannot be resolved from repository/public metadata already available;
4. Book 0 would require changing a client business decision rather than architecture ratification;
5. repository corruption/branch mismatch prevents safe writes.

Do not stop for ordinary ambiguity that can be resolved through evidence, conservative classification or explicit `UNRESOLVED` P1/P2 tracking.

Zero P0 may remain at Book 0 completion.

---

# 10. COMMIT DISCIPLINE

Make the following checkpoints:

```text
1. G0-B0-C1: build R0 artifact manifest and lineage validator
2. G0-B0-C2: normalize R0 architecture decisions
3. G0-B0-C3: close R0 P0 contradictions and drift
4. G0-B0-C4-C5: freeze non-goals and prototype register
5. G0-B0-C6: implement ratification Reality Lock and tests
6. G0-B0-BOOK: complete Book 0 implementation and evidence packet
```

Do not create `G0-B0-RATIFY` yourself unless the operating workflow explicitly authorizes the implementation agent to self-ratify. Preferred workflow is:

- implementation agent produces `G0-B0-BOOK`;
- independent reviewer inspects it;
- repair commits occur if needed;
- reviewer/operator authorizes final ratification commit.

This separation is deliberate.

---

# 11. BOOK-COMPLETE REPORT FORMAT

When Book 0 implementation is complete, report:

```text
BOOK: G0-B0
STATUS: BOOK_COMPLETE_AWAITING_REVIEW
START_SHA: ...
END_SHA: ...

CHECKPOINT COMMITS
- ...

DELIVERABLES
- ...

TESTS
- command / result
- pass/fail totals

REALITY LOCK
- PASS/FAIL
- predicate summary

P0 OPEN
- 0 or list

P1/P2 OPEN
- list with rationale

MAJOR RATIFIED DECISIONS
- concise summary

PROTOTYPE_REQUIRED
- concise list

REJECTED / NON-GOALS
- concise list

CONTRADICTIONS RESOLVED
- IDs + outcome

KNOWN LIMITATIONS
- ...

REVIEW REQUEST
Please independently review commit range <START_SHA>..<END_SHA> against Book 0 master plan.
```

Do not provide a vague narrative instead of this report.

---

# 12. QUALITY STANDARD

This project is being built with the same meticulous philosophy as a quant/OCE research program:

- decisions require evidence;
- claims require source lineage;
- state transitions require gates;
- test counts must be truthful;
- blocked work must remain visibly blocked;
- legacy/history is not current truth unless ratified;
- fail-closed means fail-closed;
- “looks good” is not proof;
- documentation and machine-readable contracts must agree;
- do not declare completion while required evidence is missing.

Depth and correctness are more important than speed.

Do not shorten the book because implementation appears easy.

---

# 13. FINAL EXECUTION INSTRUCTION

Begin now on `grant-sector-r0-salvage`.

Read the authoritative files, build Book 0 continuously, create the required checkpoint commits, run all tests, produce the Reality Lock and `G0-B0-BOOK` checkpoint, then stop and return the book-complete report for independent review.

Do not begin Book 1 implementation after finishing Book 0.
