# R0 Salvage Map

**Document ID:** GS-R0-MAP-001  
**Version:** 0.2  
**Status:** DEEP-DIVE PASS COMPLETE — VALIDATION/PROMOTION PENDING  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-24

---

## 0. Executive Finding

The deep archaeology materially changes the build posture.

`larger-lab` already contains a substantial generic cognition/agent platform hidden primarily in `master`, archived Hermes snapshots, `execution-runtime-foundation`, current OCE, and content tooling. The Grant Sector product should therefore **not** begin as a greenfield agent application.

The recommended approach is to create a clean product repository later and transplant a deliberately selected kernel consisting of:

1. Dual-Hermes boundary and Hermes/OCE MCP gateway pattern;
2. OCE governance, authority, event, audit, and memory concepts;
3. Research Mesh ingestion/rate-limit/dedupe/queue/lifecycle patterns;
4. parser normalization into source objects;
5. bounded semantic retrieval and evidence graph concepts;
6. agent hook / policy interception patterns;
7. context compaction and sidechain isolation;
8. skill evaluation/benchmark loops;
9. selected artifact/document generation tooling;
10. fresh product-specific Postgres schemas and deterministic Grant domain logic.

Do **not** merge `master`, `execution-runtime-foundation`, or an archive wholesale. Much of the reusable architecture is historically valuable but coupled to old paths, SQLite/local state, Obsidian assumptions, trading nomenclature, or prototype-grade code.

---

## 1. Disposition Vocabulary

- **ADOPT** — use largely as-is after normal dependency/security verification.
- **FORK** — preserve upstream lineage and develop our own maintained version.
- **WRAP** — keep upstream component behind a stable product adapter.
- **PORT** — move a bounded implementation/pattern into the product and modernize it.
- **REWRITE** — preserve contract/idea but replace implementation.
- **REJECT** — do not carry forward.
- **DEFER** — useful but not needed for first build.

Confidence:

- **A** — implementation inspected and directly relevant.
- **B** — architecture/docs inspected; implementation needs targeted validation.
- **C** — catalog/branch evidence only; requires fresh inspection before adoption.

---

# 2. Tier A — Foundation Candidates

| Capability | Source | Evidence | Disposition | Confidence | Product use |
|---|---|---|---|---|---|
| OCE-Hermes filtered MCP facade | `hermes-set-up/oce-hermes-telegram-operator/` | Architecture, schemas, audit, adversarial/unit/integration tests, runbooks | **FORK / PORT** | A | CEO Hermes and later Personal Hermes access the product only through governed capabilities |
| Hermes sidechain subagent pattern | archived `.hermes/skills/subagent-manager` | Full worker transcript separated from short parent summary | **PORT** | A | Keeps CEO context clean while retaining forensic/audit record |
| Hermes context compaction | archived `.hermes/skills/context-compaction` | Five-layer compaction protocol | **PORT / REWRITE** | A | Context-budget manager for both Hermes roles; different policies per role |
| OCE structural memory model | `main/oce/backend/structural_memory.py` | WORK/LEARNED/KNOWLEDGE + TTL + FTS | **PORT / REWRITE storage** | A | Bounded operational memory and promotion lifecycle |
| OCE constitutional governance | `docs/oce-golden-system/*` | Authority, truth labels, evidence hierarchy, gates, retention | **ADOPT doctrine / PORT contracts** | A | Governing control model |
| OCE Block 1 runtime principles | Block 1 dossier | Postgres truth, Redis transport, disposable workers, backups/restore | **ADOPT doctrine** | A | Production infrastructure baseline |
| Research Mesh task queue state model | `master/core/research/agents/queue.py` | priority, retries, result, confidence, token/cost fields | **PORT contract / REWRITE backend** | A | Grant research and document-work queue |
| Research agent lifecycle | `master/core/research/agents/lifecycle.py` | concurrency, heartbeat, timeout, retries, stale cleanup | **PORT / REWRITE** | A | Specialist worker lifecycle manager |
| Source rate limiter/backoff | `master/core/research/ingestion/rate_limit.py` | async token bucket + retry/backoff | **PORT** | A | Grant portals/APIs/web-source politeness and reliability |
| Source dedupe/write gate concept | `master/core/research/ingestion/cache.py` | primary identity + fuzzy fallback + write cap | **PORT concept / REWRITE** | A | Opportunity/source dedupe and ingestion quotas |
| Parser normalization contract | `master/core/parser/README.md` + parser forks | universal parsing → Cognition Object | **PORT contract / WRAP engines** | B | Uploads, grant docs, business plans, winner PDFs, attachments |
| Pre-tool policy hook | `master/tools/agent-hooks/pre-tool-use-enhanced.py` | denylist + protected-file interception + fail-closed | **PORT / REWRITE policy engine** | A | CEO Hermes action guardrail before tool execution |
| Post-tool validation/audit hook | `master/tools/agent-hooks/post-tool-use-enhanced.py` | validation + JSONL tool audit | **PORT / REWRITE** | A | Output validation, action journal, automatic checks |
| Hermes skill evaluation loop | archived `.hermes/skills/skill-creator` | baseline-vs-skill eval, assertions, grader, timing/token benchmarks, human review | **PORT / GENERALIZE** | A | Regression harness for grant-agent skills/prompts/workflows |

