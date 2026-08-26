"""G0-B5-C21 — Performance & scale envelope benchmark harness.

Measures p50/p95 latency for the six plan workloads against the explicit
substrate. Methodology is explicit (fixture sizes, sample counts); results
are compared to the prototype ceiling (not an invented SLA) and written as
machine-readable evidence for the Reality Lock.
"""
from __future__ import annotations

import statistics
import time
from typing import Any

from prototype.g0.evidence.dependencies import DependencyGraph
from prototype.g0.evidence.models import EvidenceGraph, make_ref

WORKLOADS = (
    "exact_provenance_trace", "contradiction_lookup",
    "dependency_invalidation", "evidence_bundle_assembly",
    "replay_packet_assembly", "graph_traversal",
)


def build_fixture_graph(*, tenants: int, opportunities: int) -> EvidenceGraph:
    """Deterministic synthetic fixture: tenants x opportunities with
    snapshot/claim/fact/decision neighborhoods and contradiction edges."""
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    edge_cfg = yaml.safe_load((root / "config/g0/evidence/"
                               "evidence_edge_types.yaml")
                              .read_text(encoding="utf-8"))
    graph = EvidenceGraph(edge_types_config=edge_cfg,
                          endpoint_rules=edge_cfg.get("edge_endpoint_rules", []))
    edges_per_opp = 5
    for t in range(tenants):
        tenant = f"tenant-{t}"
        for o in range(opportunities):
            base = f"{tenant}:opp-{o}"
            snap = make_ref(ref_id=f"snap:{base}", ref_type="SOURCE_SNAPSHOT",
                            entity_type="SourceSnapshot", entity_id=base,
                            tenant_id=tenant, content_hash=f"s{base}"[:32])
            claim = make_ref(ref_id=f"claim:{base}", ref_type="EVIDENCE_CLAIM",
                             entity_type="EvidenceClaim", entity_id=base,
                             tenant_id=tenant, content_hash=f"c{base}"[:32])
            fact = make_ref(ref_id=f"fact:{base}", ref_type="CANONICAL_FACT",
                            entity_type="CanonicalFact", entity_id=base,
                            tenant_id=tenant, content_hash=f"f{base}"[:32])
            rival = make_ref(ref_id=f"claim:rival:{base}",
                             ref_type="EVIDENCE_CLAIM",
                             entity_type="EvidenceClaim", entity_id=base,
                             tenant_id=tenant, content_hash=f"r{base}"[:32])
            decision = make_ref(ref_id=f"decision:{base}",
                                ref_type="ELIGIBILITY_DECISION",
                                entity_type="EligibilityDecision",
                                entity_id=base, tenant_id=tenant,
                                content_hash=f"d{base}"[:32])
            for ref in (snap, claim, fact, rival, decision):
                graph.put_ref(ref)
            graph.add_edge(edge_type="OBSERVED_IN", from_ref=snap,
                           to_ref=fact, tenant_scope=tenant, created_by="bench")
            graph.add_edge(edge_type="NORMALIZED_FROM", from_ref=claim,
                           to_ref=snap, tenant_scope=tenant, created_by="bench")
            graph.add_edge(edge_type="SUPPORTS", from_ref=claim,
                           to_ref=fact, tenant_scope=tenant, created_by="bench")
            graph.add_edge(edge_type="CONTRADICTS", from_ref=rival,
                           to_ref=claim, tenant_scope=tenant, created_by="bench")
            graph.add_edge(edge_type="DECISION_USED", from_ref=decision,
                           to_ref=fact, tenant_scope=tenant, created_by="bench")
    return graph


def build_fixture_dependencies(graph: EvidenceGraph) -> DependencyGraph:
    deps = DependencyGraph()
    for edge in graph.edges(edge_type="DECISION_USED"):
        deps.add_dependency(dependent_ref=edge.from_ref.ref_id,
                            depends_on_ref=edge.to_ref.ref_id,
                            dependency_type="ELIGIBILITY",
                            materiality="CRITICAL")
    return deps


def _sample(fn, n: int = 200) -> list[float]:
    times = []
    for _ in range(n):
        start = time.perf_counter()
        fn()
        times.append((time.perf_counter() - start) * 1000)
    return times


def run_benchmark(*, tenants: int, opportunities: int,
                  samples: int = 200) -> dict:
    """Run the six workloads; return p50/p95 per workload + fanout/rebuild."""
    graph = build_fixture_graph(tenants=tenants, opportunities=opportunities)
    deps = build_fixture_dependencies(graph)
    first_fact = f"fact:{'tenant-0'}:opp-0"

    workloads = {
        "exact_provenance_trace":
            lambda: graph.claim_support_chain(first_fact.replace("fact:", "claim:")),
        "contradiction_lookup":
            lambda: graph.edges(edge_type="CONTRADICTS",
                                ref_id=first_fact.replace("fact:", "claim:")),
        "dependency_invalidation":
            lambda: deps.transitive_dependents(first_fact),
        "evidence_bundle_assembly":
            lambda: graph.resolve_or_tombstone(first_fact),
        "replay_packet_assembly":
            lambda: [graph.resolve_or_tombstone(r)
                     for r in graph.neighbors(first_fact)],
        "graph_traversal":
            lambda: graph.claim_support_chain(first_fact),
    }
    results = {}
    for name, fn in workloads.items():
        samples_ms = _sample(fn, n=samples)
        results[name] = {
            "p50_ms": round(statistics.median(samples_ms), 3),
            "p95_ms": round(sorted(samples_ms)[
                min(len(samples_ms) - 1, int(0.95 * len(samples_ms)))], 3),
            "samples": len(samples_ms),
        }
    return {
        "fixture": {"tenants": tenants, "opportunities": opportunities,
                    "refs": len(graph._refs), "edges": len(graph._edges)},
        "workloads": results,
        "invalidation_fanout": len(deps.transitive_dependents(first_fact)[0]),
    }


def check_envelope(results: dict, ceiling: dict) -> tuple[bool, list[str]]:
    """Compare a benchmark run against the prototype ceilings."""
    problems = []
    for name, wl in results["workloads"].items():
        if wl["p50_ms"] > ceiling["p50_latency_ms"]:
            problems.append(f"{name}: p50 {wl['p50_ms']}ms > "
                            f"{ceiling['p50_latency_ms']}ms")
        if wl["p95_ms"] > ceiling["p95_latency_ms"]:
            problems.append(f"{name}: p95 {wl['p95_ms']}ms > "
                            f"{ceiling['p95_latency_ms']}ms")
    return (not problems, problems)
