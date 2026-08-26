# G0 Book 1 — Capability Registry

**Chapter:** B1.C5 · **Machine-readable source:** `config/g0/policy/capability_registry.yaml` · **Validator:** `tools/g0/validate_policy_package.py`

The typed action vocabulary every future tool call maps into (LAW-B1-004).
**60 capabilities** across 12 families; **54 ENABLED**, **6 DISABLED**
(all of submission + `communication.send`).

## Families and highlights

| Family | Enabled capabilities | Notes |
|---|---|---|
| organization | read / propose_update / accept_verified_update / attach_evidence | acceptance is L3 human-approved |
| opportunity | search / fetch / snapshot / normalize / compare_revision | snapshots immutable (LAW-B1-019) |
| eligibility | extract_candidate_rules / validate_rule_set / evaluate / explain | evaluate+validate deterministic-only (LAW-B1-006) |
| matching | rank / explain / recompute | explain surfaces visible research (LAW-B1-024) |
| research | funder / winner / community / organization / program | all L2, tenant+project scoped |
| evidence | extract_claim / propose_promotion / resolve_conflict / trace_lineage | promotion & resolution AP2 human-gated |
| application | create_draft_project … draft_goal_sheet, update_internal, prepare_submission_package, submit | drafting ENABLED at L2; submit DISABLED |
| budget | create / calculate / validate / render | arithmetic deterministic-only |
| qa | requirement_coverage / factuality / citation_support / numeric_consistency / cross_document_consistency / alignment / humanization | factuality checks deterministic; humanization form-only (LAW-B1-023) |
| artifact | generate / version / compare / export | export ≠ transmit |
| communication | propose / send | send DISABLED in Phase 1 tooling path |
| submission | prepare / execute / certify / sign | ALL DISABLED — registered so the boundary is typed, reachable only via amendment |
| system | inspect_health / propose_change / run_eval / promote_change | promote_change AP3 human-only |

## Client-vision rule

All Phase 1 deliverable-producing capabilities are representable at L2/L3 —
the full document suite needs no L4/L5 infrastructure. Verified by
`tests/g0/book1/test_client_coverage.py` (B1.C12).

## Phase status matrix (disabled set)

| Capability | Why disabled |
|---|---|
| application.submit | APX / L5 / LEGALLY_MATERIAL |
| submission.prepare | whole family held for ratification |
| submission.execute | APX / L5 / LEGALLY_MATERIAL |
| submission.certify | APX / L5 / LEGALLY_MATERIAL |
| submission.sign | APX / L5 / LEGALLY_MATERIAL |
| communication.send | external side effect; enters at Phase 2 with approval wiring |

Every entry carries full policy metadata: minimum_level, allowed actor types,
resource types, tenant/project scope flags, approval class, side-effect class,
reversibility, audit class, rate-limit class, failure mode.
