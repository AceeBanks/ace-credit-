# R0 External Repo Review — Batch 01

**Date:** 2026-08-24  
**Branch:** `grant-sector-r0-salvage`  
**Status:** REVIEWED AGAINST R0 GAP MAP

## Review rule

Each external project is evaluated as a capability source, not as an architectural authority. Dispositions use: ADOPT / FORK / WRAP / PORT / REWRITE / REJECT / DEFER.

---

## Executive ranking

### Tier 1 — Strong candidates for the Grant platform

1. **Crawl4AI** — WRAP / PORT selected extraction patterns.
2. **GPT Researcher** — PORT research planning/publisher patterns; do not use as sovereign research agent.
3. **Unstructured** — WRAP as one document partitioning engine behind our SourceDocument interface.
4. **Promptfoo** — ADOPT alongside our Hermes eval lab for red-team/security/regression coverage.
5. **Guardrails AI** — WRAP/PORT validators for structured outputs and selected risk checks.
6. **Univer** — EVALUATE / WRAP for spreadsheet/document UI and headless workbook processing; especially promising for budget workspaces.
7. **Activepieces** — EVALUATE / WRAP as integration connector fabric and low-code workflow surface, not canonical workflow authority.
8. **PixelRAG** — EXPERIMENT / WRAP as visual retrieval fallback for layout-heavy PDFs/web pages.

### Tier 2 — Useful but bounded / later

9. **SearXNG** — WRAP optional privacy-oriented search aggregator; useful provider diversity, not evidence authority.
10. **Documenso** — DEFER / external service integration for signatures/approvals; licensing needs care.
11. **DocuSeal** — DEFER / external service integration for signatures/forms; licensing needs care.
12. **Plane** — DEFER; useful product/work tracking concepts, but not needed as embedded runtime.
13. **MCP reference servers** — REFERENCE ONLY; use for patterns/tests, not production servers.
14. **CanvasTTY** — DEV-TOOL DEFER; potentially useful for internal operator visibility, not client product.
15. **MindsHub** — ARCHITECTURE STUDY / REJECT wholesale adoption. It overlaps heavily with Hermes/OCE and would duplicate the platform.
16. **Awesome AI Apps** — RESEARCH INDEX ONLY, not dependency.

### Licensing concern / avoid as default

17. **HyperFormula** — technically strong, but current licensing is GPLv3/proprietary. Do not embed into proprietary commercial SaaS without deliberate license decision. Univer is the more attractive starting point.

---

# 1. GPT Researcher — assafelovic/gpt-researcher

**What it does:** autonomous deep web/local research with planner → execution workers → publisher; source tracking, parallel research, report generation, MCP support, local document research.

**Fit:** HIGH.

**R0 overlap:** Our old Research Mesh already covers bounded tasks, lifecycle, evaluation, source ingestion, and synthesis. GPT Researcher adds mature research-question decomposition, parallel source gathering, report publishing, and current ecosystem support.

**Disposition:** **PORT / WRAP selected research patterns.**

**Use:**

- research-plan generation for funder/winner/community research;
- source-query decomposition;
- parallel research execution as a bounded worker capability;
- report structure/publisher patterns;
- optional MCP wrapper for specific deep-research jobs.

**Do not:** make GPT Researcher the CEO, source of truth, eligibility engine, or permanent research memory.

**Architecture:** CEO issues a ResearchTask → our policy layer → GPT Researcher-compatible bounded worker → returns ResearchPack with source snapshots/claims → Evidence Graph validates/promotes.

**License:** reported Apache-2.0 in current GitHub README, while packaging metadata may show MIT depending on version. Pin an exact commit/tag and verify its license files before use.

**Priority:** P0 experiment.

---

# 2. Unstructured — Unstructured-IO/unstructured

**What it does:** document ingestion/pre-processing and partitioning for PDFs, HTML, Word, images, and other complex formats into structured elements for downstream LLM pipelines.

**Fit:** HIGH but overlaps our historical Parser Router.

**Disposition:** **WRAP, benchmark against existing MarkItDown/OpenDataLoader/Chandra stack.**

**Use:** one parser engine behind our product-owned `SourceDocument` interface.

**Why not adopt as our ingestion architecture:** We require immutable source snapshots, authority tier, tenant scope, parsing confidence, document revision lineage, evidence references, and deterministic identity. Unstructured should produce parsed elements; our platform owns provenance and canonicalization.

**License:** Apache-2.0.

**Priority:** P0 parser benchmark candidate.

---

# 3. Promptfoo — promptfoo/promptfoo

**What it does:** LLM/agent/RAG evals, model comparison, CI/CD checks, adversarial red teaming and vulnerability scanning.

