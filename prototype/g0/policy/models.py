"""G0 Book 1 policy prototype — typed models.

Minimal, dependency-free dataclasses matching the plan's B1.C11 model shapes.
These are the PROVISIONAL executable form of the constitutional authority
model; production wiring arrives in later books.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field


class AuthorityLevel(str, enum.Enum):
    DISABLED = "DISABLED"
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"

    @classmethod
    def rank(cls, level: "AuthorityLevel | str | None") -> int:
        order = [cls.DISABLED, cls.L0, cls.L1, cls.L2, cls.L3, cls.L4, cls.L5]
        if isinstance(level, str):
            try:
                level = cls(level)
            except ValueError:
                return -1  # unknown ranks below everything -> fails closed
        return order.index(level) if level in order else -1


class Decision(str, enum.Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class Reason(str, enum.Enum):
    UNKNOWN_ACTOR = "UNKNOWN_ACTOR"
    DISABLED_ACTOR = "DISABLED_ACTOR"
    TENANT_SCOPE_MISSING = "TENANT_SCOPE_MISSING"
    TENANT_SCOPE_DENIED = "TENANT_SCOPE_DENIED"
    UNKNOWN_CAPABILITY = "UNKNOWN_CAPABILITY"
    CAPABILITY_DISABLED = "CAPABILITY_DISABLED"
    ACTOR_TYPE_DENIED = "ACTOR_TYPE_DENIED"
    INSUFFICIENT_AUTHORITY = "INSUFFICIENT_AUTHORITY"
    RESOURCE_SCOPE_DENIED = "RESOURCE_SCOPE_DENIED"
    TASK_SCOPE_DENIED = "TASK_SCOPE_DENIED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVAL_INVALID = "APPROVAL_INVALID"
    EXPLICIT_DENY = "EXPLICIT_DENY"
    ALLOW = "ALLOW"


@dataclass(frozen=True)
class Actor:
    actor_id: str
    actor_type: str
    tenant_scopes: tuple[str, ...] = ()
    authority_ceiling: AuthorityLevel = AuthorityLevel.DISABLED
    status: str = "ACTIVE"


@dataclass(frozen=True)
class Capability:
    capability_id: str
    minimum_level: AuthorityLevel
    actor_types: tuple[str, ...]
    resource_types: frozenset[str]
    approval_class: str                      # AP0..APX
    phase_status: str                        # ENABLED / DISABLED / FUTURE
    requires_tenant_scope: bool = True
    requires_project_scope: bool = False
    family: str = ""


@dataclass(frozen=True)
class ApprovalRef:
    """A human approval record (already validated to be agent-free upstream).

    Executable contract aligned with schemas/g0/policy/approval_policy.schema.json:
    every field below is carried on the record. `decided_at` is REQUIRED
    (matching the schema); `scope_project_id` and `expires_at` are nullable.
    An approval may satisfy a requested class ONLY by an explicit, tested rule
    (see evaluator._find_valid_approval) — never by implicit class inheritance.
    """
    approval_id: str
    approver_principal: str                  # must be a HUMAN principal id
    approver_role: str
    approval_class: str                      # AP1/AP2/AP3 (APX can never approve)
    scope_tenant_id: str
    subject_capability_id: str
    decided_at: str                          # ISO-8601 UTC; REQUIRED by schema
    scope_project_id: str | None = None      # None = tenant-scoped; else exact project
    expires_at: str | None = None            # ISO-8601 UTC or None (no expiry)
    status: str = "VALID"                    # VALID / EXPIRED / REVOKED

    def __post_init__(self) -> None:
        if not self.decided_at or not str(self.decided_at).strip():
            raise ValueError("ApprovalRef.decided_at is required (approval_policy.schema.json)")
        if self.approval_class not in {"AP1", "AP2", "AP3", "APX"}:
            raise ValueError(f"unknown approval_class '{self.approval_class}'")
        if self.status not in {"VALID", "EXPIRED", "REVOKED"}:
            raise ValueError(f"unknown approval status '{self.status}'")
        if self.approver_principal.lower().startswith("agent"):
            raise ValueError("agent principal cannot appear on an approval (LAW-B1-018)")


@dataclass(frozen=True)
class TaskScope:
    """Bounding contract for workers (and any delegated execution)."""
    task_id: str
    allowed_capability_ids: frozenset[str]
    tenant_id: str | None
    project_id: str | None
    max_authority_level: AuthorityLevel


@dataclass(frozen=True)
class PolicyContext:
    tenant_id: str | None
    project_id: str | None
    resource_type: str
    resource_id: str | None = None
    requested_level: AuthorityLevel = AuthorityLevel.L0  # unset => capability minimum governs
    approval_refs: tuple[ApprovalRef, ...] = ()
    task_scope: TaskScope | None = None
    explicit_deny_active: bool = False


@dataclass(frozen=True)
class PolicyDecisionResult:
    decision: Decision
    reason_code: Reason
    detail: str = ""
    step_failed_at: int | None = None
    matched_approval: ApprovalRef | None = field(default=None)

    def __post_init__(self) -> None:
        # Internal invariant: ALLOW must never coexist with another reason code.
        if self.decision is Decision.ALLOW and self.reason_code is not Reason.ALLOW:
            raise ValueError("ALLOW decisions must carry reason ALLOW")
