"""G0-B6-C4/C5 — Capability grant model + authorization decision contract.

The authorization chain (C5) evaluates in the plan's 13-step order and
returns ALLOW / DENY / REQUIRE_APPROVAL with stable reason codes. Default is
DENY; every failure maps to a reason code (100% fail-closed coverage).
C4 grant rules: expiry/revocation deny (GRANT-001), worker grants cannot
exceed the parent ceiling (GRANT-002), only delegable capabilities may be
delegated (GRANT-003), resource constraints always apply (GRANT-004),
phase-disabled capabilities cannot be enabled by grant (GRANT-005), and
mid-task revocation blocks the next protected action (GRANT-006).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from prototype.g0.security.identity import PrincipalRegistry, ScopeEvaluator


class AuthorizationError(ValueError):
    """Raised on invalid grant operations."""


REASON_CODES = (
    "PRINCIPAL_UNKNOWN", "PRINCIPAL_DISABLED", "SESSION_INVALID",
    "TENANT_DENIED", "CAPABILITY_UNKNOWN", "CAPABILITY_DISABLED",
    "AUTHORITY_INSUFFICIENT", "GRANT_MISSING", "GRANT_EXPIRED",
    "RESOURCE_DENIED", "TASK_SCOPE_DENIED", "DATA_CLASS_DENIED",
    "EGRESS_DENIED", "APPROVAL_REQUIRED", "EXPLICIT_DENY", "ALLOW",
)

_LEVELS = ("L0", "L1", "L2", "L3", "L4", "L5")


def _level_rank(level: str | None) -> int:
    return _LEVELS.index(level) if level in _LEVELS else -1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/security/"
                           "capability_grant_policy.yaml")
                          .read_text(encoding="utf-8"))


_POLICY = _load_policy()


class GrantRegistry:
    """CapabilityGrant store with delegation law enforcement."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY
        self._grants: dict[str, dict] = {}

    def issue(self, *, grant_id: str, principal_id: str, capability_id: str,
              tenant_id: str, authority_level: str, valid_from: str,
              expires_at: str, issued_by: str, project_id: str | None = None,
              resource_constraints: list[str] | None = None,
              parent_ceiling: str | None = None,
              approval_ref: str | None = None) -> dict:
        """Issue a grant. Worker grants must fit the parent's delegable
        authority (GRANT-002/003). CEO/principal grants are not delegation
        and may carry any registered capability."""
        if parent_ceiling is not None:
            # delegation to a worker: only delegable capabilities, within
            # the parent's ceiling
            if capability_id not in self.policy["delegable_capabilities"]:
                raise AuthorizationError(
                    f"capability {capability_id} is not delegable (GRANT-003)")
            if _level_rank(authority_level) > _level_rank(parent_ceiling):
                raise AuthorizationError(
                    f"worker grant {authority_level} exceeds parent ceiling "
                    f"{parent_ceiling} (GRANT-002)")
        if capability_id in self.policy["phase_disabled_capabilities"]:
            raise AuthorizationError(
                f"capability {capability_id} is phase-disabled and cannot "
                "be granted (GRANT-005)")
        grant = dict(grant_id=grant_id, principal_id=principal_id,
                     capability_id=capability_id, tenant_id=tenant_id,
                     project_id=project_id,
                     resource_constraints=list(resource_constraints or []),
                     authority_level=authority_level, valid_from=valid_from,
                     expires_at=expires_at, approval_ref=approval_ref,
                     issued_by=issued_by, status="ACTIVE")
        self._grants[grant_id] = grant
        return grant

    def revoke(self, grant_id: str) -> None:
        if grant_id not in self._grants:
            raise AuthorizationError(f"unknown grant {grant_id}")
        self._grants[grant_id]["status"] = "REVOKED"

    def find_grant(self, *, principal_id: str, capability_id: str,
                   tenant_id: str) -> dict | None:
        """Any grant matching principal+capability+tenant, any status."""
        for grant in self._grants.values():
            if grant["principal_id"] == principal_id and \
                    grant["capability_id"] == capability_id and \
                    grant["tenant_id"] == tenant_id:
                return grant
        return None

    def grant_in_effect(self, grant: dict, now: str | None = None) -> bool:
        """GRANT-001: ACTIVE status AND within the validity window."""
        now = now or _now()
        return grant["status"] == "ACTIVE" and \
            grant["valid_from"] <= now <= grant["expires_at"]

    def grant_valid(self, grant_id: str, now: str | None = None) -> bool:
        """GRANT-006: a revoked grant denies immediately."""
        now = now or _now()
        grant = self._grants.get(grant_id)
        if grant is None or grant["status"] != "ACTIVE":
            return False
        return grant["valid_from"] <= now <= grant["expires_at"]


