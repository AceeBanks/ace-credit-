# G0 Book 9 — Environment Strategy

**Chapter:** B9.C14
**Date:** 2026-08-27
**Status:** FROZEN

## Environments

| Environment | Purpose | Data | Secrets | Notes |
|---|---|---|---|---|
| **LOCAL** | developer laptop; core dev without paid cloud | dev fixtures (non-production) | dev-only dummy (`env.example`, `.env.local`) | sqlite or local Postgres; local object store |
| **TEST/CI** | ephemeral, reproducible | synthetic test data | none real | empty-DB migration + full G0 suite + policy tests |
| **STAGING** | production-like | synthetic/test tenant data | staging secrets (secret store) | same migrations/contracts as prod; no real client data |
| **PRODUCTION** | real tenants | real data | production secrets (secret store) | destructive ops gated; approval-gated release |

## Rules

1. Same schemas/contracts across environments; only credentials/config
   differ.
2. Configs separated from secrets — `config/` holds structure, secret
   store holds values (C21).
3. Migrations tested on empty DB (CI) and staging before production.
4. Production credentials unavailable locally by default.
5. Destructive operations (deletes, resets, rollbacks) are gated behind
   operator approval.
6. `GRANT_ENV` selects the environment; unknown value fails closed.
