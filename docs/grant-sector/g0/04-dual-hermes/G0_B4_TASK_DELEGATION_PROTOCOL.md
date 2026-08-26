# G0 Book 4 — Task Delegation Protocol

**Document ID:** GS-G0-B4-C6-C7-PROTOCOL-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C6-C7
**Schemas:** `schemas/g0/agents/task_plan.schema.json`, `schemas/g0/agents/task_contract.schema.json`
**Policy:** `config/g0/agents/worker_context_policy.yaml`
**Prototype:** `prototype/g0/agents/task_builder.py`
**Validator:** `tools/g0/validate_task_delegation.py`

---

## 1. Purpose

Define CEO's operational decomposition (TaskPlan) and the minimum-information,
maximum-clarity worker boundary (TaskContract) before any work is delegated.

## 2. TaskPlan

```yaml
plan_id:
intent_id:
application_project_id:
objective:
steps:
dependencies:
parallelizable_groups:
critical_path:
required_capabilities:
budget_constraints:
time_constraints:
stop_conditions:
human_review_points:
created_by:
version:
```

### Plan principles

- explicit dependency graph;
- deterministic services used where available;
- worker count reflects work, not agent theater;
- parallel work only when context/data boundaries allow;
- plan is versioned when material assumptions change.

### Eligibility gate (frozen)

> A plan cannot schedule drafting before a required hard-eligibility failure
> is resolved **unless explicitly mock/research-only**.

### Rejections

- circular dependency chains;
- unknown dependency step references;
- any submission-family or phase-disabled capability.

## 3. TaskContract

```yaml
task_id:
plan_id:
tenant_id:
project_id:
worker_role:
objective:
capability_id:
inputs_refs:
allowed_context_refs:
constraints:
required_outputs:
quality_gates:
source_requirements:
authority_scope:
side_effect_policy:
max_attempts:
time_budget:
token_or_cost_budget:
expires_at:
```

### Context minimization rule (frozen)

> Workers receive object/evidence refs or bounded extracted context — not the
> full CEO prompt/history.

`allowed_context_refs` is the *only* context the worker may touch; unlisted
ref access is DENIED and audited.

### Delegation law (frozen)

> CEO may delegate only capabilities explicitly delegable within its own
> authority. CEO-owned capabilities (`application.draft_full_proposal`,
> `application.create_draft_project`, `application.prepare_submission_package`,
> `match.rank`, ...) are never granted to workers.

### Worker roles (logical, not permanent processes)

FunderResearchWorker · WinnerResearchWorker · CommunityEvidenceWorker ·
RequirementNormalizationWorker · ProposalSectionWorker · BusinessPlanWorker ·
BudgetValidationWorker · CitationQAWorker · DeterministicService.

### Expiry and lineage

- `expires_at` enforced; expired tasks cannot execute.
- Retries keep the same `task_id` lineage with new attempt ids
  (`task-1/attempt-1`, `task-1/attempt-2`).

## 4. Worker context policy (frozen)

- `context_minimization: REFS_AND_BOUNDED_EXTRACTS_ONLY`
- never inject: full CEO prompt history, raw client transcript, other-task
  scratch, raw secrets, closed-project chatter;
- worker memory default: **stateless across tasks**; persistent worker memory
  prohibited without a ratified ADR;
- task scratch expires after configured retention.

## 5. Verified behaviors

- `test_plan_requires_eligibility_before_drafting`
- `test_plan_circular_dependencies_rejected`
- `test_plan_disabled_capability_rejected`
- `test_task_cannot_omit_tenant_scope` / `test_task_cannot_omit_project_scope`
- `test_task_cannot_grant_ceo_owned_capability`
- `test_worker_cannot_access_unlisted_context_ref`
- `test_task_expiration_enforced`
- `test_task_retries_preserve_lineage`
