"""G0-B6-REPAIR-01 — end-to-end authorization→tool seam harness.

Builds the REAL production chain with no mocked decisions:

    PrincipalRegistry → GrantRegistry → Authorizer (+ ApprovalRegistry)
    → AuthorizationDecision (registry-sealed) → ToolGateway

Every test using this harness obtains ALLOWs only by executing the chain.
Attack scenarios A..N (REPAIR-01 item 7) live in
tests/g0/book6/test_authorizer_gateway_e2e.py.
"""
from __future__ import annotations

import itertools

from prototype.g0.security.approvals_audit import ApprovalRegistry
from prototype.g0.security.authorization import Authorizer, GrantRegistry
from prototype.g0.security.identity import PrincipalRegistry, ScopeEvaluator
from prototype.g0.security.models import Principal
from prototype.g0.security.tool_gateway import ToolGateway, ToolRegistry

T0 = "2026-08-26T00:00:00+00:00"
T_FAR = "2027-12-31T00:00:00+00:00"
T_PAST = "2026-01-01T00:00:00+00:00"

_ids = itertools.count(1)


def _principal(principal_id, ptype, level,
               parent_task_id=None) -> Principal:
    return Principal(principal_id=principal_id, principal_type=ptype,
                     subject_id=f"{principal_id}-1", status="ACTIVE",
                     authentication_method="SERVICE_TOKEN",
                     tenant_memberships=["tenant-a"], created_at=T0,
                     credential_class="VAULT_REF", authority_level=level,
                     parent_task_id=parent_task_id)


class SeamStack:
    """A fully wired authorizer↔gateway stack over one tenant."""

    def __init__(self) -> None:
        self.principals = PrincipalRegistry()
        self.scope = ScopeEvaluator()
        self.grants = GrantRegistry()
        self.approvals = ApprovalRegistry()

        self.principals.register(_principal("ceo", "HERMES_CEO", "L3"))
        self.principals.register(_principal("worker-a", "WORKER_AGENT",
                                            "L1", parent_task_id="task-w"))

        self.scope.add_membership(membership_id="m-ceo",
                                  tenant_id="tenant-a",
                                  principal_id="ceo", role_ids=["ADMIN"],
                                  valid_from=T0, valid_to=T_FAR)
        self.scope.add_membership(membership_id="m-worker-a",
                                  tenant_id="tenant-a",
                                  principal_id="worker-a",
                                  role_ids=["MEMBER"],
                                  valid_from=T0, valid_to=T_FAR)

        # structurally scoped resources across two projects of one tenant
        self.scope.register_resource("res:research-a", "tenant-a",
                                     project_id="proj-a")
        self.scope.register_resource("res:research-a2", "tenant-a",
                                     project_id="proj-a")
        self.scope.register_resource("res:app-b", "tenant-a",
                                     project_id="proj-b")

        self.authz = Authorizer(principals=self.principals,
                                scope=self.scope, grants=self.grants,
                                approvals=self.approvals)
        self.authz.register_capability("research.run", required_level="L1")
        self.authz.register_capability("qa.factuality", required_level="L2")
        self.authz.register_capability("application.move_workflow_state",
                                       required_level="L3")
        self.authz.register_capability("egress.send_external",
                                       required_level="L3")

        self.tools = ToolRegistry()
        for cap in ("research.run", "qa.factuality",
                    "application.move_workflow_state",
                    "egress.send_external"):
            self.tools.approve_capability(cap)
        self.gateway = ToolGateway(self.tools,
                                   decisions=self.authz.decisions)
        self._grant_seq = itertools.count(1)

    # -------------------------------------------------------------- tools

    def register_tool(self, tool_id: str, capability_ids: list[str],
                      side_effect_class: str = "READ_ONLY",
                      destinations: list[str] | None = None) -> dict:
        return self.tools.register(
            dict(tool_id=tool_id, version="1.0",
                 status="APPROVED_PRODUCTION",
                 side_effect_class=side_effect_class,
                 capability_ids=list(capability_ids),
                 network_destinations=list(destinations or [])),
            reviewed=True)

    # ------------------------------------------------------------- grants

    def grant(self, capability_id: str, *, principal_id: str = "ceo",
              authority_level: str | None = None,
              project_id: str | None = None,
              parent_ceiling: str | None = None,
              project: str | None = None,  # alias for readability
              valid_from: str = T0, expires_at: str = T_FAR,
              constraints: list[str] | None = None) -> dict:
        return self.grants.issue(
            grant_id=f"g{next(self._grant_seq)}",
            principal_id=principal_id, capability_id=capability_id,
            tenant_id="tenant-a",
            authority_level=authority_level or {"worker-a": "L1",
                                                "ceo": "L3"}[principal_id],
            valid_from=valid_from, expires_at=expires_at,
            issued_by="admin",
            project_id=(project if project is not None else project_id),
            resource_constraints=constraints or [],
            parent_ceiling=parent_ceiling)

    def request(self, capability_id: str, *, principal_id: str = "ceo",
                resource_id: str | None = None,
                project_id: str | None = None,
                request_id: str | None = None, **extra) -> dict:
        req = dict(request_id=request_id or f"r{next(_ids)}",
                   principal_id=principal_id,
                   capability_id=capability_id, tenant_id="tenant-a",
                   resource_id=resource_id, project_id=project_id)
        req.update(extra)
        return req

    # ------------------------------------------------------- tool surface

    def dispatch(self, tool_id: str, decision: dict, *,
                 actor: str = "ceo", body: dict | None = None,
                 tenant_id: str = "tenant-a", project_id: str | None = None,
                 resource_id: str | None = None,
                 credential_ref_id: str | None = None, vault=None) -> dict:
        return self.gateway.dispatch(
            tool_id=tool_id, request_body=dict(body or {}),
            authorization_decision=decision, actor=actor,
            credential_ref_id=credential_ref_id, vault=vault,
            tenant_id=tenant_id, project_id=project_id,
            resource_id=resource_id)
