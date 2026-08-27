# G1 Wave 4 — Full Grant Application Factory

**Line:** `grant-sector-g1-production`
**Status:** IMPLEMENTED — first complete full-proposal LIVE experiment executed
**Commit series:** `G1-W4-C1` … `G1-W4-BOOK`

## Governing Question (G1.7/G1.8)

*Can the engine produce the COMPLETE application required by the exact
solicitation — not a four-section demo?*

## What Was Implemented (`production-seed/grant_platform/factory/`)

| Module | Responsibility |
|---|---|
| `blueprint.py` | Derives all required sections, word limits, required attachments, required terminology deterministically from the OpportunityRevision (Book 8 C34 — never model prose). Length follows solicitation; no forced 20–40 pages. |
| `drafting.py` | Section drafting: each section receives its requirement, organization context, governed evidence, protected facts. Two honest lanes: **LIVE_MODEL** (governed invoke callable) and **DETERMINISTIC_BASELINE** (labeled as such, never passed off as model output). Per-section protected-fact gate + contradiction detection (Oct 16, $500,000, Alabama, 2010, 19.5 → FAIL). Unknowns stay visible as `UNKNOWN:` — never invented. |
| `synthesis.py` | Cross-section consistency: terminology, deadline/ceiling/statistic/revision values, future-vs-historical claim markers, budget alignment. Reports only — never introduces claims. |
| `budget.py` | Line items, categories, totals, ceiling reconciliation. Governed fixture lines + optional CLIENT lines (honored verbatim, checked). Over-ceiling → `ok=False`. |
| `qa.py` | Full proposal QA: 9 hard gates (sections complete, word limits, budget ≤ ceiling, deadline correct, revision correct, required terminology, no fabricated material claims, no fabricated partnerships, submission disabled). `submission_ready_mock` = zero failures. |
| `render.py` | **Real** DOCX (dependency-free OOXML zip writer: headings, page breaks, footer page-number fields, document metadata) and **real** PDF (reportlab: styles, page numbers, artifact version footer). Content-faithful — formatting never hides missing content. |
| `orchestrator.py` | Composition boundary: blueprint → draft → synthesize → budget → QA → render → `SUBMISSION_READY_MOCK` or `BLOCKED` (never fake-ready). |

## G1-W4-LIVE — First Complete Full-Proposal Experiment

`tools/g1/run_w4_live.py` wires the factory's `model_invoke` through the
**governed G0 Model Gateway** (same credential/egress/authorization rules
as D2-LIVE; credentials resolved server-side, never exposed).

Artifacts (`docs/grant-sector/g1/w4-live/`):

- `W4_LIVE_PROPOSAL.md` / `.docx` / `.pdf` — real payloads
- `W4_LIVE_MODEL_RUN.json` — model/lane provenance
- `W4_LIVE_REPORT.json` — full summary

**Result:** `SUBMISSION_READY_MOCK`, generation mode **LIVE_MODEL**
(minimax/minimax-m3:free via governed gateway), 7/7 sections, word count
1607, budget `$50,000.00` within ceiling, QA **9/9 pass, 0 fail**,
submission disabled. The model draft preserves every protected fact
verbatim, keeps unknown client facts as `UNKNOWN:`, and cites the governed
statistic (Dade County 18.2%, 2023 ACS).

**Honest limitation recorded:** this is one fixture's first full-package
experiment — it proves the factory architecture and grounding, not
universal proposal quality (same statistical discipline as D2).

## Tests

`tests/test_grant_factory.py` — 11 tests: blueprint catalog, deterministic
lane grounded/honest, live lane bounded + protected-fact preserved, live
lane altered-fact → BLOCKED, budget reconciliation, over-ceiling
fail-closed, synthesis terminology, full factory SUBMISSION_READY_MOCK,
DOCX OOXML-valid (zip magic, parts, content), PDF valid (`%PDF-`), live
lane full factory pass.

**Seed suite at Wave 4:** 63 passed, 0 failed. Fresh-clone verification PASS.
