"""G0-B5-C21 — Performance & scale envelope tests.

Covers the small and medium fixture benchmarks, envelope ceilings, and the
deterministic-lane rule (PERF-002).
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.benchmarks import (  # noqa: E402
    WORKLOADS,
    check_envelope,
    run_benchmark,
)
from tools.g0._common import load_yaml  # noqa: E402


def _ceiling() -> dict:
    return load_yaml(_ROOT / "config/g0/evidence/performance_envelope.yaml")[
        "prototype_ceilings"]


def test_small_fixture_benchmark_within_envelope():
    results = run_benchmark(tenants=1, opportunities=10, samples=50)
    assert set(results["workloads"]) == set(WORKLOADS)
    ok, problems = check_envelope(results, _ceiling())
    assert ok, problems


def test_medium_fixture_benchmark():
    results = run_benchmark(tenants=10, opportunities=100, samples=20)
    assert results["fixture"]["refs"] > 0
    assert results["invalidation_fanout"] >= 0
    # all six workloads produce p50/p95 numbers
    for wl in WORKLOADS:
        assert "p50_ms" in results["workloads"][wl]
        assert "p95_ms" in results["workloads"][wl]


def test_ceiling_check_detects_violation():
    ceiling = _ceiling()
    fake = {"workloads": {
        wl: {"p50_ms": 0.1, "p95_ms": 1.0} for wl in WORKLOADS}}
    ok, problems = check_envelope(fake, ceiling)
    assert ok and not problems
    bad = {"workloads": {
        wl: {"p50_ms": 99999.0, "p95_ms": 999999.0} for wl in WORKLOADS}}
    ok, problems = check_envelope(bad, ceiling)
    assert not ok and problems


def test_exact_lane_is_deterministic():
    # PERF-002: exact provenance trace resolves without semantic search
    from prototype.g0.evidence.benchmarks import build_fixture_graph
    graph = build_fixture_graph(tenants=1, opportunities=5)
    chain = graph.claim_support_chain("claim:tenant-0:opp-0")
    assert any(c.get("ref_id") == "snap:tenant-0:opp-0" for c in chain)