---

# 3. Hermes Salvage Map

## 3.1 Archive deduplication result

The three branches:

- `archive/hermes-02e51f11`
- `archive/hermes-262c2f34`
- `archive/hermes-cde01a2a`

expose the same `.hermes` object SHAs for `MEMORY.md`, `SOUL.md`, `USER.md`, config, cron, memories, and skills. For Hermes-specific salvage they are effectively duplicate snapshots. R0 therefore uses one representative deep read and preserves the other two only as lineage references.

### 3.2 Hermes Five-Pillar model

Historical Hermes organized itself around:

- Memory;
- Skills;
- Soul;
- Crons;
- Self-improving loop.

**Disposition: PORT CONCEPT.**

For the Grant system this becomes:

- Personal Hermes: Relationship Memory + client skills + conversation interface + scheduled client workflows + client feedback loop.
- CEO Hermes: Operational Memory + operator skills + scheduled system workflows + execution-improvement loop.

The two must not share one mutable memory namespace.

### 3.3 Progressive skill disclosure

Archived Hermes skills load metadata broadly, skill body on trigger, bundled resources only as needed.

**Disposition: ADOPT PATTERN.**

This is important for avoiding context pollution. Grant skills should follow the same progressive-disclosure pattern instead of injecting every grant workflow into every session.

### 3.4 Context compaction

Historical five layers:

1. budget reduction;
2. older-turn snipping;
3. micro-compaction/dedupe;
4. context collapse;
5. LLM-generated summary only as last resort.

**Disposition: PORT/REWRITE.**

Required improvements:

- preservation classes rather than fixed “first 2 + last 4” assumptions;
- distinct Personal vs CEO policies;
- canonical-state references instead of copying durable facts into summaries;
- explicit compaction provenance;
- automatic stale-memory demotion;
- no credentials or sensitive raw data in compacted memory.

### 3.5 Sidechain subagent manager

Historical pattern:

- worker gives parent only a concise result;
- full execution trace is stored separately as JSONL;
- parent gets a pointer to the sidechain.

**Disposition: PORT — foundational.**

New version should write trace metadata/artifact references to durable system storage, with retention classes and redaction rather than permanent filesystem accumulation.

### 3.6 Hermes workflows / crons

Historical chief-of-staff workflows demonstrate fresh scheduled sessions and structured outputs.

**Disposition: PORT SCHEDULING PATTERN, REJECT literal old workflow set.**

Potential Grant workflows:

- daily opportunity discovery;
- deadline watch;
- stale-profile check;
- missing-evidence watch;
- application readiness digest;
- weekly grant pipeline report;
- later outreach follow-up.

