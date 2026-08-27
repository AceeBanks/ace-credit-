"""G0-B6-REPAIR-01 — End-to-end seam attacks A..N.

Every scenario runs the real chain — PrincipalRegistry → GrantRegistry →
Authorizer (+ ApprovalRegistry) → ToolGateway — and obtains ALLOWs only
from live Authorizer output. No AuthorizationDecision is ever hand-built,
except where the scenario deliberately tampers with a genuine one.

Scenarios:
A  research ALLOW reused for application mutation
B  ALLOW reused for a different tool (other capability)
C  ALLOW reused for a different tenant
D  ALLOW reused for a different project
E  ALLOW reused for a different resource
F  expired grant
G  lower-authority grant
H  revoked approval
I  approval for previous resource version
J  worker Project A reaches Project B (same tenant)
K  missing capability in decision
L  forged granted capability in caller-created dict
M  replay of ALLOW decision
N  submission remains impossible
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from datetime import datetime, timedelta, timezone  # noqa: E402

from prototype.g0.security.authorization import (  # noqa: E402
    AuthorizationError,
    compute_decision_id,
)
from prototype.g0.security.models import Principal  # noqa: E402
from prototype.g0.security.tool_gateway import ToolError  # noqa: E402

from tests.g0.book6._seam import T_FAR, T0, SeamStack  # noqa: E402

_SND_DEST = ["https://api.example.com"]


def _fresh(*, bound_research: bool = True) -> SeamStack:
    s = SeamStack()
    s.grant("research.run", project="proj-a" if bound_research else None)
    s.register_tool("tool.research", ["research.run"])
    s.register_tool("tool.app.mutate",
                    ["application.move_workflow_state"],
                    side_effect_class="INTERNAL_MUTATION")
    return s


def _research_allow(s: SeamStack) -> dict:
    d = s.authz.authorize(s.request(
        "research.run", resource_id="res:research-a", project_id="proj-a"))
    assert d["decision"] == "ALLOW", d
    return d


# ------------------------------------------------------------------ A / B

def test_a_research_allow_cannot_drive_application_mutation():
    s = _fresh()
    allow = _research_allow(s)
    # the sealed decision binds research.run; the mutation tool declares a
    # different capability, so the gateway must refuse regardless of who asks
    with pytest.raises(ToolError):
        s.dispatch("tool.app.mutate", allow, resource_id="res:app-b",
                   project_id="proj-b")


def test_b_allow_not_portable_to_tool_with_other_capability():
    s = _fresh()
    allow = _research_allow(s)
    s.register_tool("tool.archive", ["application.move_workflow_state"],
                    side_effect_class="INTERNAL_MUTATION")
    with pytest.raises(ToolError):  # even when registry issuance verifies,
        # the capability/tool declaration check denies
        s.dispatch("tool.archive", allow, resource_id="res:app-b",
                   project_id="proj-b")


# ------------------------------------------------------------------ C/D/E

def test_c_allow_reused_for_different_tenant_denied():
    s = _fresh(bound_research=False)
    allow = _research_allow(s)
    with pytest.raises(ToolError):
        s.dispatch("tool.research", allow, tenant_id="tenant-b",
                   resource_id="res:research-a")


def test_d_allow_reused_for_different_project_denied():
    s = _fresh()
    allow = _research_allow(s)
    with pytest.raises(ToolError):
        s.dispatch("tool.research", allow, project_id="proj-b",
                   resource_id="res:research-a")


def test_e_allow_reused_for_different_resource_denied():
    s = _fresh(bound_research=False)
    allow = _research_allow(s)
    with pytest.raises(ToolError):
        s.dispatch("tool.research", allow, project_id="proj-a",
                   resource_id="res:research-a2")


def test_e2_allow_request_id_rebinding_denied():
    s = _fresh(bound_research=False)
    allow = _research_allow(s)
    with pytest.raises(ToolError):  # attacker swaps the request id too
        s.dispatch("tool.research", allow, body={"request_id": "r-other"},
                   project_id="proj-a", resource_id="res:research-a")


# ------------------------------------------------------------------ F / G

def test_f_expired_grant_produces_no_usable_allow():
    s = _fresh()
    s.grant("qa.factuality", expires_at="2026-08-27T00:00:00+00:00")
    later = "2026-08-27T01:00:00+00:00"
    d = s.authz.authorize(
        s.request("qa.factuality", resource_id="res:research-a",
                  project_id="proj-a"), now=later)
    assert d["decision"] == "DENY"
    assert d["reason_code"] == "GRANT_EXPIRED"
    allows = [x for x in s.authz.decisions.lookup_all()
              if x.get("capability_id") == "qa.factuality"
              and x["decision"] == "ALLOW"]
    assert allows == []


def test_f2_stale_presented_allow_rejected_by_gateway_freshness_bound():
    """An ALLOW minted at a backdated PDP-time cannot ride an old clock past
    the gateway's freshness window."""
    s = _fresh(bound_research=False)
    old_now = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    d = s.authz.authorize(
        s.request("research.run", resource_id="res:research-a",
                  project_id="proj-a"), now=old_now)
    assert d["decision"] == "ALLOW"
    s.gateway.max_decision_age_seconds = 60.0
    with pytest.raises(ToolError):
        s.dispatch("tool.research", d)