**Fit:** VERY HIGH.

**Disposition:** **ADOPT as complementary eval/security tool.**

Our archived Hermes skill-creator already gives candidate-vs-baseline behavioral evals and human review. Promptfoo should supplement that rather than replace it.

**Use:**

- prompt/agent regression suites;
- jailbreak and prompt-injection tests;
- tool-use red teaming;
- PII/security checks;
- model comparison;
- CI gates.

**Combined architecture:** Hermes Eval Lab owns domain-specific assertions and promotion policy; Promptfoo provides mature testing/red-team execution.

**License:** MIT; README states it remains open-source.

**Priority:** P0.

---

# 4. CanvasTTY — howdeploy/CanvasTTY

**What it does:** Electron spatial desktop for real local PTYs and agent CLI sessions, with typed allow-listed renderer capabilities, browser/audit log, runtime plugins, and direct support for Hermes/Codex/Claude/etc.

**Fit:** MEDIUM for our internal development/operator environment; LOW for client SaaS.

**Disposition:** **DEFER / DEV-TOOL EVALUATION.**

Potential value:

- internal CEO/operator observability during development;
- live agent session management;
- agent terminal workspace;
- inspiration for typed plugin capability boundaries.

Do not put this in the Grant production architecture.

**License:** MIT.

**Priority:** P3 internal tooling.

---

# 5. SearXNG — searxng/searxng

**What it does:** self-hosted privacy-focused metasearch aggregator across multiple search services/databases.

**Fit:** MEDIUM-HIGH as search provider diversity.

**Disposition:** **WRAP optional search provider.**

Use under our Research Source Fabric so research workers can query multiple search providers without binding us to a single paid search API.

Important rule: search results are discovery hints, not evidence. Research worker must fetch and snapshot the original source before a claim can be promoted.

**License:** AGPL-3.0. Network-use obligations matter if modified/embedded. Safer posture is isolated service integration with legal review rather than copy/paste into proprietary source tree.

**Priority:** P1/P2.

---

# 6. Crawl4AI — unclecode/crawl4ai

**What it does:** LLM-friendly crawler/scraper for structured web extraction.

**Fit:** VERY HIGH.

**Disposition:** **WRAP, with selective PORT of extraction/retry/browser patterns if useful.**

This is one of the strongest external finds for our open R0 browser/extraction gap.

Use for:

- grant pages without APIs;
- foundation/corporate sites;
- funder history pages;
- prior winner pages;
- structured markdown/data extraction;
- browser-backed dynamic pages.

Required product additions:

- immutable raw page snapshot;
- fetch metadata;
- content hash;
- source authority;
- retry/robots/terms policies;
- adversarial webpage/prompt-injection sanitization;
- tenant/project context kept outside crawler.

**License:** current repository presents Apache-2.0; verify exact pinned commit and attribution requirements before production.

**Priority:** P0.

---

# 7. Documenso — documenso/documenso

**What it does:** self-hostable DocuSign alternative with signing, PDF signatures, Postgres-backed app, APIs/SDKs and enterprise features.

**Fit:** MEDIUM, mainly later human approval/signature workflows.

**Disposition:** **DEFER / integrate via API or isolated service rather than fork.**

Potential Grant uses:

- client certification/signature;
- board approval;
- letters of commitment;
- final internal sign-off packages;
- Phase 2 partner documents.

Not a proposal document compiler.

**License:** Community Edition AGPL-3.0; enterprise areas commercial. This is important for proprietary SaaS architecture.

**Priority:** P2/P3.

---

# 8. Activepieces — activepieces/activepieces

**What it does:** self-hostable workflow automation / integration platform with a large connector ecosystem, MCP and AI-agent tooling.

**Fit:** HIGH as connector/integration fabric, but dangerous if allowed to become a second control plane.

**Disposition:** **EVALUATE / WRAP selected connector execution.**

Potential value:

- email/calendar/storage/CRM integrations;
- later outreach workflows;
- administrative automations;
- external SaaS connectors;
- rapid proof of integrations that can later be hardened.

Architecture rule:

> CEO Hermes/OCE remains workflow authority. Activepieces executes bounded integration tasks through explicit contracts; it does not own canonical application state.

**License:** Community core MIT, enterprise directories commercial. Need exact feature/license mapping before relying on functionality.

**Priority:** P1 connector evaluation, especially for Phase 2 integrations.

---

# 9. Model Context Protocol reference servers — modelcontextprotocol/servers

**What it does:** official/reference MCP server implementations and pointers to community servers.

**Fit:** MEDIUM as standards/reference material.

