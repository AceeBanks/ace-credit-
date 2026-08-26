"""G0-B3-C11 — Conflict resolution protocol.

Resolves disagreement without destroying evidence lineage. Lower-authority
stale values become SUPERSEDED (never deleted); equal-authority contradiction
blocks critical use until a resolution method (precedence, effective-date,
refresh, merge, human review, official clarification) resolves it or
UNRESOLVED_BLOCK takes over.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ConflictType(Enum):
    VALUE_CONFLICT = "VALUE_CONFLICT"
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"
    GEOGRAPHY_CONFLICT = "GEOGRAPHY_CONFLICT"
    UNIT_CONFLICT = "UNIT_CONFLICT"
    SOURCE_VERSION_CONFLICT = "SOURCE_VERSION_CONFLICT"
    INTERPRETATION_CONFLICT = "INTERPRETATION_CONFLICT"
    USER_OFFICIAL_CONFLICT = "USER_OFFICIAL_CONFLICT"


class ResolutionMethod(Enum):
    SOURCE_PRECEDENCE = "SOURCE_PRECEDENCE"
    EFFECTIVE_DATE = "EFFECTIVE_DATE"
    SOURCE_REFRESH = "SOURCE_REFRESH"
    MERGE_COMPATIBLE = "MERGE_COMPATIBLE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    OFFICIAL_CLARIFICATION = "OFFICIAL_CLARIFICATION"
    UNRESOLVED_BLOCK = "UNRESOLVED_BLOCK"


class ResolutionStatus(Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    BLOCKED = "BLOCKED"


# Critical-use facts: unresolved conflict blocks or clearly degrades readiness.
CRITICAL_BLOCK_FACT_CLASSES = {
    "opportunity_deadline",
    "opportunity_eligibility",
    "opportunity_award_ceiling",
    "opportunity_required_attachments",
    "legal_organization_name",
    "opportunity_submission_instructions",
}


@dataclass
class Conflict:
    conflict_id: str
    subject_entity_id: str
    fact_class: str
    claim_refs: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    conflict_type: ConflictType = ConflictType.VALUE_CONFLICT
    severity: str = "medium"
    resolution_status: ResolutionStatus = ResolutionStatus.OPEN
    resolution_method: Optional[ResolutionMethod] = None
    resolved_value_ref: Optional[str] = None
    resolver_actor: Optional[str] = None
    resolved_at: Optional[str] = None

    @property
    def critical(self) -> bool:
        return self.fact_class in CRITICAL_BLOCK_FACT_CLASSES


class ConflictRegistry:
    def __init__(self) -> None:
        self._conflicts: dict[str, Conflict] = {}
        self._events: list[dict] = []

    def register(self, c: Conflict) -> None:
        if c.conflict_id in self._conflicts:
            raise ValueError(f"duplicate conflict {c.conflict_id}")
        self._conflicts[c.conflict_id] = c

    def get(self, conflict_id: str) -> Optional[Conflict]:
        return self._conflicts.get(conflict_id)

    def resolve(self, conflict: Conflict, method: ResolutionMethod,
                resolved_value_ref: str, actor: str, resolved_at: str) -> None:
        existing = self._conflicts.get(conflict.conflict_id)
        if existing is None:
            raise KeyError(f"unknown conflict {conflict.conflict_id}")
        existing.resolution_status = ResolutionStatus.RESOLVED
        existing.resolution_method = method
        existing.resolved_value_ref = resolved_value_ref
        existing.resolver_actor = actor
        existing.resolved_at = resolved_at
        self._events.append({
            "conflict_id": conflict.conflict_id, "method": method.value,
            "actor": actor, "resolved_at": resolved_at,
        })

    def readiness_allows(self, fact_classes: set[str]) -> bool:
        """Fail-closed: any OPEN/BLOCKED conflict on a critical fact blocks use."""
        for c in self._conflicts.values():
            if c.fact_class in fact_classes and c.resolution_status in (
                    ResolutionStatus.OPEN, ResolutionStatus.BLOCKED):
                return False
        return True


def supersede_old(conflict: Conflict, lower_value_ref: str) -> str:
    """A lower-authority stale value becomes SUPERSEDED, not deleted.

    Returns a marker describing that the value is retained in history as
    superseded (evidence lineage preserved).
    """
    return f"SUPERSEDED:{lower_value_ref}"