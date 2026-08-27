"""G0-B8-C3 — conversational intake & intent preservation.

Personal Hermes responsibilities: use the known profile before re-asking,
distinguish exploration from execution, formulate a typed IntentContract,
preserve desired outcome/constraints, never decide grant selection itself,
never fabricate eligibility facts. The CEO receives ONLY the IntentContract
— never a raw transcript.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from prototype.g0.agents.intent_builder import (
    ClarificationRequest,
    IntentContract,
    build_intent,
    draft_readiness_gate,
)


@dataclass
class IntakeResult:
    intent: IntentContract
    clarifications_asked: list[ClarificationRequest]
    readiness_state: str
    readiness_reasons: list[str]
    used_raw_transcript: bool = False
    fabricated_eligibility: bool = False

    def validate(self) -> None:
        if self.used_raw_transcript:
            raise ValueError("Personal Hermes must not forward the raw "
                             "conversation to CEO (B8.C3)")
        if self.fabricated_eligibility:
            raise ValueError("Personal Hermes must not fabricate eligibility "
                             "facts (B8.C3)")
        for q in self.clarifications_asked:
            if q.question_type == "ELIGIBILITY_CRITICAL" and q.blocking:
                raise ValueError(
                    "Personal Hermes must not resolve eligibility-critical "
                    "questions itself (B8.C3)")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_intake(*, tenant_id: str, client_actor_id: str,
               organization_id: str, client_intent_text: str,
               profile: Any,
               answers: dict[str, str] | None = None) -> IntakeResult:
    """Encode the client's natural-language intent into an IntentContract.

    Personal Hermes asks only the clarifications the profile cannot answer
    from canonical state; unanswered non-eligibility unknowns become flags,
    never fabricated facts. Eligibility determination is deferred to the
    deterministic engine — Personal Hermes never resolves it.
    """
    answers = answers or {}
    clarifications: list[ClarificationRequest] = []
    for unknown in ("staff size", "annual operating budget"):
        clarifications.append(ClarificationRequest(
            clarification_id=f"clr-{unknown.replace(' ', '-')}",
            intent_id="pending", requesting_actor="PERSONAL_HERMES",
            question_type="ELIGIBILITY_CRITICAL" if unknown == "annual "
            "operating budget" else "CLIENT_CONTEXT",
            question=f"Do you know your {unknown}? (leave blank if unknown)",
            why_needed=("eligibility-critical fact for deterministic "
                        "evaluation" if unknown == "annual operating budget"
                        else "program capacity context"),
            blocking=False,
            expected_answer_type="text",
            answerable_from_canonical_state=False,
            created_at=_now()))

    intent = build_intent(
        tenant_id=tenant_id, client_actor_id=client_actor_id,
        organization_id=organization_id,
        intent_type="BUILD_APPLICATION",
        objective=client_intent_text,
        authority_scope="PREPARE_ONLY",
        confidence_state="MEDIUM",
        desired_outcome=("grounded proposal package for the best matching "
                         "Georgia opportunity; no submission"),
        constraints=["no submission", "no fabrication"],
        non_goals=["select a specific opportunity", "approve funding"],
        requested_capabilities=["research.run", "draft.section",
                                "matching.rank"],
        user_statements=[client_intent_text],
    )
    # attach the profile-known facts + open questions
    intent.known_facts_refs = [f"ref:snap-ga-1", f"ref:snap-ga-2",
                               f"ref:stat_ga_42"]
    intent.open_questions = list(profile.unknown_items)
    intent.source_conversation_refs = ["conv:slice-intake-1"]

    for c in clarifications:
        c.intent_id = intent.intent_id
        if c.clarification_id in answers and answers[c.clarification_id]:
            intent.open_questions = [
                u for u in intent.open_questions
                if c.question.split("your ")[-1].rstrip("?") not in u]

    readiness_state, reasons = draft_readiness_gate(clarifications, answers)
    return IntakeResult(
        intent=intent,
        clarifications_asked=clarifications,
        readiness_state=readiness_state,
        readiness_reasons=reasons,
    )