**Disposition:** **REFERENCE / PORT test patterns only.**

The maintainers explicitly warn these are reference implementations, not production-ready solutions. We already have an OCE-Hermes MCP facade, so this repo should help us validate protocol conventions, schemas, filesystem boundaries, and SDK usage rather than become our server suite.

**Priority:** P1 development reference.

---

# 10. MindsHub — mindsdb/mindshub

**What it does:** broad AI cowork platform with connected data, model routing, open agent harnesses including Hermes, artifacts, memory, skills, scheduling, desktop/web apps and deploy-anywhere posture.

**Fit:** VERY INTERESTING architecturally but enormous overlap with our intended platform.

**Disposition:** **STUDY / REJECT wholesale adoption.**

This is probably the most useful architecture comparison in the batch because it independently converges on several decisions we made:

- Hermes as swappable operator harness;
- connectors behind scoped credentials;
- model routing;
- artifacts;
- schedules;
- connected data;
- deploy local/VPC/on-prem.

Potential salvage:

- connector/vault architecture;
- artifact/project APIs;
- agent-harness abstraction;
- credential scoping patterns;
- submodule/pinning development methodology.

Why not build on it: it would duplicate OCE/Hermes and turn a focused Grant platform into a fork of another general-purpose agent OS.

**License:** top-level MIT, but bundled submodules have independent licenses and require per-component review.

**Priority:** P0 architecture study, not dependency.

---

# 11. Guardrails AI — guardrails-ai/guardrails

**What it does:** structured LLM outputs plus composable input/output validators and risk guards.

**Fit:** HIGH.

**Disposition:** **WRAP / PORT selected validators.**

Use for:

- typed output validation;
- malformed structured result repair/rejection;
- PII/content validators where appropriate;
- bounded safety checks;
- post-generation constraints.

Do not make it our policy/authorization system. Deterministic domain rules remain Pydantic/JSON Schema/domain code/OCE policy.

Current project direction moved validators toward standard PyPI packages and away from hosted remote inferencing, which is favorable for local/private execution.

**License:** Apache-2.0.

**Priority:** P0/P1.

---

# 12. PixelRAG — StarTrail-org/PixelRAG

**What it does:** visual retrieval by rendering web pages/PDFs/images into screenshot tiles and retrieving over visual representations, retaining layout, charts, tables and infographics that text parsers may lose.

**Fit:** HIGH as a specialized fallback, not primary RAG.

**Disposition:** **EXPERIMENT / WRAP.**

Potential uses:

- grant PDFs with complex tables/layout;
- award reports;
- infographics;
- scanned/layout-heavy webpages;
- verifying information that text extraction destroys.

Architecture:

```text
normal parser succeeds → use structured text
normal parser low-quality/layout-sensitive → PixelRAG visual path
```

This avoids the cost/complexity of making all retrieval pixel-native.

**License:** Apache-2.0.

**Priority:** P1 benchmark.

---

# 13. Plane — makeplane/plane

**What it does:** self-hosted project/work management platform with work items, cycles, modules, pages, analytics; Postgres/Redis stack.

**Fit:** LOW-MEDIUM as product runtime; MEDIUM as development/admin inspiration.

**Disposition:** **DEFER.**

We already have GitHub/issues and intend to own application/project state in Postgres. Embedding Plane would create another project-state authority. Could be used externally by the dev/operations team or mined for UX patterns.

**License:** AGPL-3.0.

**Priority:** P3.

---

# 14. HyperFormula — handsontable/hyperformula

**What it does:** high-speed headless spreadsheet formula parser/evaluator with ~400 functions, custom functions and Node support.

**Fit:** TECHNICALLY HIGH for budgets; LICENSE RISK HIGH.

**Disposition:** **DEFER / likely REJECT as default commercial dependency unless licensed.**

Current repo states GPLv3 or proprietary licensing. For our proprietary commercial SaaS this demands an explicit legal/commercial decision.

The capabilities are exactly relevant to deterministic budget/financial calculation, but we should first investigate Apache/MIT-compatible engines or use our own narrower calculation model.

**Priority:** P2 only after license decision.

---

# 15. Univer — dream-num/univer

**What it does:** full-stack spreadsheet/document/presentation framework with browser and headless modes, formulas, validation, formatting, tables and extensible APIs; Apache-2.0 core.

**Fit:** VERY HIGH for our budget workspace and possibly client-editable artifact experiences.

**Disposition:** **EVALUATE / WRAP / potential FORK of bounded open-source modules.**

Most interesting uses:

- budget spreadsheet UI;
- headless workbook processing;
- validation and formulas;
- client editable financial models;
- shared document architecture concepts;
- future proposal/doc workspaces.

