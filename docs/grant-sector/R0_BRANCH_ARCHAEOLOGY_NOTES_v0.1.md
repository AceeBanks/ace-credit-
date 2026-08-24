# R0 Branch Archaeology Notes

**Document ID:** GS-R0-ARCH-001  
**Version:** 0.2  
**Status:** DEEP-DIVE PASS COMPLETE  
**Date:** 2026-08-24

This file records branch-level archaeology for the Grant Sector salvage pass. It preserves lineage and distinguishes reusable generic infrastructure from trading-domain baggage.

---

## 1. Scope

Deeply inspected or structurally compared:

- `main`
- `master`
- `execution-runtime-foundation`
- `hermes-set-up`
- `archive/hermes-02e51f11`
- `archive/hermes-262c2f34`
- `archive/hermes-cde01a2a`
- `archive/pruned-master-2026-08-15`
- `archive/review-branch`
- `archive/content-oc2`
- current OCE / Golden System planning material

Trading-specific branches (`capital-routing`, MVE, crypto, CEREBUS strategy foundries, trading-bot branches) are excluded as product logic. Generic infrastructure historically shared with those branches is captured through `master`, OCE, tools, archives, and the runtime-foundation branch.

---

# 2. Main

`main` is the cleaned current branch and should remain the primary source for currently surviving OCE code and Golden System governance.

Important current survivors:

- `oce/backend/` remains extensive;
- OCE docs/plans remain authoritative for current Golden System intent;
- generic `tools/` survives;
- historical `core/` cognition/research tree is no longer present on `main` and must be salvaged from `master`/archives;
- current `ARCHITECTURE.md` documents Observer Core, Forge, knowledge/memory, execution, monitoring, and external integration at a high level.

Current OCE still exposes historically useful generic modules including:

- structural memory;
- adaptive compression;
- alerting;
- command center;
- consensus;
- drift detection;
- event classification/routing;
- execution optimization;
- coevolution;
- broader backend modules requiring targeted promotion review.

Conclusion: **source of current governance and surviving runtime components, not sole source of reusable platform history.**

---

# 3. Master

`master` is the most important archaeology source.

It diverges heavily from current `main` and preserves the old generalized cognition platform removed during cleanup. It should never be merged wholesale, but it contains high-value reusable subsystems.

Major discoveries:

## 3.1 `core/parser`

Historical universal document ingestion architecture using multiple parsing engines and normalizing output into a typed Cognition Object.

Relevant to:

- organization uploads;
- grant PDFs;
- prior winning proposal documents;
- public reports;
- partnership letters;
- business plans;
- scanned/image material.

## 3.2 `core/semantic`

Historical chunking, embeddings, vector storage, semantic retrieval, clustering, and associative recall.

Relevant as conceptual basis for evidence retrieval, but storage architecture should be simplified and modernized for the new product.

## 3.3 `core/knowledge/graph`

Historical entities/edges, typed relationships, contradiction detection, confidence, inference, abstraction, and gap detection.

Direct conceptual precursor to the Grant Evidence Graph.

## 3.4 `core/research`

Highest-value subsystem found in `master`.

Contains:

- ingestion adapters;
- source models;
- SQLite cache;
- dedupe;
- async rate limiter;
- scheduler;
- research agents;
- evaluator;
- router;
- bounded task queue;
- agent lifecycle;
- task generation;
- research synthesis;
- tests.

Historical README reports 106/106 tests and an end-to-end autonomous research cycle. That claim is lineage evidence only until the relevant code is isolated and rerun in a clean environment.

## 3.5 `core/cognition`

Contains procedural cognition and unified cognition routing. Useful as architecture reference, but old imports/coupling argue for rewriting a cleaner Grant-specific interface rather than lifting code wholesale.

## 3.6 OCE backend history

Historical OCE architecture documents a large FastAPI runtime with memory, event fabric, agent lifecycle, research APIs, governance, execution, tracing, alerting, metrics, and self-heal patterns.

## 3.7 O2C doctrine

Extremely valuable architectural documents found in master:

