# G0 Book 1 — Constitutional Law Catalog (rendered view)

**Machine-readable source of truth:** `config/g0/policy/constitutional_laws.yaml`
**Validator:** `tools/g0/validate_constitution.py`
**Count:** 30 laws (23 FROZEN, 7 amendable by MINOR/MAJOR as recorded).

This document renders summaries only; the YAML is authoritative and drift-checked.

## Enforcement categories

| Category | Meaning |
|---|---|
| deterministic_policy_engine | Enforced by `prototype/g0/policy/evaluator.py` decision order |
| schema_validation | JSON schemas in `schemas/g0/policy/` reject violations |
| audit_requirement | Durable structured audit evidence mandatory |
| governance_protocol | Process gate: approval/amendment/self-improvement lifecycle |
| architecture_constraint | Structural invariant proven by book tests |

## Law register

| ID | Law | Enforcement |
|---|---|---|
| LAW-B1-001 | Canonical truth external to agent memory | architecture_constraint |
| LAW-B1-002 | Durable state survives agent replacement | architecture_constraint |
| LAW-B1-003 | Tool availability ≠ authority | policy_engine |
| LAW-B1-004 | Capabilities explicit and scoped | policy_engine |
| LAW-B1-005 | Unknown authority fails closed | policy_engine |
| LAW-B1-006 | Deterministic constraints deterministically evaluated | policy_engine |
| LAW-B1-007 | Evidence precedes factual promotion | audit_requirement |
| LAW-B1-008 | Conflicts remain visible until resolved | audit_requirement |
| LAW-B1-009 | Personal/CEO cognition separated | architecture_constraint |
| LAW-B1-010 | Workers bounded, disposable, non-sovereign | policy_engine |
| LAW-B1-011 | Worker traces stay out of parent context | architecture_constraint |
| LAW-B1-012 | Human sovereignty over high-consequence action | governance_protocol |
| LAW-B1-013 | Safe drafting authorized early at L2 | policy_engine |
| LAW-B1-014 | Secrets outside conversational memory | schema_validation |
| LAW-B1-015 | Tenant boundaries mandatory | policy_engine |
| LAW-B1-016 | Consequential actions auditable | audit_requirement |
| LAW-B1-017 | No silent production self-modification | governance_protocol |
| LAW-B1-018 | Agents cannot ratify own authority expansion | governance_protocol |
| LAW-B1-019 | Source revisions immutable lineage events | architecture_constraint |
| LAW-B1-020 | Material source changes invalidate dependencies | architecture_constraint |
| LAW-B1-021 | Interoperability keeps internal semantics | architecture_constraint |
| LAW-B1-022 | Provider IDs not internal sovereignty | schema_validation |
| LAW-B1-023 | QA cannot fabricate facts | policy_engine |
| LAW-B1-024 | Research visibility is product obligation | architecture_constraint |
| LAW-B1-025 | Proposal and business plan distinct artifacts | architecture_constraint |
| LAW-B1-026 | Dynamic grant alignment required | architecture_constraint |
| LAW-B1-027 | Impact/community-benefit evidence first-class | architecture_constraint |
| LAW-B1-028 | Uncertain quality screening stays advisory | governance_protocol |
| LAW-B1-029 | Replay beats memory | audit_requirement |
| LAW-B1-030 | Extension cannot weaken controls | governance_protocol |

Full normative statements and rationales live in the YAML catalog.