### 3.7 Skill creator / eval viewer

This is one of the strongest finds. It already embodies a quantitative model-development loop:

- with-skill vs baseline;
- parallel evals;
- formal assertions;
- human qualitative review;
- token/time tracking;
- grader;
- aggregate benchmarks;
- analyst pass for variance/non-discriminating tests;
- iterative skill improvement.

**Disposition: PORT/GENERALIZE — high priority.**

This can become the Grant Agent Evaluation Lab for:

- intent translation;
- grant eligibility extraction;
- research synthesis;
- proposal section generation;
- QA critics;
- humanization;
- Personal→CEO handoff quality.

### 3.8 Critical security finding

Historical Hermes persistent memory included raw credentials. Values are intentionally omitted from this dossier.

**Disposition: REJECT practice / CRITICAL remediation rule.**

New system rule:

> No credential, API token, password, secret, or reusable authentication material may be written into Personal Hermes memory, CEO Hermes memory, sidechains, prompts, logs, or Git.

Use scoped service identities / secret storage and redact before logging.

---

# 4. Master Branch — Hidden Generic Platform

`master` is not merely an old trading branch. It contains a substantial generalized cognition/research stack that was later pruned from `main`.

## 4.1 Parser orchestration

Historical components/forks:

- Microsoft MarkItDown;
- OpenDataLoader PDF;
- LiteParse;
- Chandra.

Normalized output is a typed Cognition Object with source hash/type, extracted text/markdown, summary, concepts/tags, metadata, citations, and embedding.

**Disposition: WRAP upstream parsers + REWRITE normalized product SourceDocument contract.**

Grant-specific SourceDocument should add:

- tenant/org identity;
- source URL/provider;
- retrieval timestamp;
- immutable source snapshot hash;
- authority tier;
- document effective date;
- expiration/freshness policy;
- grant/funder/applicant relationship;
- PII/sensitivity classification;
- parsing quality/evidence confidence.

## 4.2 Semantic memory

Historical stack:

- semantic chunking;
- pluggable embeddings;
- TurboVec primary + FAISS fallback;
- live retrieval and associative recall;
- concept clustering.

**Disposition: PORT chunking/retrieval contracts, REWRITE storage architecture.**

For commercial product, prefer simplifying around the canonical Postgres estate (for example Postgres + vector extension if validated) before introducing independent FAISS/TurboVec services. Vector search must supplement—not replace—deterministic eligibility, relational filters, or source lineage.

## 4.3 Knowledge graph

Historical engine includes entity canonicalization, typed edges, confidence, contradiction relationships, inference, abstraction, and gap detection.

**Disposition: REWRITE as narrower Evidence Graph; PORT ontology/contradiction ideas.**

The Grant product does not need a generic “AI cognition graph” first. It needs exact relationships such as:

- claim SUPPORTS source snapshot;
- claim CONTRADICTS claim;
- claim USED_IN artifact section;
- grant ISSUED_BY funder;
- winner RECEIVED award;
- eligibility rule DERIVED_FROM grant source;
- organization SATISFIES / FAILS rule;
- statistic APPLIES_TO geography/population;
- artifact VERSION_DEPENDS_ON canonical fact.

## 4.4 Unified cognition router

Historical `CognitionRouter` attempts a single API for ingest, recall, synthesis, and procedural execution.

**Disposition: REWRITE contract.**

Useful idea: one stable cognition/evidence interface. Old implementation is coupled to historical engines and imports; do not port blindly.

---

# 5. Research Mesh — Highest-Value Master Subsystem

The Research Mesh is the closest existing internal analogue to Grant Intelligence research.

Historical architecture already includes:

- multi-source ingestion;
- cache/dedup;
- rate limits and retry;
- scheduled collection;
- parser normalization;
- semantic memory;
- knowledge graph;
- gap detection;
- task generation;
- bounded research agents;
- evaluation;
- synthesis;
- consensus;
- action logging;
- LLM cost caps.

