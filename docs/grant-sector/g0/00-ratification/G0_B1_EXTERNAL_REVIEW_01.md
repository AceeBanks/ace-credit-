# G0 Book 1 — External Review Record 01

**Review id:** `G0_B1_EXTERNAL_REVIEW_01`
**Reviewed surface:** Book 1 executable approval contract (`prototype/g0/policy/`),
`schemas/g0/policy/approval_policy.schema.json`, Book 1 test evidence, Reality Lock.
**Date:** 2026-08-26

## Review status

| Stage | Status |
|---|---|
| External review finding | **REPAIR_REQUIRED** |
| Repair commit | `5c99ac6b` — `G0-B1-REPAIR-02: close approval class, scope and expiry authorization gaps` |
| Post-repair verification | **PASS** (see below) |
| External review resolution | **RESOLVED** — authorized to continue Book 2 execution |

## Finding P0 — approval-class substitution (authorization gap)

**Severity: P0 (fail-open authorization).**

`prototype/g0/policy/evaluator.py::_find_valid_approval` matched an approval by
capability/tenant/status only — it did NOT require the approval's class to equal
the capability's required class. Consequences:

- An **AP1** (review-after) approval could satisfy an **AP2** (approval-before)
  capability requirement.
- An **AP1** or **AP2** approval could satisfy an **AP3** (dual approval)
  requirement as long as two distinct principals appeared.

This is implicit privilege inheritance the constitution never defines
(contradicts LAW-B1-005 fail-closed and the B1.C6 approval matrix).

**Schema side:** `subject_capability_id` was absent from `required` in
`approval_policy.schema.json`, and the executable `ApprovalRef` model did not
carry `scope_project_id`, `decided_at` or `expires_at`.

### Repair (commit `5c99ac6b`)

- `_find_valid_approval` is now class-exact: AP2 requires AP2; AP3 requires AP3
  from two distinct human principals; AP1 never satisfies AP2/AP3; APX is
  unsatisfiable. No implicit inheritance.
- Project scope enforced: an approval carrying `scope_project_id` authorizes
  ONLY that project; a project-scoped approval can never authorize another
  project.
- Time enforced: `status == VALID` AND `decided_at` parseable/not-future AND
  `expires_at` (when present) > evaluation time. An expired timestamp fails even
  if `status` is still `VALID`; future-decided and revoked approvals fail.
- `ApprovalRef` contract aligned with the schema: `decided_at` required,
  `scope_project_id`/`expires_at` carried, agent principals rejected at the
  contract boundary (LAW-B1-018).
- `approval_policy.schema.json`: `subject_capability_id` now required; project
  scope and exact-class semantics made explicit in descriptions; date-time
  format kept on both timestamps.
- 16 adversarial tests added in `tests/g0/book1/test_approval_integrity.py`
  (all ten mandated scenarios plus schema-contract and future-decided cases).

## Finding P1 — evidence-count drift

**Severity: P1 (evidence hygiene).**

Reported test counts did not match the tree at several checkpoints: the Book 1
test report claimed 103 tests at C16 while per-file counts differed slightly;
REPAIR-01 grew Book 1 to 117 and the full suite to 168; the report was not
regenerated, leaving the stale 103 figure live.

### Repair (commit `5c99ac6b`)

- `G0_B1_TEST_REPORT_AND_REALITY_LOCK_REPORT.md` regenerated with exact
  per-suite counts and a test-count history table explaining 103 → 117 → 133.
- `G0_B1_REALITY_LOCK.json` regenerated (records 132 passed + 1 self-excluded
  freshness test) and `G0_B0_REALITY_LOCK.json` regenerated (50 passed + 1
  skipped freshness self-test); both PASS.

## Note — premature internal RATIFY naming

The earlier `G0-B1-RATIFY` commit (51b0797b) was named "RATIFY" before any
external review existed. It is retained **as-is** as historical internal-readiness
evidence and is **not** rewritten or deleted; this record (`G0_B1_EXTERNAL_REVIEW_01`)
is the authoritative external review. Commit `G0-B1-RATIFY-EXT` below records the
external review resolution.

## Post-repair verification

| Suite | Command | Result |
|---|---|---|
| Book 0 | `python -m pytest tests/g0/book0 -q` | **51 passed** |
| Book 1 | `python -m pytest tests/g0/book1 -q` | **133 passed** (lock inner run: 132 + 1 self-excluded freshness) |
| Book 2 | `python -m pytest tests/g0/book2 -q` | **70 passed** |
| Total | `python -m pytest tests/g0/ -q` | **254 passed** |

- `G0_B0_REALITY_LOCK.json` → **PASS**, `ready_for_book1_ratification: true`
- `G0_B1_REALITY_LOCK.json` → **PASS**, `ready_for_book2: true`,
  `adversarial_p0_pass: true`, `p0_open: 0`
- Committed locks equal honest regeneration (freshness tests green).

## Resolution

All repaired tests and locks pass. External review is recorded as **RESOLVED**;
Book 2 execution is authorized to continue.
