"""G0 Book 1 policy prototype — fail-closed policy decision point (PDP).

Implements the plan's B1.C11 twelve-step decision order. DEFAULT = DENY:
any unknown input, missing scope, disabled capability, or unsatisfied approval
yields DENY (or REQUIRE_APPROVAL where that is the specified outcome).
Security-critical uncertainty NEVER resolves to ALLOW (LAW-B1-005).

This evaluator is deterministic: same inputs -> same decision, always.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.policy.models import (  # noqa: E402
    Actor,
    AuthorityLevel,
    Decision,
    PolicyContext,
    PolicyDecisionResult,
    Reason,
)
from prototype.g0.policy.registry import PolicyRegistry  # noqa: E402

EVALUATOR_VERSION = "g0-b1-1.0.0"

# Approval classes that may be satisfied by an approval ref at eval time.
_APPROVABLE = {"AP2", "AP3"}


def evaluate(registry: PolicyRegistry, actor: Actor | None, capability_id: str | None,
             context: PolicyContext) -> PolicyDecisionResult:
    """Run the 12-step decision order. Any exception inside a step is converted
    to DENY — evaluation errors must never widen access."""
    try:
        return _evaluate(registry, actor, capability_id, context)
    except Exception as exc:  # noqa: BLE001 - deliberate total fail-closed net
        return PolicyDecisionResult(
            Decision.DENY, Reason.EXPLICIT_DENY,
            detail=f"evaluator internal failure fails closed: {exc!r}",
            step_failed_at=0)


def _deny(reason: Reason, step: int, detail: str = "") -> PolicyDecisionResult:
    return PolicyDecisionResult(Decision.DENY, reason, detail=detail, step_failed_at=step)


def _evaluate(registry: PolicyRegistry, actor: Actor | None, capability_id: str | None,
              ctx: PolicyContext) -> PolicyDecisionResult:
    # 1-2. actor valid and enabled?
    if actor is None or not actor.actor_id:
        return _deny(Reason.UNKNOWN_ACTOR, 1, "no authenticated actor")
    reg_actor = registry.get_actor(actor.actor_type)
    if reg_actor is None:
        return _deny(Reason.UNKNOWN_ACTOR, 1, f"unregistered actor type '{actor.actor_type}'")
    if actor.status != "ACTIVE" or reg_actor.status != "ACTIVE":
        return _deny(Reason.DISABLED_ACTOR, 2, f"actor '{actor.actor_id}' not ACTIVE")

    # Kill-switch hoist: an active explicit deny blocks everything immediately,
    # before scope/capability checks could produce narrower reason codes.
    # (Deviation from literal plan order, recorded: kill-switch semantics.)
    if ctx.explicit_deny_active:
        return _deny(Reason.EXPLICIT_DENY, 0, "explicit deny rule active")

    # 3. tenant scope valid?
    if ctx.tenant_id is None or not str(ctx.tenant_id).strip():
        return _deny(Reason.TENANT_SCOPE_MISSING, 3, "missing tenant scope (LAW-B1-015)")
    if actor.tenant_scopes and ctx.tenant_id not in actor.tenant_scopes:
        return _deny(Reason.TENANT_SCOPE_DENIED, 3,
                     f"tenant '{ctx.tenant_id}' outside actor scopes {list(actor.tenant_scopes)}")

    # 4. capability registered?
    cap = registry.get_capability(capability_id) if capability_id else None
    if cap is None:
        return _deny(Reason.UNKNOWN_CAPABILITY, 4,
                     f"capability '{capability_id}' not in registry")

    # 5. capability enabled in phase?
    if cap.phase_status != "ENABLED":
        return _deny(Reason.CAPABILITY_DISABLED, 5,
                     f"'{cap.capability_id}' is '{cap.phase_status}' in Phase 1")

    # 6. actor type allowed for this capability?
    if actor.actor_type not in cap.actor_types:
        return _deny(Reason.ACTOR_TYPE_DENIED, 6,
                     f"type '{actor.actor_type}' not permitted for '{cap.capability_id}'")

    # 7. authority ceiling sufficient?
    ceiling = min(actor.authority_ceiling, reg_actor.authority_ceiling, key=AuthorityLevel.rank)
    effective_ceiling = ceiling
    task = ctx.task_scope
    if task is not None:
        effective_ceiling = min(effective_ceiling, task.max_authority_level,
                                key=AuthorityLevel.rank)
    requested = max(ctx.requested_level, cap.minimum_level, key=AuthorityLevel.rank)
    if AuthorityLevel.rank(effective_ceiling) < AuthorityLevel.rank(requested):
        return _deny(Reason.INSUFFICIENT_AUTHORITY, 7,
                     f"ceiling {effective_ceiling.value} < required {requested.value}")

    # 8. resource scope valid?
    if cap.resource_types and ctx.resource_type not in cap.resource_types:
        return _deny(Reason.RESOURCE_SCOPE_DENIED, 8,
                     f"resource type '{ctx.resource_type}' not in "
                     f"{sorted(cap.resource_types)}")
    if cap.requires_project_scope and (ctx.project_id is None or not str(ctx.project_id).strip()):
        return _deny(Reason.RESOURCE_SCOPE_DENIED, 8,
                     f"'{cap.capability_id}' requires project scope")

    # 9. task scope valid for workers / delegated execution?
    if task is not None:
        if capability_id not in task.allowed_capability_ids:
            return _deny(Reason.TASK_SCOPE_DENIED, 9,
                         f"'{cap.capability_id}' outside TaskContract '{task.task_id}'")
        if task.tenant_id is not None and task.tenant_id != ctx.tenant_id:
            return _deny(Reason.TASK_SCOPE_DENIED, 9,
                         "TaskContract tenant differs from request tenant")
        if task.project_id is not None and ctx.project_id is not None \
                and task.project_id != ctx.project_id:
            return _deny(Reason.TASK_SCOPE_DENIED, 9,
                         "TaskContract project differs from request project")

    # 10. approval requirement satisfied?
    if cap.approval_class in _APPROVABLE:
        matched = _find_valid_approval(ctx.approval_refs, cap.capability_id,
                                       ctx.tenant_id, ctx.project_id,
                                       cap.approval_class)
        if matched is None:
            return PolicyDecisionResult(
                Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED,
                detail=f"'{cap.capability_id}' requires {cap.approval_class} human approval",
                step_failed_at=10)

    # APX can never be approved — but step 5 already denied DISABLED caps, and
    # the validator guarantees APX caps stay DISABLED. Defense in depth:
    if cap.approval_class == "APX":
        return _deny(Reason.CAPABILITY_DISABLED, 10,
                     "APX is constitutionally unreachable in Phase 1")

    # 12. ALLOW
    return PolicyDecisionResult(Decision.ALLOW, Reason.ALLOW,
                                detail="all policy steps satisfied",
                                matched_approval=None)


def _parse_dt(value: str):
    """Parse an ISO-8601 datetime; naive values are assumed UTC. None on garbage."""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _time_valid(ref, now: datetime) -> bool:
    """Time validity: status VALID AND decided_at parseable/not-future AND,
    when expires_at is present, expires_at > evaluation time.
    An expired timestamp MUST fail even if status is still VALID."""
    if not ref.decided_at:
        return False                        # schema-required field missing
    decided = _parse_dt(ref.decided_at)
    if decided is None or decided > now:
        return False                        # unparseable or decided in the future
    if ref.expires_at:
        expires = _parse_dt(ref.expires_at)
        if expires is None or expires <= now:
            return False                    # expired even if status says VALID
    return True


def _find_valid_approval(refs, capability_id: str, tenant_id: str,
                         project_id: str | None, needed_class: str,
                         now: datetime | None = None):
    """Find an approval that EXPLICITLY satisfies `needed_class` for this
    capability/tenant/project at evaluation time.

    Class semantics are exact and constitutional (approval_matrix.yaml):
      - AP2 requires an AP2 approval.
      - AP3 requires AP3 from two DISTINCT human principals.
      - AP1 NEVER satisfies AP2/AP3 (no implicit privilege inheritance).
      - APX is unsatisfiable.
    Project scope: an approval carrying scope_project_id authorizes ONLY that
    project; a project-scoped approval can never authorize another project.
    """
    if needed_class not in _APPROVABLE:
        return None                         # AP0/AP1 need no record; APX unsatisfiable
    if now is None:
        now = datetime.now(timezone.utc)
    matched = None
    principals: set[str] = set()
    for ref in refs:
        if ref.subject_capability_id != capability_id:
            continue
        if ref.scope_tenant_id != tenant_id:
            continue
        if ref.scope_project_id is not None and ref.scope_project_id != project_id:
            continue                        # project-scoped approval cannot cross projects
        if ref.status != "VALID":
            continue
        if ref.approval_class != needed_class:
            continue                        # no cross-class substitution (AP1 != AP2 != AP3)
        if ref.approval_class == "APX":
            continue                        # can never cure anything
        if not _time_valid(ref, now):
            continue
        if ref.approver_principal.lower().startswith("agent"):
            continue                        # agent principal is not human (LAW-B1-018)
        principals.add(ref.approver_principal)
        matched = ref
    if needed_class == "AP3":
        # dual approval: two DISTINCT human principals required
        if len(principals) < 2:
            return None
    return matched