Historical docs report 106/106 tests for Research Mesh layers; that is useful lineage evidence but **must be re-run against whatever code we actually port** before being promoted as current proof.

## 5.1 Source adapters

Existing source clients are research-paper-specific, so their literal APIs are not useful for grants.

**Disposition: REWRITE adapters; PORT interface/reliability patterns.**

Replace with:

- Grants.gov / federal adapters;
- SAM assistance / agency sources where relevant;
- state/local portals;
- foundation/corporate sources;
- manual URL/document intake;
- winner/award sources;
- demographic/public-data sources.

## 5.2 Ingestion cache / dedupe

Old implementation uses SQLite, primary source identities, fuzzy-title fallback, and hard daily write cap.

**Disposition: PORT idea, REWRITE in Postgres.**

Grant dedupe should use layered identities:

- canonical source ID;
- normalized opportunity number;
- source URL + content hash;
- funder/title/deadline fingerprint;
- revision relationship rather than treating updates as duplicate drops.

## 5.3 Queue

Old `ResearchTask` is surprisingly close to what we need: task state, priority, assignee, result, confidence, token usage, cost, retries, errors, timestamps.

**Disposition: PORT schema/state semantics; REWRITE persistence.**

Postgres stores accepted task truth. Redis may transport wakeups/work if needed. Redis loss must not erase accepted jobs.

## 5.4 Lifecycle

Old lifecycle has concurrency limits, duration limits, retries, heartbeat, stale-worker cleanup, and abandoned state.

**Disposition: PORT/GENERALIZE.**

Extend with:

- task lease;
- authority scope;
- tenant/project scope;
- cancellation;
- idempotency key;
- artifact/evidence outputs;
- model/provider identity;
- retry policy class;
- human escalation;
- compensation/rollback state where actions are mutable.

## 5.5 Evaluator

Old finding evaluator uses hard-coded source rankings, citation counts, recency, and optional LLM self-rating.

**Disposition: REWRITE.**

The *multi-factor confidence model* is worth preserving, but grant evidence requires different factors:

- primary vs secondary source;
- directness of support;
- official/current source;
- effective date/freshness;
- geographic/population match;
- extraction confidence;
- corroboration;
- contradiction state.

LLM self-confidence must never be treated as strong independent evidence.

## 5.6 Router

Old model router chooses local vs OpenRouter largely from query length and a daily budget.

**Disposition: REWRITE, preserve budget-aware routing concept.**

New routing should use task class, required capabilities, latency, privacy, context size, quality tier, deterministic-vs-generative classification, provider health, and budget—not word count.

---

# 6. OCE Current Main — Salvage by Contract, Not Blind Copy

Current `main/oce/backend` still contains broad generic modules such as compression, alerting, command center, consensus, drift detection, execution optimization, coevolution, and structural memory.

## 6.1 Structural memory

WORK / LEARNED / KNOWLEDGE, TTL, full-text search, timeline, compression.

**Disposition: PORT data model and promotion concept / REWRITE persistence for multi-tenant product.**

Important improvement: old `compress()` drops oldest entries beyond a count. New memory pruning must be evidence-aware and preserve canonical references/anchors.

## 6.2 Adaptive compression

Current module explicitly preserves named recovery anchors while compressing other data.

**Disposition: PORT anchor-preservation concept, REWRITE implementation.**

The current implementation is byte/zlib storage compression, not sufficient semantic/context compaction by itself. Combine its “never compress these anchors” rule with Hermes semantic compaction.

## 6.3 Coevolution protocol

Useful concepts:

- agent registration;
- capability declarations;
- trust levels;
- heartbeat/status;
- failure handling.

**Disposition: REWRITE.**

Do not port current implementation directly. It contains prototype choices such as local SQLite and parsing stored structures with `eval`, which is inappropriate for enterprise production. The trust-level idea should become explicit service/agent capabilities enforced by policy.

## 6.4 Consensus / drift / self-heal / observability

