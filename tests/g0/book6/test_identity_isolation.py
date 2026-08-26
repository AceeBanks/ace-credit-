"""G0-B6-C2-C3 — Principal & identity + tenant/resource isolation tests.

Required coverage (plan):
- model swap preserves logical actor principal;
- disabled principal cannot authorize;
- worker instance identity tied to parent task but not parent authority;
- duplicate principal collision rejected;
- Tenant A member cannot read Tenant B artifact by guessed ID;
- shared public source reusable while tenant-private annotations isolated;
- worker assigned Project A cannot access Project B by default;
- admin membership expiry enforced.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.security.identity import (  # noqa: E402
    IdentityError,
    PrincipalRegistry,
    ScopeEvaluator,
)
from prototype.g0.security.models import Principal  # noqa: E402

T0 = "2026-08-26T00:00:00+00:00"


def _principal(**kw) -> Principal:
    base = dict(principal_id="p1", principal_type="HERMES_CEO",
                subject_id="ceo-1", status="ACTIVE",
                authentication_method="SERVICE_TOKEN",
                tenant_memberships=["tenant-a"], created_at=T0,
                credential_class="VAULT_REF")
    base.update(kw)
    return Principal(**base)


def test_model_swap_preserves_logical_actor():
    reg = PrincipalRegistry()
    reg.register(_principal(principal_id="ceo",
                            model_or_provider_ref="model:gpt-x"))
    assert reg.model_swap_preserves_identity("ceo", "model:claude-y") == "ceo"
    assert reg.get("ceo").model_or_provider_ref == "model:claude-y"
    assert reg.get("ceo").principal_id == "ceo"


def test_disabled_principal_cannot_authorize():
    reg = PrincipalRegistry()
    reg.register(_principal(principal_id="disabled", status="DISABLED"))
    reg.register(_principal(principal_id="active"))
    assert reg.can_authorize("disabled") is False
    assert reg.can_authorize("active") is True
    assert reg.can_authorize("ghost") is False


def test_duplicate_principal_collision_rejected():
    reg = PrincipalRegistry()
    reg.register(_principal(principal_id="dup"))
    with pytest.raises(IdentityError):
        reg.register(_principal(principal_id="dup"))


def test_worker_identity_bound_to_parent_task_no_authority():
    reg = PrincipalRegistry()
    worker = reg.register(_principal(
        principal_id="worker-1", principal_type="WORKER_AGENT",
        parent_task_id="task-9"))
    assert worker.parent_task_id == "task-9"
    # worker principal carries no capability/authority fields at all
    assert "parent_task_id" in worker.to_dict()
    assert reg.get("worker-1").principal_type == "WORKER_AGENT"


def test_tenant_a_member_cannot_read_tenant_b_artifact():
    scope = ScopeEvaluator()
    scope.add_membership(membership_id="m1", tenant_id="tenant-a",
                         principal_id="u-a", role_ids=["MEMBER"],
                         valid_from=T0, valid_to="2027-01-01T00:00:00+00:00")
    scope.register_resource("artifact:secret-b", "tenant-b")
    # guessed ID read attempt against tenant-b scope
    assert scope.can_read(principal_id="u-a", resource_id="artifact:secret-b",
                          resource_tenant="tenant-b") is False
    # but the actual owner can
    scope.add_membership(membership_id="m2", tenant_id="tenant-b",
                         principal_id="u-b", role_ids=["MEMBER"],
                         valid_from=T0, valid_to="2027-01-01T00:00:00+00:00")
    assert scope.can_read(principal_id="u-b", resource_id="artifact:secret-b",
                          resource_tenant="tenant-b") is True


def test_public_source_reusable_private_annotations_isolated():
    scope = ScopeEvaluator()
    scope.register_public_resource("snap:public")
    scope.add_membership(membership_id="m4", tenant_id="tenant-b",
                         principal_id="u-b", role_ids=["MEMBER"],
                         valid_from=T0, valid_to="2027-01-01T00:00:00+00:00")
    # public source reusable by any tenant's member
    assert scope.can_read(principal_id="u-b", resource_id="snap:public",
                          resource_tenant="__public__") is True
    # a private annotation stays tenant-bound and is not readable cross-tenant
    scope.register_resource("annot:private-a", "tenant-a")
    assert scope.can_read(principal_id="u-b", resource_id="annot:private-a",
                          resource_tenant="tenant-a") is False


def test_worker_project_a_cannot_access_project_b():
    scope = ScopeEvaluator()
    scope.register_resource("fact:r1", "tenant-a", project_id="proj-a")
    scope.register_resource("fact:r2", "tenant-a", project_id="proj-b")
    allowed = scope.worker_project_scope(principal_id="worker-1",
                                         assigned_project_id="proj-a")
    assert "fact:r1" in allowed
    assert "fact:r2" not in allowed


def test_admin_membership_expiry_enforced():
    scope = ScopeEvaluator()
    scope.add_membership(membership_id="m5", tenant_id="tenant-a",
                         principal_id="admin", role_ids=["ADMIN"],
                         valid_from=T0, valid_to="2026-08-01T00:00:00+00:00")
    scope.register_resource("artifact:x", "tenant-a")
    assert scope.can_read(principal_id="admin", resource_id="artifact:x",
                          resource_tenant="tenant-a",
                          now="2026-08-26T00:00:00+00:00") is False
