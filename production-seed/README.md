# Grant-Sector Production Seed (G0-B9)

Clean production repository seed for the Grant machine, derived from the
ratified G0 contracts (Books 0–9). This is the *seed*, not the full G1
implementation: contracts, generic infrastructure, schemas, migrations,
CI, environment tooling, tests, and G1 scaffolding only.

**Runtime substrate (ADR `G0_B9_RUNTIME_SUBSTRATE_ADR.md`):** OCE_NATIVE —
project-owned Python runtime; Postgres canonical; object storage for
immutable payloads; governed Model Gateway for model execution.

**Canonical ownership:** see `G0_B9_CANONICAL_STATE_OWNERSHIP.md`.

> **Note on repository creation:** creating a new GitHub repository is a
> pending operator action (`CLEAN_REPO_CREATION_PENDING_OPERATOR_ACTION`).
> This seed lives in an isolated `production-seed/` path inside the G0
> repository; an operator can lift it into a fresh repo when authorized.

## Layout

```text
production-seed/
  migrations/        # SQLite TEST_ONLY / DEV_FAST_PATH (append-only)
  migrations/postgres/  # canonical production schema (TIMESTAMPTZ/now()/jsonb)
  config/            # environment config (secrets referenced, never stored)
  tests/             # seed verification tests
  bootstrap.py       # local bootstrap: SQLite DEV_FAST_PATH only
```

## Bootstrap (local-first, no paid cloud)

```bash
python -m venv .venv
.venv/bin/pip install -r config/requirements.txt   # minimal deps
python bootstrap.py --db sqlite:///./dev.db        # migrate empty DB
python -m pytest tests/ -q                          # seed verification
```

Postgres (staging/production) uses the canonical `migrations/postgres/`
path applied by the G1 migration runner; `bootstrap.py` is SQLite-only
(TEST_ONLY / DEV_FAST_PATH) and is NOT used against Postgres.

SQLite (CI/dev) runs `migrations/*.sql` (DEV_FAST_PATH); Postgres runs
`migrations/postgres/` (canonical). The two are NOT interchangeable — see
the P1-01 migration-truth repair. No reliance on developer machine state,
old paths, hidden env files, or archived Hermes memory.

## Verification contract (B9.C25)

Fresh clone must: bootstrap → validate configs → migrate empty DB → load
fixtures → run core tests → run policy tests → run a minimal mock Grant
workflow. See `G0_B9_SEED_VERIFICATION_REPORT.md`.
