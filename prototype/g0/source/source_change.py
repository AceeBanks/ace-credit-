"""G0-B3-C12 — Revision & source-change protocol.

Converts changing source state into explicit governed SourceChangeEvents with
materiality classes (P0 application-critical, P1 significant strategy/research,
P2 nonmaterial). A structured semantic diff (field/requirement level), not a raw
byte diff, is the basis for classification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Materiality(Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class ChangeClass(Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    CANCELLED = "CANCELLED"
    PARSER_OUTPUT_CHANGE = "PARSER_OUTPUT_CHANGE"
    METADATA_CHANGE = "METADATA_CHANGE"


# P0 triggers: application-critical semantic changes.
P0_SIGNALS = [
    "eligibility_changed",
    "deadline_changed",
    "award_ceiling_or_floor_changed",
    "match_requirement_changed",
    "required_attachment_changed",
    "submission_path_changed",
    "geography_changed",
    "opportunity_cancelled",
    "mandatory_question_changed",
]

# P1 signals: significant strategy/research.
P1_SIGNALS = [
    "program_description_changed",
    "scoring_guidance_changed",
    "contact_changed",
    "explanatory_guidance_changed",
    "historical_award_corrected",
]


@dataclass
class SourceChangeEvent:
    change_event_id: str
    source_id: str
    entity_type: str
    entity_id: str
    old_snapshot_id: Optional[str]
    new_snapshot_id: str
    detected_at: str
    change_class: ChangeClass
    materiality: Materiality
    affected_fields: list[str] = field(default_factory=list)
    semantic_diff_ref: Optional[str] = None
    status: str = "RECORDED"
    signals: list[str] = field(default_factory=list)


def classify_change(change_class: ChangeClass, signals: list[str],
                    affected_fields: list[str]) -> Materiality:
    """Classify materiality from semantic signals (fail-closed).

    Raw byte diff is insufficient; the caller must supply structured signals.
    Any P0 signal => P0; otherwise any P1 signal => P1; else P2.
    """
    if change_class == ChangeClass.CANCELLED:
        return Materiality.P0
    # A mandatory deadline/eligibility field change with no explicit signal is
    # still P0 because the affected field is application-critical.
    critical_fields = {
        "deadline", "eligibility", "award_ceiling", "award_floor",
        "required_attachments", "submission_path", "geography",
    }
    if any(cf in affected_fields for cf in critical_fields):
        return Materiality.P0
    if any(s in P0_SIGNALS for s in signals):
        return Materiality.P0
    if any(s in P1_SIGNALS for s in signals):
        return Materiality.P1
    return Materiality.P2


def is_true_source_change(event: SourceChangeEvent, raw_same: bool) -> bool:
    """Distinguish a parser-output change from a true source change."""
    if event.change_class == ChangeClass.PARSER_OUTPUT_CHANGE:
        return False
    if raw_same:
        return False
    return True