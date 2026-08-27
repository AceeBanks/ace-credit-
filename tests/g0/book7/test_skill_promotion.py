"""B7.C20 — Skill promotion protocol tests.

Single promotion path, direct-write prohibition, generator cannot
self-promote, rollback identity required.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.models import (  # noqa: E402
    EvalError,
    MetricBundle,
)
from prototype.g0.evaluation.promotion import (  # noqa: E402
    CandidateChange,
    evaluate_promotion,
)


def _candidate(source="human-author", rollback_ref="rb-1") -> CandidateChange:
    return CandidateChange(
        candidate_change_id="cc-1", change_type="SKILL",
        baseline_version="1.0", candidate_version="2.0",
        source_or_generator=source, reason="better drafting",
        expected_benefit="requirement coverage",
        risk_class="LOW", affected_capabilities=("research.run",),
        required_eval_suites=("grant-quality",), rollback_ref=rollback_ref)


def _metrics(*, coverage=0.9, cost=0.01) -> MetricBundle:
    return MetricBundle(metric_bundle_id="mb-1", dimensions=(
        {"dimension_id": "correctness_requirement_coverage", "family": "correctness",
         "gate": "HARD", "direction": "higher_is_better", "value": coverage},
        {"dimension_id": "ops_cost", "family": "operations",
         "gate": "OPTIMIZE", "direction": "lower_is_better", "value": cost},
    ))


def test_candidate_change_requires_rollback_ref():
    with pytest.raises(EvalError):
        CandidateChange(
            candidate_change_id="cc-x", change_type="SKILL",
            baseline_version="1", candidate_version="2",
            source_or_generator="human", reason="x",
            expected_benefit="y", risk_class="LOW",
            affected_capabilities=(), required_eval_suites=(),
            rollback_ref="")


def test_candidate_unknown_change_type_rejected():
    with pytest.raises(EvalError):
        CandidateChange(
            candidate_change_id="cc-x", change_type="MAGIC",
            baseline_version="1", candidate_version="2",
            source_or_generator="human", reason="x",
            expected_benefit="y", risk_class="LOW",
            affected_capabilities=(), required_eval_suites=(),
            rollback_ref="rb")


def test_promotion_requires_independent_evaluator():
    candidate = _candidate(source="skillclaw")
    baseline = _metrics(coverage=0.8)
    cand = _metrics(coverage=0.95)
    gates = [{"dimension_id": "correctness_requirement_coverage",
              "family": "correctness", "passed": True}]
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=baseline,
                           candidate_metrics=cand,
                           hard_gate_results=gates,
                           independent_evaluator="skillclaw")
    assert r["decision"] == "REJECT"
    assert "PROM-005_SELF_EVALUATION" in r["reason_codes"]


def test_promote_on_improvement():
    candidate = _candidate()
    baseline = _metrics(coverage=0.8, cost=0.10)
    cand = _metrics(coverage=0.95, cost=0.01)
    gates = [{"dimension_id": "correctness_requirement_coverage",
              "family": "correctness", "passed": True}]
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=baseline,
                           candidate_metrics=cand,
                           hard_gate_results=gates)
    assert r["decision"] == "PROMOTE"
    # coverage is a HARD dimension (gate), so the improvement that triggers
    # PROM-007 is the optimization dimension (cost down 10x)
    assert "ops_cost" in r["improved_dimensions"]


def test_hard_gate_failure_rejects():
    candidate = _candidate()
    baseline = _metrics(coverage=0.8)
    cand = _metrics(coverage=0.95)
    gates = [{"dimension_id": "security_tenant_isolation",
              "family": "security", "passed": False}]
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=baseline,
                           candidate_metrics=cand,
                           hard_gate_results=gates)
    assert r["decision"] == "QUARANTINE"


def test_hard_regression_rejects_even_with_style_gain():
    """EVAL-LAW-003: prettier prose + hard regression = REJECT."""
    candidate = _candidate()
    baseline = MetricBundle(metric_bundle_id="mb", dimensions=(
        {"dimension_id": "grant_readability", "family": "grant_quality",
         "gate": "OPTIMIZE", "direction": "higher_is_better", "value": 0.5},
        {"dimension_id": "factuality_material_claim_support",
         "family": "factuality", "gate": "HARD",
         "direction": "higher_is_better", "value": 0.9},
    ))
    cand = MetricBundle(metric_bundle_id="mb", dimensions=(
        {"dimension_id": "grant_readability", "family": "grant_quality",
         "gate": "OPTIMIZE", "direction": "higher_is_better", "value": 0.9},
        {"dimension_id": "factuality_material_claim_support",
         "family": "factuality", "gate": "HARD",
         "direction": "higher_is_better", "value": 0.6},
    ))
    gates = [{"dimension_id": "factuality_material_claim_support",
              "family": "factuality", "passed": False}]
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=baseline,
                           candidate_metrics=cand,
                           hard_gate_results=gates)
    assert r["decision"] in ("REJECT", "QUARANTINE")


def test_defer_when_no_improvement():
    candidate = _candidate()
    baseline = _metrics(coverage=0.9, cost=0.01)
    cand = _metrics(coverage=0.9, cost=0.01)
    gates = [{"dimension_id": "correctness_requirement_coverage",
              "family": "correctness", "passed": True}]
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=baseline,
                           candidate_metrics=cand,
                           hard_gate_results=gates)
    assert r["decision"] == "DEFER"
    assert "PROM-007_NO_IMPROVEMENT" in r["reason_codes"]


def test_revise_on_undocumented_tradeoff():
    candidate = _candidate()
    baseline = _metrics(coverage=0.8, cost=0.01)
    cand = _metrics(coverage=0.95, cost=0.15)  # cost 14x worse
    gates = [{"dimension_id": "correctness_requirement_coverage",
              "family": "correctness", "passed": True}]
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=baseline,
                           candidate_metrics=cand,
                           hard_gate_results=gates)
    assert r["decision"] == "REVISE"
    assert "ops_cost" in r["regressed_dimensions"]


def test_promotion_decision_carries_rollback():
    from prototype.g0.evaluation.promotion import PromotionDecision
    d = PromotionDecision(
        promotion_decision_id="pd-1", candidate_change_id="cc-1",
        baseline_run_ref="run-b", candidate_run_ref="run-c",
        corpus_version_id="corpus-1", suite_id="s1", suite_version=1,
        decision="PROMOTE", reason_codes=("PROM-001",),
        rollout_policy_ref="rollout-1", rollback_ref="rb-1",
        decided_by="reviewer-1")
    assert d.rollback_ref == "rb-1"
    assert d.decided_at
