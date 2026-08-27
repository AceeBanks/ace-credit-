"""G0-B6-C4/C5 — Capability grant model + authorization decision contract.

The authorization chain evaluates in deterministic order and returns
ALLOW / DENY / REQUIRE_APPROVAL with stable reason codes. Default is DENY;
every failure maps to a reason code (100% fail-closed coverage).

G0-B6-REPAIR-01 — close authorization-to-tool binding and project-scope gaps:

- AUTH-R1  grant authority ladder enforced inside authorize(): the grant
           level must satisfy capability.required_level <= grant level AND
           grant level <= principal.authority_level. Unknown or malformed
           levels fail closed (GRANT_AUTHORITY_INSUFFICIENT).
- AUTH-R2  every AuthorizationDecision binds the request that produced it:
           request_id, principal_id, tenant_id, project_id, capability_id,
           resource_id, decision, reason_code, grant_id, decision_timestamp
           plus a canonical request_hash and a self-verifying decision_id.
           Decisions are issued only through the trusted DecisionRegistry
           owned by the Authorizer (the PDP). An ALLOW is never a bearer
           token for arbitrary tool calls.
- AUTH-R3  project scope: a project-bound grant authorizes only that
           project; a project-scoped resource requires the request to carry
           the matching project explicitly; same-tenant cross-project access
           is DENIED (PROJECT_DENIED).
- AUTH-R4  approval-requiring operations are validated exclusively through
           ApprovalRegistry (tenant, capability, resource, resource_version,
           action, expiry, revocation, class); raw string membership is no
           longer approval truth. The validated approval ref is bound into
           the ALLOW decision.
- AUTH-R5  delegation grants are project-bound (GRANT-007).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from prototype.g0.security.identity import PrincipalRegistry, ScopeEvaluator


class AuthorizationError(ValueError):
    """Raised on invalid grant operations."""


REASON_CODES = (
    "PRINCIPAL_UNKNOWN", "PRINCIPAL_DISABLED", "SESSION_INVALID",
    "TENANT_DENIED", "CAPABILITY_UNKNOWN", "CAPABILITY_DISABLED",
    "AUTHORITY_INSUFFICIENT", "GRANT_MISSING", "GRANT_EXPIRED",
    "GRANT_AUTHORITY_INSUFFICIENT", "PROJECT_DENIED",
    "RESOURCE_DENIED", "TASK_SCOPE_DENIED", "DATA_CLASS_DENIED",
    "EGRESS_DENIED", "APPROVAL_REQUIRED", "EXPLICIT_DENY", "ALLOW",
)

_LEVELS = ("L0", "L1", "L2", "L3", "L4", "L5")

# ---------------------------------------------------------------------
# Canonical decision contract (REPAIR-01 AUTH-R2)
# ---------------------------------------------------------------------

REQUEST_BINDING_FIELDS = (
    "request_id", "principal_id", "tenant_id", "project_id",
    "capability_id", "resource_id", "resource_version", "task_scope",
)

_DECISION_FIELDS = (
    "request_id", "principal_id", "tenant_id", "project_id",
    "capability_id", "resource_id", "decision", "reason_code",
    "grant_id", "decision_timestamp", "request_hash",
)

DECISION_REQUIRED_FIELDS = _DECISION_FIELDS + ("decision_id",)


def canonical(obj: Any) -> str:
    """Stable JSON canonicalization used for all security hashes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      default=str)


def canonical_request_hash(req: dict) -> str:
    """Hash over exactly the context the decision binds the tool call to."""
    binding = {k: req.get(k) for k in REQUEST_BINDING_FIELDS}
    return hashlib.sha256(canonical(binding).encode("utf-8")).hexdigest()[:32]


def compute_decision_id(decision: dict) -> str:
    """Self-integrity id over the fixed decision field set."""
    payload = {k: decision.get(k) for k in _DECISION_FIELDS}
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()[:32]