**Disposition: PORT selected contracts after targeted code review; not automatically required for MVP.**

The Grant product benefits from:

- drift detection for prompts/workflows/source adapters;
- consensus only at high-value ambiguous review points;
- self-heal for infrastructure/retryable workflow failures, not autonomous product-policy changes;
- metrics/tracing from first production build.

---

# 7. Agent Harness / Development-Control Salvage

## 7.1 Harness Engineering doctrine

Strong reusable rules discovered in `master` doctrine:

- explicit harness construction;
- constrain before execution;
- verify after execution;
- compress memory rather than allow linear growth;
- observable runtime;
- pre-tool, post-tool, and stop hooks;
- separate memory categories;
- state/progress files for cold restart;
- phase-gated testing;
- JSONL audit trail.

**Disposition: ADOPT doctrine / REWRITE product harness.**

## 7.2 Pre-tool hook

Old enhanced hook can block dangerous shell patterns and protected-file edits.

**Disposition: PORT pattern, replace regex-only enforcement with typed policy rules.**

Product CEO should not have arbitrary shell access in normal operation. Policy should act on typed capabilities (`grant.research`, `application.draft`, `email.send`, etc.), resource identity, tenant, authority level, and risk class.

## 7.3 Post-tool hook

Old hook validates Python/JSON/YAML/Markdown and logs tool calls.

**Disposition: PORT architecture.**

Generalize validators by output contract:

- JSON Schema;
- Pydantic/domain validation;
- citation coverage;
- numerical reconciliation;
- artifact integrity;
- external-action receipt verification.

## 7.4 AI Team Orchestration skill

Useful patterns:

- separate roles;
- explicit handoffs;
- project brief as durable truth;
- sprint plan/progress/done artifacts;
- cold-start recovery;
- bugs live in issue tracker instead of chat.

**Disposition: PORT DEVELOPMENT PROCESS ONLY.**

Do not copy its exact personas/team topology into runtime Grant agents.

## 7.5 Context Map skill

Requires codebase dependency/test/risk map before changes.

**Disposition: ADOPT/PORT for development agents.**

This is especially useful once Hermes CEO is later allowed to propose improvements to the application itself.

---

# 8. Context Preservation Infrastructure

Current `main/tools/chat_summarizer.py` provides another useful lineage pattern:

- archive full chat before condensing;
- keep recent messages intact;
- preserve high-priority directives/handoffs;
- collapse routine old status chatter into dated summaries.

**Disposition: PORT CONCEPT, not literal parser.**

This reinforces the system doctrine:

> Archive raw history separately; preserve priority anchors; summarize operational chatter; never force all history into active context.

---

# 9. Existing Forked Open-Source Assets Found in Master

These are **internal discoveries, not yet fresh external due diligence**. Licenses, current upstream maintenance, CVEs, and compatibility must be rechecked before production use.

| Asset | Historical purpose | Grant relevance | R0 posture |
|---|---|---|---|
| Microsoft MarkItDown | universal document → Markdown | high | WRAP candidate |
| OpenDataLoader PDF | layout/table/PDF extraction | very high | WRAP/FORK candidate |
| LiteParse | code/web parsing | medium | DEFER/WRAP if useful |
| Chandra | OCR / image extraction | medium-high | WRAP if scanned grant docs needed |
| TurboVec | ANN/vector index | medium | DEFER; simplify storage first |
| CodeGraph | graph/code relationships | low for runtime, medium dev tooling | DEFER |
| book-to-skill | procedural knowledge generation | medium | research later |
| SkillTree | skill routing | medium-high | research later |
| mattpocock/skills | skill library | development aid | DEFER/selectively mine |
| notebooklm-py | research distillation interface | medium-high | evaluate externally before use |
| Horizon | research signals | uncertain | DEFER pending architecture review |
| Open Design | HTML/PDF/PPTX/MP4 and design systems | high for client artifacts | evaluate/fork selectively |
| D2 | diagrams | low-medium | WRAP dev/report utility |
| Web Artifacts Builder | React/shadcn standalone artifacts | medium for prototypes/internal review | development tool, not core product runtime |

