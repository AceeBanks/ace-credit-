"""B7.C11 — Personal Hermes evaluation tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.agent_eval import (  # noqa: E402
    intent_contract_validity,
    personal_hermes_eval,
    personal_intent_semantic_preservation,
)


def test_personal_hermes_clean_pass():
    r = personal_hermes_eval(
        used_canonical_state_before_asking=True,
        unnecessary_questions=0,
        intent_type_valid=True,
        performed_ceo_only_operation=False,
        cross_project_contamination=False,
        uncertainty_communicated=True,
        explanation_packet_used=True)
    assert r["all_pass"] is True


def test_personal_hermes_ceo_work_fails():
    r = personal_hermes_eval(
        used_canonical_state_before_asking=True,
        unnecessary_questions=0,
        intent_type_valid=True,
        performed_ceo_only_operation=True,
        cross_project_contamination=False,
        uncertainty_communicated=True,
        explanation_packet_used=True)
    assert r["all_pass"] is False
    assert r["failed"] == 1


def test_personal_hermes_unnecessary_question_fails():
    r = personal_hermes_eval(
        used_canonical_state_before_asking=False,
        unnecessary_questions=2,
        intent_type_valid=True,
        performed_ceo_only_operation=False,
        cross_project_contamination=False,
        uncertainty_communicated=True,
        explanation_packet_used=True)
    assert r["all_pass"] is False


def test_personal_hermes_cross_project_contamination_fails():
    r = personal_hermes_eval(
        used_canonical_state_before_asking=True,
        unnecessary_questions=0,
        intent_type_valid=True,
        performed_ceo_only_operation=False,
        cross_project_contamination=True,
        uncertainty_communicated=True,
        explanation_packet_used=True)
    assert r["all_pass"] is False


def test_warm_personality_cannot_compensate_wrong_intent():
    # "warmer personality" is not a metric; wrong intent translation is
    # caught by intent validity + semantic preservation
    r = personal_hermes_eval(
        used_canonical_state_before_asking=True,
        unnecessary_questions=0,
        intent_type_valid=False,
        performed_ceo_only_operation=False,
        cross_project_contamination=False,
        uncertainty_communicated=True,
        explanation_packet_used=True)
    assert r["all_pass"] is False
    assert any(x["metric_id"] == "P1_intent_capture" and not x["passed"]
               for x in r["results"])


def test_intent_contract_validity_required_fields():
    ok = intent_contract_validity(
        intent={"intent_id": "i1", "tenant_id": "t", "intent_type": "FIND_GRANTS"},
        required_fields=("intent_id", "tenant_id", "intent_type"))
    assert ok.passed
    missing = intent_contract_validity(
        intent={"intent_id": "i1"},
        required_fields=("intent_id", "tenant_id", "intent_type"))
    assert not missing.passed
    assert "tenant_id" in missing.detail


def test_intent_semantic_preservation():
    ok = personal_intent_semantic_preservation(
        client_idea="expand youth workforce program into two more Georgia counties",
        intent_objective="expand youth workforce program into two more Georgia counties")
    assert ok.passed
    drift = personal_intent_semantic_preservation(
        client_idea="expand youth workforce program into two more Georgia counties",
        intent_objective="purchase office furniture")
    assert not drift.passed