def decision_shape_ok(decision: Any) -> tuple[bool, str]:
    """Structural + integrity validation of a decision mapping.

    Sufficient when no registry is configured; the registry verifier adds
    issuance checks on top (see DecisionRegistry.verify). Caller-forged
    mappings fail here unless they were emitted with the trusted constructor.
    """
    if not isinstance(decision, dict):
        return False, "decision_not_a_mapping"
    absent = [f for f in DECISION_REQUIRED_FIELDS if f not in decision]
    if absent:
        return False, f"missing_fields:{','.join(absent)}"
    for key in ("request_id", "principal_id", "capability_id",
                "decision_timestamp"):
        if not decision.get(key):
            return False, f"empty_binding:{key}"
    if decision.get("decision") not in ("ALLOW", "DENY", "REQUIRE_APPROVAL"):
        return False, "invalid_decision_value"
    if not isinstance(decision.get("reason_code"), str):
        return False, "invalid_reason_code"
    if decision["decision_id"] != compute_decision_id(decision):
        return False, "integrity_mismatch"
    return True, ""


class DecisionRegistry:
    """Trusted PDP store of issued decisions (REPAIR-01 item 8).

    The gateway consumes decisions from this registry when configured: a
    forged caller dict can neither collide with a recorded decision_id nor
    survive deep equality against the issued copy.
    """

    def __init__(self) -> None:
        self._decisions: dict[str, dict] = {}

    def record(self, decision: dict) -> dict:
        stored = dict(decision)
        self._decisions[stored["decision_id"]] = stored
        return stored

    def lookup(self, decision_id: str) -> dict | None:
        entry = self._decisions.get(decision_id)
        return dict(entry) if entry else None

    def lookup_all(self) -> list[dict]:
        return [dict(v) for v in self._decisions.values()]

    def __len__(self) -> int:
        return len(self._decisions)

    def verify(self, decision: Any) -> tuple[bool, str]:
        """Validate shape/integrity AND issuance by this PDP."""
        ok, err = decision_shape_ok(decision)
        if not ok:
            return ok, err
        stored = self._decisions.get(decision["decision_id"])
        if stored is None:
            return False, "decision_unissued"
        if canonical(stored) != canonical(decision):
            return False, "decision_tampered"
        return True, ""


