"""G0-B6-C9-C11 — Tool registry, gateway & MCP facade tests.

Required coverage (plan):
C9: unknown tool denied; version change requires review if side effects/
    schema change; tool cannot declare capability outside registry;
    disabled tool denied even if capability allowed.
C10: caller cannot override injected auth header; caller cannot redirect
    credential to attacker host; credential never appears in returned
    payload; capability/tool mismatch denied; external side effect requires
    side-effect capability.
C11: Personal cannot call CEO-only tool; CEO cannot discover hidden
    submission tool; no arbitrary DB query tool; task worker receives
    reduced tool manifest; request context propagation audited.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.security.authn import CredentialVault  # noqa: E402
from prototype.g0.security.authorization import (  # noqa: E402
    Authorizer,
    GrantRegistry,
)
from prototype.g0.security.identity import (  # noqa: E402
    PrincipalRegistry,
    ScopeEvaluator,
)
from prototype.g0.security.models import Principal  # noqa: E402
from prototype.g0.security.tool_gateway import (  # noqa: E402
    MCPFacade,
    ToolError,
    ToolGateway,
    ToolRegistry,
)

T_FAR = "2027-12-31T00:00:00+00:00"
T0 = "2026-08-26T00:00:00+00:00"


def _registry() -> ToolRegistry:
    reg = ToolRegistry()
    for cap in ("research.run", "client.read_approved_data",
                "application.draft_internal", "egress.send_external",
                "operational.state_bounded", "qa.run"):
        reg.approve_capability(cap)
    return reg


def _definition(**kw) -> dict:
    base = dict(tool_id="tool:search", version="1.0", provider="internal",
                description="search tool", capability_ids=["research.run"],
                side_effect_class="READ_ONLY", network_destinations=[],
                credential_requirements=[], read_write_class="READ",
                status="APPROVED_PRODUCTION")
    base.update(kw)
    return base


def _allow(cap: str = "research.run", **kw) -> dict:
    """REPAIR-01: no hand-built decisions — obtain a real, sealed ALLOW
    through the live authorizer chain."""
    stack = _authz_stack()
    req = dict(request_id=kw.pop("request_id", f"gw-{cap}"),
               principal_id=kw.pop("principal_id", "ceo"),
               capability_id=cap, tenant_id="tenant-a",
               resource_id="res:any")
    req.update(kw)
    d = stack.authorize(req)
    assert d["decision"] == "ALLOW", d
    return d


_AUTHZ_STACK_CACHE: list = []


def _authz_stack() -> Authorizer:
    if _AUTHZ_STACK_CACHE:
        return _AUTHZ_STACK_CACHE[0]
    principals = PrincipalRegistry()
    scope = ScopeEvaluator()
    grants = GrantRegistry()
    principals.register(
        Principal(principal_id="ceo", principal_type="HERMES_CEO",
                  subject_id="ceo-1", status="ACTIVE",
                  authentication_method="SERVICE_TOKEN",
                  tenant_memberships=["tenant-a"], created_at=T0,
                  credential_class="VAULT_REF", authority_level="L3"))
    scope.add_membership(membership_id="m-gw", tenant_id="tenant-a",
                         principal_id="ceo", role_ids=["ADMIN"],
                         valid_from=T0, valid_to=T_FAR)
    scope.register_public_resource("res:any")
    authz = Authorizer(principals=principals, scope=scope, grants=grants)
    for cap in ("research.run", "client.read_approved_data",
                "application.draft_internal", "egress.send_external",
                "operational.state_bounded", "qa.run"):
        authz.register_capability(cap, required_level="L0")
        grants.issue(grant_id=f"g-gw-{cap}", principal_id="ceo",
                     capability_id=cap, tenant_id="tenant-a",
                     authority_level="L3", valid_from=T0,
                     expires_at=T_FAR, issued_by="admin")
    _AUTHZ_STACK_CACHE.append(authz)
    return authz


def _vault(ref_id: str = "cred:search", cap: str = "research.run") -> \
        CredentialVault:
    vault = CredentialVault()
    vault.store(ref_id=ref_id, provider="API_KEY", tenant_id="tenant-a",
                owner="svc-tool-gateway", allowed_capabilities=[cap],
                allowed_destinations=["https://api.example"], expires_at=T_FAR,
                raw_secret="secret-search-key")
    return vault


def test_unknown_tool_denied():
    reg = _registry()
    gateway = ToolGateway(reg)
    with pytest.raises(ToolError):
        gateway.dispatch(tool_id="tool:ghost", request_body={},
                         authorization_decision=_allow(), actor="ceo")


def test_version_change_requires_review():
    reg = _registry()
    reg.register(_definition())
    with pytest.raises(ToolError):
        reg.register(_definition(version="2.0", side_effect_class="EXTERNAL_SEND"))
    ok = reg.register(_definition(version="2.0",
                                  side_effect_class="EXTERNAL_SEND"),
                      reviewed=True)
    assert ok["version"] == "2.0"


def test_tool_cannot_declare_capability_outside_registry():
    reg = _registry()
    with pytest.raises(ToolError):
        reg.register(_definition(capability_ids=["cap:never-registered"]))


def test_disabled_tool_denied_even_if_capability_allowed():
    reg = _registry()
    reg.register(_definition(status="DISABLED"))
    gateway = ToolGateway(reg)
    with pytest.raises(ToolError):
        gateway.dispatch(tool_id="tool:search", request_body={},
                         authorization_decision=_allow(), actor="ceo")


def test_discovered_tool_not_auto_authorized():
    reg = _registry()
    with pytest.raises(ToolError):
        reg.register(_definition(discovered=True,
                                 status="APPROVED_PRODUCTION"))
    ok = reg.register(_definition(discovered=True, status="EXPERIMENTAL"))
    assert ok["status"] == "EXPERIMENTAL"


def test_caller_cannot_override_injected_auth_header():
    reg = _registry()
    reg.register(_definition(network_destinations=["https://api.example"]))
    gateway = ToolGateway(reg)
    vault = _vault()
    with pytest.raises(ToolError):
        gateway.dispatch(
            tool_id="tool:search",
            request_body={"headers": {"Authorization": "Bearer attacker"},
                          "destination": "https://api.example",
                          "request_id": "r1"},
            authorization_decision=_allow(), actor="ceo",
            credential_ref_id="cred:search", vault=vault, tenant_id="tenant-a")


def test_caller_cannot_redirect_credential_to_attacker_host():
    reg = _registry()
    reg.register(_definition(network_destinations=["https://api.example"]))
    gateway = ToolGateway(reg)
    vault = _vault()
    with pytest.raises(ToolError):
        gateway.dispatch(
            tool_id="tool:search",
            request_body={"destination": "https://evil.example"},
            authorization_decision=_allow(), actor="ceo",
            credential_ref_id="cred:search", vault=vault, tenant_id="tenant-a")


def test_credential_never_appears_in_returned_payload():
    reg = _registry()
    reg.register(_definition(network_destinations=["https://api.example"]))
    gateway = ToolGateway(reg)
    vault = _vault()
    result = gateway.dispatch(
        tool_id="tool:search",
        request_body={"destination": "https://api.example",
                      "request_id": "r1"},
        authorization_decision=_allow(request_id="r1"), actor="ceo",
        credential_ref_id="cred:search", vault=vault, tenant_id="tenant-a")
    assert "secret-search-key" not in str(result)


def test_capability_tool_mismatch_denied():
    reg = _registry()
    reg.register(_definition())
    gateway = ToolGateway(reg)
    with pytest.raises(ToolError):
        gateway.dispatch(tool_id="tool:search", request_body={},
                         authorization_decision=_allow(
                             cap="client.read_approved_data"),
                         actor="ceo")


def test_external_side_effect_requires_side_effect_capability():
    reg = _registry()
    reg.register(_definition(side_effect_class="EXTERNAL_SEND",
                             network_destinations=["https://api.example"]))
    gateway = ToolGateway(reg)
    with pytest.raises(ToolError):
        gateway.dispatch(
            tool_id="tool:search",
            request_body={"destination": "https://api.example"},
            authorization_decision=_allow(cap="research.run"), actor="ceo")


def test_denied_decision_not_bypassed():
    reg = _registry()
    reg.register(_definition())
    gateway = ToolGateway(reg)
    with pytest.raises(ToolError):
        gateway.dispatch(tool_id="tool:search", request_body={},
                         authorization_decision={
                             "decision": "DENY",
                             "reason_code": "GRANT_MISSING"},
                         actor="ceo")


def test_personal_cannot_call_ceo_only_tool():
    reg = _registry()
    reg.register(_definition(tool_id="tool:qa",
                             capability_ids=["qa.run"]))
    facade = MCPFacade(reg)
    facade.bind_tool("tool:search", ["research.run"])
    facade.bind_tool("tool:qa", ["qa.run"])
    personal = facade.surface_for("PERSONAL_HERMES")
    assert "tool:qa" not in personal
    ceo = facade.surface_for("CEO_HERMES")
    assert "tool:qa" in ceo


def test_ceo_cannot_discover_hidden_submission_tool():
    reg = _registry()
    reg.approve_capability("submission.execute")
    reg.register(_definition(tool_id="tool:submit",
                             capability_ids=["submission.execute"],
                             side_effect_class="EXTERNAL_SUBMIT"))
    facade = MCPFacade(reg)
    facade.bind_tool("tool:submit", ["submission.execute"])
    with pytest.raises(ToolError):
        facade.discover("tool:submit")


def test_no_arbitrary_db_query_tool():
    reg = _registry()
    reg.approve_capability("database.query_arbitrary")
    reg.register(_definition(tool_id="tool:db",
                             capability_ids=["database.query_arbitrary"]))
    facade = MCPFacade(reg)
    facade.bind_tool("tool:db", ["database.query_arbitrary"])
    with pytest.raises(ToolError):
        facade.discover("tool:db")


def test_worker_receives_reduced_manifest():
    reg = _registry()
    reg.register(_definition(tool_id="tool:state",
                             capability_ids=["operational.state_bounded"],
                             side_effect_class="INTERNAL_MUTATION"))
    reg.register(_definition(tool_id="tool:research",
                             capability_ids=["research.run"]))
    facade = MCPFacade(reg)
    facade.bind_tool("tool:state", ["operational.state_bounded"])
    facade.bind_tool("tool:research", ["research.run"])
    worker = facade.surface_for("WORKER")
    assert "tool:research" in worker
    assert "tool:state" not in worker  # reduced: no operational state


def test_request_context_propagation_audited():
    reg = _registry()
    reg.register(_definition())
    gateway = ToolGateway(reg)
    gateway.dispatch(tool_id="tool:search",
                     request_body={"request_id": "req-42"},
                     authorization_decision=_allow(request_id="req-42"),
                     actor="ceo")
    trail = gateway.audit_trail()
    assert trail and trail[0]["request_id"] == "req-42"
    assert trail[0]["actor"] == "ceo"
    assert trail[0]["capability_id"] == "research.run"
    assert trail[0]["decision_id"] == \
        gateway.audit_trail()[0]["decision_id"]
