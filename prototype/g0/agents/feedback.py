"""B4.C20-C21 — Client feedback loop and co-adaptation (prototype).

  * classify_feedback: user corrections are classified into first-class
    feedback types;
  * apply_feedback: geography change invalidates the relevant match/search
    plan; tone feedback updates a preference + artifact revision request
    (never canonical grant facts); factual corrections become proposals;
  * coadaptation_lesson: repeated clarification produces a CM-LESSON-CANDIDATE
    that cannot promote without Book 7 evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

FEEDBACK_TYPES = {
    "INTENT_MISUNDERSTOOD", "FACTUAL_CORRECTION", "PREFERENCE_CORRECTION",
    "ARTIFACT_REVISION_REQUEST", "PRIORITY_CHANGE",
    "PROJECT_CANCELLATION_PAUSE", "RESULT_DISAGREEMENT",
}

GEOGRAPHY_MARKERS = ("georgia", "atlanta", "state", "county", "region",
                     "service area", "tennessee", "alabama", "florida",
                     "north carolina", "south carolina")
TONE_MARKERS = ("tone", "too formal", "too casual", "not how we talk",
                "voice", "wording", "style")
FACT_MARKERS = ("revenue", "ein", "address", "employees", "incorrect",
                "wrong number", "deadline is")


class FeedbackError(ValueError):
    """Raised when a feedback event violates the routing rules."""


@dataclass
class FeedbackEvent:
    feedback_id: str
    client_actor_id: str
    tenant_id: str
    raw_text: str
    feedback_type: str
    routing: str
    operational_impact: bool = False
    created_at: str = ""


@dataclass
class FeedbackResult:
    feedback_type: str
    routing: str
    invalidated_plan_ids: list[str] = field(default_factory=list)
    intent_amendment: dict[str, Any] | None = None
    fact_proposal: dict[str, Any] | None = None
    preference_supersession: dict[str, Any] | None = None
    artifact_revision_request: dict[str, Any] | None = None
    canonical_fact_mutation: bool = False


def classify_feedback(text: str) -> str:
    lowered = text.lower()
    if any(m in lowered for m in GEOGRAPHY_MARKERS) and \
            ("search" in lowered or "match" in lowered or
             "target" in lowered or "focus" in lowered or
             "look at" in lowered or "change" in lowered):
        return "PRIORITY_CHANGE"
    if any(m in lowered for m in TONE_MARKERS):
        return "PREFERENCE_CORRECTION"
    if any(m in lowered for m in FACT_MARKERS):
        return "FACTUAL_CORRECTION"
    if "didn't mean" in lowered or "not what i" in lowered or \
            "misunderstood" in lowered or "that's not what i wanted" in lowered:
        return "INTENT_MISUNDERSTOOD"
    if "revise" in lowered or "rework" in lowered or "rewrite" in lowered:
        return "ARTIFACT_REVISION_REQUEST"
    if "cancel" in lowered or "pause" in lowered or "stop the project" in lowered:
        return "PROJECT_CANCELLATION_PAUSE"
    if "disagree" in lowered or "i don't believe" in lowered:
        return "RESULT_DISAGREEMENT"
    raise FeedbackError(f"unclassifiable feedback: {text}")


ROUTING = {
    "INTENT_MISUNDERSTOOD": "INTENT_AMENDMENT",
    "FACTUAL_CORRECTION": "FACT_PROPOSAL",
    "PREFERENCE_CORRECTION": "MEMORY_SUPERSESSION",
    "ARTIFACT_REVISION_REQUEST": "ARTIFACT_REVISION_REQUEST",
    "PRIORITY_CHANGE": "INTENT_AMENDMENT",
    "PROJECT_CANCELLATION_PAUSE": "PROJECT_STATE_CHANGE",
    "RESULT_DISAGREEMENT": "EXPLANATION_REVIEW",
}


def apply_feedback(*, feedback_id: str, client_actor_id: str, tenant_id: str,
                   raw_text: str, active_plan_ids: list[str] | None = None,
                   geography_keyword: str | None = None) -> FeedbackResult:
    """Route feedback per the frozen policy; fail closed on unknown types."""
    try:
        feedback_type = classify_feedback(raw_text)
    except FeedbackError:
        raise
    routing = ROUTING[feedback_type]
    result = FeedbackResult(feedback_type=feedback_type, routing=routing)

    if feedback_type == "PRIORITY_CHANGE":
        # FEEDBACK-001: geography change invalidates relevant match plan
        result.operational_impact = True
        lowered = raw_text.lower()
        if any(m in lowered for m in GEOGRAPHY_MARKERS):
            result.invalidated_plan_ids = list(active_plan_ids or [])
            result.intent_amendment = {
                "type": "GEOGRAPHY_SCOPE_CHANGE",
                "previous_scope": geography_keyword,
                "new_scope": "pending clarification",
            }
    elif feedback_type == "PREFERENCE_CORRECTION":
        # FEEDBACK-002: tone feedback updates preference/artifact, never facts
        result.preference_supersession = {
            "class": "PM-PREFERENCE",
            "statement": f"client prefers: {raw_text.strip()}",
        }
        result.artifact_revision_request = {
            "request": "revise communication tone per client feedback",
        }
        result.canonical_fact_mutation = False
    elif feedback_type == "FACTUAL_CORRECTION":
        # FEEDBACK-003: factual correction is a proposal, not silent mutation
        result.fact_proposal = {
            "class": "FACT_PROPOSAL",
            "statement": raw_text.strip(),
            "status": "ASSERTION",
        }
        result.canonical_fact_mutation = False
    elif feedback_type == "INTENT_MISUNDERSTOOD":
        result.operational_impact = True
        result.intent_amendment = {"type": "INTENT_REDEFINITION"}
    elif feedback_type == "ARTIFACT_REVISION_REQUEST":
        result.artifact_revision_request = {"request": raw_text.strip()}
    elif feedback_type == "PROJECT_CANCELLATION_PAUSE":
        result.operational_impact = True
        result.intent_amendment = {"type": "PROJECT_CANCELLATION_PAUSE"}
    elif feedback_type == "RESULT_DISAGREEMENT":
        result.artifact_revision_request = {"request": "review explanation"}
    return result


def coadaptation_lesson(metric: str, observation: str) -> dict:
    """Repeated clarification on a metric produces a lesson candidate.

    The lesson can never promote without Book 7 evaluation (FEEDBACK-004 /
    PROMO-004). Returns a CM-LESSON-CANDIDATE-style record.
    """
    return {
        "memory_class": "CM-LESSON-CANDIDATE",
        "statement": f"co-adaptation: {observation} (metric {metric})",
        "classification": "PROMOTE_FOR_REVIEW",
        "book7_eval_required": True,
    }