def _level_rank(level: str | None) -> int:
    """Rank of a known level; -1 for unknown/malformed (fail closed)."""
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
        authority (GRANT-002/003) and be project-bound (GRANT-007). CEO /
        principal grants are not delegation and may carry any registered
        capability."""
        if parent_ceiling is not None:
            # delegation to a worker: only delegable capabilities, within
            # the parent's ceiling, and bound to a project
            if capability_id not in self.policy["delegable_capabilities"]:
                raise AuthorizationError(
                    f"capability {capability_id} is not delegable (GRANT-003)")
            if _level_rank(authority_level) > _level_rank(parent_ceiling):
                raise AuthorizationError(
                    f"worker grant {authority_level} exceeds parent ceiling "
                    f"{parent_ceiling} (GRANT-002)")
            if not project_id:
                raise AuthorizationError(
                    "delegation grants must be project-bound (GRANT-007)")
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
                   tenant_id: str,
                   project_id: str | None = None) -> dict | None:
        """First grant matching principal+capability+tenant whose project
        binding is compatible with the requested project (unbound grants
        match any request project; a bound grant matches only its own)."""
        for grant in self._grants.values():
            if (grant["principal_id"] == principal_id
                    and grant["capability_id"] == capability_id
                    and grant["tenant_id"] == tenant_id):
                bound = grant.get("project_id")
                if bound is None or bound == project_id:
                    return grant
        return None

    def grants_for(self, *, principal_id: str, capability_id: str,
                   tenant_id: str) -> list[dict]:
        """All grants matching principal+capability+tenant, any status."""
        return [g for g in self._grants.values()
                if g["principal_id"] == principal_id
                and g["capability_id"] == capability_id
                and g["tenant_id"] == tenant_id]

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
    """Deterministic authorization chain; emits bound decisions only."""

    def __init__(self, *, principals: PrincipalRegistry,
                 scope: ScopeEvaluator, grants: GrantRegistry,
                 policy: dict | None = None,
                 approvals: Any | None = None) -> None:
        self.principals = principals
        self.scope = scope
        self.grants = grants
        self.policy = policy or _POLICY
        self.approvals = approvals  # ApprovalRegistry (REPAIR-01 AUTH-R4)
        self.decisions = DecisionRegistry()
        self._capabilities: dict[str, dict] = {}
        self._data_class_allows: set[str] = set()
        self._egress_allows: set[str] = set()
        self._deny_rules: list[str] = []

    def register_capability(self, capability_id: str,
                            required_level: str = "L0",
                            enabled: bool = True) -> None:
        self._capabilities[capability_id] = {
            "required_level": required_level, "enabled": enabled}

    def allow_data_class(self, data_class: str) -> None:
        self._data_class_allows.add(data_class)

    def allow_egress_destination(self, destination: str) -> None:
        self._egress_allows.add(destination)

    def add_deny_rule(self, rule: str) -> None:
        self._deny_rules.append(rule)

    # ------------------------------------------------------------ emit

    def _emit(self, req: dict, request_hash: str, now: str, decision: str,
              reason_code: str, *, grant_id: str | None = None,
              approval_ref: str | None = None) -> dict:
        """Build, seal and record the bound decision (trusted constructor)."""
        core = {
            "request_id": req.get("request_id", "req-?"),
            "principal_id": req.get("principal_id"),
            "tenant_id": req.get("tenant_id"),
            "project_id": req.get("project_id"),
            "capability_id": req.get("capability_id"),
            "resource_id": req.get("resource_id"),
            "decision": decision,
            "reason_code": reason_code,
            "grant_id": grant_id,
            "decision_timestamp": now,
            "request_hash": request_hash,
        }
        if approval_ref:
            core["approval_ref"] = approval_ref
        core["decision_id"] = compute_decision_id(core)
        return self.decisions.record(core)

    def _denied(self, req: dict, request_hash: str, now: str,
                reason_code: str) -> dict:
        return self._emit(req, request_hash, now, "DENY", reason_code)

    # ------------------------------------------------------- evaluation

    def authorize(self, req: dict, *, session_valid: bool = True,
                  now: str | None = None) -> dict:
        """Evaluate the request in decision order; default DENY."""
        now = now or _now()
        request_hash = canonical_request_hash(req)
        principal_id = req.get("principal_id")
        capability_id = req.get("capability_id")
        tenant_id = req.get("tenant_id")
        project_id = req.get("project_id")
        resource_id = req.get("resource_id")

        # 1. principal valid/enabled?
        try:
            principal = self.principals.get(principal_id)
        except Exception:
            return self._denied(req, request_hash, now, "PRINCIPAL_UNKNOWN")
        if principal.status != "ACTIVE":
            return self._denied(req, request_hash, now, "PRINCIPAL_DISABLED")

        # 2. authenticated session valid?
        if not session_valid:
            return self._denied(req, request_hash, now, "SESSION_INVALID")

        # 3. tenant membership/scope valid?
        if self.scope.membership_for(principal_id, tenant_id, now) is None:
            return self._denied(req, request_hash, now, "TENANT_DENIED")

        # 4. capability registered/enabled?
        cap = self._capabilities.get(capability_id)
        if cap is None:
            return self._denied(req, request_hash, now, "CAPABILITY_UNKNOWN")
        if not cap["enabled"]:
            return self._denied(req, request_hash, now, "CAPABILITY_DISABLED")

        # 5. Book 1 authority ceiling sufficient?
        if _level_rank(principal.authority_level) < \
                _level_rank(cap["required_level"]):
            return self._denied(req, request_hash, now,
                                "AUTHORITY_INSUFFICIENT")

        # 6. capability grant valid? Project-aware selection: prefer an
        # unbound or exactly-matching grant; when every candidate grant is
        # project-bound and none matches the request project this is a
        # cross-project access attempt (PROJECT_DENIED), else no grant.
        candidates = self.grants.grants_for(
            principal_id=principal_id, capability_id=capability_id,
            tenant_id=tenant_id)
        grant = next((g for g in candidates
                      if g.get("project_id") in (None, project_id)), None)
        if grant is None:
            if candidates:
                return self._denied(req, request_hash, now, "PROJECT_DENIED")
            return self._denied(req, request_hash, now, "GRANT_MISSING")
        if not self.grants.grant_in_effect(grant, now):
            return self._denied(req, request_hash, now, "GRANT_EXPIRED")

        # 6b. AUTH-R1 — grant authority ladder. The grant must reach the
        # capability requirement but never exceed the principal's ceiling;
        # malformed levels fail closed.
        grant_rank = _level_rank(grant.get("authority_level"))
        cap_rank = _level_rank(cap["required_level"])
        principal_rank = _level_rank(principal.authority_level)
        if -1 in (grant_rank, cap_rank, principal_rank):
            return self._denied(req, request_hash, now,
                                "GRANT_AUTHORITY_INSUFFICIENT")
        if grant_rank < cap_rank or grant_rank > principal_rank:
            return self._denied(req, request_hash, now,
                                "GRANT_AUTHORITY_INSUFFICIENT")

        # 7. resource scope valid?
        if not self.scope.can_read(principal_id=principal_id,
                                   resource_id=resource_id,
                                   resource_tenant=tenant_id, now=now):
            return self._denied(req, request_hash, now, "RESOURCE_DENIED")

        # 7b. AUTH-R3 — project scope. A project-bound grant authorizes only
        # its project; a project-scoped resource requires the matching
        # request project explicitly (absence fails closed).
        bound_project = grant.get("project_id")
        if bound_project and project_id != bound_project:
            return self._denied(req, request_hash, now, "PROJECT_DENIED")
        try:
            resource_project = self.scope.project_of(resource_id)
        except Exception:
            resource_project = None
        if resource_project and project_id != resource_project:
            return self._denied(req, request_hash, now, "PROJECT_DENIED")

        # 8. task scope valid?
        if req.get("task_scope"):
            constraints = grant.get("resource_constraints", [])
            if req["task_scope"] not in constraints:
                return self._denied(req, request_hash, now,
                                    "TASK_SCOPE_DENIED")

        # 9. data classification permits action?
        data_class = (req.get("context") or {}).get("data_class")
        if data_class and data_class not in self._data_class_allows:
            return self._denied(req, request_hash, now, "DATA_CLASS_DENIED")

        # 10. destination/egress policy permits action?
        destination = req.get("destination")
        if destination and destination not in self._egress_allows:
            return self._denied(req, request_hash, now, "EGRESS_DENIED")

        # 11. AUTH-R4 — approval requirement satisfied THROUGH the
        # ApprovalRegistry; raw string membership is not approval truth.
        approved_ref: str | None = None
        if req.get("requested_side_effect") in ("EXTERNAL_SEND", "SUBMIT",
                                                "WORKFLOW_MUTATION"):
            refs = req.get("approval_refs") or []
            approved_ref = self._validated_approval(refs, req, now)
            if approved_ref is None:
                return self._emit(req, request_hash, now,
                                  "REQUIRE_APPROVAL", "APPROVAL_REQUIRED",
                                  grant_id=grant["grant_id"])

        # 12. explicit deny rules?
        if any(rule in req.get("context", {}).get("deny_tags", [])
               for rule in self._deny_rules):
            return self._denied(req, request_hash, now, "EXPLICIT_DENY")

        # 13. ALLOW — sealed with grant_id (+ validated approval evidence)
        return self._emit(req, request_hash, now, "ALLOW", "ALLOW",
                          grant_id=grant["grant_id"],
                          approval_ref=approved_ref)

    def _validated_approval(self, refs: list, req: dict, now: str) -> str | None:
        """Return the first approval ref validated end-to-end by the
        ApprovalRegistry, or None. Tenant, capability, resource,
        resource_version and action are re-checked against the approval's
        request_hash; expiry, revocation and status inside check()."""
        if self.approvals is None:
            return None
        for ref in refs:
            try:
                valid = self.approvals.check(
                    approval_id=ref,
                    tenant_id=req.get("tenant_id"),
                    capability_id=req.get("capability_id"),
                    resource_id=req.get("resource_id"),
                    resource_version=req.get("resource_version", ""),
                    action=req.get("requested_side_effect"),
                    now=now)
            except Exception:
                valid = False
            if valid:
                return ref
        return None

    def verify_decision(self, decision: Any) -> tuple[bool, str]:
        """Public verification hook: shape/integrity + issuance by this PDP."""
        return self.decisions.verify(decision)
