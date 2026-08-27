# G1 Wave 5 — Client Chat Application

**Line:** `grant-sector-g1-production`
**Status:** IMPLEMENTED — live API verified end-to-end; Next.js app builds
**Commit series:** `G1-W5-C1` … `G1-W5-BOOK`

## Product Principle (Appendix B §12)

> The Grant product is primarily **CHAT + WORK PROGRESS + DELIVERABLES**.
> User says what they need → system works → high-level progress → final
> deliverable appears in chat.

## Client API (`apps/api/` — FastAPI)

| Route | Purpose |
|---|---|
| `POST /chat` | message → Personal Hermes intent → CEO plan → durable tasks |
| `GET /chat/{id}/messages` | persisted history (never raw-chat canonical state) |
| `GET /projects/{id}/progress` | task states from the durable Store — never timer-faked |
| `POST /projects/{id}/produce` | full Grant factory → SUBMISSION_READY_MOCK / BLOCKED |
| `GET /projects/{id}/deliverables` | artifact metadata (DOCX/PDF) |
| `GET /artifacts/{id}/download` | real DOCX/PDF payload bytes |
| `GET /models` · `POST /models/select` | governed Model Registry (Appendix A) |
| `GET /consoles` | Advanced Personal/CEO Hermes console refs |

Auth: principal header gate; tenant scope enforced structurally. Submission
is structurally absent — no route reaches an external submission capability
(asserted by test).

## Web App (`apps/web/` — Next.js)

Next.js 15 · React 19 · TypeScript · Tailwind (Appendix B §20 stack).

- **Left sidebar:** New Chat · History · Deliverables
- **Center:** chat conversation (streamed-style messages, deliverable card
  with QA counts + DOCX/PDF downloads)
- **Right panel:** Work preview from durable task states (Finding
  opportunities / Checking eligibility / Drafting sections / Building
  budget / Running QA / Packaging) — never private chain-of-thought
- **Model picker:** defaults to **Auto — Recommended**; lists only governed
  approved models; client never needs model infrastructure (Appendix A §10)
- `next.config` rewrites `/api/*` → FastAPI backend (`API_URL` env)
- Submission stays disabled — UI says "review only"

Verified: `npm run build` (production build clean), `npm run typecheck`.

## Verification

- `apps/api/tests/test_client_api.py` — 10 tests (chat, fail-closed
  submission normalization, durable progress, produce, real DOCX/PDF
  downloads, governed model selection + unknown denial, auth, forged
  project, no-submission-route).
- `tools/g1/verify_web_flow.py` — 18 live API checks across the full
  browser-flow contract (Appendix B §61): intake → history → progress →
  produce → deliverables → model picker → security denials. **PASS.**
- Seed suite: 63 passed (was 64 after deny-unknown model test; final
  count re-verified at checkpoint).

## Honest Status

- Auth is a dev principal header; production session/JWT + Postgres
  adapter are G1.10 hardening items (recorded in the G1 backlog).
- The Next.js app is functional and builds; visual polish per Beautiful
  UI / Transitions.dev remains selective post-pilot work.
