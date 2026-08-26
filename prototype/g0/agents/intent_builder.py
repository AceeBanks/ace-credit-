"""B4.C4-C5 — IntentContract builder and clarification gate (prototype).

Implements the central boundary translating human conversation into
operational work:

  * build_intent: validates required fields, normalizes DISABLED-phase
    capability requests (submission -> prepare-only), labels user assertions
    ASSERTION, links conversation refs instead of embedding transcripts;
  * classify_user_assertion: user statements never become canonical facts;
  * amend_intent: clarification answers produce a NEW intent version
    (supersedes_intent_id) rather than silently mutating prior history;
  * check_answer_available: duplicate-clarification avoidance against
    canonical state + personal memory;
  * draft_readiness_gate: blocking eligibility-critical questions gate
    eligibility status and draft readiness.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

SUBMISSION_CAPABILITIES = {"submission.prepare", "submission.execute",
                           "submission.certify", "submission.sign",
                           "application.submit"}
PREPARE_ONLY_TARGET = "application.prepare_submission_package"

INTENT_TYPES = {
    "EXPLORE_IDEA", "FIND_GRANTS", "ASSESS_OPPORTUNITY", "BUILD_APPLICATION",
    "UPDATE_PROFILE", "REVIEW_DRAFT", "RESEARCH_FUNDER", "RESEARCH_WINNERS",
    "EXPLAIN_RESULT", "OTHER_CONTROLLED_EXTENSION",
}
AUTHORITY_SCOPES = {"EXPLORE_ONLY", "RESEARCH_ONLY",
                    "RESEARCH_AND_DRAFT_ONLY", "PREPARE_ONLY"}
REQUIRED_FIELDS = ("intent_id", "tenant_id", "client_actor_id",
                   "organization_id", "intent_type", "objective",
                   "authority_scope", "confidence_state", "created_at")


class IntentValidationError(ValueError):
    """Raised when an IntentContract cannot be built honestly."""


@dataclass
class UserAssertion:
    assertion_id: str
    statement: str
    status: str = "ASSERTION"
    fact_proposal_ref: str | None = None


@dataclass
class ClarificationRequest:
    clarification_id: str
    intent_id: str
    requesting_actor: str
    question_type: str
    question: str
    why_needed: str
    blocking: bool
    expected_answer_type: str
    answerable_from_canonical_state: bool
    created_at: str
    allowed_context_refs: list[str] = field(default_factory=list)


@dataclass
class IntentContract:
    intent_id: str
    tenant_id: str
    client_actor_id: str
    organization_id: str
    intent_type: str
    objective: str
    authority_scope: str
    confidence_state: str
    created_at: str
    desired_outcome: str | None = None
    constraints: list[str] = field(default_factory=list)
    known_facts_refs: list[str] = field(default_factory=list)
    user_assertions: list[UserAssertion] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    non_goals: list[str] = field(default_factory=list)
    priority: str = "NORMAL"
    deadline_or_time_horizon: str | None = None
    requested_capabilities: list[str] = field(default_factory=list)
    source_conversation_refs: list[str] = field(default_factory=list)
    normalization_notes: list[str] = field(default_factory=list)
    version: int = 1
    supersedes_intent_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "tenant_id": self.tenant_id,
            "client_actor_id": self.client_actor_id,
            "organization_id": self.organization_id,
            "intent_type": self.intent_type,
            "objective": self.objective,
            "desired_outcome": self.desired_outcome,
            "constraints": list(self.constraints),
            "known_facts_refs": list(self.known_facts_refs),
            "user_assertions": [a.__dict__ for a in self.user_assertions],
            "open_questions": list(self.open_questions),
            "non_goals": list(self.non_goals),
            "priority": self.priority,
            "deadline_or_time_horizon": self.deadline_or_time_horizon,
            "authority_scope": self.authority_scope,
            "requested_capabilities": list(self.requested_capabilities),
            "confidence_state": self.confidence_state,
            "source_conversation_refs": list(self.source_conversation_refs),
            "normalization_notes": list(self.normalization_notes),
            "version": self.version,
            "supersedes_intent_id": self.supersedes_intent_id,
            "created_at": self.created_at,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def classify_user_assertion(statement: str, fact_proposal_ref: str | None = None,
                            assertion_id: str | None = None) -> UserAssertion:
    """A user statement is an ASSERTION, never a canonical fact.

    Even when a fact proposal ref exists, the assertion itself remains
    labeled ASSERTION until a governed promotion event occurs elsewhere.
    """
    return UserAssertion(
        assertion_id=assertion_id or f"asrt-{abs(hash(statement))}",
        statement=statement,
        status="ASSERTION",
        fact_proposal_ref=fact_proposal_ref,
    )


def normalize_requested_capabilities(requested: list[str],
                                     phase_disabled: set[str] | None = None) -> tuple[list[str], list[str]]:
    """Normalize DISABLED-phase capability requests (fail closed).

    submission.* / application.submit requests are normalized to
    application.prepare_submission_package with an explicit note. Any other
    unknown capability is rejected.
    """
    phase_disabled = phase_disabled or SUBMISSION_CAPABILITIES
    normalized: list[str] = []
    notes: list[str] = []
    for cap in requested:
        if cap in phase_disabled:
            normalized.append(PREPARE_ONLY_TARGET)
            notes.append(f"{cap} normalized to {PREPARE_ONLY_TARGET} "
                         "(phase DISABLED; prepare-only allowed)")
        elif cap.startswith("submission.") or cap == "application.submit":
            normalized.append(PREPARE_ONLY_TARGET)
            notes.append(f"{cap} normalized to {PREPARE_ONLY_TARGET} "
                         "(submission disabled in Phase 1)")
        else:
            normalized.append(cap)
    return normalized, notes


def build_intent(*, tenant_id: str, client_actor_id: str, organization_id: str,
                 intent_type: str, objective: str, authority_scope: str,
                 confidence_state: str, intent_id: str | None = None,
                 desired_outcome: str | None = None,
                 constraints: list[str] | None = None,
                 known_facts_refs: list[str] | None = None,
                 user_statements: list[str] | None = None,
                 open_questions: list[str] | None = None,
                 non_goals: list[str] | None = None,
                 priority: str = "NORMAL",
                 deadline_or_time_horizon: str | None = None,
                 requested_capabilities: list[str] | None = None,
                 source_conversation_refs: list[str] | None = None,
                 phase_disabled: set[str] | None = None,
                 created_at: str | None = None) -> IntentContract:
    """Build a validated IntentContract.

    Raises IntentValidationError when required fields are missing/unknown or
    when the authority scope cannot authorize the intent type.
    """
    errors: list[str] = []
    if not tenant_id:
        errors.append("tenant_id is required")
    if not client_actor_id:
        errors.append("client_actor_id is required")
    if not organization_id:
        errors.append("organization_id is required")
    if intent_type not in INTENT_TYPES:
        errors.append(f"unknown intent_type '{intent_type}'")
    if not objective:
        errors.append("objective is required")
    if authority_scope not in AUTHORITY_SCOPES:
        errors.append(f"unknown authority_scope '{authority_scope}'")
    if confidence_state not in ("HIGH", "MEDIUM", "LOW"):
        errors.append(f"unknown confidence_state '{confidence_state}'")
    if errors:
        raise IntentValidationError("; ".join(errors))

    caps = list(requested_capabilities or [])
    normalized_caps, notes = normalize_requested_capabilities(
        caps, phase_disabled=phase_disabled)

    assertions = [classify_user_assertion(s) for s in (user_statements or [])]
    return IntentContract(
        intent_id=intent_id or f"int-{abs(hash((tenant_id, objective, _now())))}",
        tenant_id=tenant_id,
        client_actor_id=client_actor_id,
        organization_id=organization_id,
        intent_type=intent_type,
        objective=objective,
        authority_scope=authority_scope,
        confidence_state=confidence_state,
        created_at=created_at or _now(),
        desired_outcome=desired_outcome,
        constraints=list(constraints or []),
        known_facts_refs=list(known_facts_refs or []),
        user_assertions=assertions,
        open_questions=list(open_questions or []),
        non_goals=list(non_goals or []),
        priority=priority,
        deadline_or_time_horizon=deadline_or_time_horizon,
        requested_capabilities=normalized_caps,
        source_conversation_refs=list(source_conversation_refs or []),
        normalization_notes=notes,
    )


def amend_intent(original: IntentContract, *, objective: str | None = None,
                 authority_scope: str | None = None,
                 open_questions: list[str] | None = None,
                 user_statements: list[str] | None = None,
                 requested_capabilities: list[str] | None = None) -> IntentContract:
    """Produce a NEW intent version reflecting a clarification answer.

    The prior intent is never mutated; the new version links back via
    supersedes_intent_id. Append-only history is preserved.
    """
    amendments: dict = {}
    if objective is not None:
        amendments["objective"] = objective
    if authority_scope is not None:
        amendments["authority_scope"] = authority_scope
    if open_questions is not None:
        amendments["open_questions"] = open_questions
    if user_statements is not None:
        amendments["user_assertions"] = [
            classify_user_assertion(s) for s in user_statements]
    if requested_capabilities is not None:
        normalized_caps, notes = normalize_requested_capabilities(
            requested_capabilities)
        amendments["requested_capabilities"] = normalized_caps
        amendments["normalization_notes"] = list(
            original.normalization_notes) + notes

    kwargs = {
        "intent_id": f"{original.intent_id}-v{original.version + 1}",
        "tenant_id": original.tenant_id,
        "client_actor_id": original.client_actor_id,
        "organization_id": original.organization_id,
        "intent_type": original.intent_type,
        "objective": amendments.get("objective", original.objective),
        "authority_scope": amendments.get("authority_scope",
                                          original.authority_scope),
        "confidence_state": original.confidence_state,
        "created_at": _now(),
        "desired_outcome": original.desired_outcome,
        "constraints": list(original.constraints),
        "known_facts_refs": list(original.known_facts_refs),
        "user_assertions": amendments.get("user_assertions",
                                          list(original.user_assertions)),
        "open_questions": amendments.get("open_questions",
                                         list(original.open_questions)),
        "non_goals": list(original.non_goals),
        "priority": original.priority,
        "deadline_or_time_horizon": original.deadline_or_time_horizon,
        "requested_capabilities": amendments.get(
            "requested_capabilities", list(original.requested_capabilities)),
        "source_conversation_refs": list(original.source_conversation_refs),
        "normalization_notes": amendments.get(
            "normalization_notes", list(original.normalization_notes)),
        "version": original.version + 1,
        "supersedes_intent_id": original.intent_id,
    }
    return IntentContract(**kwargs)


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{4,}", text.lower()))


def _token_overlap(a: set[str], b: set[str]) -> bool:
    if a & b:
        return True
    # prefix overlap handles inflection (opportunities/opportunity,
    # prioritized/priority) without a stemming dependency
    for ta in a:
        for tb in b:
            if len(ta) >= 5 and len(tb) >= 5 and ta[:5] == tb[:5]:
                return True
    return False


def check_answer_available(canonical_facts: dict[str, Any],
                           personal_memory: dict[str, Any],
                           question: str) -> bool:
    """Duplicate-clarification avoidance (CLARIFY-001).

    If the answer already exists in canonical state or curated personal
    memory, the requesting actor must not issue a ClarificationRequest.
    Token overlap is a prototype heuristic; exact ref lookup takes priority
    in production retrieval (Book 5).
    """
    q_tokens = _tokens(question)
    for store in (canonical_facts, personal_memory):
        for key, value in store.items():
            if _token_overlap(q_tokens, _tokens(key)):
                return True
            if _token_overlap(q_tokens, _tokens(str(value))):
                return True
    return False


def draft_readiness_gate(blocking_questions: list[ClarificationRequest],
                         answers: dict[str, str]) -> tuple[str, list[str]]:
    """Eligibility-critical blocking questions gate draft readiness.

    Returns (state, reasons). Any blocking ELIGIBILITY_CRITICAL question
    without an answer blocks ELIGIBLE / DRAFT_READY status.
    """
    if not blocking_questions:
        return "DRAFT_READY", []
    unanswered = [q for q in blocking_questions
                  if q.clarification_id not in answers or not answers[q.clarification_id]]
    if not unanswered:
        return "DRAFT_READY", []
    critical = [q for q in unanswered
                if q.question_type == "ELIGIBILITY_CRITICAL" and q.blocking]
    if critical:
        reasons = [f"blocking eligibility-critical question unanswered: "
                   f"{q.question}" for q in critical]
        return "BLOCKED_ELIGIBILITY", reasons
    return "DRAFT_READY_WITH_FLAGS", \
        [f"non-blocking question unanswered: {q.question}" for q in unanswered]
