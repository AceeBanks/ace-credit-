"""B4.C2-C3 — Personal and CEO Operating Contract tests.

Personal is a first-class product interface; CEO is a governed application
operator. Proves the six plan tests plus fail-closed injections:
  * Personal cannot call application.submit;
  * a casual revenue mention creates a fact proposal/candidate, not silent
    canonical mutation;
  * old unrelated grant-work transcript is excluded from a new brainstorming
    context;
  * CEO can operate with no raw Personal transcript given a complete
    IntentContract;
  * CEO requests clarification rather than guessing unresolved critical
    constraints;
  * CEO context excludes closed project chatter after archival.
"""
from __future__ import annotations

import copy

import pytest

from tools.g0.validate_role_contracts import (
    ROLE_CONTRACTS_PATH,
    load,
    validate,
)


@pytest.fixture(scope="module")
def contracts() -> dict:
    return load()


def test_personal_cannot_call_application_submit(contracts):
    prefixes = contracts["personal_contract"]["prohibited_capability_prefixes"]
    assert any(p == "application.submit" or p.startswith("application.submit")
               for p in prefixes)
    assert any(p == "submission." or p.startswith("submission.")
               for p in prefixes)
    assert contracts["personal_contract"]["canonical_mutation_allowed"] is False


def test_revenue_mention_creates_proposal_not_canonical_mutation(contracts):
    personal = contracts["personal_contract"]
    assert personal["fact_handling"] == "PROPOSAL_ONLY"
    assert "FACT_UPDATE_PROPOSAL" in personal["output_classes"]
    assert "MEMORY_CANDIDATE" in personal["output_classes"]
    # The inference policy must explicitly keep conversational inference
    # out of canonical truth
    assert "never written as canonical truth" in personal["inference_policy"]
    assert "ASSERTION" in personal["inference_policy"]


def test_old_transcript_excluded_from_brainstorming_context(contracts):
    personal = contracts["personal_contract"]
    assert "RAW_CLIENT_TRANSCRIPT_HISTORY" in personal["forbidden_context_classes"]
    assert "CLOSED_PROJECT_CHATTER" in personal["forbidden_context_classes"]
    # Brainstorming context comes from curated memory, not raw history
    assert "CURATED_RELATIONSHIP_MEMORY" in personal["context_classes"]
    assert "RAW_CLIENT_TRANSCRIPT_HISTORY" not in personal["context_classes"]


def test_ceo_operates_without_raw_transcript(contracts):
    ceo = contracts["ceo_contract"]
    assert ceo["raw_transcript_required"] is False
    assert ceo["operates_from"] == "INTENT_CONTRACT"
    assert "INTENT_CONTRACT" in ceo["context_classes"]
    assert "RAW_CLIENT_TRANSCRIPT" in ceo["forbidden_context_classes"]
    assert "HOLD_FULL_USER_CONVERSATION_HISTORY" in ceo["non_responsibilities"]


def test_ceo_clarifies_rather_than_guesses(contracts):
    ceo = contracts["ceo_contract"]
    assert ceo["unresolved_critical_input_behavior"] == "CLARIFICATION_REQUEST"
    assert "REQUEST_CLARIFICATION_WHEN_INTENT_DATA_INSUFFICIENT" in \
        ceo["responsibilities"]


def test_ceo_excludes_closed_project_chatter(contracts):
    ceo = contracts["ceo_contract"]
    assert ceo["closed_project_chatter"] == "EXCLUDED_BY_DEFAULT"
    assert "CLOSED_PROJECT_CHATTER" in ceo["forbidden_context_classes"]


# --- adversarial fail-closed -------------------------------------------------

def test_personal_canonical_mutation_fails():
    data = copy.deepcopy(load())
    data["personal_contract"]["canonical_mutation_allowed"] = True
    ok, report = validate(data)
    assert not ok
    assert any("canonical_mutation_allowed" in e for e in report["errors"])


def test_personal_proposal_only_violation_fails():
    data = copy.deepcopy(load())
    data["personal_contract"]["fact_handling"] = "DIRECT_MUTATION"
    ok, report = validate(data)
    assert not ok
    assert any("PROPOSAL_ONLY" in e for e in report["errors"])


def test_personal_missing_submission_prohibition_fails():
    data = copy.deepcopy(load())
    prefixes = data["personal_contract"]["prohibited_capability_prefixes"]
    data["personal_contract"]["prohibited_capability_prefixes"] = [
        p for p in prefixes if not p.startswith("submission.")]
    ok, report = validate(data)
    assert not ok
    assert any("submission." in e for e in report["errors"])


def test_personal_transcript_in_context_fails():
    data = copy.deepcopy(load())
    data["personal_contract"]["forbidden_context_classes"] = [
        c for c in data["personal_contract"]["forbidden_context_classes"]
        if c != "RAW_CLIENT_TRANSCRIPT_HISTORY"]
    ok, report = validate(data)
    assert not ok
    assert any("forbidden context classes missing" in e for e in report["errors"])


def test_ceo_transcript_required_fails():
    data = copy.deepcopy(load())
    data["ceo_contract"]["raw_transcript_required"] = True
    ok, report = validate(data)
    assert not ok
    assert any("raw_transcript_required" in e for e in report["errors"])


def test_ceo_operates_from_chat_fails():
    data = copy.deepcopy(load())
    data["ceo_contract"]["operates_from"] = "RAW_CONVERSATION"
    ok, report = validate(data)
    assert not ok
    assert any("operates_from" in e for e in report["errors"])


def test_ceo_guessing_behavior_fails():
    data = copy.deepcopy(load())
    data["ceo_contract"]["unresolved_critical_input_behavior"] = "GUESS_AND_CONTINUE"
    ok, report = validate(data)
    assert not ok
    assert any("CLARIFICATION_REQUEST" in e for e in report["errors"])


def test_ceo_closed_chatter_in_context_fails():
    data = copy.deepcopy(load())
    data["ceo_contract"]["forbidden_context_classes"] = [
        c for c in data["ceo_contract"]["forbidden_context_classes"]
        if c != "CLOSED_PROJECT_CHATTER"]
    ok, report = validate(data)
    assert not ok
    assert any("forbidden context classes missing" in e for e in report["errors"])


def test_missing_contract_fails():
    data = copy.deepcopy(load())
    del data["ceo_contract"]
    ok, report = validate(data)
    assert not ok
    assert any("ceo_contract missing" in e for e in report["errors"])


def test_clean_contracts_pass():
    ok, report = validate(load())
    assert ok, report["errors"]
    assert report["personal_responsibilities"] >= 10
    assert report["ceo_responsibilities"] >= 10
