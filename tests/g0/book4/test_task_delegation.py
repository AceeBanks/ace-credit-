"""B4.C6-C7 — TaskPlan and TaskContract delegation tests.

C6: plans cannot schedule drafting before a required hard-eligibility
failure is resolved (unless mock/research-only), circular dependencies are
rejected, disabled capabilities are rejected.
C7: tasks cannot omit tenant/project scope, cannot grant capability above
CEO's delegated authority, workers cannot access unlisted context refs, task
expiration is enforced, retries retain lineage. Plus schema/policy
adversarial injections.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.task_builder import (  # noqa: E402
    CEOS_DELEGABLE_CAPABILITIES,
    CEOS_OWN_CAPABILITIES,
    TaskContractError,
    TaskPlanError,
    build_plan,
    build_task_contract,
    check_context_ref_allowed,
    is_expired,
    new_attempt,
)
from tools.g0.validate_task_delegation import (  # noqa: E402
    validate_worker_context_policy,
)


def _steps() -> list[dict]:
    return [
        {"step_id": "s1", "step_type": "VERIFY_OPPORTUNITY_REVISION",
         "objective": "pin exact revision", "required_capability": "opportunity.fetch"},
        {"step_id": "s2", "step_type": "EVALUATE_ELIGIBILITY",
         "objective": "evaluate hard rules", "required_capability": "eligibility.extract_candidate_rules"},
        {"step_id": "s3", "step_type": "DRAFT_SECTION",
         "objective": "draft narrative", "required_capability": "application.draft_section"},
    ]


def _future() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()


# --- C6 plan tests ----------------------------------------------------------

def test_plan_requires_eligibility_before_drafting():
    with pytest.raises(TaskPlanError, match="hard-eligibility"):
        build_plan(
            plan_id="plan-1", intent_id="int-1",
            objective="build application", steps=_steps(),
            dependencies=[("s1", "s2"), ("s2", "s3")],
            required_capabilities=["opportunity.fetch"],
            hard_eligibility_verified=False,
        )


def test_plan_drafting_allowed_when_eligibility_verified():
    plan = build_plan(
        plan_id="plan-1", intent_id="int-1", objective="build application",
        steps=_steps(), dependencies=[("s1", "s2"), ("s2", "s3")],
        required_capabilities=["opportunity.fetch"],
        hard_eligibility_verified=True)
    assert plan.eligibility_gate["hard_eligibility_verified"] is True


def test_plan_mock_research_only_drafting_allowed():
    steps = _steps()
    steps[2]["mock_or_research_only"] = True
    plan = build_plan(
        plan_id="plan-2", intent_id="int-1", objective="mock draft",
        steps=steps, dependencies=[("s1", "s2"), ("s2", "s3")],
        required_capabilities=["opportunity.fetch"],
        hard_eligibility_verified=False)
    assert plan.plan_id == "plan-2"


def test_plan_circular_dependencies_rejected():
    with pytest.raises(TaskPlanError, match="cycle"):
        build_plan(
            plan_id="plan-3", intent_id="int-1", objective="x", steps=_steps(),
            dependencies=[("s1", "s2"), ("s2", "s3"), ("s3", "s1")],
            required_capabilities=["opportunity.fetch"],
            hard_eligibility_verified=True)


def test_plan_unknown_dependency_step_rejected():
    with pytest.raises(TaskPlanError, match="unknown step"):
        build_plan(
            plan_id="plan-4", intent_id="int-1", objective="x", steps=_steps(),
            dependencies=[("s1", "s2"), ("s2", "ghost")],
            required_capabilities=["opportunity.fetch"],
            hard_eligibility_verified=True)


def test_plan_disabled_capability_rejected():
    with pytest.raises(TaskPlanError, match="submission"):
        build_plan(
            plan_id="plan-5", intent_id="int-1", objective="x", steps=_steps(),
            dependencies=[("s1", "s2"), ("s2", "s3")],
            required_capabilities=["submission.execute"],
            hard_eligibility_verified=True)


def test_plan_requires_phase_disabled_capability_rejected():
    steps = _steps()
    steps[0]["required_capability"] = "application.submit"
    with pytest.raises(TaskPlanError, match="disabled"):
        build_plan(
            plan_id="plan-6", intent_id="int-1", objective="x", steps=steps,
            dependencies=[("s1", "s2"), ("s2", "s3")],
            required_capabilities=[],
            hard_eligibility_verified=True,
            phase_disabled={"application.submit"})


def test_plan_empty_steps_rejected():
    with pytest.raises(TaskPlanError, match="at least one step"):
        build_plan(
            plan_id="plan-7", intent_id="int-1", objective="x", steps=[],
            dependencies=[], required_capabilities=[],
            hard_eligibility_verified=True)


# --- C7 task contract tests -------------------------------------------------

def _contract_kwargs(**overrides) -> dict:
    kwargs = dict(
        task_id="task-1", plan_id="plan-1", tenant_id="tenant-georgia-youth",
        project_id="project-after-school", worker_role="FunderResearchWorker",
        objective="research funder priorities", capability_id="research.funder",
        inputs_refs=["opp/rev-3"], allowed_context_refs=["ctx/opp-3"],
        required_outputs=["research_finding"], expires_at=_future())
    kwargs.update(overrides)
    return kwargs


def test_task_cannot_omit_tenant_scope():
    with pytest.raises(TaskContractError, match="tenant"):
        build_task_contract(**_contract_kwargs(tenant_id=""))


def test_task_cannot_omit_project_scope():
    with pytest.raises(TaskContractError, match="project"):
        build_task_contract(**_contract_kwargs(project_id=""))


def test_task_cannot_grant_ceo_owned_capability():
    with pytest.raises(TaskContractError, match="CEO-owned"):
        build_task_contract(**_contract_kwargs(
            capability_id="application.draft_full_proposal"))
    assert "application.draft_full_proposal" in CEOS_OWN_CAPABILITIES


def test_task_cannot_grant_unknown_capability():
    with pytest.raises(TaskContractError, match="not a registered"):
        build_task_contract(**_contract_kwargs(capability_id="totally.bogus"))


def test_task_unknown_worker_role_rejected():
    with pytest.raises(TaskContractError, match="worker_role"):
        build_task_contract(**_contract_kwargs(worker_role="OmnipotentAgent"))


def test_task_expiration_enforced():
    contract = build_task_contract(**_contract_kwargs())
    assert is_expired(contract) is False
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    expired = build_task_contract(**_contract_kwargs(expires_at=past))
    assert is_expired(expired) is True


def test_task_requires_expiration():
    with pytest.raises(TaskContractError, match="expiration"):
        build_task_contract(**_contract_kwargs(expires_at=""))


def test_worker_cannot_access_unlisted_context_ref():
    contract = build_task_contract(**_contract_kwargs())
    assert check_context_ref_allowed(contract, "ctx/opp-3") is True
    assert check_context_ref_allowed(contract, "ctx/secret-other-project") is False


def test_task_retries_preserve_lineage():
    contract = build_task_contract(**_contract_kwargs())
    a1 = new_attempt(contract.task_id, 1)
    a2 = new_attempt(contract.task_id, 2)
    assert a1 == "task-1/attempt-1"
    assert a2 == "task-1/attempt-2"
    assert a1 != a2
    assert a1.startswith(contract.task_id)


def test_valid_contract_builds():
    contract = build_task_contract(**_contract_kwargs())
    assert contract.tenant_id == "tenant-georgia-youth"
    assert contract.project_id == "project-after-school"
    assert contract.issued_by == "CEO_HERMES"
    assert contract.capability_id in CEOS_DELEGABLE_CAPABILITIES


# --- validator adversarial checks -------------------------------------------

def test_worker_context_policy_clean():
    errors: list[str] = []
    validate_worker_context_policy(errors)
    assert errors == []


def test_worker_policy_full_history_injection_fails(monkeypatch):
    import tools.g0.validate_task_delegation as mod
    data = {
        "context_minimization": "REFS_AND_BOUNDED_EXTRACTS_ONLY",
        "never_inject": ["RAW_CLIENT_TRANSCRIPT", "OTHER_TASK_SCRATCH",
                         "RAW_SECRETS", "CLOSED_PROJECT_CHATTER"],
        "allowed_inputs": ["TASK_CONTRACT"],
        "allowed_outputs": ["WORKER_RESULT"],
        "worker_memory_default": "STATELESS_ACROSS_TASKS",
        "persistent_worker_memory_rule": "prohibited without ADR",
        "scratch_retention": "EXPIRES_AFTER_CONFIGURED_RETENTION",
        "scratch_retention_ref": "x",
        "context_ref_policy": {"unlisted_ref_access": "DENIED",
                               "enforcement": "x"},
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_worker_context_policy(errors)
    assert any("never_inject missing" in e and "FULL_CEO_PROMPT_HISTORY" in e
               for e in errors)


def test_worker_policy_unlisted_ref_allowed_fails(monkeypatch):
    import tools.g0.validate_task_delegation as mod
    data = {
        "context_minimization": "REFS_AND_BOUNDED_EXTRACTS_ONLY",
        "never_inject": ["FULL_CEO_PROMPT_HISTORY", "RAW_CLIENT_TRANSCRIPT",
                         "OTHER_TASK_SCRATCH", "RAW_SECRETS",
                         "CLOSED_PROJECT_CHATTER"],
        "allowed_inputs": ["TASK_CONTRACT"],
        "allowed_outputs": ["WORKER_RESULT"],
        "worker_memory_default": "STATELESS_ACROSS_TASKS",
        "persistent_worker_memory_rule": "prohibited without ADR",
        "scratch_retention": "EXPIRES_AFTER_CONFIGURED_RETENTION",
        "scratch_retention_ref": "x",
        "context_ref_policy": {"unlisted_ref_access": "ALLOWED",
                               "enforcement": "x"},
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_worker_context_policy(errors)
    assert any("DENIED" in e for e in errors)


def test_schemas_strict_and_complete():
    from tools.g0.validate_task_delegation import _check_schema
    from tools.g0.validate_task_delegation import (PLAN_REQUIRED,
                                                   CONTRACT_REQUIRED)
    errors: list[str] = []
    _check_schema("task_plan.schema.json", PLAN_REQUIRED, errors)
    _check_schema("task_contract.schema.json", CONTRACT_REQUIRED, errors)
    assert errors == []
