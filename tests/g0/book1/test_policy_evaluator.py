"""B1.C11 tests — executable policy evaluator.

Covers the twelve-step decision order, deny-by-default, and the exact
plan-mandated scenarios. Adversarial scenarios live in
test_adversarial_authority.py.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from prototype.g0.policy.evaluator import evaluate
from prototype.g0.policy.models import (
    Actor,
    ApprovalRef,
    AuthorityLevel,
    Decision,
    PolicyContext,
    Reason,
    TaskScope,
)
from prototype.g0.policy.registry import PolicyRegistry

_ROOT = Path(__file__).resolve().parents[3]

# Fixed, past, parseable decision timestamp for approval records (schema requires
# decided_at; evaluator rejects unparseable/future decisions).
_DECIDED = "2026-08-01T00:00:00Z"


@pytest.fixture(scope="module")
def reg() -> PolicyRegistry:
    return PolicyRegistry.load()


def ceo(tenants=("tenant-alpha",)) -> Actor:
    return Actor("ceo-1", "ACTOR-HERMES-CEO", tuple(tenants), AuthorityLevel.L2)


def personal() -> Actor:
    return Actor("personal-1", "ACTOR-HERMES-PERSONAL", ("tenant-alpha",), AuthorityLevel.L1)


def worker(task: TaskScope) -> Actor:
    return Actor("worker-9", "ACTOR-WORKER", (), AuthorityLevel.L2)


def ctx(**kw) -> PolicyContext:
    kw.setdefault("tenant_id", "tenant-alpha")
    kw.setdefault("project_id", "proj-1")
    kw.setdefault("resource_type", "application_draft")
    return PolicyContext(**kw)


# --- plan-mandated scenarios -------------------------------------------------

def test_draft_at_ceo_l2_allows(reg):
    result = evaluate(reg, ceo(), "application.draft_full_proposal", ctx())
    assert (result.decision, result.reason_code) == (Decision.ALLOW, Reason.ALLOW)


def test_submit_at_ceo_l2_denies(reg):
    r = evaluate(reg, ceo(), "application.submit",
                 ctx(resource_type="submission_package"))
    assert r.decision is Decision.DENY
    assert r.reason_code in (Reason.CAPABILITY_DISABLED, Reason.ACTOR_TYPE_DENIED)


def test_worker_can_research_assigned_grant(reg):
    task = TaskScope("t1", frozenset({"research.winner"}), "tenant-alpha", None,
                     AuthorityLevel.L2)
    w = Actor("worker-9", "ACTOR-WORKER", ("tenant-alpha",), AuthorityLevel.L2)
    r = evaluate(reg, w, "research.winner",
                 ctx(resource_type="research_pack", task_scope=task))
    assert r.decision is Decision.ALLOW


def test_worker_cannot_change_tenant_profile(reg):
    task = TaskScope("t1", frozenset({"organization.accept_verified_update"}),
                     "tenant-alpha", None, AuthorityLevel.L3)
    w = Actor("worker-9", "ACTOR-WORKER", ("tenant-alpha",), AuthorityLevel.L2)
    r = evaluate(reg, w, "organization.accept_verified_update",
                 ctx(resource_type="organization_profile", task_scope=task))
    # denied by ceiling AND actor-type AND task scope — any of them suffices
    assert r.decision is Decision.DENY


def test_personal_hermes_cannot_accept_profile_update(reg):
    r = evaluate(reg, personal(), "organization.accept_verified_update",
                 ctx(resource_type="organization_profile"))
    assert r.decision is Decision.DENY


def test_personal_hermes_can_propose_update(reg):
    r = evaluate(reg, personal(), "organization.propose_update",
                 ctx(resource_type="organization_profile"))
    assert r.decision is Decision.ALLOW

# --- decision-order steps ----------------------------------------------------

def test_unknown_actor_denied(reg):
    r = evaluate(reg, None, "opportunity.search", ctx())
    assert (r.decision, r.reason_code) == (Decision.DENY, Reason.UNKNOWN_ACTOR)


def test_unknown_capability_denied(reg):
    r = evaluate(reg, ceo(), "grant.auto_apply_all", ctx())
    assert (r.decision, r.reason_code) == (Decision.DENY, Reason.UNKNOWN_CAPABILITY)


def test_missing_tenant_denied(reg):
    r = evaluate(reg, ceo(), "opportunity.search",
                 ctx(tenant_id=None))
    assert (r.decision, r.reason_code) == (Decision.DENY, Reason.TENANT_SCOPE_MISSING)


def test_wrong_tenant_denied(reg):
    r = evaluate(reg, ceo(tenants=("tenant-alpha",)), "opportunity.search",
                 ctx(tenant_id="tenant-beta"))
    assert (r.decision, r.reason_code) == (Decision.DENY, Reason.TENANT_SCOPE_DENIED)


def test_wrong_project_scope_denied(reg):
    r = evaluate(reg, ceo(), "application.draft_full_proposal", ctx(project_id=None))
    assert (r.decision, r.reason_code) == (Decision.DENY, Reason.RESOURCE_SCOPE_DENIED)


def test_wrong_resource_type_denied(reg):
    r = evaluate(reg, ceo(), "application.draft_full_proposal",
                 ctx(resource_type="funder_portal"))
    assert (r.decision, r.reason_code) == (Decision.DENY, Reason.RESOURCE_SCOPE_DENIED)


def test_insufficient_authority_denied(reg):
    # L1 personal attempting an L2-only capability it isn't typed for either way
    r = evaluate(reg, personal(), "application.update_internal",
                 ctx(resource_type="application_project"))
    assert (r.decision, r.reason_code) == (Decision.DENY, Reason.ACTOR_TYPE_DENIED)


def test_disabled_actor_denied(reg):
    suspended = Actor("ceo-x", "ACTOR-HERMES-CEO", ("tenant-alpha",),
                      AuthorityLevel.L2, status="SUSPENDED")
    r = evaluate(reg, suspended, "opportunity.search", ctx())
    assert (r.decision, r.reason_code) == (Decision.DENY, Reason.DISABLED_ACTOR)


# --- approval enforcement ------------------------------------------------------

def test_ap2_without_approval_yields_require_approval(reg):
    r = evaluate(reg, ceo(), "evidence.propose_promotion",
                 ctx(resource_type="evidence_record"))
    assert (r.decision, r.reason_code) == (
        Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


def test_ap2_with_valid_human_approval_satisfied(reg):
    approval = ApprovalRef("ap-1", "human-owner", "HUMAN_CLIENT_APPROVER", "AP2",
                           "tenant-alpha", "evidence.propose_promotion",
                           decided_at=_DECIDED)
    r = evaluate(reg, ceo(), "evidence.propose_promotion",
                 ctx(resource_type="evidence_record", approval_refs=(approval,)))
    assert r.decision is Decision.ALLOW


def test_expired_approval_fails_closed(reg):
    approval = ApprovalRef("ap-1", "human-owner", "HUMAN_CLIENT_APPROVER", "AP2",
                           "tenant-alpha", "evidence.propose_promotion",
                           decided_at=_DECIDED, status="EXPIRED")
    r = evaluate(reg, ceo(), "evidence.propose_promotion",
                 ctx(resource_type="evidence_record", approval_refs=(approval,)))
    assert r.decision is Decision.REQUIRE_APPROVAL


def test_agent_principal_approval_is_ignored(reg):
    # The ApprovalRef contract now REJECTS agent principals at construction
    # (LAW-B1-018); the evaluator keeps its own agent check as defense in depth.
    with pytest.raises(ValueError):
        ApprovalRef("ap-2", "agent-ceo-self", "HUMAN_CLIENT_APPROVER", "AP2",
                    "tenant-alpha", "evidence.propose_promotion",
                    decided_at=_DECIDED)
    r = evaluate(reg, ceo(), "evidence.propose_promotion",
                 ctx(resource_type="evidence_record"))
    assert r.decision is Decision.REQUIRE_APPROVAL


def test_ap3_requires_two_distinct_humans(reg):
    promote_ctx = ctx(tenant_id="tenant-alpha", resource_type="system_state",
                      project_id=None)
    a1 = ApprovalRef("a", "owner-1", "DUAL_OWNER_PLUS_ADMIN", "AP3",
                     "tenant-alpha", "system.promote_change", decided_at=_DECIDED)
    same_guy = [ApprovalRef("a", "owner-1", "DUAL_OWNER_PLUS_ADMIN", "AP3",
                            "tenant-alpha", "system.promote_change",
                            decided_at=_DECIDED),
                ApprovalRef("b", "owner-1", "HUMAN_ADMIN_APPROVER", "AP3",
                            "tenant-alpha", "system.promote_change",
                            decided_at=_DECIDED)]
    r_same = evaluate(reg, Actor("admin-1", "ACTOR-HUMAN-ADMIN", (), AuthorityLevel.L5),
                      "system.promote_change",
                      PolicyContext(tenant_id=promote_ctx.tenant_id, project_id=None,
                                    resource_type="system_state",
                                    approval_refs=tuple(same_guy)))
    assert r_same.decision is Decision.REQUIRE_APPROVAL  # same principal twice

    distinct = [same_guy[0],
                ApprovalRef("c", "admin-2", "HUMAN_ADMIN_APPROVER", "AP3",
                            "tenant-alpha", "system.promote_change",
                            decided_at=_DECIDED)]
    r_ok = evaluate(reg, Actor("admin-1", "ACTOR-HUMAN-ADMIN", (), AuthorityLevel.L5),
                    "system.promote_change",
                    PolicyContext(tenant_id="tenant-alpha", project_id=None,
                                  resource_type="system_state",
                                  approval_refs=tuple(distinct)))
    assert r_ok.decision is Decision.ALLOW


def test_explicit_deny_overrides_everything(reg):
    r = evaluate(reg, ceo(), "opportunity.search",
                 ctx(explicit_deny_active=True))
    assert (r.decision, r.reason_code) == (Decision.DENY, Reason.EXPLICIT_DENY)


def test_evaluator_crash_fails_closed(monkeypatch, reg):
    from prototype.g0.policy import evaluator as ev
    def boom(*a, **k):
        raise RuntimeError("registry exploded")
    monkeypatch.setattr(ev, "_find_valid_approval", boom)
    approval = ApprovalRef("ap-1", "human-owner", "HUMAN_CLIENT_APPROVER", "AP2",
                           "tenant-alpha", "evidence.propose_promotion",
                           decided_at=_DECIDED)
    r = ev.evaluate(reg, ceo(), "evidence.propose_promotion",
                    ctx(resource_type="evidence_record", approval_refs=(approval,)))
    assert r.decision is Decision.DENY  # internal failure never yields ALLOW
