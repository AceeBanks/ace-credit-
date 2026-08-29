# Grant Agent — Review Package

This folder is a **review package** for the Grant Agent work completed on
2026-08-29. The full codebase does **not** live in this repository.

| Item | Location |
|---|---|
| Full Grant Agent code | `C:\Users\User\workspace\larger-lab` (clone of `https://github.com/dabigestpoppa/larger-lab.git`) |
| Branch | `grant-sector-g1-production` @ `3a639d89865188506b8267a433c5bf8464f4ee7b` |
| Python env | `workspace\larger-lab\.venv` (Python 3.12.14) |
| Report | `GRANT_AGENT_LOCAL_SETUP_REPORT.md` (start here) |
| Launchers | `start_grant_agent.cmd` / `start_grant_agent.ps1` — run them **from the larger-lab repo root** (they resolve paths relative to where they live) |
| Config template | `.env.example` — copy to `.env` in larger-lab; the real `OPENROUTER_API_KEY` is kept only in the local, gitignored `.env` |

## Status summary

- Tests: **130 passed / 10 skipped / 0 failed** (all grant suites, with live key)
- Live-model path verified end-to-end (AUTO produce → `LIVE_MODEL` via governed gateway)
- Submission structurally disabled; deterministic lane honestly reports `BLOCKED`/`NEEDS_CLIENT_INPUT`
- Remaining items: Postgres adapter, S3 object store, session/JWT auth (G1.10) — documented in the report

No secrets are committed anywhere in this repository.
