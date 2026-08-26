"""G0-B5-C15 — ExplanationPacket builder.

Converts a DecisionRecord into a client transparency packet that cites only
structured decision evidence (EXPL-001/002), never chain-of-thought
(EXPL-003), and surfaces stale indicators (EXPL-004) and conflicts
(EXPL-005). Unsupported rationale is rejected, not silently dropped.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ExplanationError(ValueError):
    """Raised when an explanation packet violates the policy."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _decision_input_refs(decision: Any) -> list[str]:
    """Extract the ref ids the decision actually consumed."""
    return [i.ref for i in decision.input_refs]


def _decision_output_refs(decision: Any) -> list[str]:
    return list(getattr(decision, "output_refs", []) or [])


def _stale_class_of(ref_id: str, graph: Any) -> str | None:
    """Return the stale class for a ref per explanation_policy.yaml, else None."""
    resolved = graph.resolve_or_tombstone(ref_id)
    if resolved.get("tombstoned"):
        return "TOMBSTONED"
    return None


def _conflicts_among(refs: list[str], graph: Any) -> list[dict]:
    """Find CONTRADICTS edges among the cited refs (EXPL-005)."""
    ref_set = set(refs)
    out = []
    for edge in graph.edges(edge_type="CONTRADICTS"):
        a, b = edge.from_ref.ref_id, edge.to_ref.ref_id
        if a in ref_set and b in ref_set:
            out.append({"ref_a": a, "ref_b": b, "edge_type": edge.edge_type})
    return out


def build_explanation_packet(
    *, decision: Any, graph: Any,
    explanation_id: str | None = None,
    extra_cited_refs: list[str] | None = None,
    explicit_assumptions: list[str] | None = None,
) -> dict:
    """Build a policy-conformant ExplanationPacket from a DecisionRecord.

    Raises ExplanationError for unsupported rationale (a cited ref that is
    not a decision input/output and not explicitly flagged as an assumption).
    """
    input_refs = _decision_input_refs(decision)
    output_refs = _decision_output_refs(decision)
    allowed = set(input_refs) | set(output_refs)
    assumptions = list(explicit_assumptions or [])
    extra = list(extra_cited_refs or [])

    # EXPL-001/EXPL-002: every citation must trace to the decision or be an
    # explicit assumption. Unknown refs are rejected, not silently dropped.
    unsupported = [r for r in extra if r not in allowed]
    if unsupported:
        raise ExplanationError(
            f"unsupported rationale rejected (EXPL-002): refs {unsupported} "
            "are not decision inputs/outputs and were not flagged as assumptions")

    cited = sorted(allowed)

    # EXPL-004: staleness must be surfaced.
    stale = []
    for ref in cited:
        cls = _stale_class_of(ref, graph)
        if cls:
            stale.append({"ref": ref, "stale_class": cls})

    # EXPL-005: conflicts among cited refs must be disclosed.
    conflicts = _conflicts_among(cited, graph)

    result = decision.result or {}
    reason_codes = list(getattr(decision, "reason_codes", []) or [])
    summary = result.get("summary") or result.get("outcome") or (
        f"{decision.decision_type} decision recorded")

    return {
        "explanation_id": explanation_id or f"exp-{decision.decision_id}",
        "decision_record_ref": decision.decision_id,
        "decision_type": decision.decision_type,
        "tenant_id": decision.tenant_id,
        "project_id": decision.project_id,
        "summary": summary,
        "cited_evidence_refs": cited,
        "reason_codes": reason_codes,
        "stale_indicators": stale,
        "conflict_disclosures": conflicts,
        "assumptions": assumptions,
        "created_at": _now(),
    }
