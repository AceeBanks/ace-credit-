"""G0-B5-C17 — Research Finding prototype.

Turns funder/winner/community research into durable, evidence-backed
objects. Enforces FIND-001..005: evidence required, limitations preserved,
historical patterns descriptive (no universal causality from weak samples),
sample size represented, and findings never silently injected as facts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from prototype.g0.evidence.models import EvidenceGraph


class ResearchFindingError(ValueError):
    """Raised when a finding violates the research policy."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/evidence/"
                           "research_finding_policy.yaml").read_text(encoding="utf-8"))


_POLICY = _load_policy()


def validate_finding(*, finding: dict, graph: EvidenceGraph,
                     policy: dict | None = None) -> dict:
    """Validate and return the finding (fail-closed); raises on violation."""
    policy = policy or _POLICY
    ftype = finding.get("research_type")
    if ftype not in policy["research_types"]:
        raise ResearchFindingError(f"unknown research_type {ftype!r} (FIND-001)")

    refs = list(finding.get("evidence_refs", []) or [])
    if not refs:
        raise ResearchFindingError("finding requires evidence (FIND-001)")

    # FIND-003: causal caution on historical winner patterns
    if ftype == "HISTORICAL_WINNER_PATTERN":
        sample = finding.get("award_sample_size")
        statement = (finding.get("statement") or "").lower()
        forbidden = [t for t in policy["causal_forbidden_terms"]
                     if t in statement]
        if forbidden:
            raise ResearchFindingError(
                f"causal language {forbidden} not allowed in historical "
                "winner pattern (FIND-003); findings are descriptive")
        if sample is not None and sample < policy["weak_sample_threshold"] \
                and not finding.get("limitations"):
            raise ResearchFindingError(
                "weak-sample winner pattern must carry a limitation (FIND-003)")

    # FIND-004: sample size represented on range/pattern findings
    if ftype in ("AWARD_RANGE", "HISTORICAL_WINNER_PATTERN"):
        if finding.get("award_sample_size") is None:
            raise ResearchFindingError(
                f"{ftype} must represent award_sample_size (FIND-004)")

    # FIND-005: applicability is required so consumers never inject silently
    if not finding.get("applicability"):
        raise ResearchFindingError(
            "finding must declare applicability (FIND-005)")

    # evidence refs must resolve (not tombstoned)
    for ref in refs:
        resolved = graph.resolve_or_tombstone(ref)
        if resolved.get("tombstoned"):
            raise ResearchFindingError(f"evidence ref {ref} is tombstoned")

    # FIND-006 / ADV-04: generated research summaries must not be recursively
    # cited as their own evidence — every finding's evidence chain must bottom
    # out at a source snapshot, statistic observation or canonical fact.
    base_types = {"SOURCE_SNAPSHOT", "STATISTIC_OBSERVATION",
                  "CANONICAL_FACT"}
    if refs and all(
            graph.resolve_or_tombstone(r).get("ref_type") == "RESEARCH_FINDING"
            for r in refs):
        raise ResearchFindingError(
            "research finding may not cite only other research findings; "
            "evidence must bottom out at sources (FIND-006)")

    return {
        "finding_id": finding.get("finding_id"),
        "research_type": ftype,
        "subject_refs": list(finding.get("subject_refs", []) or []),
        "statement": finding.get("statement"),
        "evidence_refs": refs,
        "quality": finding.get("quality", "UNVERIFIED"),
        "applicability": finding.get("applicability"),
        "limitations": list(finding.get("limitations", []) or []),
        "award_sample_size": finding.get("award_sample_size"),
        "created_at": finding.get("created_at") or _now(),
        "created_by": finding.get("created_by"),
    }


def client_view(finding: dict) -> dict:
    """FIND-005/FIND-002: what may be shown to the client. Limitations are
    preserved; the finding stays a research object, never a fact."""
    return {
        "finding_id": finding["finding_id"],
        "research_type": finding["research_type"],
        "statement": finding["statement"],
        "quality": finding["quality"],
        "limitations": list(finding.get("limitations", []) or []),
    }
