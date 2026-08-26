# G0-B5 — Handoff to Book 6

| Field | Value |
|---|---|
| Status | INTERNAL REALITY LOCK PASS (external ratification separate) |
| Branch | `grant-sector-r0-salvage` |
| Lock | `G0_B5_REALITY_LOCK.json` — status PASS, `ready_for_book6: true`, `p0_open: 0` |
| Full suite | `python -m pytest tests/g0 -q` → **1186 passed, 3 skipped** |
| Book 5 suite | 228 passed, 3 skipped (21 files) |
| Bake-off | Semantica 0.6.6 vs baseline — both correct on all shared workloads; verdict ADOPT_OPTIONAL_ACCELERATOR (deferred); storage ADR ratified Pattern A |

## What Book 6 receives (plan C27 list)

- ProvenanceRef contract
- Evidence graph edge semantics
- Evidence visibility classes
- DecisionRecord contract
- Audit ↔ decision ↔ evidence linkage
- Tenant-scoped retrieval requirements
- Graph/vector projection boundaries
- Storage ADR
- Optional framework role (Semantica: deferred)
- Failure/degraded modes
- Human approval lineage requirements

## Book 6 must then answer

> Which authenticated identity may retrieve, mutate, approve, export or act
> on these resources, through which capability/tool gateway, with which
> secret and tenant boundaries?

Book 6 must not redefine evidence authority merely because an integration
exposes a convenient API.

## Key contracts now executable

| Area | Artifact |
|---|---|
| Evidence laws | `config/g0/evidence/evidence_constitution.yaml` |
| Graph semantics | `config/g0/evidence/evidence_edge_types.yaml` |
| Decisions/replay | `schemas/g0/evidence/decision_record.schema.json`, `prototype/g0/evidence/replay.py` |
| Linkage | `config/g0/evidence/linkage_policy.yaml` |
| Visibility | `config/g0/evidence/visibility_policy.yaml` |
| Degraded modes | `config/g0/evidence/degraded_modes.yaml` |
| Adversarial catalog | `config/g0/evidence/adversarial_evidence.yaml` |
| Storage ADR | `G0_B5_STORAGE_ADR.md` |

## Open items for Book 6 attention

1. The tool gateway, credential brokerage and secret isolation (Book 6
   scope) must integrate with evidence visibility classes (VIS-001..007) and
   degraded modes (DEG-001..003).
2. The Semantica adapter remains frozen but uninstalled; Book 6 must not
   activate it without a new ADR with measured benefit.
3. D0/D1 readiness (C20) is evidence-ready; Book 6 must ensure no execution
   path can raise submission authority (submission remains structurally
   disabled).