def test_g_lower_authority_grant_denied_end_to_end():
    s = _fresh(bound_research=False)
    # the principal itself meets the L2 requirement, so only the GRANT
    # ladder must deny; the delegation ceiling is L2 but the granted level
    # sits below the capability requirement
    s.principals.register(
        Principal(principal_id="worker-low", principal_type="WORKER_AGENT",
                  subject_id="worker-low-1", status="ACTIVE",
                  authentication_method="SERVICE_TOKEN",
                  tenant_memberships=["tenant-a"], created_at=T0,
                  authority_level="L2"))
    s.scope.add_membership(membership_id="m-worker-low",
                           tenant_id="tenant-a", principal_id="worker-low",
                           role_ids=["MEMBER"], valid_from=T0,
                           valid_to=T_FAR)
    s.grants.issue(grant_id="g-lower", principal_id="worker-low",
                   capability_id="qa.factuality", tenant_id="tenant-a",
                   authority_level="L1", valid_from=T0, expires_at=T_FAR,
                   issued_by="admin", project_id="proj-a",
                   parent_ceiling="L2")
    d = s.authz.authorize(s.request("qa.factuality",
                                    principal_id="worker-low",
                                    resource_id="res:research-a",
                                    project_id="proj-a"))
    assert d["decision"] == "DENY"
    assert d["reason_code"] == "GRANT_AUTHORITY_INSUFFICIENT"
    # and no ALLOW for worker-low+qa.factuality exists anywhere
    assert not [x for x in s.authz.decisions.lookup_all()
                if x.get("principal_id") == "worker-low"
                and x["decision"] == "ALLOW"]


# ------------------------------------------------------------- H / I / J

def _approval_stack() -> tuple[SeamStack, dict]:
    s = _fresh(bound_research=False)
    s.grant("egress.send_external", project=None)
    # the outbound queue is a tenant-wide (unprojected) resource
    s.scope.register_resource("res:send-queue", "tenant-a")
    s.register_tool("email.send", ["egress.send_external"],
                    side_effect_class="EXTERNAL_SEND",
                    destinations=_SND_DEST)
    s.authz.allow_egress_destination(_SND_DEST[0])
    return s, dict(capability_id="egress.send_external",
                   resource_id="res:send-queue",
                   requested_side_effect="EXTERNAL_SEND")


def test_h_revoked_approval_yields_no_allow():
    s, base = _approval_stack()
    denied = s.authz.authorize(s.request(**base))
    assert denied["decision"] == "REQUIRE_APPROVAL"

    s.approvals.record_from_ux(
        approval_id="ap-h", principal_id="ceo", tenant_id="tenant-a",
        capability_id="egress.send_external", resource_id="res:send-queue",
        resource_version="", action="EXTERNAL_SEND", approval_class="AP2",
        expires_at=T_FAR)
    ok_req = dict(base, approval_refs=["ap-h"])
    allowed = s.authz.authorize(s.request(**ok_req))
    assert allowed["decision"] == "ALLOW"
    assert allowed.get("approval_ref") == "ap-h"

    s.approvals.revoke("ap-h")
    r = s.authz.authorize(s.request(**dict(base, approval_refs=["ap-h"])))
    assert r["decision"] != "ALLOW"


def test_i_previous_version_approval_cannot_authorize_new_version():
    s, base = _approval_stack()
    v1 = dict(base, resource_version="v1", approval_refs=["ap-i"])
    s.approvals.record_from_ux(
        approval_id="ap-i", principal_id="ceo", tenant_id="tenant-a",
        capability_id="egress.send_external", resource_id="res:send-queue",
        resource_version="v1", action="EXTERNAL_SEND", approval_class="AP2",
        expires_at=T_FAR)
    ok = s.authz.authorize(s.request(**v1))
    assert ok["decision"] == "ALLOW"

    stale = dict(base, resource_version="v2", approval_refs=["ap-i"])
    d = s.authz.authorize(s.request(**stale))
    assert d["decision"] == "REQUIRE_APPROVAL"


def test_j_worker_project_a_cannot_reach_project_b_same_tenant():
    s = _fresh()
    # the worker holds a delegable, correctly-bound Project A research grant
    s.grant("research.run", principal_id="worker-a", project_id="proj-a",
            parent_ceiling="L1")
    d = s.authz.authorize(s.request("research.run",
                                    principal_id="worker-a",
                                    resource_id="res:app-b",
                                    project_id="proj-b"))
    assert d["decision"] == "DENY"
    assert d["reason_code"] == "PROJECT_DENIED"
    # omitting the project does not help either (fail closed)
    d2 = s.authz.authorize(s.request("research.run",
                                     principal_id="worker-a",
                                     resource_id="res:app-b"))
    assert d2["decision"] == "DENY"
    # and the bound grant still works inside its own project
    d3 = s.authz.authorize(s.request("research.run",
                                     principal_id="worker-a",
                                     resource_id="res:research-a",
                                     project_id="proj-a"))
    assert d3["decision"] == "ALLOW"


