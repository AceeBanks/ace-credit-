"""B7.C17 — Parser & retrieval evaluation tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.routing_eval import (  # noqa: E402
    parser_compare,
    parser_eval,
    retrieval_compare,
    retrieval_task_appropriateness,
    stale_authority_check,
)


def test_parser_eval_metrics():
    r = parser_eval(text_fidelity=0.95, heading_fidelity=0.9,
                    table_fidelity=0.85, locator_lineage=0.95,
                    extraction_errors=2, latency_ms=500, cost_usd=0.01,
                    failure_detected=True)
    assert r["passes_locator_hard_gate"] is True


def test_parser_locator_gate_fails():
    r = parser_eval(text_fidelity=0.99, heading_fidelity=0.99,
                    table_fidelity=0.99, locator_lineage=0.5,
                    extraction_errors=0, latency_ms=100, cost_usd=0.001,
                    failure_detected=False)
    assert r["passes_locator_hard_gate"] is False


def test_parser_compare_candidate_wins():
    baseline = parser_eval(text_fidelity=0.9, heading_fidelity=0.9,
                           table_fidelity=0.7, locator_lineage=0.9,
                           extraction_errors=4, latency_ms=500,
                           cost_usd=0.01, failure_detected=True)
    candidate = parser_eval(text_fidelity=0.95, heading_fidelity=0.95,
                            table_fidelity=0.9, locator_lineage=0.95,
                            extraction_errors=1, latency_ms=600,
                            cost_usd=0.02, failure_detected=True)
    r = parser_compare(baseline, candidate)
    assert r["verdict"] == "CANDIDATE"


def test_parser_compare_table_loss_blocks_candidate():
    # C29-5: faster parser loses table cells -> cannot win
    baseline = parser_eval(text_fidelity=0.9, heading_fidelity=0.9,
                           table_fidelity=0.9, locator_lineage=0.9,
                           extraction_errors=2, latency_ms=500,
                           cost_usd=0.01, failure_detected=True)
    candidate = parser_eval(text_fidelity=0.95, heading_fidelity=0.95,
                            table_fidelity=0.5, locator_lineage=0.95,
                            extraction_errors=1, latency_ms=200,
                            cost_usd=0.005, failure_detected=True)
    r = parser_compare(baseline, candidate)
    assert r["verdict"] == "BASELINE"


def test_retrieval_exact_lookup_does_not_reward_semantic():
    assert retrieval_task_appropriateness(task_kind="deadline_lookup",
                                          semantic_used=False)
    assert not retrieval_task_appropriateness(task_kind="deadline_lookup",
                                              semantic_used=True)


def test_retrieval_compare_exact_wins_for_exact_tasks():
    r = retrieval_compare(exact_recall=1.0, semantic_recall=0.7,
                          exact_precision=1.0, semantic_precision=0.5,
                          task_kind="revision_lookup")
    assert r["appropriate_winner"] == "EXACT"
    assert r["semantic_rewarded_inappropriately"] is False


def test_retrieval_semantic_wins_for_research_tasks():
    r = retrieval_compare(exact_recall=0.4, semantic_recall=0.9,
                          exact_precision=0.3, semantic_precision=0.8,
                          task_kind="research_synthesis")
    assert r["semantic_rewarded_inappropriately"] is False


def test_stale_authority_check_fails():
    r = stale_authority_check(
        retrieved_freshness=["opp_rev_ga_501_1", "opp_rev_ga_501_2"],
        expected_current_revision="opp_rev_ga_501_2")
    assert r["pass"] is False
    assert "opp_rev_ga_501_1" in r["stale_refs"]


def test_stale_authority_clean():
    r = stale_authority_check(
        retrieved_freshness=["opp_rev_ga_501_2"],
        expected_current_revision="opp_rev_ga_501_2")
    assert r["pass"] is True
