# G0 Book 9 — CI / CD Policy

**Chapter:** B9.C17
**Date:** 2026-08-27
**Status:** FROZEN

## CI gates (required on every change)

| Gate | Tool/command | Failure = block |
|---|---|---|
| Format/lint | ruff/black (G1) | yes |
| Unit tests | `pytest tests/g0 -q` | yes |
| Schema tests | `production-seed/tests/` (empty-DB migration) | yes |
| Domain invariants | G0 domain suites (books 0–6) | yes |
| Policy/security tests | Book 6 seam probes + book9 runtime tests | yes |
| Migration tests | empty-DB build (sqlite) + staging Postgres run | yes |
| Provenance tests | seed manifest lineage + license register | yes |
| Eval smoke | Book 7 deterministic eval smoke (no live model in CI) | yes |
| Secret scanning | scan repo for secret patterns; fail on hit | yes |
| Dependency/license checks | dependency manifest completeness | yes |
| Build/container checks | image builds + entrypoints | yes |

## CD (protected deployment)

- **Branch protection** on production branch; changes reviewed.
- **Environment approval** for STAGING→PRODUCTION promotion.
- **Immutable build artifact** — build once, promote the same artifact.
- **Migration preview** — migrations run against a preview DB before
  production apply.
- **Release version/tag** — semver or commit-derived; recorded.
- **Rollback reference** — every release identifies its rollback target
  (previous build artifact + migration policy).

## Relationship to Book 7 promotion

Book 7 candidate promotion (model/prompt/skill/Humanizer) is a *separate
governed process* from code deployment, but must integrate: a promoted
CandidateChange references a ReleaseCandidate that went through the same
immutable-artifact path. Code deploy never bypasses eval governance; eval
promotion never bypasses code deploy controls.

## What CI never does

- Never runs with production credentials.
- Never runs live model calls (deterministic baseline/mocks only).
- Never has a submission capability in its test surface.