# ------------------------------------------------------------ K / L / M

def test_k_missing_capability_in_decision_denied():
    s = _fresh()
    genuine = _research_allow(s)
    mutilated = {k: v for k, v in genuine.items() if k != "capability_id"}
    # isolated gateway without a registry: the mandatory-capability contract
    # still denies structurally incomplete decisions
    s.gateway.decisions = None
    with pytest.raises(ToolError):
        s.gateway.dispatch(tool_id="tool.research",
                           request_body={"request_id":
                                         genuine["request_id"]},
                           authorization_decision=mutilated, actor="ceo")


def test_l_forged_capability_in_caller_created_dict_denied():
    s = _fresh()
    forged = {"request_id": "forged-r1", "principal_id": "ceo",
              "tenant_id": "tenant-a", "project_id": "proj-a",
              "resource_id": "res:app-b", "decision": "ALLOW",
              "reason_code": "ALLOW", "grant_id": None,
              "decision_timestamp": "2026-08-27T00:00:00+00:00",
              "request_hash": "deadbeefdeadbeefdeadbeefdeadbeef",
              "capability_id": "application.move_workflow_state"}
    forged["decision_id"] = compute_decision_id(forged)  # re-sealed forgery
    with pytest.raises(ToolError):  # never issued by this PDP
        s.dispatch("tool.app.mutate", forged, resource_id="res:app-b",
                   project_id="proj-b")


def test_m_replay_of_external_send_blocked():
    s, base = _approval_stack()
    s.approvals.record_from_ux(
        approval_id="ap-m", principal_id="ceo", tenant_id="tenant-a",
        capability_id="egress.send_external", resource_id="res:send-queue",
        resource_version="", action="EXTERNAL_SEND", approval_class="AP2",
        expires_at=T_FAR)
    req = dict(base, approval_refs=["ap-m"])
    allow = s.authz.authorize(s.request(request_id="req-m-41", **req))
    assert allow["decision"] == "ALLOW"
    body = {"request_id": "req-m-41", "destination": _SND_DEST[0]}
    sent = s.dispatch("email.send", allow, body=dict(body),
                      resource_id="res:send-queue")
    assert sent["status"] == "OK"
    with pytest.raises(ToolError):  # replaying the same ALLOW + request
        s.dispatch("email.send", allow, body=dict(body),
                   resource_id="res:send-queue")


# -------------------------------------------------------------------- N

def test_n_submission_remains_impossible():
    from prototype.g0.security.authorization import GrantRegistry as GR
    s = _fresh()

    # 1) the capability can never be granted (phase-disabled, GRANT-005)
    with pytest.raises(AuthorizationError):
        s.grants.issue(grant_id="g-sub", principal_id="ceo",
                       capability_id="submission.execute",
                       tenant_id="tenant-a", authority_level="L3",
                       valid_from=T0, expires_at=T_FAR, issued_by="admin")

    # 2) no authorization pathway reaches ALLOW for submission
    s.authz.register_capability("submission.execute", required_level="L3")
    d = s.authz.authorize(s.request("submission.execute",
                                    requested_side_effect="SUBMIT",
                                    resource_id="res:app-b",
                                    project_id="proj-b"))
    assert d["decision"] != "ALLOW"

    # 3) even a fully resealed caller-forged submission decision fails at
    #    the registry-wired gateway (not issued by this PDP), and hidden
    #    tools stay undiscoverable
    forged = {"request_id": "forge-sub", "principal_id": "ceo",
              "tenant_id": "tenant-a", "project_id": "proj-b",
              "resource_id": "res:app-b", "decision": "ALLOW",
              "reason_code": "ALLOW", "grant_id": None,
              "decision_timestamp": "2026-08-27T00:00:00+00:00",
              "request_hash": "cafecafecafecafecafecafecafe"}
    forged["decision_id"] = compute_decision_id(forged)
    s.tools.approve_capability("submission.execute")
    s.tools.register(dict(tool_id="submission.tool", version="1.0",
                          status="APPROVED_PRODUCTION",
                          side_effect_class="EXTERNAL_SUBMIT",
                          capability_ids=["submission.execute"]),
                     reviewed=True)
    with pytest.raises(ToolError):
        s.dispatch("submission.tool", forged, resource_id="res:app-b",
                   project_id="proj-b")

    from prototype.g0.security.tool_gateway import MCPFacade
    facade = MCPFacade(s.tools)
    facade.bind_tool("submission.tool", ["submission.execute"])
    with pytest.raises(ToolError):
        facade.discover("submission.tool")
