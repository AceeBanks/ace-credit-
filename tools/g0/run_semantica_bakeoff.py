#!/usr/bin/env python3
"""G0-B5-C13 — Semantica bake-off runner.

Executes W1-W10 workloads against the baseline explicit substrate and the
semantica-backed projection, records measured results (correctness,
latency), and writes them to
docs/grant-sector/g0/05-evidence/G0_B5_SEMANTICA_BAKEOFF_RESULTS.json
for the results report and Reality Lock.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# scoped bake-off dependency (optional; recorded in the ledger)
_BAKEOFF = _ROOT / ".bakeoff" / "semantica_pkg"
if _BAKEOFF.exists() and str(_BAKEOFF) not in sys.path:
    sys.path.insert(0, str(_BAKEOFF))

from prototype.g0.evidence.models import EvidenceGraph, make_ref  # noqa: E402
from prototype.g0.evidence.semantica_adapter import (  # noqa: E402
    SemanticaAdapter,
    run_full_bakeoff,
)
from tools.g0._common import load_yaml  # noqa: E402


def build_fixture_graph() -> EvidenceGraph:
    edge_cfg = load_yaml(Path("config/g0/evidence/evidence_edge_types.yaml"))
    graph = EvidenceGraph(edge_types_config=edge_cfg,
                          endpoint_rules=edge_cfg.get("edge_endpoint_rules", []))
    refs = {
        "fact:deadline": make_ref(ref_id="fact:deadline",
                                  ref_type="CANONICAL_FACT",
                                  entity_type="CanonicalFact",
                                  entity_id="deadline", tenant_id="tenant-a",
                                  content_hash="d1" * 4),
        "fact:ceiling": make_ref(ref_id="fact:ceiling",
                                 ref_type="CANONICAL_FACT",
                                 entity_type="CanonicalFact",
                                 entity_id="ceiling", tenant_id="tenant-a",
                                 content_hash="d2" * 4),
        "claim:org-status": make_ref(ref_id="claim:org-status",
                                     ref_type="EVIDENCE_CLAIM",
                                     entity_type="EvidenceClaim",
                                     entity_id="org-status",
                                     tenant_id="tenant-a", content_hash="c1" * 4),
        "claim:rival-status": make_ref(ref_id="claim:rival-status",
                                       ref_type="EVIDENCE_CLAIM",
                                       entity_type="EvidenceClaim",
                                       entity_id="rival-status",
                                       tenant_id="tenant-a", content_hash="c2" * 4),
        "snap:official": make_ref(ref_id="snap:official",
                                  ref_type="SOURCE_SNAPSHOT",
                                  entity_type="SourceSnapshot",
                                  entity_id="official", tenant_id="tenant-a",
                                  content_hash="s1" * 4),
        "snap:stats": make_ref(ref_id="snap:stats", ref_type="SOURCE_SNAPSHOT",
                               entity_type="SourceSnapshot",
                               entity_id="stats", tenant_id="tenant-a",
                               content_hash="s2" * 4),
        "decision:eligibility-1": make_ref(
            ref_id="decision:eligibility-1", ref_type="ELIGIBILITY_DECISION",
            entity_type="EligibilityDecision", entity_id="eligibility-1",
            tenant_id="tenant-a", content_hash="e1" * 4),
    }
    for ref in refs.values():
        graph.put_ref(ref)
    graph.add_edge(edge_type="SUPPORTS", from_ref=refs["claim:org-status"],
                   to_ref=refs["fact:deadline"], tenant_scope="tenant-a",
                   created_by="bakeoff")
    graph.add_edge(edge_type="NORMALIZED_FROM",
                   from_ref=refs["claim:org-status"], to_ref=refs["snap:official"],
                   tenant_scope="tenant-a", created_by="bakeoff")
    graph.add_edge(edge_type="OBSERVED_IN", from_ref=refs["snap:official"],
                   to_ref=refs["fact:deadline"], tenant_scope="tenant-a",
                   created_by="bakeoff")
    graph.add_edge(edge_type="DECISION_USED",
                   from_ref=refs["decision:eligibility-1"],
                   to_ref=refs["fact:deadline"],
                   tenant_scope="tenant-a", created_by="bakeoff")
    graph.add_edge(edge_type="OBSERVED_IN", from_ref=refs["snap:stats"],
                   to_ref=refs["fact:ceiling"], tenant_scope="tenant-a",
                   created_by="bakeoff")
    graph.add_edge(edge_type="CONTRADICTS",
                   from_ref=refs["claim:rival-status"],
                   to_ref=refs["claim:org-status"], tenant_scope="tenant-a",
                   created_by="bakeoff")
    return graph


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the Semantica bake-off")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    graph = build_fixture_graph()
    adapter = SemanticaAdapter()
    start = time.perf_counter()
    results = run_full_bakeoff(graph)
    elapsed = time.perf_counter() - start

    package = {
        "bakeoff": "G0-B5-C13",
        "candidate": "semantica-agi/semantica (PyPI semantica 0.6.6)",
        "baseline": "explicit relational evidence/dependency substrate "
                    "(prototype EvidenceGraph)",
        "semantica_available": adapter.available,
        "comparison": "BASELINE EXPLICIT SUBSTRATE vs BASELINE + SEMANTICA ADAPTER/PROJECTION",
        "total_elapsed_ms": round(elapsed * 1000, 2),
        "workloads": [r.to_dict() for r in results],
        "baseline_correct": sum(1 for r in results if r.candidate == "baseline" and r.correct),
        "semantica_correct": sum(1 for r in results if r.candidate == "semantica" and r.correct),
        "baseline_mean_latency_ms": round(sum(r.latency_ms for r in results
                                              if r.candidate == "baseline") / 10, 2),
        "semantica_mean_latency_ms": round(sum(r.latency_ms for r in results
                                               if r.candidate == "semantica") / 10, 2),
    }
    out_path = args.out or (
        _ROOT / "docs" / "grant-sector" / "g0" / "05-evidence"
        / "G0_B5_SEMANTICA_BAKEOFF_RESULTS.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(package, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
