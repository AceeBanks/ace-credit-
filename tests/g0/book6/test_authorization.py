"""G0-B6-C4-C5 — Capability grant + authorization decision tests.

Required coverage (plan):
- broad role cannot bypass narrow resource scope;
- worker grant exceeds parent ceiling -> reject;
- expired grant denies;
- grant revoked mid-task blocks next protected action;
- phase-disabled capability cannot be enabled through grant alone;
- 100% fail-closed reason-code coverage (all 16 codes reachable).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.security.authorization import (  # noqa: E402
    REASON_CODES,
    Authorizer,
    AuthorizationError,
    GrantRegistry,
)
from prototype.g0.security.identity import (  # noqa: E402
    PrincipalRegistry,
    ScopeEvaluator,
)
from prototype.g0.security.models import Principal  # noqa: E402

T0 = "2026-08-26T00:00:00+00:00"
T_FAR = "2027-12-31T00:00:00+00:00"


def _principal(**kw) -> Principal:
    base = dict(principal_id="ceo", principal_type="HERMES_CEO",
                subject_id="ceo-1", status="ACTIVE",
                authentication_method="SERVICE_TOKEN",
                tenant_memberships=["tenant-a"], created_at=T0,
                credential_class="VAULT_REF", authority_level="L3")
    base.update(kw)
    return Principal(**base)


def _stack(**kw) -> tuple[Authorizer, PrincipalRegistry, ScopeEvaluator,
                          GrantRegistry]:
    principals = PrincipalRegistry()
    scope = ScopeEvaluator()
    grants = GrantRegistry()
    principals.register(_principal())
    principals.register(_principal(principal_id="worker",
                                   principal_type="WORKER_AGENT",
                                   authority_level="L1",
                                   parent_task_id="task-1"))
    principals.register(_principal(principal_id="disabled",
                                   principal_type="HUMAN_USER",
                                   status="DISABLED", authority_level="L2"))
    scope.add_membership(membership_id="m1", tenant_id="tenant-a",
                         principal_id="ceo", role_ids=["ADMIN"],
                         valid_from=T0, valid_to=T_FAR)
    scope.add_membership(membership_id="m2", tenant_id="tenant-a",
                         principal_id="worker", role_ids=["MEMBER"],
                         valid_from=T0, valid_to=T_FAR)
    scope.add_membership(membership_id="m3", tenant_id="tenant-a",
                         principal_id="disabled", role_ids=["MEMBER"],
                         valid_from=T0, valid_to=T_FAR)
    scope.register_resource("artifact:1", "tenant-a", project_id="proj-a")
    scope.register_resource("artifact:2", "tenant-b", project_id="proj-b")
    auth = Authorizer(principals=principals, scope=scope, grants=grants)
    auth.register_capability("research.run", required_level="L1")
    auth.register_capability("eligibility.execute_deterministic",
                             required_level="L2")
    auth.register_capability("credentials.read", required_level="L4")
    auth.register_capability("egress.send_external", required_level="L3")
    auth.register_capability("phase.disabled", required_level="L1",
                             enabled=False)
    auth.allow_data_class("PUBLIC_SOURCE")
    auth.allow_egress_destination("https://api.example.com")
    auth.add_deny_rule("deny-alpha")
    return auth, principals, scope, grants


def _req(**kw) -> dict:
    # requests carry an explicit project by default: artifact:1 is
    # project-scoped (proj-a) and REPAIR-01 enforces project scope strictly
    base = dict(request_id="r1", principal_id="ceo",
                capability_id="research.run", tenant_id="tenant-a",
                resource_type="ARTIFACT", resource_id="artifact:1",
                project_id="proj-a")
    base.update(kw)
    return base


def test_reason_codes_complete():
    expected = (
        "PRINCIPAL_UNKNOWN", "PRINCIPAL_DISABLED", "SESSION_INVALID",
        "TENANT_DENIED", "CAPABILITY_UNKNOWN", "CAPABILITY_DISABLED",
        "AUTHORITY_INSUFFICIENT", "GRANT_MISSING", "GRANT_EXPIRED",
        "GRANT_AUTHORITY_INSUFFICIENT", "PROJECT_DENIED",
        "RESOURCE_DENIED", "TASK_SCOPE_DENIED", "DATA_CLASS_DENIED",
        "EGRESS_DENIED", "APPROVAL_REQUIRED", "EXPLICIT_DENY", "ALLOW",
    )
    assert set(REASON_CODES) == set(expected)


def test_every_reason_code_reachable():
    auth, _, _, grants = _stack()
    grants.issue(grant_id="g1", principal_id="ceo",
                 capability_id="research.run", tenant_id="tenant-a",
                 authority_level="L3", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin", resource_constraints=["task-1"])
    cases = [
        (dict(_req(principal_id="ghost")), "PRINCIPAL_UNKNOWN"),
        (dict(_req(principal_id="disabled")), "PRINCIPAL_DISABLED"),
        (dict(_req(tenant_id="tenant-b")), "TENANT_DENIED"),
        (dict(_req(capability_id="nope.run")), "CAPABILITY_UNKNOWN"),
        (dict(_req(capability_id="phase.disabled")), "CAPABILITY_DISABLED"),
        (dict(_req(principal_id="worker",
                   capability_id="eligibility.execute_deterministic")),
         "AUTHORITY_INSUFFICIENT"),
        (dict(_req(capability_id="credentials.read")), "AUTHORITY_INSUFFICIENT"),
    ]
    for req, code in cases:
        decision = auth.authorize(req)
        assert decision["reason_code"] == code, req
    assert auth.authorize(_req(), session_valid=False)["reason_code"] == \
        "SESSION_INVALID"

    # GRANT_MISSING (registered capability, active principal, no grant)
    auth2, _, _, _ = _stack()
    d = auth2.authorize(_req())
    assert d["reason_code"] == "GRANT_MISSING"

    # GRANT_EXPIRED
    auth3, _, _, grants3 = _stack()
    grants3.issue(grant_id="gx", principal_id="ceo",
                  capability_id="research.run", tenant_id="tenant-a",
                  authority_level="L3", valid_from=T0,
                  expires_at="2026-08-01T00:00:00+00:00", issued_by="admin")
    assert auth3.authorize(_req())["reason_code"] == "GRANT_EXPIRED"

    # GRANT_AUTHORITY_INSUFFICIENT — grant below capability requirement
    authGA, _, _, grantsGA = _stack()
    grantsGA.issue(grant_id="g-lauth", principal_id="ceo",
                   capability_id="research.run", tenant_id="tenant-a",
                   authority_level="L0", valid_from=T0, expires_at=T_FAR,
                   issued_by="admin")
    d = authGA.authorize(_req())
    assert d["reason_code"] == "GRANT_AUTHORITY_INSUFFICIENT"

    # PROJECT_DENIED — grant bound to another project of the same tenant
    authP, _, _, grantsP = _stack()
    grantsP.issue(grant_id="g-pb", principal_id="ceo",
                  capability_id="research.run", tenant_id="tenant-a",
                  authority_level="L3", valid_from=T0, expires_at=T_FAR,
                  issued_by="admin", project_id="proj-b")
    d = authP.authorize(_req())  # request carries proj-a
    assert d["reason_code"] == "PROJECT_DENIED"

    # PROJECT_DENIED — project-scoped resource without an explicit project
    authP2, _, _, grantsP2 = _stack()
    grantsP2.issue(grant_id="g-any", principal_id="ceo",
                   capability_id="research.run", tenant_id="tenant-a",
                   authority_level="L3", valid_from=T0, expires_at=T_FAR,
                   issued_by="admin")
    d = authP2.authorize(_req(project_id=None))
    assert d["reason_code"] == "PROJECT_DENIED"

    # RESOURCE_DENIED
    auth4, _, _, grants4 = _stack()
    grants4.issue(grant_id="g4", principal_id="ceo",
                  capability_id="research.run", tenant_id="tenant-a",
                  authority_level="L3", valid_from=T0, expires_at=T_FAR,
                  issued_by="admin")
    d = auth4.authorize(_req(resource_id="artifact:2"))
    assert d["reason_code"] == "RESOURCE_DENIED"

    # TASK_SCOPE_DENIED
    auth5, _, _, grants5 = _stack()
    grants5.issue(grant_id="g5", principal_id="ceo",
                  capability_id="research.run", tenant_id="tenant-a",
                  authority_level="L3", valid_from=T0, expires_at=T_FAR,
                  issued_by="admin", resource_constraints=["task-1"])
    d = auth5.authorize(_req(task_scope="task-2"))
    assert d["reason_code"] == "TASK_SCOPE_DENIED"

    # DATA_CLASS_DENIED
    auth6, _, _, grants6 = _stack()
    grants6.issue(grant_id="g6", principal_id="ceo",
                  capability_id="research.run", tenant_id="tenant-a",
                  authority_level="L3", valid_from=T0, expires_at=T_FAR,
                  issued_by="admin")
    d = auth6.authorize(_req(context={"data_class": "TENANT_PRIVATE"}))
    assert d["reason_code"] == "DATA_CLASS_DENIED"

    # EGRESS_DENIED
    auth7, _, _, grants7 = _stack()
    grants7.issue(grant_id="g7", principal_id="ceo",
                  capability_id="egress.send_external", tenant_id="tenant-a",
                  authority_level="L3", valid_from=T0, expires_at=T_FAR,
                  issued_by="admin")
    d = auth7.authorize(_req(capability_id="egress.send_external",
                             destination="https://evil.example.com"))
    assert d["reason_code"] == "EGRESS_DENIED"

    # APPROVAL_REQUIRED
    auth8, _, _, grants8 = _stack()
    grants8.issue(grant_id="g8", principal_id="ceo",
                  capability_id="egress.send_external", tenant_id="tenant-a",
                  authority_level="L3", valid_from=T0, expires_at=T_FAR,
                  issued_by="admin")
    d = auth8.authorize(_req(capability_id="egress.send_external",
                             destination="https://api.example.com",
                             requested_side_effect="EXTERNAL_SEND"))
    assert d["reason_code"] == "APPROVAL_REQUIRED"

    # EXPLICIT_DENY
    auth9, _, _, grants9 = _stack()
    grants9.issue(grant_id="g9", principal_id="ceo",
                  capability_id="research.run", tenant_id="tenant-a",
                  authority_level="L3", valid_from=T0, expires_at=T_FAR,
                  issued_by="admin")
    d = auth9.authorize(_req(context={"deny_tags": ["deny-alpha"]}))
    assert d["reason_code"] == "EXPLICIT_DENY"

    # ALLOW
    auth10, _, _, grants10 = _stack()
    grants10.issue(grant_id="g10", principal_id="ceo",
                   capability_id="research.run", tenant_id="tenant-a",
                   authority_level="L3", valid_from=T0, expires_at=T_FAR,
                   issued_by="admin", resource_constraints=["task-1"])
    d = auth10.authorize(_req(task_scope="task-1",
                              context={"data_class": "PUBLIC_SOURCE"}))
    assert d["reason_code"] == "ALLOW"
    assert d["decision"] == "ALLOW"


def test_worker_grant_exceeding_parent_ceiling_rejected():
    _, _, _, grants = _stack()
    with pytest.raises(AuthorizationError):
        grants.issue(grant_id="wg", principal_id="worker",
                     capability_id="research.run", tenant_id="tenant-a",
                     authority_level="L3", valid_from=T0, expires_at=T_FAR,
                     issued_by="ceo", parent_ceiling="L1")


def test_non_delegable_capability_rejected():
    _, _, _, grants = _stack()
    with pytest.raises(AuthorizationError):
        grants.issue(grant_id="nd", principal_id="worker",
                     capability_id="application.approve", tenant_id="tenant-a",
                     authority_level="L1", valid_from=T0, expires_at=T_FAR,
                     issued_by="ceo", parent_ceiling="L1")


def test_phase_disabled_cannot_be_granted():
    _, _, _, grants = _stack()
    with pytest.raises(AuthorizationError):
        grants.issue(grant_id="pd", principal_id="worker",
                     capability_id="submission.execute", tenant_id="tenant-a",
                     authority_level="L1", valid_from=T0, expires_at=T_FAR,
                     issued_by="ceo", parent_ceiling="L3")


def test_expired_grant_denies():
    auth, _, _, grants = _stack()
    grants.issue(grant_id="ge", principal_id="ceo",
                 capability_id="research.run", tenant_id="tenant-a",
                 authority_level="L3", valid_from=T0,
                 expires_at="2026-08-01T00:00:00+00:00", issued_by="admin")
    assert auth.authorize(_req())["decision"] == "DENY"


def test_revoked_mid_task_blocks_next_action():
    auth, _, _, grants = _stack()
    grants.issue(grant_id="gr", principal_id="ceo",
                 capability_id="research.run", tenant_id="tenant-a",
                 authority_level="L3", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin", resource_constraints=["task-1"])
    assert auth.authorize(_req(task_scope="task-1"))["decision"] == "ALLOW"
    grants.revoke("gr")  # revoked mid-task
    assert auth.authorize(_req(task_scope="task-1"))["decision"] == "DENY"
    assert grants.grant_valid("gr") is False


# ------------------------------------------------------------------
# G0-B6-REPAIR-01 — AUTH-R1 grant authority ladder (mandated cases)
# ------------------------------------------------------------------

def _ladder_stack(principal_level: str):
    """A minimal L4-grade stack for ladder scenarios."""
    principals = PrincipalRegistry()
    scope = ScopeEvaluator()
    grants = GrantRegistry()
    principals.register(
        Principal(principal_id="exec", principal_type="HERMES_CEO",
                  subject_id="exec-1", status="ACTIVE",
                  authentication_method="SERVICE_TOKEN",
                  tenant_memberships=["tenant-a"], created_at=T0,
                  credential_class="VAULT_REF",
                  authority_level=principal_level))
    scope.add_membership(membership_id="m-exec", tenant_id="tenant-a",
                         principal_id="exec", role_ids=["ADMIN"],
                         valid_from=T0, valid_to=T_FAR)
    scope.register_resource("app:workflow-1", "tenant-a")
    auth = Authorizer(principals=principals, scope=scope, grants=grants)
    auth.register_capability("application.approve", required_level="L4")
    return auth, grants


def _ladder_req(**kw) -> dict:
    base = dict(request_id="r-lad", principal_id="exec",
                capability_id="application.approve", tenant_id="tenant-a",
                resource_id="app:workflow-1")
    base.update(kw)
    return base


def test_ladder_l4_principal_l2_grant_l4_capability_denies():
    auth, grants = _ladder_stack("L4")
    grants.issue(grant_id="g-low", principal_id="exec",
                 capability_id="application.approve", tenant_id="tenant-a",
                 authority_level="L2", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin")
    d = auth.authorize(_ladder_req())
    assert d["decision"] == "DENY"
    assert d["reason_code"] == "GRANT_AUTHORITY_INSUFFICIENT"


def test_ladder_l4_principal_l4_grant_l4_capability_allows():
    auth, grants = _ladder_stack("L4")
    grants.issue(grant_id="g-eq", principal_id="exec",
                 capability_id="application.approve", tenant_id="tenant-a",
                 authority_level="L4", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin")
    d = auth.authorize(_ladder_req())
    assert d["decision"] == "ALLOW"
    assert d["grant_id"] == "g-eq"
    # the sealed decision carries the full binding contract
    for field in ("request_id", "principal_id", "tenant_id", "project_id",
                  "capability_id", "resource_id", "decision",
                  "reason_code", "grant_id", "decision_timestamp",
                  "request_hash", "decision_id"):
        assert field in d, field


def test_ladder_malformed_grant_level_fails_closed():
    auth, grants = _ladder_stack("L4")
    grants.issue(grant_id="g-mal", principal_id="exec",
                 capability_id="application.approve", tenant_id="tenant-a",
                 authority_level="BROKEN", valid_from=T0,
                 expires_at=T_FAR, issued_by="admin")
    d = auth.authorize(_ladder_req())
    assert d["decision"] == "DENY"
    assert d["reason_code"] == "GRANT_AUTHORITY_INSUFFICIENT"
    # malformed CAPABILITY level must fail closed too
    auth.register_capability("weird.cap", required_level="NOT_A_LEVEL")
    grants.issue(grant_id="g-mal2", principal_id="exec",
                 capability_id="weird.cap", tenant_id="tenant-a",
                 authority_level="L4", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin")
    d = auth.authorize(_ladder_req(capability_id="weird.cap"))
    assert d["decision"] == "DENY"


def test_grant_above_principal_ceiling_cannot_authorize():
    # an L2 principal may meet an L2 capability personally, but an issued
    # L3 grant must never lift them past their own ceiling
    auth, grants = _ladder_stack("L2")
    auth.register_capability("application.review", required_level="L2")
    grants.issue(grant_id="g-over", principal_id="exec",
                 capability_id="application.review", tenant_id="tenant-a",
                 authority_level="L3", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin")
    d = auth.authorize(_ladder_req(capability_id="application.review"))
    assert d["decision"] == "DENY"
    assert d["reason_code"] == "GRANT_AUTHORITY_INSUFFICIENT"
