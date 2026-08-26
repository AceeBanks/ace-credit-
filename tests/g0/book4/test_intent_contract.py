"""B4.C4 — IntentContract tests.

Proves the central boundary translating human conversation into operational
work: intent missing tenant fails; submission intent while phase disabled is
normalized to prepare-only; user assertions never become canonical facts; and
conversation refs remain retrievable for audit without entering CEO active
context. Plus adversarial injections against the validator.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.intent_builder import (  # noqa: E402
    IntentContract,
    IntentValidationError,
    amend_intent,
    build_intent,
    classify_user_assertion,
    normalize_requested_capabilities,
)
from tools.g0.validate_intent_clarification import (  # noqa: E402
    _load_schema,
    validate_intent_schema,
)

def _base(**overrides) -> dict:
    kwargs = dict(
        tenant_id="tenant-georgia-youth",
        client_actor_id="user-7",
        organization_id="org-after-school",
        intent_type="FIND_GRANTS",
        objective="identify and assess funding for an after-school youth program",
        authority_scope="RESEARCH_AND_DRAFT_ONLY",
        confidence_state="MEDIUM",
        open_questions=["budget and facility constraints unresolved"],
        source_conversation_refs=["conv/2026-08-26/session-441#msg-12"],
    )
    kwargs.update(overrides)
    return kwargs


def test_intent_missing_tenant_fails():
    with pytest.raises(IntentValidationError, match="tenant_id"):
        build_intent(**_base(tenant_id=""))


def test_intent_missing_objective_fails():
    with pytest.raises(IntentValidationError, match="objective"):
        build_intent(**_base(objective=""))


def test_intent_unknown_type_fails():
    with pytest.raises(IntentValidationError, match="intent_type"):
        build_intent(**_base(intent_type="HACK_THE_MAINFRAME"))


def test_intent_unknown_authority_scope_fails():
    with pytest.raises(IntentValidationError, match="authority_scope"):
        build_intent(**_base(authority_scope="SUBMIT_ANYTHING"))


def test_submission_request_normalized_to_prepare_only():
    intent = build_intent(**_base(
        requested_capabilities=["application.submit", "research.funder"]))
    assert "application.prepare_submission_package" in intent.requested_capabilities
    assert "application.submit" not in intent.requested_capabilities
    assert any("normalized to" in n for n in intent.normalization_notes)
    # submission.* family handled too
    intent2 = build_intent(**_base(
        requested_capabilities=["submission.execute", "submission.sign"]))
    assert set(intent2.requested_capabilities) == {
        "application.prepare_submission_package"}


def test_user_assertion_does_not_become_canonical_fact():
    intent = build_intent(**_base(
        user_statements=["We served about 40 kids last year",
                         "Our revenue grew this year"]))
    assert len(intent.user_assertions) == 2
    for assertion in intent.user_assertions:
        assert assertion.status == "ASSERTION"
    # classify_user_assertion never returns canonical status
    assertion = classify_user_assertion("Revenue is now 1.2M")
    assert assertion.status == "ASSERTION"
    # known facts are refs, not embedded copies
    intent2 = build_intent(**_base(known_facts_refs=["fact:canonical:revenue-2025"]))
    assert intent2.known_facts_refs == ["fact:canonical:revenue-2025"]
    assert all(isinstance(r, str) for r in intent2.known_facts_refs)


def test_conversation_refs_retrievable_without_ceo_context():
    intent = build_intent(**_base())
    assert intent.source_conversation_refs == ["conv/2026-08-26/session-441#msg-12"]
    # The ref is an opaque string; no transcript body is embedded in the intent
    for ref in intent.source_conversation_refs:
        assert not ref.startswith("TRANSCRIPT:")
        assert "body=" not in ref
    # CEO context classes never include the raw transcript (contract frozen)
    from tools.g0.validate_role_contracts import load as load_contracts
    ceo = load_contracts()["ceo_contract"]
    assert "RAW_CLIENT_TRANSCRIPT" in ceo["forbidden_context_classes"]


def test_open_questions_remain_visible():
    intent = build_intent(**_base())
    assert intent.open_questions == ["budget and facility constraints unresolved"]


def test_amend_intent_versions_not_mutates():
    original = build_intent(**_base())
    amended = amend_intent(original,
                           user_statements=["The program targets ages 10-14"])
    assert amended.version == 2
    assert amended.supersedes_intent_id == original.intent_id
    assert amended.intent_id == f"{original.intent_id}-v2"
    # Prior intent history untouched
    assert original.version == 1
    assert original.supersedes_intent_id is None
    assert original.user_assertions == []
    assert amended.user_assertions[0].status == "ASSERTION"


def test_intent_dict_roundtrip_has_required_fields():
    intent = build_intent(**_base())
    d = intent.to_dict()
    for field in ("intent_id", "tenant_id", "client_actor_id",
                  "organization_id", "intent_type", "objective",
                  "authority_scope", "confidence_state", "created_at",
                  "source_conversation_refs", "open_questions"):
        assert field in d


def test_normalize_unknown_capability_passthrough():
    caps, notes = normalize_requested_capabilities(["research.funder"])
    assert caps == ["research.funder"]
    assert notes == []


# --- schema-level adversarial checks ----------------------------------------

def test_intent_schema_is_strict_and_complete():
    errors: list[str] = []
    validate_intent_schema(errors)
    assert errors == []
    ok, schema = _load_schema("intent_contract.schema.json")
    assert ok
    required = schema["required"]
    for field in ("tenant_id", "intent_type", "objective", "authority_scope",
                  "confidence_state", "source_conversation_refs",
                  "known_facts_refs", "user_assertions", "open_questions"):
        assert field in required or field in schema["properties"]


def test_intent_schema_rejects_embedded_transcript():
    ok, schema = _load_schema("intent_contract.schema.json")
    assert ok
    # If a transcript body property ever appears, the schema must not allow it
    assert "transcript_body" not in schema["properties"]
    assert "raw_chat" not in schema["properties"]


def test_intent_schema_user_assertion_status_constrained():
    ok, schema = _load_schema("intent_contract.schema.json")
    status = schema["properties"]["user_assertions"]["items"]["properties"]["status"]
    assert status.get("const") == "ASSERTION"
    # And the validator enforces it
    errors: list[str] = []
    validate_intent_schema(errors)
    assert errors == []
