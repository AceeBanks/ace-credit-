# G0 Book 9 — Dependency & License Freeze

**Chapter:** B9.C12
**Date:** 2026-08-27
**Status:** COMPLETE

No mystery prototype dependency. Every selected dependency is pinned,
licensed, justified, and has a replacement path. "Because it was in a
prototype" is not a reason.

## Runtime dependencies (production)

| Dependency | Version/commit | License | Purpose | Required? | Security maintenance | Replacement path | Feature subset used |
|---|---|---|---|---|---|---|---|
| Python | 3.11 | PSF | runtime language | required | active | — | stdlib only for kernel |
| `requests` | >=2.31,<3 | Apache-2.0 | OpenRouter adapter HTTP | required | active | `httpx` or stdlib `urllib` | POST /chat/completions |
| Postgres | 15+ (managed or self-hosted) | PostgreSQL License | canonical state | required | active | any SQL DB via portable DDL | relational tables per C13 |
| Object storage (S3-compatible) | any S3 API | vendor | immutable payloads | required | vendor | filesystem adapter (local-first) | put/get refs |

## Provider adapters (replaceable, not dependencies)

| Adapter | Status | License | Notes |
|---|---|---|---|
| OpenRouter (`pp_openrouter_dev`) | in use (dev) | provider API | `openrouter/free` is dev-only; NOT production pricing basis |
| Model providers | replaceable | — | adapter registry; no vendor lock |

## Runtime candidate components (NOT adopted)

| Component | Status | Why not adopted |
|---|---|---|
| CompozyOS | DEFER (Batch 04) | hard gate 7 — framework-owned state risks dual sovereignty; not installed |
| QM | DEFER (reference only) | hard gate 7 — framework-owned session state; not installed |
| Kubernetes / service mesh | NOT selected | no measured evidence of need at G0; revisit only on measured trigger |

## Dev/test dependencies

| Dependency | Purpose | License |
|---|---|---|
| `pytest` | test runner | MIT |
| `sqlite3` (stdlib) | empty-DB migration tests | PSF |

## License risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Proprietary framework license (if Compozy/QM ever re-enter) | high | hard gate 7 already disqualifies; re-review required before any adoption |
| OpenRouter free-tier availability | medium | adapter pattern; providers replaceable; cost scenarios in `G0_B9_COST_ENVELOPE.md` |
| Postgres vendor lock (managed service) | low | portable DDL; self-hosted path documented |

## Rule

Any new dependency in G1 requires a ledger entry here with the same
fields — purpose, license, optional/required, replacement path, feature
subset — before it may be added.
