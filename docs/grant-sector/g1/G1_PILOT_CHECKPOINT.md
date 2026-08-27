# G1 Pilot Checkpoint — First Client-Pilot Readiness

**Line:** `grant-sector-g1-production`
**Date:** 2026-08-27
**Status:** `PILOT_SIMULATION_COMPLETE` — `NOT_READY_FOR_PUBLIC_LAUNCH`
**Evidence:** `docs/grant-sector/g1/pilot/G1_PILOT_EVIDENCE.json`

## Pilot Flow Executed (MOCK client)

USER → chat intake → Personal Hermes IntentContract → CEO Hermes durable
TaskPlan → 10 bounded worker tasks → governed research evidence →
full Grant factory (blueprint → 7 sections → synthesis → budget → 9-gate
QA) → DOCX/PDF artifacts → chat delivery → **cold reconstruction**.

## Measured Evidence (this run)

| Metric | Value |
|---|---|
| Total runtime | 0.21 s (in-process pilot) |
| Task count / completed | 10 / 10 |
| Worker fanout | 10 handlers |
| Source count (snapshots) | 4 governed adapters |
| Claim ledger entries | 11 |
| Unsupported material claims | 4 (all `UNKNOWN` — honest gaps, not fabrications) |
| Proposal sections / words | 7 / 238 |
| Proposal pages (DOCX) | 7 |
| Artifacts | 3 (DOCX, PDF, evidence JSON) |
| Failures / retries | 0 / 0 |
| Model calls | 0 (pilot used deterministic lane) |
| QA | 9/9 pass, 0 fail → `SUBMISSION_READY_MOCK` |
| Budget | $50,000.00 within $50,000.00 ceiling |
| Cold reconstruction | `raw_chat_required=false`, all completeness flags true |

## Live-Model Lane Evidence (separate, real)

`G1-W4-LIVE` ran the full factory through the **governed Model Gateway**
(minimax/minimax-m3:free, OpenRouter adapter): 7/7 sections LIVE_MODEL,
QA 9/9, `SUBMISSION_READY_MOCK`, protected facts verbatim, unknowns
preserved as `UNKNOWN:`. This is architecture + grounding evidence — NOT
proof of universal proposal quality (single fixture, small sample).

## Honest Gaps (production-hardening input — Wave 6)

1. **Auth:** dev principal header; production session/JWT is G1.10.
2. **Persistence:** SQLite in dev/pilot; Postgres production adapter G1.10
   (same repository interface, portable schema, migration-tested).
3. **Human review:** `NOT_PERFORMED` — no reviewer available; no score
   invented. Review packet structure exists.
4. **Writing quality:** small sample; more Book 7 evaluation runs needed
   before model/prompt/Humanizer promotion decisions.
5. **Source adapters:** DEV/fixture-backed; LIVE network fetch blocked on
   authorized egress (recorded, not faked).
6. **Web UI polish:** functional chat-first app; Beautiful UI /
   Transitions.dev selective polish is post-pilot work.

## STOP Boundary (mission §65)

- ✅ **STOP here** — do not begin production hardening (Wave 6) without
  external review of: production persistence, full proposal quality,
  frontend UX, security, cost, failure recovery, pilot evidence.
- ✅ No public launch.
- ✅ No G2 architecture work.
- ✅ Submission remains **structurally disabled** — verified by test
  (`no submission route exists` → 404) and by UI (review-only).

## READY_FOR_PRODUCTION_HARDENING

`true` (foundations are in place and verified) — but the *start* of Wave 6
is gated on external review, per the mission. This checkpoint does not
self-claim that review.
