# G0 Book 9 — Clean Seed Verification Report

**Chapter:** B9.C25
**Date:** 2026-08-27
**Status:** PASS

## Method

`tools/g0/verify_production_seed.py` simulates a fresh clone:

1. Copies ONLY the committed `production-seed/` tree into a temp dir.
2. Bootstraps an empty sqlite DB via `bootstrap.py` from the copy.
3. Runs the seed test suite from the copy (4 tests).
4. Runs a representative mock workflow: tenant + opportunity seed rows,
   read-back.
5. Asserts the copy contains no hidden `.env`.

## Result

```
- seed tests: 4 passed (PASS)
fresh-clone seed verification: PASS
```

## What is proven

- Migrations build an EMPTY database (no local historical DB state).
- No dependence on developer laptop state, old larger-lab paths, hidden
  `.env`, or archived Hermes memory.
- A representative mock Grant workflow (tenant + opportunity) round-trips
  from the migrated schema.
- `production-seed/` is self-contained; an operator can lift it into a
  fresh repository when repo creation is authorized
  (`CLEAN_REPO_CREATION_PENDING_OPERATOR_ACTION`).

## Remaining (honest)

- Live Postgres migration run: exercised in CI/staging, not locally
  (bootstrap.py raises with a clear message for postgres URLs).
- Full G0 suite inside the seed: the seed is contracts/scaffolding; the
  full suite lives in the G0 repo and is migrated during G1
  (`PROMOTE_FROM_G0` items).
