# G0 Book 2 — State Machine Catalog (B2.C7)

**Source of truth:** `config/g0/domain/state_machines.yaml` (6 machines)
**Prototype:** `prototype/g0/domain/transitions.py`
**Tests:** `tests/g0/book2/test_state_machines.py`

## Machines

| Machine | States | Phase 1 terminal |
|---|---|---|
| opportunity | DISCOVERED → ACTIVE → AMENDED → CLOSED → CANCELLED → ARCHIVED | ARCHIVED |
| eligibility_decision | PENDING_INPUTS → EVALUATED → SUPERSEDED | — (result enum separate) |
| application_project | IDEA → QUALIFYING → RESEARCH → DRAFTING → QA → HUMAN_REVIEW → SUBMISSION_READY (+ future SUBMITTED/AWARDED/REJECTED/WITHDRAWN) | **SUBMISSION_READY** |
| requirement | IDENTIFIED → NORMALIZED → IN_PROGRESS → SATISFIED → VERIFIED (+ NOT_APPLICABLE/BLOCKED/WAIVED) | VERIFIED |
| artifact | DRAFT → QA_PENDING → REVIEW_REQUIRED → APPROVED_INTERNAL → SUBMISSION_READY → SUPERSEDED (+ MOCK) | SUBMISSION_READY |
| canonical_fact | PROPOSED → PROMOTED → CONFLICTED → SUPERSEDED → RETIRED | — |

## Transition contract

Every transition declares: from/to, capability required (Book 1 capability
ids), authority level, preconditions (machine-checkable codes:
`eligibility_not_ineligible`, `revision_current`,
`mandatory_requirements_satisfied`, `qa_passed`, `human_review_done`,
`evidence_promoted`, `terms_immutable`, `draft_material_satisfied`),
audit class, invalidation consequences.

## Phase 1 rules (tested)

- **SUBMITTED/AWARDED/REJECTED/WITHDRAWN are future states** — unreachable in
  Phase 1 even with L5 authority (capability `application.submit` stays
  disabled per Book 1 CD-003).
- SUBMISSION_READY is gated: stale eligibility, stale opportunity revision, or
  unsatisfied mandatory requirements block readiness.
- Stale revision forces re-evaluation: transitions requiring `revision_current`
  (RESEARCH→DRAFTING, …→SUBMISSION_READY) are blocked until re-checked.
- Illegal jumps (IDEA→QA) rejected; wrong capability / insufficient authority
  rejected; preconditions are deterministic.
