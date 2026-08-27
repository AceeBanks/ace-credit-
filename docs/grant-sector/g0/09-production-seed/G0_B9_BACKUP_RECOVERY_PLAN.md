# G0 Book 9 — Backup / Recovery / Disaster Recovery Plan

**Chapter:** B9.C20
**Date:** 2026-08-27
**Status:** FROZEN

## Backup classes

| Class | What | Method | Frequency |
|---|---|---|---|
| Canonical database | Postgres (all canonical tables) | nightly logical/物理 backup + WAL/PITR where available | daily + continuous |
| Object/artifact storage | snapshots, artifacts, evidence payloads | versioned object store replication | continuous |
| Configuration/policy | config/ + policy YAML | in Git (immutable) | on change |
| Audit evidence | audit_events + decision_records | part of DB backup | daily |
| Graph/vector indexes | projections | NOT backed up — rebuildable | n/a |

## Recovery tests (each with a pass criterion)

| Test | Criterion | Evidence |
|---|---|---|
| DB restore | restore nightly backup to empty DB, verify row counts + FK integrity | G1 quarterly drill; migration seed proves empty-DB build |
| Artifact restore | object store version retrieval returns the exact payload by content_hash | G1 drill |
| Runtime restart | process kill + cold start reconstructs slice state | MEASURED — 10 records, 1.1 ms, raw_chat_required=false |
| Graph/vector rebuild | rebuild projection from canonical state | G1 drill (projections non-sovereign by constitution) |
| Hermes reset/reconstruction | fresh Hermes, full slice state from records | MEASURED (Book 8 C33) |
| Recovery to known migration version | migrate down/up to a pinned migration | CI migration tests |

## Rules

1. Derived indexes (graph/vector) are rebuildable — never a single point of
   truth loss.
2. No system may depend on hidden conversation memory to recover an
   application (`raw_chat_required=false` is law).
3. Recovery drills run quarterly in staging; results recorded.
4. Object store versioning is enabled before first production write.
