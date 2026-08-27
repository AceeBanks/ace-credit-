# G0 Book 9 — Local Development Strategy

**Chapter:** B9.C15
**Date:** 2026-08-27
**Status:** FROZEN

## Target: local-first

```text
clone
→ python -m venv .venv && pip install -r config/requirements.txt
→ cp config/env.example .env.local        (dev-only dummies)
→ python bootstrap.py --db sqlite:///./dev.db   (migrate empty DB)
→ python -m pytest tests/ -q               (seed verification)
→ run representative mock Grant flow
```

No paid cloud required for core development:
- sqlite stands in for Postgres (same portable DDL);
- local filesystem stands in for object storage;
- model lane: deterministic baseline mode (no credential needed) or the
  governed OpenRouter adapter with a dev key (DEV_RUNTIME_ONLY);
- Redis/queue, graph, vector are optional; their absence degrades locally
  (Book 8 degraded-mode law).

## What local must provide

- env bootstrap (one command);
- Postgres (or sqlite) with migrations;
- local object store abstraction;
- mock/test model configuration (deterministic baseline);
- deterministic fixture mode (Georgia fixture pack);
- seed data;
- health checks (`bootstrap.py --check` style, G1).

## Guardrails

- Never require a developer laptop's historical state; `dev.db` is
  disposable and rebuilt from migrations + fixtures.
- Never require archived Hermes memory for a representative flow.
- `.env.local` is gitignored; only `env.example` is committed.
