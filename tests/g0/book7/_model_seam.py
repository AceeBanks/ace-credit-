"""G0-B7-PHASE-B — governed model runtime seam harness.

Builds the REAL production chain with no mocked decisions:

    PrincipalRegistry → GrantRegistry → Authorizer
    → AuthorizationDecision (registry-sealed) → ModelGateway
    → ProviderProfileRegistry → provider adapter

Attack scenarios A..O (mission §13) live in test_model_runtime.py.
"""
from __future__ import annotations

import itertools

from prototype.g0.model.adapters import FakeAdapter
from prototype.g0.model.gateway import (
    DevRuntimeCredentialResolver,
    ModelGateway,
    ProviderProfileRegistry,
)
from prototype.g0.security.authorization import Authorizer, GrantRegistry
from prototype.g0.security.identity import PrincipalRegistry, ScopeEvaluator
from prototype.g0.security.models import Principal

T0 = "2026-08-26T00:00:00+00:00"
T_FAR = "2027-12-31T00:00:00+00:00"

_ids = itertools.count(1)


def _principal(principal_id, ptype, level,
               parent_task_id=None) -> Principal:
    return Principal(principal_id=principal_id, principal_type=ptype,
                     subject_id=f"{principal_id}-1", status="ACTIVE",
                     authentication_method="SERVICE_TOKEN",
                     tenant_memberships=["tenant-a"], created_at=T0,
                     credential_class="VAULT_REF", authority_level=level,
                     parent_task_id=parent_task_id)


class ModelSeamStack:
    """A fully wired authorizer↔model-gateway stack over one tenant."""

    def __init__(self, credential_resolver=None,
                 policy: dict | None = None,
                 profiles_policy: dict | None = None) -> None:
        self.principals = PrincipalRegistry()
        self.scope = ScopeEvaluator()
        self.grants = GrantRegistry()
        self.authz = Authorizer(principals=self.principals,
                                scope=self.scope, grants=self.grants)

        self.principals.register(_principal("ceo", "HERMES_CEO", "L3"))
        self.principals.register(_principal("worker-a", "WORKER_AGENT",
                                            "L1", parent_task_id="task-w"))
        self.principals.register(_principal("personal", "HERMES_PERSONAL",
                                            "L2"))

        for pid in ("ceo", "worker-a", "personal"):
            self.scope.add_membership(membership_id=f"m-{pid}",
                                      tenant_id="tenant-a",
                                      principal_id=pid,
                                      role_ids=["MEMBER"],
                                      valid_from=T0, valid_to=T_FAR)

        self.scope.register_resource("res:model-a", "tenant-a",
                                     project_id="proj-a")
        self.scope.register_resource("res:model-b", "tenant-a",
                                     project_id="proj-b")

        self.authz.register_capability("model.invoke", required_level="L1")
        self.authz.register_capability("submission.execute",
                                       required_level="L5", enabled=False)
        self.authz.allow_egress_destination("https://openrouter.ai")

        self.profiles = ProviderProfileRegistry(policy=profiles_policy)
        self.gateway = ModelGateway(
            self.profiles, policy=policy,
            decisions=self.authz.decisions,
            credential_resolver=credential_resolver
            or DevRuntimeCredentialResolver())
        self.gateway.register_adapter("openrouter",
                                      FakeAdapter(output_text="OK"))
        self._grant_seq = itertools.count(1)

    def grant_model(self, *, principal_id: str = "ceo",
                    project_id: str | None = None,
                    authority_level: str | None = None,
                    parent_ceiling: str | None = None,
                    expires_at: str = T_FAR) -> dict:
        default_level = {"worker-a": "L1", "personal": "L2", "ceo": "L3"}[
            principal_id]
        return self.grants.issue(
            grant_id=f"g{next(self._grant_seq)}",
            principal_id=principal_id, capability_id="model.invoke",
            tenant_id="tenant-a",
            authority_level=authority_level or default_level,
            valid_from=T0, expires_at=expires_at, issued_by="admin",
            project_id=project_id,
            resource_constraints=[],
            parent_ceiling=parent_ceiling)

    def request(self, *, model_request_id: str | None = None,
                request_id: str | None = None,
                principal_id: str = "ceo",
                project_id: str | None = "proj-a",
                resource_id: str | None = "res:model-a",
                provider_profile_id: str = "pp_openrouter_dev",
                model_id: str = "openai/gpt-4o-mini",
                purpose: str = "grant_drafting",
                messages: list | None = None,
                destination: str | None = "https://openrouter.ai",
                **extra) -> dict:
        req = dict(
            model_request_id=model_request_id or f"m{next(_ids)}",
            request_id=request_id or f"r{next(_ids)}",
            tenant_id="tenant-a", project_id=project_id,
            principal_id=principal_id, task_id="task-w",
            capability_id="model.invoke",
            provider_profile_id=provider_profile_id, model_id=model_id,
            purpose=purpose,
            messages=messages or [{"role": "user", "content": "draft"}],
            created_at=T0)
        if resource_id is not None:
            req["resource_id"] = resource_id
        if destination is not None:
            req["destination"] = destination
        req.update(extra)
        return req

    def decision(self, model_request: dict) -> dict:
        """PDP-issue the decision for this exact request context."""
        return self.authz.authorize(model_request, now=T_FAR)

    def invoke(self, model_request: dict,
               decision: dict | None = None) -> dict:
        """Full chain: authorize → gateway. Returns the ModelResponse.
        Raises on any DENY path (ModelError / AuthorizationError)."""
        decision = decision or self.decision(model_request)
        principal = self.principals.get(model_request["principal_id"])
        return self.gateway.invoke(
            model_request=model_request, authorization_decision=decision,
            actor=model_request["principal_id"],
            principal_type=principal.principal_type,
            tenant_id=model_request["tenant_id"],
            project_id=model_request.get("project_id"),
            resource_id=model_request.get("resource_id"))

    def allow(self, **req_kwargs) -> dict:
        """Authorize + invoke expecting success."""
        req = self.request(**req_kwargs)
        return self.invoke(req)
