"""G0-B5-C22 — Privacy, retention & evidence visibility tests.

Required coverage (plan):
- public+private mixed graph query does not leak private node metadata;
- vector index honors deletion;
- evidence visibility survives projection/rebuild;
- tenant export can enumerate its own evidence lineage.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.models import EvidenceGraph, make_ref  # noqa: E402
from prototype.g0.evidence.visibility import VisibilityManager  # noqa: E402


def _graph() -> EvidenceGraph:
    import yaml
    edge_cfg = yaml.safe_load((_ROOT / "config/g0/evidence/"
                               "evidence_edge_types.yaml")
                              .read_text(encoding="utf-8"))
    graph = EvidenceGraph(edge_types_config=edge_cfg,
                          endpoint_rules=edge_cfg.get("edge_endpoint_rules", []))
    for rid, tenant, eid in (
        ("snap:public", "tenant-a", "public"),
        ("snap:private-a", "tenant-a", "private-a"),
        ("snap:private-b", "tenant-b", "private-b"),
    ):
        graph.put_ref(make_ref(ref_id=rid, ref_type="SOURCE_SNAPSHOT",
                               entity_type="SourceSnapshot", entity_id=eid,
                               tenant_id=tenant, content_hash=f"{rid}-h" * 2))
    return graph


def test_mixed_query_does_not_leak_private_metadata():
    graph = _graph()
    vm = VisibilityManager()
    vm.declare("snap:public", "PUBLIC_SOURCE")
    vm.declare("snap:private-a", "TENANT_PRIVATE")
    vm.declare("snap:private-b", "TENANT_PRIVATE")

    public_viewer = vm.scoped_graph_query(
        graph=graph, tenant_id=None, viewer_class="PUBLIC",
        node_ids=["snap:public", "snap:private-a", "snap:private-b"])
    assert public_viewer == ["snap:public"]

    tenant_a = vm.scoped_graph_query(
        graph=graph, tenant_id="tenant-a", viewer_class="TENANT_VIEWER",
        node_ids=["snap:public", "snap:private-a", "snap:private-b"])
    assert "snap:private-b" not in tenant_a  # other tenant's private data
    assert "snap:private-a" in tenant_a


def test_vector_index_honors_deletion():
    vm = VisibilityManager()
    vm.declare("fact:deadline", "PUBLIC_SOURCE")
    vm.declare("fact:removed", "TENANT_PRIVATE")
    vm.delete("fact:removed")
    results = vm.vector_results(
        candidates=["fact:deadline", "fact:removed"])
    assert results == ["fact:deadline"]


def test_visibility_survives_rebuild():
    vm = VisibilityManager()
    vm.declare("fact:deadline", "TENANT_SHARED_APPROVED")
    rebuilt = vm.rebuild_visibility(nodes={
        "fact:deadline": {"value": "2026-10-15"},
        "fact:other": {"value": 1},
    })
    assert rebuilt["fact:deadline"] == "TENANT_SHARED_APPROVED"
    assert rebuilt["fact:other"] == "TENANT_PRIVATE"  # default preserved


def test_tenant_export_enumerates_own_lineage():
    graph = _graph()
    vm = VisibilityManager()
    vm.declare("snap:public", "PUBLIC_SOURCE")
    vm.declare("snap:private-a", "TENANT_PRIVATE")
    vm.declare("snap:private-b", "TENANT_PRIVATE")
    export = vm.tenant_export(graph=graph, tenant_id="tenant-a")
    refs = {e["ref_id"] for e in export}
    assert "snap:private-b" not in refs  # no other tenant's data
    assert "snap:private-a" in refs
    # deletion restricts current access but content hash stays retained
    vm.delete("snap:private-a")
    export2 = vm.tenant_export(graph=graph, tenant_id="tenant-a")
    assert "snap:private-a" not in {e["ref_id"] for e in export2}
