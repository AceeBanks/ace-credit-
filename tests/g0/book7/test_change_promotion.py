"""B7.C21 — Prompt/workflow/route promotion tests.

PromotionDecision contract, Pareto behavior, no-optic-score collapse,
factuality-vs-style trade-off blocking.
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
    approve_pareto_tradeoff,
    evaluate_promotion,
)


def _candidate(change_type="PROMPT") -> CandidateChange:
    return CandidateChange(
        candidate_change_id="cc-2", change_type=change_type,
        baseline_version="v1", candidate_version="v2",
        source_or_generator="researcher", reason="align with funder priorities",
        expected_benefit="funder alignment", risk_class="MEDIUM",
        affected_capabilities=("research.run",),
        required_eval_suites=("grant-quality", "security-regression"),
        rollback_ref="rb-2")


def _full_metrics(**overrides) -> MetricBundle:
    dims = [
        {"dimension_id": "grant_funder_alignment", "family": "grant_quality",
         "gate": "OPTIMIZE", "direction": "higher_is_better", "value": 0.6},
        {"dimension_id": "ops_cost", "family": "operations",
         "gate": "OPTIMIZE", "direction": "lower_is_better", "value": 0.02},
        {"dimension_id": "factuality_unsupported_claims",
         "family": "factuality", "gate": "HARD", "direction": "lower_is_better",
         "value": 0},
        {"dimension_id": "security_capability_compliance",
         "family": "security", "gate": "HARD", "direction": "higher_is_better",
         "value": 1.0},
    ]
    for i, d in enumerate(dims):
        if d["dimension_id"] in overrides:
            dims[i]["value"] = overrides[d["dimension_id"]]
    return MetricBundle(metric_bundle_id="mb-full", dimensions=tuple(dims))


def test_pareto_tradeoff_allowed_when_documented():
    candidate = _candidate()
    baseline = _full_metrics()
    # cost regresses only ~5% (relative, within tolerance); funder alignment
    # improves 0.6 -> 0.85 (~42%); no hard gate regresses -> PROMOTE
    cand = _full_metrics(ops_cost=0.021, grant_funder_alignment=0.85)
    gates = [{"dimension_id": "security_capability_compliance",
              "family": "security", "passed": True}]
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=baseline,
                           candidate_metrics=cand,
                           hard_gate_results=gates,
                           optimization_tolerance=0.1)
    assert r["decision"] == "PROMOTE"


def test_pareto_tradeoff_needs_documentation():
    assert approve_pareto_tradeoff(candidate=_candidate(),
                                   tradeoff_doc="ok").get("approved") is False
    assert approve_pareto_tradeoff(
        candidate=_candidate(),
        tradeoff_doc="cost rises 3x but funder alignment improves by 25%; "
                     "no hard gate regresses; accepted per PROM-003").get(
        "approved") is True


def test_style_without_factuality_improvement_rejected():
    """Example from the plan: prettier prose + 3 unsupported claims = REJECT."""
    candidate = _candidate()
    baseline = _full_metrics(factuality_unsupported_claims=0)
    cand = _full_metrics(factuality_unsupported_claims=3,
                         grant_funder_alignment=0.95)
    gates = [{"dimension_id": "security_capability_compliance",
              "family": "security", "passed": True}]
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=baseline,
                           candidate_metrics=cand,
                           hard_gate_results=gates)
    assert r["decision"] in ("REJECT", "QUARANTINE")


def test_cost_down_20pct_equal_factuality_acceptable():
    """Plan example: 20% lower cost, equal factuality, +5% latency may be
    acceptable (no hard gate regresses)."""
    candidate = _candidate()
    baseline = _full_metrics(ops_cost=0.10)
    cand = _full_metrics(ops_cost=0.08)  # 20% cheaper
    gates = [{"dimension_id": "security_capability_compliance",
              "family": "security", "passed": True}]
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=baseline,
                           candidate_metrics=cand,
                           hard_gate_results=gates)
    assert r["decision"] in ("PROMOTE", "DEFER")
    # cost improved -> at least one optimization dimension improved
    assert r["decision"] == "PROMOTE"


def test_metric_bundle_dimensions_visible():
    mb = _full_metrics()
    assert len(mb.dimensions) == 4
    # EVAL-LAW-013: no single opaque score exists in the bundle
    assert not hasattr(mb, "overall_score")


def test_route_change_type_supported():
    c = _candidate(change_type="ROUTE")
    assert c.change_type == "ROUTE"


def test_promotion_decision_rejects_without_rollback():
    from prototype.g0.evaluation.promotion import PromotionDecision
    with pytest.raises(EvalError):
        PromotionDecision(
            promotion_decision_id="pd-x", candidate_change_id="cc",
            baseline_run_ref="b", candidate_run_ref="c",
            corpus_version_id="corpus", suite_id="s", suite_version=1,
            decision="PROMOTE", reason_codes=("x",),
            rollout_policy_ref="r", rollback_ref="", decided_by="me")
