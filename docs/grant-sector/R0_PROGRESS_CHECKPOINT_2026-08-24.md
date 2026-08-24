# R0 Progress Checkpoint — Before External Repo Review

**Date:** 2026-08-24  
**Branch:** `grant-sector-r0-salvage`  
**Status:** INTERNAL SALVAGE COMPLETE ENOUGH FOR TARGETED EXTERNAL REPO INTAKE

## Current locked direction

- Dual-Hermes architecture: Personal Hermes + CEO Hermes.
- Hermes operates the platform; Hermes is not the source of truth.
- Postgres is authoritative state; Redis may be transport/cache only.
- Worker agents are bounded/disposable and return short result packets; full traces live in sidechains/audit storage.
- Deterministic eligibility and numerical logic stay outside the LLM.
- OCE governance, Hermes/OCE MCP facade, Research Mesh patterns, context compaction, sidechains, skill evals, parser contracts, and selected artifact tooling are salvage candidates.
- Trading-domain logic is excluded except for generic infrastructure.
- New production repository will be created only after G0 freezes the core contracts.

## Internal capabilities already covered well enough that external repos are NOT a priority

- generic memory-agent frameworks;
- generic multi-agent orchestration frameworks;
- generic vector databases / RAG frameworks unless they solve a specific unmet constraint;
- generic PDF-to-text tools;
- generic MCP wrappers;
- generic cron/scheduler agents;
- generic prompt/skill systems;
- generic agent-evaluation frameworks;
- generic graph databases;
- trading/data/backtesting systems;
- generic chat UIs;
- generic LLM routers that only pick models by prompt size/cost;
- generic autonomous coding agents.

## Highest-value external repo categories to review next

1. Grant opportunity / public-funding data connectors and grant-domain datasets.
2. Robust web/browser extraction and change-detection systems for sites without APIs.
3. Deterministic rules/eligibility engines or policy DSLs that can be adapted to grant qualification.
4. Production document-generation systems for DOCX/PDF with templating, styles, sections, citations, tables, headers/footers, and stable rendering.
5. Spreadsheet/budget generation and formula-validation systems.
6. Multi-tenant identity, RBAC/ABAC, authorization-policy, and service-identity systems.
7. Object/artifact storage and versioning systems suitable for uploads, source snapshots, generated deliverables, and audit traces.
8. Source provenance / citation / evidence-lineage systems.
9. Workflow/state-machine engines with durable Postgres-backed execution, idempotency, retries, human approval, and resumability.
10. Production observability for LLM/tool workflows: traces, costs, workflow health, source-adapter health, and evaluation telemetry.
11. Application/form automation libraries that can map canonical data into external grant portals while preserving human approval.
12. Grant-specific or nonprofit/funder research tooling, award-history datasets, winner research, and demographic/community-impact data connectors.

## Repo intake rule

External repos are evaluated as capability candidates, not architecture authorities. Prefer narrow, replaceable components behind our own contracts. Avoid adopting large frameworks simply because they appear comprehensive.
