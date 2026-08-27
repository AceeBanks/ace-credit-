# G0 Book 9 — Canonical State Ownership Matrix

**Chapter:** B9.C7
**Date:** 2026-08-27
**Status:** FROZEN (ADR `OCE_NATIVE`)

No ambiguous dual ownership. One owner per state class. Anything not
listed here is non-sovereign (rebuildable projection or ephemeral
transport).

## Ownership matrix

| State class | Owner | Authority | Rebuildable? | Notes |
|---|---|---|---|---|
| Organization (client/org) | **Postgres** | canonical | no | tenant-scoped |
| Grant opportunity + OpportunityRevision | **Postgres** | canonical | no | append-only revision chain |
| ApplicationProject | **Postgres** | canonical | no | project-scoped |
| Requirements / blueprint | **Postgres** | canonical | no | derived from revision, stored |
| Workflow state (intent→package) | **Postgres** | canonical | no | stage records + decision refs |
| Policy / capability data | **Postgres** | canonical | no | capability registry, grant policy |
| Approvals | **Postgres** | canonical | no | ApprovalRegistry |
| DecisionRecords | **Postgres** | canonical | no | replayable |
| Audit index | **Postgres** | canonical | no | append-only |
| Tenants / users / memberships / principals | **Postgres** | canonical | no | |
| SourceSnapshots (raw) | **Object storage** | canonical | no (immutable) | content-addressed |
| Uploaded documents | **Object storage** | canonical | no | |
| Generated artifacts (ArtifactVersion) | **Object storage** | canonical | no | versioned, immutable |
| Large evidence payloads | **Object storage** | canonical | no | |
| Queue/transport messages | **Redis/queue** | transport only | yes | ephemeral, non-authoritative |
| Cache / leases / rate limits | **Redis/queue** | transport only | yes | |
| Graph/relationship projection | **Graph (projected)** | non-sovereign | **yes** | rebuildable from canonical |
| Vector/semantic index | **Vector (projected)** | non-sovereign | **yes** | rebuildable from canonical |
| Hermes memory (Personal/CEO) | **Hermes memory** | non-authoritative | yes | curated continuity only, never truth |
| Model runtime state | **Model gateway** | execution only | yes | request/response audit refs, not Grant truth |

## Rules

1. **Postgres is the only owner of workflow truth.** No runtime, agent,
   framework, or provider may hold authoritative Grant/workflow state.
2. **Object storage is the only owner of immutable payloads.** Large blobs
   never live in Postgres; their refs do.
3. **Redis/queue never owns consequential state.** A message loss may not
   lose a DecisionRecord or ApplicationProject — those are already durable
   in Postgres before any queue signal.
4. **Graph/vector are rebuildable projections.** If deleted, they
   reconstruct from canonical state; they are never required for truth.
5. **Hermes memory is curated continuity, not truth.** Cold reconstruction
   must not require it (`raw_chat_required=false` is a Book 8 invariant).
6. **Model runtime holds execution state only.** Token/cost/latency audit
   refs are evidence; the model never writes Grant state.

## Enforcement

- Migration seed (`G0_B9_DATA_MIGRATION_SEED.md`) creates the canonical
  tables; no framework owns them.
- ToolGateway/ModelGateway deny any write to canonical tables from agent
  execution paths.
- Fresh-clone verification (`G0_B9_SEED_VERIFICATION_REPORT.md`) proves
  rebuild-from-empty produces the full slice state.
