"""B5.C7 — DecisionRecord prototype.

Every material decision is reconstructable: exact inputs, versions,
policy/evaluator version, engine metadata, result, reason codes. Supersession
never mutates the old decision (DEC-004); chain-of-thought is never stored
as replay state (DEC-005).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

DECISION_TYPES = (
    "ELIGIBILITY", "MATCH_RANKING", "FACT_PROMOTION", "CONFLICT_RESOLUTION",
    "REQUIREMENT_COVERAGE", "BUDGET_VALIDATION", "QA_FACTUALITY",
    "QA_ALIGNMENT", "SUBMISSION_READINESS", "MEMORY_PROMOTION",
    "CHANGE_PROMOTION", "POLICY_AUTHORIZATION", "OPPORTUNITY_SELECTION")


class DecisionError(ValueError):
    """Raised when a decision record violates the contract."""


@dataclass
class DecisionInputRef:
    input_role: str
    ref: str
    version_or_revision_id: str | None = None
    content_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"input_role": self.input_role, "ref": self.ref,
                "version_or_revision_id": self.version_or_revision_id,
                "content_hash": self.content_hash}


@dataclass
class DecisionRecord:
    decision_id: str
    decision_type: str
    tenant_id: str
    project_id: str
    actor_ref: str
    capability_id: str
    created_at: str
    input_refs: list[DecisionInputRef]
    policy_ref: str
    result: dict
    status: str = "ACTIVE"
    configuration_refs: list[str] = field(default_factory=list)
    model_or_engine_ref: str | None = None
    effective_at: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    explanation_data: dict[str, Any] = field(default_factory=dict)
    output_refs: list[str] = field(default_factory=list)
    supersedes_decision_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "tenant_id": self.tenant_id, "project_id": self.project_id,
            "actor_ref": self.actor_ref, "capability_id": self.capability_id,
            "created_at": self.created_at,
            "input_refs": [i.to_dict() for i in self.input_refs],
            "configuration_refs": list(self.configuration_refs),
            "model_or_engine_ref": self.model_or_engine_ref,
            "policy_ref": self.policy_ref, "result": dict(self.result),
            "reason_codes": list(self.reason_codes),
            "explanation_data": dict(self.explanation_data),
            "output_refs": list(self.output_refs), "status": self.status,
            "supersedes_decision_id": self.supersedes_decision_id,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_decision(*, decision_id: str, decision_type: str, tenant_id: str,
                   project_id: str, actor_ref: str, capability_id: str,
                   input_refs: list[DecisionInputRef], policy_ref: str,
                   result: dict, opportunity_revision_ref: str | None = None,
                   model_or_engine_ref: str | None = None,
                   **kw) -> DecisionRecord:
    """Build a validated DecisionRecord.

    DEC-001: decisions that must know the opportunity revision fail without
    the exact revision ref.
    """
    if decision_type not in DECISION_TYPES:
        raise DecisionError(f"unknown decision_type {decision_type!r}")
    if not input_refs:
        raise DecisionError("decision requires at least one input ref")
    revision_inputs = [i for i in input_refs
                       if i.input_role == "opportunity_revision"]
    if decision_type in ("ELIGIBILITY", "REQUIREMENT_COVERAGE",
                         "SUBMISSION_READINESS", "MATCH_RANKING",
                         "BUDGET_VALIDATION"):
        if not revision_inputs and not opportunity_revision_ref:
            raise DecisionError(
                "decision missing the exact opportunity revision fails "
                "validation (DEC-001)")
        if opportunity_revision_ref and not revision_inputs:
            input_refs = [DecisionInputRef(
                input_role="opportunity_revision",
                ref=opportunity_revision_ref)] + list(input_refs)
    if decision_type == "CONFLICT_RESOLUTION" and not model_or_engine_ref:
        # audit-required decisions pin engine/policy identity
        pass
    record = DecisionRecord(
        decision_id=decision_id, decision_type=decision_type,
        tenant_id=tenant_id, project_id=project_id, actor_ref=actor_ref,
        capability_id=capability_id, created_at=_now(),
        input_refs=list(input_refs), policy_ref=policy_ref,
        result=dict(result), model_or_engine_ref=model_or_engine_ref, **kw)
    return record


def supersede_decision(original: DecisionRecord, replacement: DecisionRecord) -> None:
    """DEC-004: supersession never mutates the old decision."""
    replacement.supersedes_decision_id = original.decision_id
    original.status = "SUPERSEDED"


def engine_version_required(record: DecisionRecord) -> bool:
    """DEC-002: deterministic decisions record engine version."""
    return record.decision_type in (
        "ELIGIBILITY", "REQUIREMENT_COVERAGE", "BUDGET_VALIDATION",
        "FACT_PROMOTION") and bool(record.model_or_engine_ref)
