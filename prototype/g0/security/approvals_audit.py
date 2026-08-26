"""G0-B6-C18/C19 — Human approval enforcement + security audit model.

APPR-001..006: approvals bind to action/resource/version via request_hash,
old approvals cannot authorize changed versions, wrong-tenant and revoked
approvals denied, chat phrases never auto-approve, L5 stays disabled.
AUD-001..005: denied actions logged, secrets absent, audit links to
AuthorizationDecision/DecisionRecord, tenant-filtered access, append-oriented
integrity hash chain.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


class ApprovalError(ValueError):
    """Raised when approval or audit policy is violated."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/security/"
                           "approval_audit_policy.yaml")
                          .read_text(encoding="utf-8"))


_POLICY = _load_policy()


def _hash(request: dict) -> str:
    canonical = json.dumps(request, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]


class ApprovalRegistry:
    """Durable, hash-bound approvals."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY
        self._approvals: dict[str, dict] = {}
        self._ux_captured: set[str] = set()

    def record_from_ux(self, *, approval_id: str, principal_id: str,
                       tenant_id: str, capability_id: str, resource_id: str,
                       resource_version: str, action: str,
                       approval_class: str, expires_at: str,
                       issued_at: str | None = None) -> dict:
        """APPR-005: only approved UX/actions produce approvals."""
        if approval_class not in self.policy["approval_classes"]:
            raise ApprovalError(f"unknown approval class {approval_class!r}")
        if approval_class == "APX":
            raise ApprovalError("APX can never approve")
        request = {"principal_id": principal_id, "tenant_id": tenant_id,
                   "capability_id": capability_id, "resource_id": resource_id,
                   "resource_version": resource_version, "action": action}
        approval = dict(approval_id=approval_id, principal_id=principal_id,
                        tenant_id=tenant_id, capability_id=capability_id,
                        resource_id=resource_id, resource_version=resource_version,
                        action=action, request_hash=_hash(request),
                        approval_class=approval_class,
                        issued_at=issued_at or _now(), expires_at=expires_at,
                        status="VALID")
        self._approvals[approval_id] = approval
        self._ux_captured.add(approval_id)
        return approval

    def check(self, *, approval_id: str, tenant_id: str, capability_id: str,
              resource_id: str, resource_version: str, action: str,
              now: str | None = None) -> bool:
        """APPR-001..004: version-bound, tenant-bound, not revoked/expired."""
        now = now or _now()
        approval = self._approvals.get(approval_id)
        if approval is None:
            return False
        if approval["status"] != "VALID":
            return False  # APPR-004 revoked denied
        if approval["tenant_id"] != tenant_id:
            return False  # APPR-003 wrong tenant denied
        if approval["expires_at"] < now:
            return False
        if approval_id not in self._ux_captured:
            return False  # APPR-005 chat phrases never auto-approve
        # APPR-002: old approval cannot authorize a changed version
        request = {"principal_id": approval["principal_id"],
                   "tenant_id": tenant_id, "capability_id": capability_id,
                   "resource_id": resource_id, "resource_version": resource_version,
                   "action": action}
        return approval["request_hash"] == _hash(request)

    def revoke(self, approval_id: str) -> None:
        if approval_id not in self._approvals:
            raise ApprovalError(f"unknown approval {approval_id}")
        self._approvals[approval_id]["status"] = "REVOKED"

    def l5_submission_stays_disabled(self) -> bool:
        """APPR-006: L5 submission is disabled regardless of approval."""
        return False


class SecurityAudit:
    """Append-oriented audit with integrity hash chain."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY
        self._events: list[dict] = []
        self._chain: list[str] = []

    def record(self, *, event_id: str, audit_class: str, tenant_id: str,
               actor: str, action: str, resource_ref: str | None = None,
               decision_ref: str | None = None, payload: dict | None = None,
               denied_reason: str | None = None) -> dict:
        """AUD-001/002: record metadata and refs; never raw secrets."""
        if audit_class not in self.policy["audit_classes"]:
            raise ApprovalError(f"unknown audit class {audit_class!r}")
        prev_hash = self._chain[-1] if self._chain else "GENESIS"
        event = dict(event_id=event_id, audit_class=audit_class,
                     tenant_id=tenant_id, actor=actor, action=action,
                     resource_ref=resource_ref, decision_ref=decision_ref,
                     denied_reason=denied_reason, prev_hash=prev_hash,
                     timestamp=_now())
        integrity = _hash({k: v for k, v in event.items()
                           if k != "prev_hash"})
        event["event_hash"] = hashlib.sha256(
            (integrity + prev_hash).encode("utf-8")).hexdigest()[:24]
        self._events.append(event)
        self._chain.append(event["event_hash"])
        return event

    def events_for_tenant(self, tenant_id: str) -> list[dict]:
        """AUD-004: tenant-filtered audit access."""
        return [e for e in self._events if e["tenant_id"] == tenant_id]

    def verify_chain(self) -> bool:
        """AUD-005: integrity chain verifies (tamper detection)."""
        prev = "GENESIS"
        for event in self._events:
            integrity = _hash({k: v for k, v in event.items()
                               if k not in ("prev_hash", "event_hash")})
            expected = hashlib.sha256(
                (integrity + prev).encode("utf-8")).hexdigest()[:24]
            if event["event_hash"] != expected:
                return False
            if event["prev_hash"] != prev:
                return False
            prev = event["event_hash"]
        return True