---

# 10. Artifact / Document Production Salvage

The historical content farm includes Open Design and related generation tooling. The master catalog claims support for HTML, PDF, PPTX, MP4, multiple deck styles, and design systems.

**Disposition: HIGH-PRIORITY EVALUATION, not automatic adoption.**

Potential use:

- grant pitch decks;
- impact one-pagers;
- client research reports;
- internal visual QA;
- branded appendices.

The core proposal/business-plan DOCX/PDF pipeline still needs a product-specific deterministic document compiler and template/version system. Visual content tools should not become the source of document truth.

---

# 11. Archive Branch Conclusions

## `archive/pruned-master-2026-08-15`

Contains the same historical `MASTER_CATALOG.md` blob as the reviewed archive and preserves extensive pre-cleanup agent skills/forks. Treat as a retrieval snapshot, not a base branch.

## `archive/review-branch`

Shares many exact file SHAs with pruned master. Low incremental value after duplicate confirmation. Retain for lineage only unless a targeted missing file is identified.

## `archive/content-oc2`

Preserves the content-farm tree (`design`, `docs`, `github-repos`, `sites`, `tools`). Useful primarily for artifact-generation salvage, not control-plane architecture.

## Hermes archives

Duplicate `.hermes` state confirmed; one representative deep inspection is sufficient.

---

# 12. Provisional Component Decisions

| Layer | Candidate | Decision |
|---|---|---|
| Personal interface | Hermes | **FORK/configure upstream Hermes** behind product capabilities |
| CEO operator | Hermes | **FORK/configure upstream Hermes** with separate identity/memory/authority |
| Hermes→product boundary | OCE-Hermes MCP facade pattern | **FORK/PORT** |
| Canonical truth | Postgres | **NEW BUILD using OCE Block 1 doctrine** |
| Transport | Redis if needed | **NEW BUILD, non-authoritative** |
| Worker lifecycle | Research Mesh lifecycle | **PORT/REWRITE** |
| Task state | ResearchTask concepts | **PORT to Postgres schema** |
| Source reliability | rate limiter/retry | **PORT** |
| Source ingestion | Research Mesh adapters | **REWRITE adapter layer** |
| Document ingestion | Parser Router | **PORT contract / WRAP selected engines** |
| Semantic retrieval | old semantic layer | **REWRITE simplified production retrieval** |
| Evidence graph | old graph ontology | **REWRITE domain graph** |
| Context hygiene | Hermes compactor + sidechains + OCE anchors | **COMBINE / PORT** |
| Runtime memory | OCE 3-tier model | **PORT/REWRITE multi-tenant** |
| Agent policy | pre/post hooks + OCE authority | **REWRITE typed capability policy** |
| Agent evals | Hermes skill-creator benchmark loop | **PORT/GENERALIZE** |
| Client artifact visuals | Open Design | **EVALUATE/FORK selectively** |
| Proposal/doc compiler | none sufficiently proven internally | **NEW BUILD / external search** |
| Deterministic eligibility | none generic internally | **NEW BUILD** |
| Explainable matching | none directly suitable | **NEW BUILD** |

---

# 13. R0 Result

Internal salvage has now identified enough material to reject a greenfield approach.

The biggest reusable systems are not the trading engines; they are the forgotten generic platform underneath them:

- research ingestion;
- parser normalization;
- bounded agents;
- worker lifecycle;
- queues and cost accounting;
- memory promotion/pruning;
- context isolation;
- skills/evals;
- governance;
- action hooks;
- audit;
- artifact tooling;
- Hermes/OCE boundary.

R0 does **not** declare all historical code production-ready. It establishes which ideas/components deserve promotion into the new repository after focused validation.

Next program gate: convert this salvage map into the clean seed architecture and G0 constitution, then perform fresh external due diligence only for the remaining gaps.