Caution: README distinguishes open-source capabilities from Pro features such as some import/export, server-side calculation, collaboration and enhanced spreadsheet features. We must map exactly what the free Apache modules provide before architecture commitment.

**License:** Apache-2.0 for open-source repository; Pro extensions separate.

**Priority:** P0 spreadsheet/budget prototype.

---

# 16. DocuSeal — docusealco/docuseal

**What it does:** document template/form/e-signature platform with field builder, APIs, webhooks, storage integrations, roles, conditional fields/formulas, DOCX/PDF field-tag templates and embedded signing.

**Fit:** MEDIUM-HIGH for later application/forms/signatures.

**Disposition:** **DEFER / API integration candidate rather than fork.**

Potential uses:

- signed certifications;
- client questionnaires;
- document templates requiring user-filled fields;
- partner commitment forms;
- final approval workflows.

**License:** AGPLv3 with additional Section 7(b) terms. Requires deliberate legal review for any embedded/forked commercial use.

**Priority:** P2/P3.

---

# 17. Awesome AI Apps — Arindam200/awesome-ai-apps

**What it does:** curated collection of many example RAG, agent, workflow, MCP and voice projects.

**Fit:** LOW as dependency; MEDIUM as research index.

**Disposition:** **REFERENCE ONLY.**

Useful if we need examples for a very specific pattern later. Do not ingest this broad repo into the product.

**License:** MIT for repository examples.

**Priority:** P4.

---

# 18. Duplicates in submitted list

- `Unstructured-IO/unstructured` appears twice.
- Activepieces appears both as repo and organization link; treated as one candidate.
- `opensourceprojects.dev/post/univer` is a discovery page for Univer; canonical repo reviewed directly.
- DocuSeal website reviewed through its canonical GitHub project for technical/licensing conclusions.

---

# 19. X/Twitter links

Four X links were supplied:

- `iamrexei/status/2091465111755968718`
- `exm7777/status/2089714608244457543`
- `themattberman/status/2091888757909660114`
- `iamrexei/status/2090090583649861708`

The current web environment could not reliably retrieve three of them (cache/403) and returned no readable content for the fourth. No architectural claim from those posts has been assumed. If the posts are screenshots/videos naming additional repos, they should be re-sent as screenshots or direct repo links for grounded evaluation.

---

# 20. Recommended short list to actually prototype

Do **not** fork all reviewed repos. Run focused capability bake-offs.

## Prototype A — Web research path

- Crawl4AI
- GPT Researcher research decomposition
- optional SearXNG discovery
- our ResearchTask/lifecycle and Evidence Graph

Goal: one funder/winner research job with source snapshots and zero unsupported promoted claims.

## Prototype B — Document ingestion path

Compare:

- existing OpenDataLoader/MarkItDown/Chandra stack
- Unstructured
- PixelRAG fallback

Corpus:

- normal PDFs;
- scanned PDFs;
- tables;
- government forms;
- graphics-heavy annual reports;
- DOCX business plans.

Measure extraction accuracy, table retention, citation localization, latency and cost.

## Prototype C — Agent quality/security

- Hermes Skill Eval Lab
- Promptfoo
- Guardrails AI

Goal: unified test layer for intent contracts, structured worker outputs, prompt-injection resistance and regression gates.

## Prototype D — Financial workspace

- Univer headless + Sheets UI
- our canonical BudgetModel

Goal: verify that canonical budget facts can compile into an editable spreadsheet while all formula results reconcile against deterministic backend calculations.

## Prototype E — Integration fabric

- Activepieces Community
- existing OCE/Hermes capability facade

Goal: determine whether selected integrations can be exposed as bounded tools without Activepieces becoming canonical workflow state.

---

# 21. Architecture changes resulting from Batch 01

This batch does **not** overturn the R0 seed architecture. It strengthens it.

Recommended additions to G0 candidate stack:

- Crawl4AI as leading web-extraction candidate;
- Unstructured in parser bake-off;
- GPT Researcher as bounded deep-research worker/pattern source;
- Promptfoo as red-team/regression companion to internal eval lab;
- Guardrails for selected structured-output validators;
- Univer as leading budget/spreadsheet workspace candidate;
- PixelRAG as visual fallback path;
- Activepieces as bounded connector/integration candidate;
- MindsHub as architecture reference showing independent convergence on Hermes-as-harness + scoped connectors, but not as platform base.

The largest remaining external research need after this batch is no longer generic agent tooling. It is **grant-specific data sources/APIs, award-history/winner datasets, nonprofit/funder intelligence, and reliable government/foundation source connectivity**.