# G0 Book 4 — Context Compaction Policy

**Document ID:** GS-G0-B4-C17-COMPACT-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C17
**Policy:** `config/g0/agents/compaction_policy.yaml`
**Prototype:** `prototype/g0/agents/compactor.py`
**Validator:** `tools/g0/validate_compaction_reconstruction.py`

---

## 1. Purpose

A safer semantic compactor: context shrinks, **anchors never move**, facts
never change, and uncertainty is never silently converted to certainty.

## 2. Compaction stages

| Stage | Action |
|---|---|
| 0 | No compaction — use when under budget. |
| 1 | Drop disposable/redundant context (duplicates, stale tool output, already-promoted detail). |
| 2 | Snip historical low-value detail; preserve references/metadata. |
| 3 | Micro-summarize older episodes/tasks into bounded summaries. |
| 4 | Collapse inactive project context into project summary + artifact/evidence refs. |
| 5 | Model-assisted semantic compaction — last resort, schema-constrained, evaluated, with source refs and anchor preservation. |

## 3. Mandatory anchors (never compacted away)

tenant/user identity refs · active intent objective · authority scope · exact
active OpportunityRevision · unresolved critical clarification · eligibility
state · deadline-critical state · active blockers · human approvals/denials ·
source/evidence refs needed for the current task · safety/security
constraints.

## 4. Rules (frozen)

| Rule | Content |
|---|---|
| COMPACT-001 | Anchors survive every stage including stage 5; dropping an anchor is an assembly error. |
| COMPACT-002 | Factual numbers/dates/amounts/revision ids preserved verbatim — compaction may never change $75,000 to $750,000. |
| COMPACT-003 | Compaction cannot convert uncertainty to certainty. |
| COMPACT-004 | Every compaction records a CompactionManifest (removed/summarized/anchors/generator/source refs/before-after budget). |

## 5. Verified behaviors

- `test_anchors_survive_every_stage`
- `test_compaction_preserves_factual_numbers`
- `test_uncertainty_never_converted_to_certainty`
- `test_compacted_context_reproduces_same_decision`
- `test_manifest_records_everything`
