# G1 Proposal Output Analysis — Why the Proposal Is Only 2 Pages

**Date:** 2026-08-28
**Branch:** `grant-sector-g1-production`
**Commit:** `46629bd2`

---

## Current Output Metrics

| Metric | Value | Expected (for a real proposal) |
|--------|-------|-------------------------------|
| Total words | **238** | 3,000–8,000+ |
| PDF pages | **1** (report says 7 but PDF is 1 page) | 10–25+ |
| DOCX pages | **7** (ReportLab artifact count, see note) | 10–25+ |
| Sections | 7 | 7 |
| Words per section | 18–45 | 500–2,000 |
| Generation mode | DETERMINISTIC_BASELINE | Needs LIVE_MODEL |
| UNKNOWN material claims | 4 | 0 for READY |
| QA status | QA_BLOCKED | READY_FOR_REVIEW |

### Per-Section Word Counts

| Section | Words | Blueprint Limit | % Filled |
|---------|-------|-----------------|----------|
| executive_summary | 40 | 500 | 8% |
| organization_background | 35 | 800 | 4% |
| statement_of_need | 37 | 1,000 | 4% |
| program_narrative | 45 | 2,000 | 2% |
| outcomes_evaluation | 29 | 800 | 4% |
| sustainability | 18 | 600 | 3% |
| budget_narrative | 34 | 800 | 4% |
| **TOTAL** | **238** | **6,500** | **3.7%** |

---

## Root Cause Analysis

### Cause 1: Deterministic Drafting Produces Hardcoded Placeholder Text

The factory's drafting lane (`production-seed/grant_platform/factory/drafting.py`) has two paths:

1. **LIVE_MODEL** — calls an injected `model_invoke(bundle)` function that sends a prompt to a real LLM
2. **DETERMINISTIC_BASELINE** — returns hardcoded 1–3 sentence templates from the `_deterministic_section()` function

**The default path always uses DETERMINISTIC_BASELINE.** The `_deterministic_section()` function contains static strings like:

```python
"executive_summary": (
    "Community Youth Works, Inc. requests $50,000 from the Georgia "
    "Rural Community Impact Grant FY2026 (opportunity revision "
    "opp_rev_ga_501_1) to sustain after-school STEM programming in "
    "rural Georgia. The organization has been determined ELIGIBLE "
    "for this opportunity. The deadline is October 15, 2026."),
```

Each section is 1–3 sentences. There is **no logic to expand content toward the word limit** — the deterministic lane is a fixed honest baseline, not a content generator.

### Cause 2: Chat Endpoint Passes `model_invoke=None` by Default

In `apps/api/main.py`, the chat endpoint calls:

```python
factory = run_factory(project_id="proj-1", model_invoke=model_invoke, model_id=resolved)
```

The `model_invoke` comes from `_resolve_model_invoke()`, which returns `None` unless:
- `live_model=True` is explicitly set, OR
- `model_selection.mode == "MANUAL"` with a valid model_id

The frontend defaults to `mode: "AUTO"` with `live_model: false` (via the ProduceIn defaults), so `model_invoke` is always `None` in the standard flow. The factory never reaches the LIVE_MODEL path.

### Cause 3: The Deterministic Lane Was Never Designed to Produce Long-Form Content

The `_deterministic_section()` function is explicitly documented as:

> "Grounded deterministic baseline per section. Explicitly the honest
> fallback lane — it is not model generation and is labeled as such."

It is a **structural placeholder** that proves the pipeline works end-to-end (blueprint → draft → synthesis → QA → render) without requiring API credentials. It was never meant to produce real proposal content.

### Cause 4: UNKNOWN Claims Block READY Status

Even though the sections are short, 4 UNKNOWN material claims remain:

1. youth served annually
2. current program locations
3. specific activity schedule
4. baseline outcome targets

These cause `readiness_state: QA_BLOCKED` and `status: BLOCKED`. The proposal correctly refuses to claim "ready" — but the content it does have is minimal.

### Cause 5: No Solicitation-Driven Length Requirements Are Enforced

The blueprint defines generous word limits (500–2,000 per section, 6,500 total), but nothing in the pipeline enforces minimum content generation. The QA checks word limits (max), not word minimums. The factory does not fail or warn when output is 3.7% of the blueprint capacity.

---

## What Would Fix This

1. **Wire the LIVE_MODEL path end-to-end** — the frontend model selector must actually route `model_invoke` to a real provider. Currently the model selection UI is cosmetic for the standard AUTO path.

2. **Use AUTO mode to invoke a live model** — when the user selects AUTO, the governed model selection engine should resolve to an approved model and invoke it. This requires the runtime tooling (`tools/g1/run_w4_live.py`) to actually work and have valid API credentials.

3. **Enforce minimum content thresholds** — QA should warn (or fail) when sections are below 50% of their blueprint word limit.

4. **Gather missing client information** — the 4 UNKNOWN claims need real data from the user (participant counts, program schedule, locations, outcome targets) before the proposal can be substantive.

5. **Use a real solicitation** — the current `opp_rev_ga_501_1` is a dev fixture. A real solicitation with genuine narrative requirements would drive longer, more specific content.

---

## Summary

The 2-page proposal is the **expected output** of the current architecture:

- The deterministic lane is a ~240-word structural skeleton, not content
- The live model path exists but isn't wired through AUTO mode in the standard flow
- The system is honest about its gaps (UNKNOWN markers, BLOCKED status)
- The pipeline works end-to-end but produces honest stubs, not real proposals

**This is not a bug — it is the known limitation of the deterministic baseline.** The fix requires completing the live model integration (G1.7/G1.8 scope) and gathering real client information.
