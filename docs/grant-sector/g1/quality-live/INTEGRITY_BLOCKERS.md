# G1 Integrity — Open Blockers (run1/run2/run3 evidence)

_Catalogued:_ 2026-08-28 — after LIVE-01 + LIVE-02 + LIVE-03 integrity benchmarks against the real FY2026 AmeriCorps Georgia NOFO.

Artifacts:
- LIVE-01 (no client answers): [`run1_blocked/`](./run1_blocked/) — `NEEDS_CLIENT_INPUT`
- LIVE-02 (3 controlled `MOCK_CLIENT_ASSERTION` answers): [`run2_resolved/`](./run2_resolved/) — `QA_BLOCKED`
- LIVE-03 (integrity-hardened, same benchmark/answers): [`run3_integrity/`](./run3_integrity/) — `QA_BLOCKED`
- Summary: [`G1_GRANT_QUALITY_REPORT.json`](./G1_GRANT_QUALITY_REPORT.json), comparison [`RUN1_RUN2_RUN3_COMPARISON.md`](./RUN1_RUN2_RUN3_COMPARISON.md), [`G1_GRANT_ENGINE_REALITY_LOCK.json`](./G1_GRANT_ENGINE_REALITY_LOCK.json) — `FAIL`

**Head status:** all three runs fail closed honestly. Not `READY_FOR_REVIEW`.

---

## RUN3 vs RUN2 — what cleared and what remains

| Metric | RUN2 | RUN3 |
|---|---|---|
| requirement coverage % | 91.7 | **100.0** |
| words | 2858 | 4827 |
| claims total | 51 | 112 |
| claims unsupported | 31 | 54 |
| numeric conflicts | 23 | 15 |
| temporal conflicts | 0 | 3 |
| critical gaps | 0 | 0 |
| readiness | QA_BLOCKED | QA_BLOCKED |

**Cleared in RUN3:**
- MR-005 executive-summary lane failure — coverage restored to **100%**; `no_unsupported_material_claims` now **PASS** (0 unresolved material claims).
- Word-limit failure moved from `cost_effectiveness` to the newly-drafting executive summary.

**Still failing (run3 gates):** `word_limits_satisfied` (`executive_summary 2189/200`, aggregate `4827/3264`), `numeric_consistency` (15 BUDGET_DRIFT), `temporal_consistency` (3), `quantity_drift` (1 cross-section).

## Blocked QA gates (run3)

| Gate | Status | Detail |
|---|---|---|
| `all_sections_drafted` | PASS | 5 sections drafted |
| `word_limits_satisfied` | **FAIL** | `executive_summary (2189/200)`, aggregate `(4827/3264)` |
| `budget_within_ceiling` | PASS | `total 180145.00 vs ceiling 182400.00` |
| `deadline_correct` | PASS | Feb 27, 2026 3:00 PM EST bound |
| `revision_correct` | PASS | `ga_dca_nofp_2026` in provenance, not prose |
| `required_terminology` | PASS | all present |
| `no_unsupported_material_claims` | **PASS** | 0 unresolved material claims (was FAIL in run2) |
| `no_fabricated_partnerships` | PASS | none without evidence |
| `submission_disabled` | PASS | structurally disabled |
| `numeric_consistency` | **FAIL** | **15 numeric contradiction(s)** |
| `temporal_consistency` | **FAIL** | **3 temporal contradiction(s)** |
| `quantity_drift` | **FAIL** | **1 cross-section quantity-drift** |

`readiness_state`: **QA_BLOCKED**
`blockers`: `15 numeric contradiction(s)` + `3 temporal contradiction(s)` + `1 cross-section quantity-drift` + unsupported material claims

---

## Open errors / gaps

### 1. ~~MR-005 — Executive-Summary lane failure~~ **FIXED in RUN3**
- Run1/run2: Executive Summary rendered `model request replay detected (MR-005)`; coverage stuck at 91.7%.
- RUN3 (commit `aaa8d3ff`): fresh request ids per retry attempt — the exec-summary lane now drafts; coverage **100%**.

