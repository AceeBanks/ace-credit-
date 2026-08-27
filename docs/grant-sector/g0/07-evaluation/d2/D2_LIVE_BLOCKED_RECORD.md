# G0-B7-D2-LIVE-BLOCKED — Missing Authorized Model Runtime

**Commit type:** `G0-B7-D2-LIVE-BLOCKED: record missing authorized model
runtime without fabricated results`

This record documents the **first live D2 attempt** (§7–§8 of the Book 7
external-review repair mission). The truthful result is that no authorized
model runtime exists for the governed G0 pipeline, so no live AI-generated
grant draft was produced. **No results were fabricated.**

## Runtime discovery (mission §8)

Searched the repository and environment for an already configured,
authorized model runtime:

| Candidate path | Found? |
|---|---|
| Hermes configured providers | No — no provider config in the G0 pipeline |
| Local model endpoint | No |
| Project model adapter | No — `prototype/g0/` contains no model adapter |
| Approved API provider configuration | No — `config/g0/` has no provider config |
| OCE-compatible model gateway | No |

**Environment note:** `OPENROUTER_API_KEY` is present in the shell
environment, but it is consumed only by workspace tooling
(`tools/memory_sync_daemon.py`, `tools/summarize_progress.py`,
`projects/ai-tools/parallel_thought/`) — **not** by the governed G0
pipeline. A bare environment variable is not an authorized provider path:
there is no G0 adapter/gateway that consumes it, and Book 6 credential
rules (server-side secrets, no hard-coded credentials, no exposure to
Hermes context) forbid silently wiring an unauthorized external provider
into the grant pipeline. Per the mission: "Do not improvise around
blockers" (§26).

## Status

| Field | Value |
|---|---|
| `D2_LIVE_STATUS` | `BLOCKED_MODEL_RUNTIME` |
| `HUMANIZER_LIVE_STATUS` | `BLOCKED_COMPONENT_RUNTIME` |
| Model | none (provider/model/version = none) |
| Baseline live AI draft | **not generated** (no model) |
| Humanized live draft | **not generated** (no transform runtime) |
| Fabricated results | none |
| Existing D2 harness draft | deterministic-only, clearly labeled, not presented as AI-generated |

## What exists (harness truth)

- D2 harness complete: deterministic baseline draft, Claim Ledger,
  protected-claim diff (HZR-007), deterministic QA — all green.
- Book 7 evaluation infrastructure complete and green (1703 passed, 3
  skipped full suite).
- `d2_harness_complete = true`, `d2_live_model_run_complete = false`,
  `d2_live_humanizer_run_complete = false`, `humanizer_live_bakeoff_complete
  = false`, `ready_for_book8_execution = false`.

## What is required before a live D2 run

1. A repository-authorized model runtime: an adapter/gateway/config the G0
   pipeline recognizes, consistent with Book 6 credential rules.
2. The governed drafting pipeline executed against the Georgia-first
   fixture (Community Youth Works, Inc. / opp_rev_ga_501_1) through an
   actual model.
3. Optional Humanizer lane only with an executable, licensed transform
   runtime under Amendment 003.

## Consequence

`ready_for_book8_execution = false` — **Book 8 must not begin**. This is an
honest blocked state, not a failure of the Book 7 architecture (which
remains `status = PASS`).

Machine-readable: `D2_LIVE_STATUS.json` (same directory).