- Harness Engineering;
- Continuity Intelligence;
- Meta Cognition;
- Multi-Scale Orchestration;
- Operator Coevolution;
- agent workflow and data/storage doctrine.

These documents are more useful as design doctrine than much of the literal prototype implementation.

Conclusion: **master is the primary salvage quarry for Research Fabric, Memory/Continuity, Evidence, Agent Harness, and Parser concepts.**

---

# 4. Execution Runtime Foundation

This branch is deeply diverged from current main and appears to preserve a broad development-agent ecosystem.

Notable generic additions found in the branch comparison include:

- AI team orchestration skill;
- context-map skill;
- project brief/sprint-plan/brainstorm templates;
- documentation tooling;
- Copilot-related skills;
- web-artifacts builder;
- many development workflow skills;
- historical Hermes materials.

Deep inspections:

## 4.1 AI Team Orchestration

Useful durable patterns:

- role separation;
- explicit handoffs;
- durable `PROJECT_BRIEF.md` rather than chat as truth;
- sprint plan/progress/done files;
- context recovery after long chats;
- issue tracker as bug source of truth;
- separate dev/QA roles.

Use for the build process, not as the literal Grant runtime-agent organization.

## 4.2 Context Map

Requires dependency, tests, reference patterns, and risk assessment before code changes. Strong candidate for future CEO self-improvement/change-proposal workflow.

## 4.3 Web Artifacts Builder

Provides React/TypeScript/Tailwind/shadcn artifact scaffolding and single-file bundling. Useful for prototypes, review tools, and internal dashboards; not product core.

Conclusion: **do not merge branch. Port selected development skills and planning patterns.**

---

# 5. Hermes Setup

`hermes-set-up` is only one commit ahead of main but that single commit is dense and directly relevant.

It adds `oce-hermes-telegram-operator/`, including:

- isolated Hermes profile;
- Hermes config;
- MCP facade;
- schema definitions;
- structured audit logger;
- redaction;
- rate limiting;
- request IDs;
- service-token boundary;
- Docker Compose;
- systemd config;
- setup/start/stop/status/doctor scripts;
- capability matrix;
- OCE integration contract;
- threat model;
- disaster recovery;
- secret rotation;
- evidence/validation documentation;
- unit, integration, and adversarial security tests.

Its binding architecture is exactly the right direction:

> Hermes is an external operator. OCE remains authority. Hermes cannot directly reach databases/services and uses a narrow filtered facade.

Current version is observer/read-only, which makes it a safe foundation for our staged authority ladder rather than a limitation.

Conclusion: **top R0 fork/port candidate.**

---

# 6. Hermes Archives

Branches:

- `archive/hermes-02e51f11`
- `archive/hermes-262c2f34`
- `archive/hermes-cde01a2a`

The `.hermes` directory entries across all three resolve to identical object SHAs for memory, soul, user, config, cron, memories, and skills.

Therefore, repeated deep reading of the same Hermes files would add no value. The branches remain separate lineage snapshots, but Hermes salvage can use one representative snapshot.

High-value contents:

- memory architecture;
- five-pillar Hermes mental model;
- context compaction;
- subagent sidechains;
- skill creator/evaluation harness;
- cron/workflow patterns;
- goal mode;
- maintenance;
- MCP integration;
- GitHub backup/search;
- agent onboarding/harness skills.

Critical negative finding:

- historical persistent memory contained secrets/credentials. Values were not copied into Grant Sector docs and must never be carried into the new system.

Conclusion: **strong architecture/pattern source; not safe to fork as a whole user state.**

---

# 7. Pruned Master Archive

`archive/pruned-master-2026-08-15` has no common ancestor visible through normal compare against current main, so it is treated as an independent snapshot.

Its `MASTER_CATALOG.md` has the same blob SHA as the reviewed archive and documents the historical fork inventory and generalized architecture.

It preserves broad `.agents/skills/` content including generic engineering skills such as:

- accessibility;
- FastAPI Python/templates;
- frontend design;
- Next.js best practices/cache/upgrade;
- Node backend patterns;
- data/science skills;
- many trading skills that are out of scope.

