"""G0-B5-C18 — Audit <-> Evidence <-> Decision linkage.

Traverses AuditEvent -> PolicyDecision -> Capability -> DecisionRecord ->
Evidence inputs -> Output artifacts -> Human approval, and the reverse
path from a proposal artifact back to its audit event. Enforces LINK-001
(no orphaned consequential decisions), LINK-002 (approval refs resolve),
LINK-003 (actor/capability consistency), LINK-004 (redaction preserves
lineage).
"""
from __future__ import annotations

from typing import Any, Iterable

from prototype.g0.evidence.decisions import DecisionRecord
from prototype.g0.evidence.models import EvidenceGraph


class LinkageError(ValueError):
    """Raised when a linkage violates the audit policy."""


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/evidence/"
                           "linkage_policy.yaml").read_text(encoding="utf-8"))


_POLICY = _load_policy()


def _decision_inputs(decision: DecisionRecord) -> list[str]:
    return [i.ref for i in decision.input_refs]


def check_orphaned_consequential(
    decisions: Iterable[DecisionRecord],
    audit_events: Iterable[dict],
    *,
    policy: dict | None = None,
) -> list[str]:
    """LINK-001: every consequential decision must be linked to an audit
    event (matched via request_id or event_id). Returns violations."""
    policy = policy or _POLICY
    consequential = set(policy["consequential_result_classes"])
    events = list(audit_events)
    event_refs = set()
    for ev in events:
        if ev.get("event_id"):
            event_refs.add(ev["event_id"])
        if ev.get("request_id"):
            event_refs.add(ev["request_id"])
    violations = []
    for dec in decisions:
        result = dec.result or {}
        cls = result.get("result_class") or result.get("side_effect_class")
        if cls not in consequential:
            continue
        linked = dec.decision_id in event_refs \
            or any(dec.decision_id in (ev.get("resource_id") or "")
                   or dec.decision_id == ev.get("decision_record_ref")
                   for ev in events)
        if not linked:
            violations.append(
                f"orphaned consequential decision {dec.decision_id} "
                "(LINK-001)")
    return violations


def check_actor_capability_consistency(
    decision: DecisionRecord,
    audit_event: dict,
) -> list[str]:
    """LINK-003: decision actor/capability must match the audit event."""
    violations = []
    if decision.actor_ref != audit_event.get("actor_id"):
        violations.append(
            f"actor mismatch: decision {decision.actor_ref} vs audit "
            f"{audit_event.get('actor_id')} (LINK-003)")
    if decision.capability_id != audit_event.get("capability_id"):
        violations.append(
            f"capability mismatch: decision {decision.capability_id} vs audit "
            f"{audit_event.get('capability_id')} (LINK-003)")
    if decision.tenant_id != audit_event.get("tenant_id"):
        violations.append("tenant mismatch (LINK-003)")
    return violations


def resolve_approval(approval_ref: str | None,
                     approvals: dict[str, dict]) -> dict | None:
    """LINK-002: approval_ref must resolve in the approval registry."""
    if not approval_ref:
        return None
    approval = approvals.get(approval_ref)
    if approval is None:
        raise LinkageError(f"approval reference {approval_ref} does not "
                           "resolve (LINK-002)")
    return approval


def forward_lineage(*, audit_event: dict, decisions: list[DecisionRecord],
                    approvals: dict[str, dict],
                    graph: EvidenceGraph) -> dict:
    """AuditEvent -> PolicyDecision -> Capability -> DecisionRecord ->
    Evidence inputs -> Output artifacts -> Human approval (if any)."""
    policy_ref = audit_event.get("policy_decision_ref")
    capability = audit_event.get("capability_id")
    decision = next((d for d in decisions
                     if d.decision_id == audit_event.get("resource_id")
                     or d.decision_id == audit_event.get("decision_record_ref")),
                    None)
    if decision is None:
        raise LinkageError(
            f"audit event {audit_event.get('event_id')} does not resolve to "
            "a decision record (LINK-001)")
    violations = check_actor_capability_consistency(decision, audit_event)
    if violations:
        raise LinkageError("; ".join(violations))
    approval = resolve_approval(audit_event.get("approval_ref"), approvals)
    evidence = []
    for ref in _decision_inputs(decision):
        resolved = graph.resolve_or_tombstone(ref)
        evidence.append({"ref": ref, "tombstoned": resolved.get("tombstoned", False)})
    return {
        "audit_event_id": audit_event.get("event_id"),
        "policy_decision_ref": policy_ref,
        "capability_id": capability,
        "decision_record_ref": decision.decision_id,
        "evidence_inputs": evidence,
        "output_artifacts": list(decision.output_refs),
        "approval_ref": audit_event.get("approval_ref"),
        "approval_resolved": approval is not None,
    }


def backward_lineage(*, artifact_ref: str, decisions: list[DecisionRecord],
                     audit_events: list[dict]) -> dict:
    """ProposalArtifact -> generating decision -> evidence -> actor ->
    policy decision -> audit event."""
    decision = next((d for d in decisions
                     if artifact_ref in d.output_refs
                     or artifact_ref in _decision_inputs(d)), None)
    if decision is None:
        raise LinkageError(
            f"artifact {artifact_ref} does not resolve to a generating "
            "decision (LINK-001)")
    event = next((ev for ev in audit_events
                  if ev.get("resource_id") == decision.decision_id
                  or ev.get("decision_record_ref") == decision.decision_id),
                 None)
    if event is None:
        raise LinkageError(
            f"decision {decision.decision_id} has no audit event (LINK-001)")
    return {
        "artifact_ref": artifact_ref,
        "decision_record_ref": decision.decision_id,
        "evidence_inputs": _decision_inputs(decision),
        "actor_id": event.get("actor_id"),
        "policy_decision_ref": event.get("policy_decision_ref"),
        "audit_event_id": event.get("event_id"),
    }


def redact_payload(packet: dict, *, keep: set[str] | None = None,
                   policy: dict | None = None) -> dict:
    """LINK-004: replace sensitive field values with [REDACTED] while
    preserving lineage fields."""
    policy = policy or _POLICY
    keep = keep or set(policy["redaction_never_removes"])
    out = {}
    for k, v in packet.items():
        if k in keep:
            out[k] = v
        elif isinstance(v, dict):
            out[k] = redact_payload(v, keep=keep, policy=policy)
        elif isinstance(v, list):
            out[k] = [redact_payload(x, keep=keep, policy=policy)
                      if isinstance(x, dict) else "[REDACTED]" for x in v]
        else:
            out[k] = "[REDACTED]"
    return out
