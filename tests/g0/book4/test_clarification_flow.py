"""B4.C5 — Clarification Protocol tests.

Proves CEO obtains missing information without becoming a second client
relationship: no duplicate clarification when the answer is already canonical;
unresolved eligibility-critical questions block eligible status/draft
readiness; clarification answers update IntentContract versions instead of
silently mutating prior history; Personal never answers by inference. Plus
adversarial validator injections.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.intent_builder import (  # noqa: E402
    ClarificationRequest,
    IntentContract,
    amend_intent,
    build_intent,
    check_answer_available,
    draft_readiness_gate,
)
from tools.g0.validate_intent_clarification import (  # noqa: E402
    validate_clarification_policy,
    validate_clarification_schema,
)


def _intent() -> IntentContract:
    return build_intent(
        tenant_id="tenant-georgia-youth",
        client_actor_id="user-7",
        organization_id="org-after-school",
        intent_type="BUILD_APPLICATION",
        objective="build application for after-school program funding",
        authority_scope="RESEARCH_AND_DRAFT_ONLY",
        confidence_state="MEDIUM",
        open_questions=["is the program a pilot or permanent?"],
    )


def _critical_question(intent_id: str) -> ClarificationRequest:
    return ClarificationRequest(
        clarification_id="clr-1",
        intent_id=intent_id,
        requesting_actor="CEO_HERMES",
        question_type="ELIGIBILITY_CRITICAL",
        question="Is the organization a registered 501(c)(3) in Georgia?",
        why_needed="hard eligibility rule requires tax-exempt status",
        blocking=True,
        expected_answer_type="BOOLEAN",
        answerable_from_canonical_state=False,
        created_at="2026-08-26T10:00:00Z",
    )


def test_no_duplicate_clarification_when_answer_already_canonical():
    canonical = {"organization.tax_exempt_status": "VERIFIED 501(c)(3)"}
    memory = {}
    assert check_answer_available(canonical, memory,
                                  "Is the organization a 501(c)(3)?") is True
    # Not available -> clarification justified
    assert check_answer_available({}, {}, "What is the target service area?") is False


def test_answer_in_personal_memory_avoids_duplicate():
    memory = {"preference.deadline_priority": "prioritize by deadline"}
    assert check_answer_available({}, memory,
                                  "How should opportunities be prioritized?") is True


def test_unresolved_eligibility_critical_blocks_draft_readiness():
    intent = _intent()
    question = _critical_question(intent.intent_id)
    state, reasons = draft_readiness_gate([question], {})
    assert state == "BLOCKED_ELIGIBILITY"
    assert any("blocking eligibility-critical" in r for r in reasons)


def test_answered_critical_unblocks():
    intent = _intent()
    question = _critical_question(intent.intent_id)
    state, _ = draft_readiness_gate([question], {question.clarification_id: "yes"})
    assert state == "DRAFT_READY"


def test_non_blocking_question_only_flags():
    intent = _intent()
    q = ClarificationRequest(
        clarification_id="clr-2", intent_id=intent.intent_id,
        requesting_actor="CEO_HERMES", question_type="PREFERENCE_CONFIRMATION",
        question="Should drafts be surfaced before the full package?",
        why_needed="client preference", blocking=False,
        expected_answer_type="BOOLEAN",
        answerable_from_canonical_state=False,
        created_at="2026-08-26T10:05:00Z")
    state, reasons = draft_readiness_gate([q], {})
    assert state == "DRAFT_READY_WITH_FLAGS"


def test_no_questions_is_ready():
    state, reasons = draft_readiness_gate([], {})
    assert state == "DRAFT_READY"
    assert reasons == []


def test_clarification_answer_amends_intent_version():
    original = _intent()
    amended = amend_intent(original,
                           user_statements=["The program is a pilot for now"])
    assert amended.version == 2
    assert amended.supersedes_intent_id == original.intent_id
    assert amended.user_assertions[0].status == "ASSERTION"
    # Prior intent history is untouched (append-only)
    assert original.version == 1
    assert original.open_questions == ["is the program a pilot or permanent?"]
    assert amended.open_questions == ["is the program a pilot or permanent?"]


def test_clarification_schema_is_strict():
    errors: list[str] = []
    validate_clarification_schema(errors)
    assert errors == []
    import json
    from pathlib import Path
    schema = json.loads(
        (Path(__file__).parents[3] / "schemas/g0/agents"
         / "clarification_request.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["blocking"]["type"] == "boolean"
    assert "why_needed" in schema["required"]
    assert "blocking" in schema["required"]
    assert "CEO_HERMES" in schema["properties"]["requesting_actor"]["enum"]
    assert "PERSONAL_HERMES" in schema["properties"]["requesting_actor"]["enum"]


# --- validator adversarial checks -------------------------------------------

def test_policy_clean():
    errors: list[str] = []
    validate_clarification_policy(errors)
    assert errors == []


def test_policy_unknown_question_type_fails(monkeypatch, tmp_path):
    import tools.g0.validate_intent_clarification as mod
    data = {
        "question_types": ["ELIGIBILITY_CRITICAL", "BOGUS_TYPE"],
        "expected_answer_types": ["BOOLEAN"],
        "rules": [
            {"rule_id": f"CLARIFY-{n:03d}", "title": "t", "rule": "r",
             "enforcement": "MUST"} for n in range(1, 7)
        ],
        "blocking_effects": {
            "eligibility_critical_unanswered": "BLOCK_ELIGIBILITY_AND_DRAFT_READINESS",
        },
        "escalation": {"max_repeat_blocking_questions": 2,
                       "escalation_flow": "HUMAN_REVIEW_QUEUE"},
    }
    p = tmp_path / "clarification_policy.yaml"
    import yaml
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    errors: list[str] = []
    validate_clarification_policy(errors)
    assert any("unknown question types" in e for e in errors)


def test_policy_missing_rule_fails(monkeypatch):
    import tools.g0.validate_intent_clarification as mod
    data = {
        "question_types": ["MISSING_REQUIRED_INPUT", "AMBIGUOUS_INPUT",
                           "CONFLICTING_INPUT", "ELIGIBILITY_CRITICAL",
                           "SCOPE_CONFIRMATION", "PREFERENCE_CONFIRMATION"],
        "expected_answer_types": ["FREE_TEXT", "SINGLE_CHOICE", "DATE",
                                  "MONEY", "BOOLEAN", "LOCATION"],
        "rules": [
            {"rule_id": f"CLARIFY-{n:03d}", "title": "t", "rule": "r",
             "enforcement": "MUST"} for n in range(1, 6)
        ],
        "blocking_effects": {
            "eligibility_critical_unanswered": "BLOCK_ELIGIBILITY_AND_DRAFT_READINESS",
        },
        "escalation": {"max_repeat_blocking_questions": 2,
                       "escalation_flow": "HUMAN_REVIEW_QUEUE"},
    }
    errors: list[str] = []
    # direct policy validation with monkeypatched load
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_clarification_policy(errors)
    assert any("CLARIFY-006" in e for e in errors)
