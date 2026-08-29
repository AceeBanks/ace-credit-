# G1-QUALITY-PROD — STOP-Condition Report

Status of the "make the full quality engine the canonical /produce path" mission
on branch `grant-sector-g1-production`.

## Execution summary

| Item | Value |
|---|---|
| START SHA (task-stated) | `3a639d89865188506b8267a433c5bf8464f4ee7b` (handoff) |
| Branch HEAD when work began | `3e8d65c37995d3e1526353f12e6d44bd5b0ce860` |
| **FINAL SHA** | **`6a9c74f`** (`51dbedb` PROD-01..04, `6a9c74f` PROD-LIVE-01) |
| Test status | **140 passed / 10 skipped / 0 failed** |

## 1. Root cause of the short proposal

The old `POST /projects/{id}/produce` routed `AUTO`/`MANUAL` through
`run_factory` with the **W4-skeleton model invoke
(`tools/g1/run_w4_live.py::build_governed_model_invoke`)**. That invoke capped
`max_output_tokens=512` (~380 words / section). With 7 sections that yields the
7-section / 1,319-word / `QA_BLOCKED` / 15-unsupported-claims package. The
shallow skeleton was being treated as the client deliverable.

There was **no regression in the quality engine itself** — the engine was
complete but only reachable from `tools/` benchmark scripts; the API never
called it.

## 2. Old vs new production path

| | Old `/produce` | New `/produce` |
|---|---|---|
| Route | `apps/api/main.py::produce` → `run_factory(model_invoke=<W4 512-token>)` | `apps/api/main.py::produce` → `build_context_for_revision` → `produce_application_quality` |
| Orchestrator | generic factory only | `production-seed/grant_platform/factory/quality_pipeline.py::produce_application_quality` |
| Model invoke | 512 output tokens | `build_quality_model_invoke` — 4096 output tokens, same governed G0 gateway |
| Pipeline | baseline skeleton sections | solicitation → ApplicationBlueprint → OrgFactPack → MissingFactMatrix → client-question gate → SectionPlans → draft → critic → fact-critic → bounded revision → synthesis → Claim Ledger → integrity QA → budget reconciliation → render → readiness |
| No solicitation | produced generic fixture package | `NEEDS_OPPORTUNITY` (fail closed) |
| Deterministic | implicit fallback | only explicit `mode=DETERMINISTIC`, labeled `DEVELOPER_DIAGNOSTIC` |
| Provenance | none | pipeline_version / QUALITY_PRODUCTION label / solicitation_id / run_id / model runs / claim-ledger hash / fact-freeze hash |

## 3. Frontend (single path)

`apps/web/lib/api.ts::produce` calls `/api/projects/{id}/produce`, proxied to
the single FastAPI route. No alternate client-side generation implementation.
§7 satisfied.

## 4. Live benchmark — current evidence

Actual live run through the running API (`POST /projects/proj-bench/produce`,
`proj-bench` → revision `ga_dca_nofp_2026`, governed `z-ai/glm-5.2:free`):

```
readiness_state : QA_BLOCKED     pipeline_label  : QUALITY_PRODUCTION
generation_mode : LIVE_MODEL     solicitation_id : ga_dca_nofp_2026
sections        : 5              word_count      : 22
pdf_pages       : 1              requirement coverage : 16.7%
```

**Why 22 words / QA_BLOCKED:** every material section's generation was
`RATE_LIMITED` — OpenRouter's free-model daily quota was exhausted
(`429 free-models-per-day`, `X-RateLimit-Remaining: 0`). The governed invoke
walked the approved pool (`glm-5.2:free → inkling-small:free → minimax-m3:free
→ END`) and **failed closed instead of fabricating** — the designed,
integrity-preserving behavior. Provenance now records per-section
`reason=RATE_LIMITED` and the full fallback chain, so this is auditable as a
provider rate-limit, not a drafting defect.

The provider quota resets at **2026-08-30T00:00:00 UTC**. A background watcher
(`var/g1-bench-rerun.log`) re-runs the benchmark the moment the window opens and
regenerates `G1_QUALITY_API_LIVE_REPORT.json`. Manual re-run:

```
# API running with OPENROUTER_API_KEY loaded:
G1_API_BASE=http://127.0.0.1:8001 G1_DB=var/g1.bench.db \
  .venv/Scripts/python.exe tools/g1/run_quality_api_benchmark.py
```

## 5. STOP state vs success condition

- **Implementation complete** and the canonical pipeline is the ONLY client
  production path — verified end-to-end **offline through the real API** by
  `apps/api/tests/test_quality_pipeline_api.py` (drives `POST /produce` with a
  controlled governed invoke; asserts SectionPlans / critic+failure metadata /
  Claim Ledger / integrity report / real DOCX+PDF / QUALITY_PRODUCTION
  provenance + hashes).
- **Quality-proven against the live model** is pending **only** the OpenRouter
  daily free quota (external; resets ~00:00 UTC). The auto-rerun will draft the
  full AmeriCorps benchmark package on the real production path.

## 6. Open items

| # | Item | Type |
|---|---|---|
| P0 | Drawn live proposal once provider quota resets (auto-rerun armed) | external rate-limit |
| P1 | Postgres canonical storage (8 env-blocked tests) | pre-existing, out of scope |
| P1 | Session/JWT auth in place of dev `X-Principal` (G1.10) | pre-existing, out of scope |