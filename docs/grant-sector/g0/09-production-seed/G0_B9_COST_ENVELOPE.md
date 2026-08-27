# G0 Book 9 — Cost Envelope

**Chapter:** B9.C23
**Date:** 2026-08-27
**Status:** ESTIMATE (assumptions explicit; not precision)

## Cost drivers (dominant first)

1. **Model usage** — dominant. ~4 model calls per grant package, ~1.2k
   tokens/call measured. Paid production model pricing replaces the
   free-tier dev lane; scenarios below are configurable.
2. **Source/API** — funder/source adapters (G1.3) may have usage quotas.
3. **Parser/OCR** — document parsing for uploaded artifacts; volume-driven.
4. **Database** — Postgres: small at G0 scale (16 tables, ~20 rows/grant
   package).
5. **Object storage** — snapshots/artifacts; small at G0 scale.
6. **Runtime workers** — single worker instance at G0/G1 start.
7. **Observability** — collector + metrics; small.
8. **Optional paid sources** — later, on demand.

## Scenarios (model cost shown separately and as total)

Assumptions (state explicitly):
- 1 grant package ≈ 4 model calls ≈ 5,000 input + 2,000 output tokens.
- Paid production model placeholder: $0.50 / 1M input, $1.50 / 1M output
  (configurable — swap in any contract price).
- Free-tier OpenRouter is NOT a production pricing basis.

| Scenario | Concurrent clients | Grant packages/day | Model cost/day (paid placeholder) | DB+storage+workers/day (est.) | Daily total (est.) |
|---|---|---|---|---|---|
| DEV / single client | 1 | 1–2 | 2 × (5k×$0.5 + 2k×$1.5)/1M ≈ $0.011 | $0.05 | ≈ $0.06 |
| 10 clients | 10 | 20 | 20 × $0.0055 ≈ $0.11 | $0.30 | ≈ $0.41 |
| 100 clients | 100 | 200 | 200 × $0.0055 ≈ $1.10 | $2.50 | ≈ $3.60 |

Monthly at 100 clients: ≈ $110 (models) + $75 (infra est.) ≈ $185/month.

## Honest caveats

- These are estimates with explicit assumptions, not quotes.
- Real source-adapter fees, OCR volume, and production model pricing must
  be substituted before pilot.
- Cost is an optimization AFTER correctness/security floors — never a
  reason to weaken a hard gate.
- Model cost scenarios are configurable (`GRANT_MODEL_*` config), so any
  contract price can be plugged in.
