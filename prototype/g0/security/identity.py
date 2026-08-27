"""G0-B6-C2/C3 — Principal & identity + tenant/resource isolation prototype.

Identity rules IDN-001..005: logical actor identity survives model swaps,
disabled principals cannot authorize, duplicates rejected, worker
principals bind to parent task without inherited authority, least personal
data. Tenant isolation: membership expiry enforced, cross-tenant artifact
reads denied, project-scoped workers cannot cross projects.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from prototype.g0.security.models import Principal


class IdentityError(ValueError):
    """Raised when identity or scope evaluation violates policy."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/security/"
                           "principal_policy.yaml").read_text(encoding="utf-8"))


_POLICY = _load_policy()


def _is_active(status: str) -> bool:
    return status == "ACTIVE"


class PrincipalRegistry:
    """Stable logical identity registry."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY
        self._principals: dict[str, Principal] = {}
        self._workload_map: dict[str, str] = {}  # model_ref -> principal_id

    def register(self, principal: Principal) -> Principal:
        if principal.principal_id in self._principals:
            raise IdentityError(
                f"duplicate principal id {principal.principal_id} (IDN-003)")
        if principal.principal_type not in self.policy["principal_types"]:
            raise IdentityError(
                f"unknown principal_type {principal.principal_type!r}")
        if principal.status not in self.policy["principal_statuses"]:
            raise IdentityError(f"unknown status {principal.status!r}")
        self._principals[principal.principal_id] = principal
        if principal.model_or_provider_ref:
            # IDN-001: one logical principal owns the model slot
            self._workload_map[principal.model_or_provider_ref] = \
                principal.principal_id
        return principal

    def get(self, principal_id: str) -> Principal:
        p = self._principals.get(principal_id)
        if p is None:
            raise IdentityError(f"unknown principal {principal_id}")
        return p

    def can_authorize(self, principal_id: str) -> bool:
        """IDN-002: disabled/deactivated principals cannot authorize."""
        try:
            return _is_active(self.get(principal_id).status)
        except IdentityError:
            return False

    def model_swap_preserves_identity(self, principal_id: str,
                                      new_model_ref: str) -> str:
        """IDN-001: swapping the model/provider keeps the logical principal."""
        p = self.get(principal_id)
        old_ref = p.model_or_provider_ref
        if old_ref in self._workload_map:
            del self._workload_map[old_ref]
        p.model_or_provider_ref = new_model_ref
        self._workload_map[new_model_ref] = principal_id
        return principal_id


class ScopeEvaluator:
    """C3 — tenant membership + resource scope evaluation."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY
        self._memberships: dict[str, dict] = {}
        self._resource_owners: dict[str, str] = {}  # legacy id -> tenant view
        # G0-B6-REPAIR-01 AUTH-R3: structural resource metadata
        self._resources: dict[str, dict] = {}

    def add_membership(self, *, membership_id: str, tenant_id: str,
                       principal_id: str, role_ids: list[str],
                       valid_from: str, valid_to: str,
                       status: str = "ACTIVE") -> dict:
        if status not in self.policy["membership_statuses"]:
            raise IdentityError(f"unknown membership status {status!r}")
        for role in role_ids:
            if role not in self.policy["tenant_membership_roles"]:
                raise IdentityError(f"unknown product role {role!r}")
        m = dict(membership_id=membership_id, tenant_id=tenant_id,
                 principal_id=principal_id, role_ids=list(role_ids),
                 status=status, valid_from=valid_from, valid_to=valid_to)
        self._memberships[membership_id] = m
        return m

    def membership_for(self, principal_id: str, tenant_id: str,
                       now: str | None = None) -> dict | None:
        now = now or _now()
        best = None
        for m in self._memberships.values():
            if m["principal_id"] != principal_id or m["tenant_id"] != tenant_id:
                continue
            if m["status"] != "ACTIVE":
                continue
            if m["valid_from"] > now or m["valid_to"] < now:
                continue  # expiry enforced
            best = m  # last matching active membership wins
        return best

    def owns_resource(self, resource_id: str) -> str:
        """Return the owning tenant of a resource (by registry)."""
        tenant = self._resource_owners.get(resource_id)
        if tenant is None:
            raise IdentityError(f"unknown resource {resource_id}")
        return tenant

    def register_resource(self, resource_id: str, tenant_id: str,
                          project_id: str | None = None) -> None:
        """Store resource scope metadata structurally (REPAIR-01):
        resource_id -> {tenant_id, project_id}."""
        self._resources[resource_id] = {
            "resource_id": resource_id, "tenant_id": tenant_id,
            "project_id": project_id}
        self._resource_owners[resource_id] = tenant_id
        if project_id:
            self._resource_owners[f"{resource_id}@{project_id}"] = tenant_id

    def resource_meta(self, resource_id: str) -> dict | None:
        meta = self._resources.get(resource_id)
        return dict(meta) if meta else None

    def project_of(self, resource_id: str) -> str | None:
        """Project binding of a registered resource; None when the resource
        is unknown or registered tenant-wide (no project constraint)."""
        meta = self._resources.get(resource_id)
        return meta["project_id"] if meta else None

    def project_scope_ok(self, *, resource_id: str,
                         request_project_id: str | None,
                         grant_project_id: str | None = None) -> bool:
        """AUTH-R3 helper: a project-scoped resource accepts only the
        matching explicit request project (grant binding may not substitute)."""
        res_project = self.project_of(resource_id)
        if res_project is None:
            return True  # tenant-wide resource carries no project constraint
        return bool(request_project_id) and \
            request_project_id == res_project

    def register_public_resource(self, resource_id: str) -> None:
        """Shared public source: reusable by any tenant while private
        annotations stay tenant-bound."""
        self._resource_owners[resource_id] = "__public__"

    def can_read(self, *, principal_id: str, resource_id: str,
                 resource_tenant: str, now: str | None = None) -> bool:
        """Tenant A member cannot read Tenant B artifacts by guessed ID;
        public sources are reusable by any active membership."""
        try:
            actual_tenant = self.owns_resource(resource_id)
        except IdentityError:
            return False
        if actual_tenant == "__public__":
            return True
        if actual_tenant != resource_tenant:
            return False
        return self.membership_for(principal_id, actual_tenant, now) is not None

    def worker_project_scope(self, *, principal_id: str,
                             assigned_project_id: str) -> list[str]:
        """A worker assigned Project A cannot access Project B by default."""
        allowed = []
        for rid, meta in self._resources.items():
            if meta["tenant_id"] == "__public__":
                continue
            if meta["project_id"] == assigned_project_id:
                allowed.append(rid)
        return allowed
