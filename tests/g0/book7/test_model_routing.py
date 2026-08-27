"""B7.C16 — Model & routing evaluation tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.routing_eval import (  # noqa: E402
    ModelRun,
    PARSER_LOCATOR_LINEAGE_THRESHOLD,
    ROUTING_COST_JUSTIFICATION_FACTOR,
    THRESHOLD_CALIBRATION,
    compare_models,
    parser_eval,
    routing_must_beat_baseline,
    routing_structured_output_guard,
)


def _baseline() -> ModelRun:
    return ModelRun(model_id="m-small", model_version="1",
                    correctness=0.85, factuality=0.9,
                    instruction_adherence=0.9, structured_output_valid=0.7,
                    latency_ms=100, cost_usd=0.01, context_tokens=8000,
                    tool_use_reliable=0.9)


def test_model_compare_clean_improvement():
    cand = ModelRun(model_id="m-strong", model_version="2",
                    correctness=0.95, factuality=0.95,
                    instruction_adherence=0.95, structured_output_valid=0.9,
                    latency_ms=300, cost_usd=0.05, context_tokens=16000,
                    tool_use_reliable=0.95)
    r = compare_models(_baseline(), cand)
    assert r["promotable"] is True
    assert r["deltas"]["correctness"] > 0
    assert r["deltas"]["cost_usd"] < 0  # cost higher -> negative delta


def test_model_safety_regression_vetoes():
    cand = ModelRun(model_id="m-danger", model_version="2",
                    correctness=0.99, factuality=0.99,
                    instruction_adherence=0.99, structured_output_valid=0.99,
                    latency_ms=50, cost_usd=0.001, context_tokens=4000,
                    tool_use_reliable=0.99, safety_regression=True)
    r = compare_models(_baseline(), cand)
    assert r["hard_veto"] is True
    assert r["promotable"] is False
    assert r["veto_reason"] == "safety regression"


def test_model_provider_unavailable_vetoes():
    cand = ModelRun(model_id="m-down", model_version="2",
                    correctness=0.99, factuality=0.99,
                    instruction_adherence=0.99, structured_output_valid=0.99,
                    latency_ms=50, cost_usd=0.001, context_tokens=4000,
                    tool_use_reliable=0.99, provider_available=False)
    r = compare_models(_baseline(), cand)
    assert r["hard_veto"] is True


def test_routing_justified():
    r = routing_must_beat_baseline(
        simple_cost=0.02, routed_cost=0.01,
        simple_correctness=0.8, routed_correctness=0.85)
    assert r["proven_value"] is True


def test_routing_not_justified_when_not_cheaper():
    r = routing_must_beat_baseline(
        simple_cost=0.01, routed_cost=0.0099,  # only 1% cheaper
        simple_correctness=0.8, routed_correctness=0.85)
    assert r["proven_value"] is False


def test_routing_not_justified_when_less_correct():
    r = routing_must_beat_baseline(
        simple_cost=0.02, routed_cost=0.01,
        simple_correctness=0.9, routed_correctness=0.8)
    assert r["proven_value"] is False


def test_routing_structured_output_guard():
    assert routing_structured_output_guard(
        routed_model_structured_reliable=True,
        task_requires_structured=True)
    assert not routing_structured_output_guard(
        routed_model_structured_reliable=False,
        task_requires_structured=True)
    assert routing_structured_output_guard(
        routed_model_structured_reliable=False,
        task_requires_structured=False)


def test_model_dimensions_visible_not_one_score():
    cand = ModelRun(model_id="m-strong", model_version="2",
                    correctness=0.95, factuality=0.95,
                    instruction_adherence=0.95, structured_output_valid=0.9,
                    latency_ms=300, cost_usd=0.05, context_tokens=16000,
                    tool_use_reliable=0.95)
    r = compare_models(_baseline(), cand)
    assert "correctness" in r["deltas"]
    assert "factuality" in r["deltas"]
    assert "latency_ms" in r["deltas"]
    assert "cost_usd" in r["deltas"]


def test_thresholds_marked_provisional_pending_book8_evidence():
    """P2-01 repair: numeric routing/parser thresholds are machine-readably
    labeled PROVISIONAL_G0_DEFAULT, recalibrate from Book 8 evidence — not
    claimed empirically optimal."""
    assert THRESHOLD_CALIBRATION["status"] == "PROVISIONAL_G0_DEFAULT"
    assert THRESHOLD_CALIBRATION["recalibrate_from"] == \
        "BOOK8_MEASURED_EVIDENCE"
    params = {p["name"]: p["value"]
              for p in THRESHOLD_CALIBRATION["parameters"]}
    assert params["routing_cost_justification_factor"] == \
        ROUTING_COST_JUSTIFICATION_FACTOR
    assert params["parser_locator_lineage_threshold"] == \
        PARSER_LOCATOR_LINEAGE_THRESHOLD
    # the gates actually consume the labeled constants
    assert routing_must_beat_baseline(simple_cost=1.0, routed_cost=0.89,
                                      simple_correctness=0.9,
                                      routed_correctness=0.9)["proven_value"]
    pe = parser_eval(text_fidelity=1.0, heading_fidelity=1.0,
                     table_fidelity=1.0,
                     locator_lineage=PARSER_LOCATOR_LINEAGE_THRESHOLD,
                     extraction_errors=0, latency_ms=1.0, cost_usd=0.001,
                     failure_detected=False)
    assert pe["passes_locator_hard_gate"] is True
