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
  migrations/        # canonical Postgres/portable schema (append-only)
  config/            # environment config (secrets referenced, never stored)
  tests/             # seed verification tests
  bootstrap.py       # local bootstrap: init env, run migrations on a DB
```

## Bootstrap (local-first, no paid cloud)

```bash
python -m venv .venv
.venv/bin/pip install -r config/requirements.txt   # minimal deps
python bootstrap.py --db sqlite:///./dev.db        # migrate empty DB
python -m pytest tests/ -q                          # seed verification
```

With Postgres (staging/production):

```bash
python bootstrap.py --db postgres://user:pass@host/grantdb
```

The same portable migration file runs on both sqlite (CI/dev) and
Postgres (staging/production). No reliance on developer machine state, old
paths, hidden env files, or archived Hermes memory.

## Verification contract (B9.C25)

Fresh clone must: bootstrap → validate configs → migrate empty DB → load
fixtures → run core tests → run policy tests → run a minimal mock Grant
workflow. See `G0_B9_SEED_VERIFICATION_REPORT.md`.
