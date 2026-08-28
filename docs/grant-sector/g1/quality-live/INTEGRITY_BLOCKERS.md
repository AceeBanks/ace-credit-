# G1 Integrity — Open Blockers (run1/run2 evidence)

_Catalogued:_ 2026-08-28 — after LIVE-01 + LIVE-02 integrity benchmark against the real FY2026 AmeriCorps Georgia NOFO.

Artifacts:
- LIVE-01 (no client answers): [`run1_blocked/`](./run1_blocked/) — `NEEDS_CLIENT_INPUT`
- LIVE-02 (3 controlled `MOCK_CLIENT_ASSERTION` answers): [`run2_resolved/`](./run2_resolved/) — `QA_BLOCKED`
- Summary: [`G1_GRANT_QUALITY_REPORT.json`](./G1_GRANT_QUALITY_REPORT.json)

**Head status:** both runs fail closed honestly. Not `READY_FOR_REVIEW`.

---

## Blocked QA gates (run2)

| Gate | Status | Detail |
|---|---|---|
| `all_sections_drafted` | PASS | 5 sections drafted |
| `word_limits_satisfied` | **FAIL** | `cost_effectiveness (845/756)` over its individual limit |
| `budget_within_ceiling` | PASS | `total 180145.00 vs ceiling 182400.00` |
| `deadline_correct` | PASS | Feb 27, 2026 3:00 PM EST bound |
| `revision_correct` | PASS | `ga_dca_nofp_2026` in provenance, not prose |
| `required_terminology` | PASS | all present |
| `no_unsupported_material_claims` | **FAIL** | 1 unresolved material claim remains |
| `no_fabricated_partnerships` | PASS | none without evidence |
| `submission_disabled` | PASS | structurally disabled |
| `numeric_consistency` | **FAIL** | **23 numeric contradiction(s)** |

`readiness_state`: **QA_BLOCKED**
`blockers`: `23 numeric contradiction(s)` + `20 unsupported/unresolved material claim(s) with no governed authority`

---

## Open errors / gaps

### 1. MR-005 — Executive-Summary lane failure (P0)
- Executive Summary renders `model request replay detected (MR-005)` (unresolved claim `cl-int-0001`).
- Coverage stuck at **91.7%**; the section never generated.
- Action: fix the request-replay guard so the exec-summary section actually drafts.

### 2. Budget drift — 23 BUDGET_DRIFT conflicts (P0)
Prose invents a second budget that does not reconcile to the canonical plan:
- Claims **$240,000** total project cost; **$150,000** retention; **$120,000** living allowance (8 × $15k); **$46,000** personnel; various line items ($12k/$2k/$1.2k/$8k/$4k/$3k/$5k/$1k/$9k…).
- Canonical (from run's own `budget_within_ceiling`): total **$180,145** / federal **$182,400** / cash match **$39,600** / in-kind **$18,000** / **24%** match.
- Action: bind every prose dollar figure to the canonical budget; block prose amounts that are not canonical budget values.

### 3. Dosage invented despite cleared missing-fact (P0)
Prose asserts: 3 afternoons/week, 90-min sessions, 1,700-hour term, ~32 hrs/week, 32-week year, 144 hrs/member, 80-hr summer bridge, twelve 2-hr workshops.
- All unsupported `MODEL_INFERENCE` (cl-int-0004/0005/0006). `member_dosage` was cleared as a critical gap but the model re-invented dosage anyway.
- Action (mission §9): prohibit dosage claims in SectionPlan pre-generation and in the claim-checker post-generation.

### 4. Organization facts invented (P1)
EIN 58-2345671, founded 2012, HQ 1420 Elm St LaFayette GA, SAM UEI JJ7KQM4XLYY3, staff of 7 FT + 11 PT (cl-int-0015 …). None have a governed source.
- Action: organization-fact audit — every org identity value must resolve to `OrganizationFactPack` or be reclassified/blocked.

### 5. Unsupported outcome statistics (P1)
+0.4/+0.5 grade-equivalent gains, 91% vs 78% on-time graduation (cl-int-0011), 87%/84% attendance metrics (cl-int-0013) — `MODEL_INFERENCE` with no research source.
- Action: research-claim audit — reclassify as `EXTERNAL_RESEARCH` with real source, or as `ASSUMPTION`/`FUTURE_TARGET`, or remove.

---

## Next steps to reach `READY_FOR_REVIEW`
1. Fix MR-005 exec-summary lane failure → restore 100% coverage.
2. Reconcile budget prose to canonical budget (kill drift).
3. Bind dosage claims to governed facts (mission §9).
4. Audit org facts + outcome stats for governed lineage.
5. Re-run benchmark → expect run3 to clear `QA_BLOCKED`.