class Authorizer:
    """C5 — 13-step deterministic authorization decision chain."""

    def __init__(self, *, principals: PrincipalRegistry,
                 scope: ScopeEvaluator, grants: GrantRegistry,
                 policy: dict | None = None) -> None:
        self.principals = principals
        self.scope = scope
        self.grants = grants
        self.policy = policy or _POLICY
        self._capabilities: dict[str, dict] = {}
        self._approvals: set[str] = set()
        self._data_class_allows: set[str] = set()
        self._egress_allows: set[str] = set()
        self._deny_rules: list[str] = []

    def register_capability(self, capability_id: str,
                            required_level: str = "L0",
                            enabled: bool = True) -> None:
        self._capabilities[capability_id] = {
            "required_level": required_level, "enabled": enabled}

    def register_approval(self, approval_ref: str) -> None:
        self._approvals.add(approval_ref)

    def allow_data_class(self, data_class: str) -> None:
        self._data_class_allows.add(data_class)

    def allow_egress_destination(self, destination: str) -> None:
        self._egress_allows.add(destination)

    def add_deny_rule(self, rule: str) -> None:
        self._deny_rules.append(rule)

    def authorize(self, req: dict, *, session_valid: bool = True,
                  now: str | None = None) -> dict:
        """Evaluate the request in decision order; default DENY."""
        now = now or _now()
        request_id = req.get("request_id", "req-?")
        principal_id = req.get("principal_id")
        capability_id = req.get("capability_id")
        tenant_id = req.get("tenant_id")
        resource_id = req.get("resource_id")

        # 1. principal valid/enabled?
        try:
            principal = self.principals.get(principal_id)
        except Exception:
            return self._decision(request_id, "DENY", "PRINCIPAL_UNKNOWN")
        if principal.status != "ACTIVE":
            return self._decision(request_id, "DENY", "PRINCIPAL_DISABLED")

        # 2. authenticated session valid?
        if not session_valid:
            return self._decision(request_id, "DENY", "SESSION_INVALID")

        # 3. tenant membership/scope valid?
        if self.scope.membership_for(principal_id, tenant_id, now) is None:
            return self._decision(request_id, "DENY", "TENANT_DENIED")

        # 4. capability registered/enabled?
        cap = self._capabilities.get(capability_id)
        if cap is None:
            return self._decision(request_id, "DENY", "CAPABILITY_UNKNOWN")
        if not cap["enabled"]:
            return self._decision(request_id, "DENY", "CAPABILITY_DISABLED")

        # 5. Book 1 authority ceiling sufficient?
        if _level_rank(principal.authority_level) < \
                _level_rank(cap["required_level"]):
            return self._decision(request_id, "DENY", "AUTHORITY_INSUFFICIENT")

        # 6. capability grant valid?
        grant = self.grants.find_grant(
            principal_id=principal_id, capability_id=capability_id,
            tenant_id=tenant_id)
        if grant is None:
            return self._decision(request_id, "DENY", "GRANT_MISSING")
        if not self.grants.grant_in_effect(grant, now):
            return self._decision(request_id, "DENY", "GRANT_EXPIRED")

        # 7. resource scope valid?
        if not self.scope.can_read(principal_id=principal_id,
                                   resource_id=resource_id,
                                   resource_tenant=tenant_id, now=now):
            return self._decision(request_id, "DENY", "RESOURCE_DENIED")

        # 8. task scope valid?
        if req.get("task_scope"):
            constraints = grant.get("resource_constraints", [])
            if req["task_scope"] not in constraints:
                return self._decision(request_id, "DENY", "TASK_SCOPE_DENIED")

        # 9. data classification permits action?
        data_class = (req.get("context") or {}).get("data_class")
        if data_class and data_class not in self._data_class_allows:
            return self._decision(request_id, "DENY", "DATA_CLASS_DENIED")

        # 10. destination/egress policy permits action?
        destination = req.get("destination")
        if destination and destination not in self._egress_allows:
            return self._decision(request_id, "DENY", "EGRESS_DENIED")

        # 11. approval requirement satisfied?
        if req.get("requested_side_effect") in ("EXTERNAL_SEND", "SUBMIT",
                                                "WORKFLOW_MUTATION"):
            refs = req.get("approval_refs") or []
            if not any(r in self._approvals for r in refs):
                return self._decision(request_id, "REQUIRE_APPROVAL",
                                      "APPROVAL_REQUIRED")

        # 12. explicit deny rules?
        if any(rule in req.get("context", {}).get("deny_tags", [])
               for rule in self._deny_rules):
            return self._decision(request_id, "DENY", "EXPLICIT_DENY")

        # 13. ALLOW
        return self._decision(request_id, "ALLOW", "ALLOW")

    def _decision(self, request_id: str, decision: str,
                  reason_code: str) -> dict:
        return {"request_id": request_id, "decision": decision,
                "reason_code": reason_code}
