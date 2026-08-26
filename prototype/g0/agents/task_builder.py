"""B4.C6-C7 — TaskPlan and TaskContract builder (prototype).

Implements CEO's bounded delegation:
  * build_plan: explicit dependency graph with cycle rejection, disabled
    capability rejection, and the drafting-before-eligibility gate (drafting
    may not be scheduled before a required hard-eligibility failure is
    resolved unless explicitly mock/research-only);
  * build_task_contract: tenant/project scope mandatory, capability must be
    delegable within the CEO's authority, expiry enforced;
  * is_expired / new_attempt: task expiration and attempt lineage;
  * check_context_ref_allowed: worker may only touch listed context refs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

DRAFTING_STEP_TYPES = {"DRAFT_SECTION", "RECONCILE_BUDGET",
                       "CROSS_DOCUMENT_QA"}

CEOS_DELEGABLE_CAPABILITIES = {
    "research.funder", "research.winner", "research.community",
    "research.organization", "research.program", "opportunity.fetch",
    "opportunity.compare_revision", "eligibility.extract_candidate_rules",
    "application.create_blueprint", "application.draft_section",
    "application.update_internal", "budget.create", "budget.render",
    "qa.requirement_coverage", "qa.cross_document_consistency",
    "qa.alignment", "qa.humanization", "artifact.generate",
    "artifact.version", "artifact.export", "evidence.extract_claim",
    "evidence.trace_lineage", "match.explain",
}

CEOS_OWN_CAPABILITIES = {  # NOT delegable to workers
    "application.create_draft_project", "application.draft_full_proposal",
    "application.draft_business_plan", "application.prepare_submission_package",
    "match.rank", "match.recompute", "system.propose_change",
    "system.inspect_health",
}

VALID_WORKER_ROLES = {
    "FunderResearchWorker", "WinnerResearchWorker", "CommunityEvidenceWorker",
    "RequirementNormalizationWorker", "ProposalSectionWorker",
    "BusinessPlanWorker", "BudgetValidationWorker", "CitationQAWorker",
    "DeterministicService", "OtherBoundedWorker",
}


class TaskPlanError(ValueError):
    """Raised when a TaskPlan violates the delegation laws."""


class TaskContractError(ValueError):
    """Raised when a TaskContract violates the delegation laws."""


@dataclass
class PlanStep:
    step_id: str
    step_type: str
    objective: str
    required_capability: str
    mock_or_research_only: bool = False


@dataclass
class TaskPlan:
    plan_id: str
    intent_id: str
    objective: str
    steps: list[PlanStep]
    dependencies: list[tuple[str, str]]
    required_capabilities: list[str]
    created_by: str = "CEO_HERMES"
    version: int = 1
    application_project_id: str | None = None
    parallelizable_groups: list[list[str]] = field(default_factory=list)
    critical_path: list[str] = field(default_factory=list)
    stop_conditions: list[str] = field(default_factory=list)
    human_review_points: list[str] = field(default_factory=list)
    eligibility_gate: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def step_ids(self) -> set[str]:
        return {s.step_id for s in self.steps}


@dataclass
class TaskContract:
    task_id: str
    plan_id: str
    tenant_id: str
    project_id: str
    worker_role: str
    objective: str
    capability_id: str
    inputs_refs: list[str]
    allowed_context_refs: list[str]
    required_outputs: list[str]
    authority_scope: str
    side_effect_policy: str
    expires_at: str
    constraints: list[str] = field(default_factory=list)
    quality_gates: list[str] = field(default_factory=list)
    source_requirements: list[str] = field(default_factory=list)
    max_attempts: int = 3
    time_budget: str | None = None
    token_or_cost_budget: int | None = None
    issued_by: str = "CEO_HERMES"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _detect_cycles(steps: list[PlanStep],
                   dependencies: list[tuple[str, str]]) -> list[str]:
    """Return a cycle description or [] when the graph is acyclic."""
    edges = {f: t for f, t in dependencies}
    step_ids = {s.step_id for s in steps}
    for f, t in dependencies:
        if f not in step_ids or t not in step_ids:
            return [f"dependency references unknown step: {f}->{t}"]
    # DFS cycle detection
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, path: list[str]) -> list[str]:
        if node in visiting:
            return path[path.index(node):] + [node]
        if node in visited:
            return []
        visiting.add(node)
        path.append(node)
        nxt = edges.get(node)
        if nxt:
            result = visit(nxt, path)
            if result:
                return result
        visiting.remove(node)
        path.pop()
        visited.add(node)
        return []

    for step in steps:
        result = visit(step.step_id, [])
        if result:
            return [f"dependency cycle: {' -> '.join(result)}"]
    return []


def build_plan(*, plan_id: str, intent_id: str, objective: str,
               steps: list[dict], dependencies: list[tuple[str, str]],
               required_capabilities: list[str],
               hard_eligibility_verified: bool = False,
               drafting_allowed_before_resolution: bool = False,
               phase_disabled: set[str] | None = None,
               version: int = 1,
               application_project_id: str | None = None,
               parallelizable_groups: list[list[str]] | None = None,
               critical_path: list[str] | None = None,
               stop_conditions: list[str] | None = None,
               human_review_points: list[str] | None = None) -> TaskPlan:
    """Build a validated TaskPlan (fail closed on C6 laws)."""
    errors: list[str] = []
    if not steps:
        errors.append("plan requires at least one step")

    plan_steps = [PlanStep(**s) for s in steps] if steps else []
    for s in plan_steps:
        if s.required_capability.startswith("submission.") or \
                s.required_capability == "application.submit":
            errors.append(f"{s.step_id}: plan cannot require submission "
                          "capability (disabled in Phase 1)")
        if phase_disabled and s.required_capability in phase_disabled:
            errors.append(f"{s.step_id}: requires disabled capability "
                          f"'{s.required_capability}'")

    cycle_errors = _detect_cycles(plan_steps, dependencies)
    errors.extend(cycle_errors)

    # Drafting-before-eligibility gate
    has_drafting = any(s.step_type in DRAFTING_STEP_TYPES for s in plan_steps)
    if has_drafting and not hard_eligibility_verified:
        mock_only = all(s.mock_or_research_only for s in plan_steps
                        if s.step_type in DRAFTING_STEP_TYPES)
        if not (mock_only or drafting_allowed_before_resolution):
            errors.append(
                "plan cannot schedule drafting before the required "
                "hard-eligibility failure is resolved unless explicitly "
                "mock/research-only")

    for cap in required_capabilities:
        if cap.startswith("submission.") or cap == "application.submit":
            errors.append(f"required capability '{cap}' is disabled")

    if errors:
        raise TaskPlanError("; ".join(errors))

    return TaskPlan(
        plan_id=plan_id,
        intent_id=intent_id,
        objective=objective,
        steps=plan_steps,
        dependencies=list(dependencies),
        required_capabilities=list(required_capabilities),
        version=version,
        application_project_id=application_project_id,
        parallelizable_groups=list(parallelizable_groups or []),
        critical_path=list(critical_path or []),
        stop_conditions=list(stop_conditions or []),
        human_review_points=list(human_review_points or []),
        eligibility_gate={
            "hard_eligibility_verified": hard_eligibility_verified,
            "drafting_allowed_before_resolution": drafting_allowed_before_resolution,
            "reason": ("" if hard_eligibility_verified or
                       drafting_allowed_before_resolution
                       else "blocked by unresolved hard-eligibility failure"),
        },
        created_at=_now_iso(),
    )


def build_task_contract(*, task_id: str, plan_id: str, tenant_id: str,
                        project_id: str, worker_role: str, objective: str,
                        capability_id: str, inputs_refs: list[str],
                        allowed_context_refs: list[str],
                        required_outputs: list[str], expires_at: str,
                        authority_scope: str = "TASK_SCOPED_L2",
                        side_effect_policy: str = "READ_ONLY",
                        max_attempts: int = 3,
                        time_budget: str | None = None,
                        token_or_cost_budget: int | None = None) -> TaskContract:
    """Build a validated TaskContract (fail closed on C7 laws)."""
    errors: list[str] = []
    if not tenant_id:
        errors.append("task cannot omit tenant scope")
    if not project_id:
        errors.append("task cannot omit project scope")
    if worker_role not in VALID_WORKER_ROLES:
        errors.append(f"unknown worker_role '{worker_role}'")
    if capability_id not in CEOS_DELEGABLE_CAPABILITIES:
        if capability_id in CEOS_OWN_CAPABILITIES:
            errors.append(f"capability '{capability_id}' is CEO-owned and "
                          "not delegable to workers")
        else:
            errors.append(f"capability '{capability_id}' is not a registered "
                          "delegable capability")
    if not expires_at:
        errors.append("task expiration (expires_at) is required")
    if not inputs_refs:
        errors.append("task requires at least one input ref")
    if not required_outputs:
        errors.append("task requires at least one required output")
    if authority_scope not in ("TASK_SCOPED_L0", "TASK_SCOPED_L2"):
        errors.append(f"unknown authority_scope '{authority_scope}'")
    if side_effect_policy not in ("READ_ONLY", "INTERNAL_WRITE_SCOPED",
                                  "NO_EXTERNAL_SIDE_EFFECTS"):
        errors.append(f"unknown side_effect_policy '{side_effect_policy}'")
    if errors:
        raise TaskContractError("; ".join(errors))

    return TaskContract(
        task_id=task_id, plan_id=plan_id, tenant_id=tenant_id,
        project_id=project_id, worker_role=worker_role, objective=objective,
        capability_id=capability_id, inputs_refs=list(inputs_refs),
        allowed_context_refs=list(allowed_context_refs),
        required_outputs=list(required_outputs),
        authority_scope=authority_scope, side_effect_policy=side_effect_policy,
        expires_at=expires_at, max_attempts=max_attempts,
        time_budget=time_budget, token_or_cost_budget=token_or_cost_budget,
    )


def is_expired(contract: TaskContract, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    expires = datetime.fromisoformat(contract.expires_at.replace("Z", "+00:00"))
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return now > expires


def check_context_ref_allowed(contract: TaskContract, ref: str) -> bool:
    """A worker may only touch context refs listed in the contract."""
    return ref in contract.allowed_context_refs


def new_attempt(task_id: str, attempt_number: int) -> str:
    """Retries retain the same task lineage with a new attempt id."""
    return f"{task_id}/attempt-{attempt_number}"
