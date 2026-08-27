"""G0-B8-C25/C26 — submission-ready MOCK package and client explanation.

The package is SUBMISSION_READY_MOCK only: everything a reviewer needs to
inspect, with submission structurally impossible. The client explanation is
evidence/decision-consistent and answers the north-star questions without
requiring chain-of-thought.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from prototype.g0.evidence.decisions import (
    DecisionInputRef,
    DecisionRecord,
)
from prototype.g0.evidence.explanation import build_explanation_packet


def _decision_from_dict(d: dict) -> DecisionRecord:
    """Rebuild a DecisionRecord from its serialized form (nested refs)."""
    return DecisionRecord(
        decision_id=d["decision_id"], decision_type=d["decision_type"],
        tenant_id=d["tenant_id"], project_id=d["project_id"],
        actor_ref=d["actor_ref"], capability_id=d["capability_id"],
        created_at=d["created_at"],
        input_refs=[DecisionInputRef(**i) for i in d.get("input_refs", [])],
        policy_ref=d["policy_ref"], result=dict(d.get("result", {})),
        status=d.get("status", "ACTIVE"),
        configuration_refs=list(d.get("configuration_refs", [])),
        model_or_engine_ref=d.get("model_or_engine_ref"),
        reason_codes=list(d.get("reason_codes", [])),
        explanation_data=dict(d.get("explanation_data", {})),
        output_refs=list(d.get("output_refs", [])),
        supersedes_decision_id=d.get("supersedes_decision_id"),
    )


class _Graph:
    """Minimal graph stub for the explanation packet (no stale/conflict)."""

    def resolve_or_tombstone(self, ref: str) -> dict:
        return {"ref_type": "SOURCE_SNAPSHOT", "tombstoned": False}

    def edges(self, edge_type: str = ""):
        return []

    def stale_class_of(self, ref):
        return None

    def conflicts_among(self, refs):
        return []


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PackageResult:
    package_id: str
    state: str  # "SUBMISSION_READY_MOCK"
    label: str  # "MOCK_NON_SUBMISSION"
    artifacts: dict
    explanation: dict
    submission_enabled: bool = False
    created_at: str = ""

    def validate(self) -> None:
        assert self.state == "SUBMISSION_READY_MOCK", \
            "package state must be SUBMISSION_READY_MOCK (B8.C25)"
        assert self.label == "MOCK_NON_SUBMISSION", \
            "package must be labeled MOCK_NON_SUBMISSION"
        assert self.submission_enabled is False, \
            "submission must remain disabled (B8.C25)"


def build_package(*, package_id: str, project_id: str, tenant_id: str,
                  sections: dict[str, str], claim_ledger: list[dict],
                  budget_lines: list[dict], budget_total: str,
                  qa_report: dict, human_review: dict,
                  revision_id: str, eligibility_result: str,
                  explanation_decisions: list[DecisionRecord]) -> PackageResult:
    """Assemble the reviewable mock package + client explanation."""
    artifacts = {
        "proposal": {k: v for k, v in sections.items()},
        "budget": {"lines": budget_lines, "total": budget_total},
        "claim_ledger": claim_ledger,
        "qa_report": qa_report,
        "human_review": human_review,
        "opportunity_revision_id": revision_id,
        "eligibility_result": eligibility_result,
    }
    # explanation packet built from the real decisions (eligibility + match
    # + project); the first decision anchors the packet
    decision = explanation_decisions[0]
    explanation = build_explanation_packet(
        decision=decision, graph=_Graph(),
        explicit_assumptions=["unknowns: staff size, annual budget"])
    result = PackageResult(
        package_id=package_id, state="SUBMISSION_READY_MOCK",
        label="MOCK_NON_SUBMISSION", artifacts=artifacts,
        explanation=explanation, submission_enabled=False,
        created_at=_now())
    result.validate()
    return result
