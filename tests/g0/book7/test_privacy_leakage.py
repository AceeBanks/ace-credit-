"""B7.C24/C25 — Cost/latency/reliability + privacy/leakage tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.ops_eval import (  # noqa: E402
    OperationalRun,
    cost_guard,
    cross_tenant_leakage_check,
    feedback_is_not_training_truth,
    harvest_failure_case,
    holdout_contamination_check,
    latency_acceptability,
    memorization_not_capability,
    operational_report,
    privacy_leakage_scan,
    reliability_metrics,
)


def _run(cap="research.run", cost=0.01, latency=100, **kw) -> OperationalRun:
    base = dict(capability_id=cap, tokens_in=2000, tokens_out=800,
                model_cost_usd=cost, external_api_cost_usd=0.0,
                p50_latency_ms=latency, p95_latency_ms=latency * 2,
                timeouts=0, retries=0, schema_failures=0, tool_failures=0,
                context_tokens=12000)
    base.update(kw)
    return OperationalRun(**base)


def test_operational_report_aggregates():
    runs = [_run(cap="research.run", cost=0.01, latency=100),
            _run(cap="research.run", cost=0.02, latency=200),
            _run(cap="drafting.run", cost=0.05, latency=500)]
    r = operational_report(runs)
    assert r["total_calls"] == 3
    assert r["total_cost_usd"] == round(0.08, 4)
    assert r["capabilities"]["research.run"]["calls"] == 2
    assert r["capabilities"]["research.run"]["p50_latency_ms"] == 150.0


def test_cost_guard_blocks_bypass():
    assert cost_guard(cost_improvement=True, correctness_ok=True,
                      security_ok=True, evidence_ok=True)["allowed"]
    assert not cost_guard(cost_improvement=True, correctness_ok=True,
                          security_ok=False, evidence_ok=True)["allowed"]
    assert not cost_guard(cost_improvement=False, correctness_ok=True,
                          security_ok=True, evidence_ok=True)["allowed"]


def test_latency_acceptability():
    assert latency_acceptability(p95_ms=900, budget_ms=1000)["acceptable"]
    assert not latency_acceptability(p95_ms=1500, budget_ms=1000)["acceptable"]


def test_reliability_metrics():
    runs = [_run(), _run(timeouts=1), _run(schema_failures=1)]
    r = reliability_metrics(runs=runs)
    assert r["success_rate"] == round(1 - 2 / 3, 4)
    assert r["timeout_rate"] == round(1 / 3, 4)


def test_privacy_leakage_scan_detects_pii():
    r = privacy_leakage_scan(
        text="contact Jane at jane@example.com, EIN 58-2345671",
        redact_required=["jane@example.com", "58-2345671", "ssn"])
    assert r["leakage_found"] is True
    assert "jane@example.com" in r["leaked_tokens"]


def test_privacy_leakage_clean():
    r = privacy_leakage_scan(text="plain prose", redact_required=["ein"])
    assert r["leakage_found"] is False


def test_cross_tenant_leakage_p0():
    r = cross_tenant_leakage_check(case_tenant="tenant-b",
                                   corpus_tenant_scope="tenant-a")
    assert r["pass"] is False
    assert r["severity"] == "P0"
    assert cross_tenant_leakage_check(
        case_tenant="tenant-a", corpus_tenant_scope="tenant-a")["pass"]


def test_holdout_contamination_p0():
    r = holdout_contamination_check(case_ids=["c1", "c2"],
                                    holdout_case_ids={"c2"})
    assert r["pass"] is False
    assert r["severity"] == "P0"
    assert holdout_contamination_check(
        case_ids=["c1"], holdout_case_ids={"c2"})["pass"]


def test_memorization_not_capability():
    assert memorization_not_capability(
        case_hash_seen_in_training=True,
        claimed_capability="eligibility")["pass"] is False
    assert memorization_not_capability(
        case_hash_seen_in_training=False,
        claimed_capability="eligibility")["pass"]


def test_failure_case_not_training_truth():
    fc = harvest_failure_case(
        capability_id="research.run", input_refs=["ref-1"],
        observed_output_ref="out-1", expected_behavior="cite source",
        failure_taxonomy="missing_citation", severity="P1",
        reproducible=True)
    assert fc["is_training_truth"] is False  # EVAL-LAW-012
    assert fc["failure_taxonomy"] == "missing_citation"


def test_feedback_interpretation():
    r = feedback_is_not_training_truth(outcome="grant_lost",
                                       feedback_type="grant_lost")
    assert r["direct_training_truth"] is False
    assert "not proof of draft quality" in r["interpretation"]
