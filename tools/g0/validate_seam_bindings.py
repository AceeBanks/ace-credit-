#!/usr/bin/env python3
"""G0-B6-REPAIR-01 — seam-binding validators (live micro-flows).

Each probe runs the REAL seam end-to-end — PrincipalRegistry → GrantRegistry
→ Authorizer (→ ApprovalRegistry where required) → ToolGateway — against a
purpose-built attack. These are not assertions over constants: every probe
exercises production code paths and returns False if any control regresses.

Used by tools/g0/build_book6_reality_lock.py to derive the six REPAIR-01
predicates from executable evidence.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.security.approvals_audit import ApprovalRegistry  # noqa: E402
from prototype.g0.security.authorization import Authorizer  # noqa: E402
from prototype.g0.security.identity import PrincipalRegistry  # noqa: E402
from prototype.g0.security.identity import ScopeEvaluator  # noqa: E402
from prototype.g0.security.authorization import GrantRegistry  # noqa: E402
from prototype.g0.security.models import Principal  # noqa: E402
from prototype.g0.security.tool_gateway import ToolError  # noqa: E402
from prototype.g0.security.tool_gateway import ToolGateway  # noqa: E402
from prototype.g0.security.tool_gateway import ToolRegistry  # noqa: E402

T0 = "2026-08-26T00:00:00+00:00"
T_FAR = "2027-12-31T00:00:00+00:00"


def _principal(principal_id: str = "ceo", level: str = "L4",
               ptype: str = "HERMES_CEO") -> Principal:
    return Principal(principal_id=principal_id, principal_type=ptype,
                     subject_id=f"{principal_id}-1", status="ACTIVE",
                     authentication_method="SERVICE_TOKEN",
                     tenant_memberships=["tenant-a"], created_at=T0,
                     credential_class="VAULT_REF", authority_level=level)


def _stack(level: str = "L4") -> tuple[Authorizer, ScopeEvaluator,
                                       GrantRegistry]:
    principals = PrincipalRegistry()
    scope = ScopeEvaluator()
    grants = GrantRegistry()
    principals.register(_principal("ceo", level))
    scope.add_membership(membership_id="m1", tenant_id="tenant-a",
                         principal_id="ceo", role_ids=["ADMIN"],
                         valid_from=T0, valid_to=T_FAR)
    scope.register_resource("research:doc-a", "tenant-a", project_id="proj-a")
    scope.register_resource("application:wf-b", "tenant-a",
                            project_id="proj-b")
    authz = Authorizer(principals=principals, scope=scope, grants=grants)
    authz.register_capability("research.run", required_level="L4")
    authz.register_capability("application.mutate", required_level="L4")
    return authz, scope, grants


def _grant(authz_grants: GrantRegistry, cap: str, level: str,
           project: str | None = None, grant_id: str | None = None) -> dict:
    return authz_grants.issue(
        grant_id=grant_id or f"g-{cap}-{level}-{project or 'any'}",
        principal_id="ceo", capability_id=cap, tenant_id="tenant-a",
        authority_level=level, valid_from=T0, expires_at=T_FAR,
        issued_by="admin", project_id=project)


def _req(**kw):
    base = dict(request_id="rq-probe", principal_id="ceo",
                tenant_id="tenant-a")
    base.update(kw)
    return base


def probe_grant_authority_enforced() -> bool:
    """AUTH-R1: L2 grant cannot drive an L4 capability even for an L4
    principal; L4+L4+L4 allows; malformed levels deny."""
    try:
        authz, _, grants = _stack("L4")
        _grant(grants, "research.run", "L2")  # below the L4 requirement
        d = authz.authorize(_req(capability_id="research.run",
                                 resource_id="research:doc-a",
                                 project_id="proj-a"))
        if d["decision"] != "DENY" or \
                d["reason_code"] != "GRANT_AUTHORITY_INSUFFICIENT":
            return False

        authz2, _, grants2 = _stack("L4")
        _grant(grants2, "research.run", "L4")
        if authz2.authorize(_req(capability_id="research.run",
                                 resource_id="research:doc-a",
                                 project_id="proj-a"))["decision"] != "ALLOW":
            return False

        authz3, _, grants3 = _stack("L4")
        g = _grant(grants3, "research.run", "L4")
        g["authority_level"] = "MISC"  # malformed → must fail closed
        if authz3.authorize(_req(capability_id="research.run",
                                 resource_id="research:doc-a",
                                 project_id="proj-a"))["decision"] != "DENY":
            return False
        return True
    except Exception:
        return False


def probe_authorization_capability_binding() -> bool:
    """AUTH-R6/R8: missing decision capability denies; undeclared-by-tool
    capability denies; caller-forged dicts never verify."""
    try:
        reg = ToolRegistry()
        for cap in ("research.run", "application.mutate"):
            reg.approve_capability(cap)
        reg.register(dict(tool_id="tool.research", version="1.0",
                          status="APPROVED_PRODUCTION",
                          side_effect_class="READ_ONLY",
                          capability_ids=["research.run"]), reviewed=True)
        authz, _, grants = _stack()
        _grant(grants, "research.run", "L4", project=None)
        gw = ToolGateway(reg, decisions=authz.decisions)
        good = authz.authorize(_req(capability_id="research.run",
                                    resource_id="research:doc-a",
                                    project_id="proj-a"))
        if good["decision"] != "ALLOW":
            return False
        ok = gw.dispatch(tool_id="tool.research",
                         request_body={"request_id": "rq-probe"},
                         authorization_decision=good, actor="ceo",
                         tenant_id="tenant-a", project_id="proj-a",
                         resource_id="research:doc-a")

        # mandatory capability field: removing it must deny even when the
        # decision is otherwise intact
        missing = {k: v for k, v in good.items() if k != "capability_id"}
        try:
            gw.dispatch(tool_id="tool.research", request_body={},
                        authorization_decision=missing, actor="ceo")
            return False
        except ToolError:
            pass

        # forged caller-created dict: shape/integrity defeats tampering and
        # the registry defeats re-hashing
        forged = {"decision": "ALLOW", "reason_code": "ALLOW",
                  "request_id": "forged", "principal_id": "ceo",
                  "capability_id": "application.mutate"}
        try:
            gw.dispatch(tool_id="tool.research", request_body={},
                        authorization_decision=forged, actor="ceo")
            return False
        except ToolError:
            pass
        return ok.get("status") == "OK"
    except Exception:
        return False


def probe_authorization_resource_binding() -> bool:
    """AUTH-R7: an ALLOW for one resource/tenant cannot drive a dispatch
    bound to another resource or tenant."""
    try:
        reg = ToolRegistry()
        reg.approve_capability("research.run")
        reg.register(dict(tool_id="tool.research", version="1.0",
                          status="APPROVED_PRODUCTION",
                          side_effect_class="READ_ONLY",
                          capability_ids=["research.run"]), reviewed=True)
        authz, _, grants = _stack()
        _grant(grants, "research.run", "L4", project=None)
        gw = ToolGateway(reg, decisions=authz.decisions)
        allow_a = authz.authorize(_req(capability_id="research.run",
                                       resource_id="research:doc-a",
                                       project_id="proj-a"))
        if allow_a["decision"] != "ALLOW":
            return False
        try:  # reused for a different resource -> deny
            gw.dispatch(tool_id="tool.research",
                        request_body={"request_id": "rq-probe"},
                        authorization_decision=allow_a, actor="ceo",
                        tenant_id="tenant-a", project_id="proj-b",
                        resource_id="application:wf-b")
            return False
        except ToolError:
            pass
        try:  # reused for a different tenant -> deny
            gw.dispatch(tool_id="tool.research",
                        request_body={"request_id": "rq-probe"},
                        authorization_decision=allow_a, actor="ceo",
                        tenant_id="tenant-b", project_id="proj-a",
                        resource_id="research:doc-a")
            return False
        except ToolError:
            pass
        gw.dispatch(tool_id="tool.research",
                    request_body={"request_id": "rq-probe"},
                    authorization_decision=allow_a, actor="ceo",
                    tenant_id="tenant-a", project_id="proj-a",
                    resource_id="research:doc-a")
        return True
    except Exception:
        return False


def probe_project_scope() -> bool:
    """AUTH-R3/R5: same-tenant cross-project access is denied for a
    project-bound grant and for project-scoped resources."""
    try:
        authz, _, grants = _stack()
        _grant(grants, "research.run", "L4", project="proj-a")
        d = authz.authorize(_req(capability_id="research.run",
                                 resource_id="research:doc-a",
                                 project_id="proj-a"))
        if d["decision"] != "ALLOW":
            return False
        d2 = authz.authorize(_req(capability_id="research.run",
                                  resource_id="research:doc-a",
                                  project_id="proj-b"))
        if d2["decision"] != "DENY" or d2["reason_code"] != "PROJECT_DENIED":
            return False
        # project-scoped resource without an explicit request project denies
        _grant(grants, "application.mutate", "L4", project=None)
        d3 = authz.authorize(_req(capability_id="application.mutate",
                                  resource_id="application:wf-b"))
        if d3["decision"] != "DENY" or d3["reason_code"] != "PROJECT_DENIED":
            return False
        return True
    except Exception:
        return False


def probe_approval_registry_integration() -> bool:
    """AUTH-R4: approval-requiring operations validate ONLY through the
    ApprovalRegistry; validated refs bind into the ALLOW decision."""
    try:
        reg = ToolRegistry()
        reg.approve_capability("egress.send_external")
        reg.register(dict(tool_id="email.send", version="1.0",
                          status="APPROVED_PRODUCTION",
                          side_effect_class="EXTERNAL_SEND",
                          capability_ids=["egress.send_external"],
                          network_destinations=["https://api.example.com"]),
                     reviewed=True)
        principals = PrincipalRegistry()
        scope = ScopeEvaluator()
        grants = GrantRegistry()
        principals.register(_principal("ceo", "L3"))
        scope.add_membership(membership_id="m1", tenant_id="tenant-a",
                             principal_id="ceo", role_ids=["ADMIN"],
                             valid_from=T0, valid_to=T_FAR)
        scope.register_resource("msg:1", "tenant-a")
        approvals = ApprovalRegistry()
        authz = Authorizer(principals=principals, scope=scope,
                           grants=grants, approvals=approvals)
        authz.register_capability("egress.send_external", required_level="L3")
        authz.allow_egress_destination("https://api.example.com")
        _grant(grants, "egress.send_external", "L3")

        req = _req(capability_id="egress.send_external",
                   resource_id="msg:1",
                   destination="https://api.example.com",
                   requested_side_effect="EXTERNAL_SEND")
        d = authz.authorize(req)
        if d["decision"] != "REQUIRE_APPROVAL":
            return False

        approvals.record_from_ux(approval_id="appr-9", principal_id="ceo",
                                 tenant_id="tenant-a",
                                 capability_id="egress.send_external",
                                 resource_id="msg:1", resource_version="v1",
                                 action="EXTERNAL_SEND", approval_class="AP2",
                                 expires_at=T_FAR)
        req_ok = dict(req, request_id="rq-ok", approval_refs=["appr-9"],
                      resource_version="v1")
        allowed = authz.authorize(req_ok)
        if allowed["decision"] != "ALLOW" or \
                allowed.get("approval_ref") != "appr-9":
            return False

        gw = ToolGateway(reg, decisions=authz.decisions)
        body = {"request_id": "rq-ok",   # bound to the decision's request id
                "destination": "https://api.example.com"}
        sent = gw.dispatch(tool_id="email.send", request_body=dict(body),
                           authorization_decision=allowed, actor="ceo",
                           tenant_id="tenant-a", resource_id="msg:1")
        if sent.get("status") != "OK":
            return False

        approvals.revoke("appr-9")
        req_rv = dict(req, request_id="rq-rv", approval_refs=["appr-9"],
                      resource_version="v1")
        if authz.authorize(req_rv)["decision"] == "ALLOW":
            return False  # revoked approval can no longer allow

        # stale version: an approval recorded against v1 cannot authorize a
        # changed resource version (APPR-002 through the authorizer seam)
        approvals.record_from_ux(approval_id="appr-stale", principal_id="ceo",
                                 tenant_id="tenant-a",
                                 capability_id="egress.send_external",
                                 resource_id="msg:1", resource_version="v1",
                                 action="EXTERNAL_SEND", approval_class="AP2",
                                 expires_at=T_FAR)
        req_stale = dict(req, request_id="rq-stale",
                         approval_refs=["appr-stale"],
                         resource_version="v2")
        if authz.authorize(req_stale)["decision"] == "ALLOW":
            return False
        return True
    except Exception:
        return False


PROBES = {
    "grant_authority_enforced": probe_grant_authority_enforced,
    "authorization_capability_binding": probe_authorization_capability_binding,
    "authorization_resource_binding": probe_authorization_resource_binding,
    "project_scope": probe_project_scope,
    "approval_registry_integration": probe_approval_registry_integration,
}


def run_all() -> dict[str, bool]:
    out: dict[str, bool] = {}
    for name, fn in PROBES.items():
        try:
            out[name] = bool(fn())
        except Exception:
            out[name] = False
    return out


def main() -> int:
    results = run_all()
    failed = [k for k, v in results.items() if not v]
    for name, ok in results.items():
        print(f"{name}: {'OK' if ok else 'FAILED'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
