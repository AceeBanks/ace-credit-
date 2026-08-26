"""G0-B3-C13 — Dependency invalidation protocol.

Ensures stale upstream facts cannot masquerade as current downstream work.
Tracks dependency edges so a source update only invalidates the affected
decisions/artifacts (selective invalidation), not the entire world.

Invalidation states:
  CURRENT, STALE_RECOMPUTE_REQUIRED, STALE_REVIEW_REQUIRED, INVALID, SUPERSEDED
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class InvalidationState(Enum):
    CURRENT = "CURRENT"
    STALE_RECOMPUTE_REQUIRED = "STALE_RECOMPUTE_REQUIRED"
    STALE_REVIEW_REQUIRED = "STALE_REVIEW_REQUIRED"
    INVALID = "INVALID"
    SUPERSEDED = "SUPERSEDED"


# Dependency map: downstream artifact -> set of upstream fact classes it
# depends on. Used for selective invalidation.
DEPENDENCIES: dict[str, set[str]] = {
    "eligibility_decision": {
        "opportunity_deadline", "opportunity_eligibility",
        "organization_financial_filings", "opportunity_required_attachments",
    },
    "match_explanation": {
        "opportunity_deadline", "opportunity_eligibility",
        "opportunity_matching_cost_share", "opportunity_award_ceiling",
    },
    "requirement_set": {"opportunity_deadline", "opportunity_required_attachments"},
    "draft_context_bundle": {"requirements", "organization_financial_filings"},
    "proposal_section": {"requirements", "community_statistics",
                         "historical_award_amount"},
    "budget": {"opportunity_award_ceiling", "opportunity_award_floor",
               "opportunity_matching_cost_share"},
    "submission_package": {"requirements", "opportunity_submission_instructions"},
}

# Which downstream artifacts a given invalidation reason (signal) touches.
# Map P0/P1 signals to affected artifacts (selective, not full-invalidation).
SIGNAL_TARGETS: dict[str, set[str]] = {
    "eligibility_changed": {"eligibility_decision", "match_explanation",
                            "draft_context_bundle", "proposal_section"},
    "deadline_changed": {"eligibility_decision", "match_explanation",
                         "requirement_set", "submission_package"},
    "award_ceiling_or_floor_changed": {"budget", "match_explanation",
                                       "proposal_section"},
    "match_requirement_changed": {"budget", "match_explanation", "proposal_section"},
    "required_attachment_changed": {"requirement_set", "submission_package",
                                    "draft_context_bundle"},
    "submission_path_changed": {"submission_package"},
    "geography_changed": {"proposal_section", "draft_context_bundle"},
    "opportunity_cancelled": {"submission_package", "eligibility_decision",
                              "budget", "draft_context_bundle"},
}


@dataclass
class DependencyNode:
    artifact_id: str
    state: InvalidationState = InvalidationState.CURRENT
    depends_on: set[str] = field(default_factory=set)


class DependencyGraph:
    """Tracks upstream fact dependencies and invalidates only affected nodes."""

    def __init__(self) -> None:
        self._nodes: dict[str, DependencyNode] = {}

    def add(self, artifact_id: str, depends_on: set[str]) -> None:
        self._nodes[artifact_id] = DependencyNode(
            artifact_id=artifact_id, depends_on=set(depends_on),
            state=InvalidationState.CURRENT)

    def state(self, artifact_id: str) -> Optional[InvalidationState]:
        node = self._nodes.get(artifact_id)
        return node.state if node else None

    def invalidate(self, changed_fact_classes: set[str],
                    signal: str | None = None,
                    materiality: str = "P0") -> list[str]:
        """Set affected nodes to STALE_RECOMPUTE_REQUIRED. Fail-closed:
        a P0 change on a critical fact invalidates; a P2 change invalidates
        nothing unless the artifact directly depends on the changed fact."""
        affected: list[str] = []
        for node in self._nodes.values():
            # Direct fact-class dependency
            if node.depends_on & changed_fact_classes:
                node.state = InvalidationState.STALE_RECOMPUTE_REQUIRED
                affected.append(node.artifact_id)
                continue
            # Signal-based selective targets apply for material changes
            if materiality in ("P0", "P1") and signal:
                if node.artifact_id in SIGNAL_TARGETS.get(signal, set()):
                    node.state = InvalidationState.STALE_RECOMPUTE_REQUIRED
                    affected.append(node.artifact_id)
        return affected

    def mark_to_review(self, artifact_id: str) -> None:
        node = self._nodes.get(artifact_id)
        if node and node.state == InvalidationState.CURRENT:
            node.state = InvalidationState.STALE_REVIEW_REQUIRED

    def recompute(self, artifact_id: str) -> None:
        node = self._nodes.get(artifact_id)
        if node:
            node.state = InvalidationState.CURRENT