"""B7.C18 — Evaluator governance tests.

Declarations, LLM judge advisory role, deterministic-truth-wins,
independence (no self-evaluation), calibration/bias measurement.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.evaluators import (  # noqa: E402
    EvaluatorDeclaration,
    EvaluatorError,
    EvaluatorRegistry,
    LLMJudge,
    calibration_report,
    independence_ok,
)


def test_declaration_requires_measures_and_cannot_measure():
    with pytest.raises(EvaluatorError):
        EvaluatorDeclaration(evaluator_id="e1", evaluator_type="llm_judge",
                             measures="clarity", cannot_measure="",
                             version="m1")
    ok = EvaluatorDeclaration(evaluator_id="e1", evaluator_type="llm_judge",
                              measures="clarity", cannot_measure="facts",
                              version="m1")
    assert ok.measures == "clarity"


def test_llm_judge_requires_version():
    with pytest.raises(EvaluatorError):
        EvaluatorDeclaration(evaluator_id="e1", evaluator_type="llm_judge",
                             measures="x", cannot_measure="y", version="")


def test_unknown_evaluator_type_rejected():
    with pytest.raises(EvaluatorError):
        EvaluatorDeclaration(evaluator_id="e1", evaluator_type="oracle",
                             measures="x", cannot_measure="y", version="1")


def test_registry_register_and_get():
    reg = EvaluatorRegistry()
    decl = EvaluatorDeclaration(evaluator_id="det-1",
                                evaluator_type="deterministic_assertion",
                                measures="eligibility",
                                cannot_measure="tone", version="1.0")
    reg.register(decl)
    assert reg.get("det-1") is decl
    with pytest.raises(EvaluatorError):
        reg.get("nope")


def test_llm_judge_is_advisory():
    judge = LLMJudge(judge_id="j1", model_version="m-v2",
                     known_biases=("verbosity_bias", "position_bias"))
    score = judge.score(dimension="clarity", candidate_id="c1",
                        sample={}, score=0.9, confidence=0.6)
    assert score["role"] == "ADVISORY"
    assert "factuality" in score["cannot_override"]
    assert "security" in score["cannot_override"]


def test_deterministic_truth_wins_on_conflict():
    judge = LLMJudge("j1", "m1")
    conflict = LLMJudge.conflict_with_deterministic(
        deterministic_result={"all_pass": False}, judge_score=0.95)
    assert conflict["judge_overridden"] is True
    agree = LLMJudge.conflict_with_deterministic(
        deterministic_result={"all_pass": True}, judge_score=0.5)
    assert agree["judge_overridden"] is False


def test_candidate_cannot_be_sole_judge_of_self():
    decl = EvaluatorDeclaration(evaluator_id="j1", evaluator_type="llm_judge",
                                measures="quality", cannot_measure="facts",
                                version="m1",
                                required_independence="independent_of_candidate")
    assert independence_ok(candidate_id="c1", evaluator=decl,
                           judge_owner="c2")
    assert not independence_ok(candidate_id="c1", evaluator=decl,
                               judge_owner="c1")


def test_calibration_report_measures_bias():
    agreements = [
        {"agrees": True, "position_bias": False, "verbosity_bias": False},
        {"agrees": True, "position_bias": True, "verbosity_bias": False},
        {"agrees": False, "position_bias": False, "verbosity_bias": True},
    ]
    r = calibration_report(agreements)
    assert r["sample_size"] == 3
    assert r["agreement_rate"] == round(2 / 3, 3)
    assert r["positional_bias"] == round(1 / 3, 3)
    assert r["verbosity_bias"] == round(1 / 3, 3)


def test_calibration_report_empty_is_null_not_zero():
    r = calibration_report([])
    assert r["sample_size"] == 0
    assert r["agreement_rate"] is None  # no fake precision