### 2. Executive Summary over-length + reasoning dump (P0 — NEW in run3)
- The exec-summary lane now drafts but produced **2,189 words against a 200-word limit**: it echoed the funder's fill-in-the-template notes, the fact list, and its own planning reasoning as section text (chain-of-thought leak), repeating match figures 5–7×.
- **Fix implemented (this session):** deterministic word-limit enforcement in the drafting loop (`_length_weakness` forces a revision with an explicit LENGTH directive until within the hard limit; `max_revisions` 1→3) plus prompt rules 9/10 (hard length, output-only-final-prose). Verified by `test_over_length_section_forced_into_revision`.

### 3. Budget drift — 15 BUDGET_DRIFT conflicts (P0)
RUN3 drift is entirely match figures, not invented line items:
- 5× **$39,600** (cash match) + 7× **$57,600** (cash+in-kind = $39,600+$18,000) + 1× **$39,600** in cost-effectiveness, all in the exec-summary dump; plus 2× a mangled **$57,6008**.
- Canonical: total **$180,145** / ceiling **$182,400** / cash match **$39,600** / in-kind **$18,000** / **24%** match. The match figures live in the governed `match_ability` fact, but `check_numerics` only licensed budget-line values.
- **Fix implemented (this session):** `check_numerics` now also licenses governed fact-pack dollar figures and derived pair-sums with lineage (mission §17); `_classify` marks them `CANONICAL_FACT`/`BUDGET_DERIVED`. The mangled `$57,6008` still correctly blocks. Verified by `test_governed_fact_dollar_not_budget_drift` / `test_derived_match_total_licensed` / `test_mangled_dollar_figure_still_blocks`.

### 4. Temporal conflicts — 3 in run3
- cl-int-0002/0012 are `member_count = 8 (target)` / `leveraged_volunteers = 60 (target)` echoes inside the exec-summary dump — expected to disappear once the dump is cut to 200 words.
- cl-int-0088 (program_design): "facilitates quarterly community-forum events" — present-tense claim carrying 2026; verify after the word-limit fix whether it was part of the dump.

### 5. Cross-section quantity-drift gate — false positive (P0)
- The run3 `quantity_drift` conflict is noise: subjectless claims (empty subject/predicate) were bucketed under a synthetic `(org|quantity)` key, so years (2024/2025), budget figures, and unrelated counts were reported as "drift".
- **Fix implemented (this session):** only NAMED quantities (real subject+predicate) are compared; calendar years are excluded. Verified by `test_subjectless_numbers_not_cross_section_drift` / `test_named_quantity_drift_still_caught`.

### 6. Dosage invented despite cleared missing-fact (P0 — carried from run2)
- Prose asserted dosage details (3 afternoons/week, 90-min sessions, 1,700-hr term, etc.) as `MODEL_INFERENCE` with no governed source. `member_dosage` was cleared as a critical gap but the model re-invented dosage.
- Action (mission §9): dosage facts must resolve to the client answer verbatim; invention stays blocked. Not re-measured in run3 gate output — re-check on the next run.

### 7. Organization facts invented (P1 — carried from run2)
EIN 58-2345671, founded 2012, HQ 1420 Elm St LaFayette GA, SAM UEI JJ7KQM4XLYY3, staff of 7 FT + 11 PT (cl-int-0015 …). None have a governed source.
- Action: organization-fact audit — every org identity value must resolve to `OrganizationFactPack` or be reclassified/blocked.

### 8. Unsupported outcome statistics (P1 — carried from run2)
+0.4/+0.5 grade-equivalent gains, 91% vs 78% on-time graduation (cl-int-0011), 87%/84% attendance metrics (cl-int-0013) — `MODEL_INFERENCE` with no research source.
- Action: research-claim audit — reclassify as `EXTERNAL_RESEARCH` with real source, or as `ASSUMPTION`/`FUTURE_TARGET`, or remove.

---

## Next steps to reach `READY_FOR_REVIEW`
1. Validate the implemented fixes (word-limit enforcement, match-figure licensing, drift-gate scoping) on a fresh live run — expect `word_limits_satisfied` to pass and BUDGET_DRIFT to drop to ~0.
2. Re-check dosage + org-fact + outcome-stat claims under the fixed gates.
3. Re-run benchmark → expect run4 to clear `QA_BLOCKED` and flip the reality lock to PASS.