Conclusion: **use as skill/fork recovery snapshot when a specific historical asset is missing elsewhere. Do not use as seed.**

---

# 8. Review Branch

`archive/review-branch` shares important exact SHAs with `archive/pruned-master-2026-08-15`, including the same historical Master Catalog.

Conclusion: **low incremental salvage value after duplicate confirmation; preserve for lineage and targeted recovery only.**

---

# 9. Content OC2 Archive

`archive/content-oc2` preserves a complete content-farm tree:

- `content-farm/design`;
- `content-farm/docs`;
- `content-farm/github-repos`;
- `content-farm/sites`;
- `content-farm/tools`.

Historical catalog associates this with Open Design and related artifact systems capable of presentation/deck/visual outputs.

Potential Grant use:

- pitch decks;
- research briefs;
- impact reports;
- branded one-pagers;
- client-facing evidence summaries.

Conclusion: **artifact-generation quarry only; do not import the content farm wholesale.**

---

# 10. Generic Tools

Current and historical `tools/` contain multiple transferable utilities.

Deeply confirmed:

## Agent Hooks

`pre-tool-use-enhanced.py`:

- denylist interception;
- protected config/identity files;
- explicit approval requirement;
- fail-closed parse/error behavior.

`post-tool-use-enhanced.py`:

- post-edit validation;
- Python syntax checks;
- JSON/YAML/Markdown validation;
- structured JSONL tool-call audit.

These should become typed product policy hooks rather than remain shell-regex scripts.

## Chat Summarizer

Current `chat_summarizer.py`:

- archives full history;
- keeps recent messages intact;
- preserves priority directives/handoffs;
- condenses older routine messages into summaries.

This directly validates the bounded-memory doctrine for CEO Hermes.

Other current tools visible in main include agent onboarding, error analysis, architecture commits, cron/workflow tooling, chat sync, and Claude/Hermes MCP integration. These remain targeted candidates rather than automatic dependencies.

---

# 11. Historical Fork Inventory Relevant to Grant Product

Master Catalog identifies internal copies/forks of:

### Document/Parser
- `microsoft/markitdown`
- `opendataloader-project/opendataloader-pdf`
- `run-llama/liteparse`
- `datalab-to/chandra`

### Semantic / Graph
- `RyanCodrai/turbovec`
- `colbymchenry/codegraph`

### Skills / Procedural Cognition
- `virgiliojr94/book-to-skill`
- `maipianworni/SkillTree`
- `mattpocock/skills`

### Research / Distillation
- `teng-lin/notebooklm-py`
- `Thysrael/Horizon`

### Artifact Production
- `nexu-io/open-design`
- `terrastruct/d2`

Other media/voice/content assets exist but are lower priority for the Grant product.

Important: historical presence does not establish current upstream license/maintenance/security suitability. External due diligence follows internal salvage.

---

# 12. Pure Trading Branch Rule Applied

No effort was spent re-deriving MVE, capital routing, crypto strategy, CEREBUS setup logic, market prediction, or broker execution.

Reusable generic patterns previously generated in that broader workspace—testing discipline, agent lifecycle, orchestration, data contracts, research systems, observability, and runtime controls—were captured from domain-neutral locations instead.

This keeps R0 focused and prevents accidental trading coupling.

---

# 13. Branch-Level Recommendation

The clean product repository should eventually be seeded from **selected files/contracts**, not any existing branch.

Recommended source hierarchy:

1. **Current OCE Golden System docs** — authority/governance source.
2. **`hermes-set-up`** — Hermes/operator boundary implementation source.
3. **`master/core/research`** — research fabric implementation source.
4. **`master/core/parser`** — document ingestion contract/source.
5. **current OCE memory/runtime code** — bounded memory and runtime patterns.
6. **archived Hermes skills** — context/sidechain/eval patterns.
7. **`execution-runtime-foundation`** — build/development agent-process assets.
8. **content archive** — artifact production assets.
9. archives/pruned/review — recovery/lineage only.

No existing branch should become the production base verbatim.