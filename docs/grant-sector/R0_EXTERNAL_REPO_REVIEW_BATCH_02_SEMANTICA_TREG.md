# R0 External Repo Review — Batch 02: Semantica + Treg

**Date:** 2026-08-24
**Branch:** `grant-sector-r0-salvage`

## Semantica — P0 architecture bake-off

Disposition: **PORT + WRAP candidate; potentially foundational for the Grant Evidence/Decision layer.**

Semantica is graph-native context/accountability infrastructure rather than merely generic RAG. Relevant capabilities include typed context graphs, decision chains, provenance, deterministic reasoning, conflict detection, entity resolution, temporal graph state, ontology/SHACL tooling, hybrid retrieval, normalization and structured exports.

### Proposed role

We continue to own the Grant ontology, schemas and domain contracts. Semantica is evaluated as an implementation substrate for:

- Grant Evidence Graph;
- claim → source provenance;
- decision ledger;
- causal/precedent relationships;
- conflicting-fact detection;
- temporal source state;
- deterministic graph reasoning;
- evidence lineage/export.

Do **not** replace the separate Personal-Hermes and CEO-Hermes memory doctrines with generic Semantica agent memory. Agent memory and auditable evidence are related but distinct concerns.

### Architecture hypothesis

`Grant ontology/contracts → Semantica graph/provenance/reasoning substrate → Grant Evidence Graph → deterministic domain kernel`

License observed from GitHub metadata: MIT. Exact production pin still requires license/dependency review.

## Treg — architecture pattern / restricted embedding

Disposition: **PORT architectural pattern / evaluate service usage; do not casually embed in proprietary commercial product.**

Treg describes itself as an OpenRouter-like layer for agent tools. Its architecture is directly relevant to the OCE/Hermes capability boundary: tools are registered centrally, credentials remain server-side, requests are proxied with credential injection, and calls are audited.

### Proposed pattern

`CEO Hermes → OCE policy/capability gate → tool registry + credential vault + injector/proxy → external API/OAuth/CLI provider`

This reinforces the R0 invariant that secrets never enter Hermes memory, prompts, sidechains, normal logs or Git.

Useful concepts to reproduce behind our own contracts:

- tool registry;
- capability metadata;
- encrypted credential vault;
- provider/credential health;
- credential injection;
- faithful request proxy;
- organization/member tool access;
- audit ledger;
- optional cost/provider metadata.

### Licensing caution

GitHub metadata reports a nonstandard license rather than plain MIT/Apache. Treat code embedding/forking as blocked pending explicit license review/permission. Architectural ideas can still inform our independently implemented Tool Gateway.

## Updated candidate stack

- Operator: Hermes
- Governance/control plane: OCE
- Research lifecycle: salvaged Research Mesh
- Deep research patterns: GPT Researcher
- Web extraction: Crawl4AI
- Search discovery: optional SearXNG
- Parsing: existing parser fabric + Unstructured bake-off
- Visual parsing fallback: PixelRAG
- Evidence/provenance/decision substrate: **Semantica bake-off**
- Agent regression/red-team: Promptfoo + Hermes Eval Lab
- Structured output validation: Guardrails
- Budget/spreadsheet workspace: Univer
- Integration execution: bounded Activepieces
- Tool registry/credential proxy: **Treg-inspired pattern behind OCE policy**

## Next external research priority

Stop broad generic agent-framework hunting. Highest-value next work is Grant-domain data and source connectivity: federal/state/local grant opportunities, historical awards, foundations, nonprofit filings, winner intelligence, demographic/community-impact datasets, and reliable government/foundation source adapters.