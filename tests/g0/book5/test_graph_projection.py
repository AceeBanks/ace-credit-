"""G0-B5-C11-C12 — vector index + graph projection tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.projections import (  # noqa: E402
    GraphProjection,
    VectorIndex,
)
from tools.g0.validate_retrieval_projection import (  # noqa: E402
    validate,
)

PROJ_CFG = yaml.safe_load(
    (_ROOT / "config/g0/evidence/projection_policies.yaml").read_text(
        encoding="utf-8"))


def test_full_vector_store_loss_recoverable():
    index = VectorIndex()
    index.index(ref="ev-1", text="Georgia youth literacy grant deadline",
                tenant_scope="tenant-a", visibility="PUBLIC_SOURCE",
                evidence_class="EVIDENCE_CLAIM")
    sources = {"ev-1": "Georgia youth literacy grant deadline"}
    assert index.rebuild(sources) == 1
    assert index.resolve("ev-1")["ref"] == "ev-1"


def test_embedding_model_swap_does_not_alter_domain_ids():
    index = VectorIndex(embedding_model="pseudo-v1")
    index.index(ref="ev-2", text="census population 2020", tenant_scope="tenant-a",
                visibility="PUBLIC_SOURCE", evidence_class="STATISTIC_OBSERVATION")
    swapped = VectorIndex(embedding_model="pseudo-v2")
    swapped.index(ref="ev-2", text="census population 2020", tenant_scope="tenant-a",
                  visibility="PUBLIC_SOURCE", evidence_class="STATISTIC_OBSERVATION")
    assert swapped.resolve("ev-2")["ref"] == index.resolve("ev-2")["ref"]
    assert index.resolve("ev-2")["embedding_model"] == "pseudo-v1"
    assert swapped.resolve("ev-2")["embedding_model"] == "pseudo-v2"


def test_deleted_vector_not_retrievable():
    index = VectorIndex()
    index.index(ref="ev-private", text="client confidential note",
                tenant_scope="tenant-a", visibility="TENANT_PRIVATE",
                evidence_class="EVIDENCE_CLAIM")
    index.delete("ev-private")
    assert index.resolve("ev-private")["deleted"] is True
    assert "ev-private" not in [r["ref"] for r in
                                index.search("confidential", tenant_scope="tenant-a")]


def test_no_cross_tenant_similarity_by_default():
    index = VectorIndex()
    index.index(ref="ev-a", text="tenant alpha secret project",
                tenant_scope="tenant-a", visibility="TENANT_PRIVATE",
                evidence_class="EVIDENCE_CLAIM")
    index.index(ref="ev-b", text="tenant beta secret project",
                tenant_scope="tenant-b", visibility="TENANT_PRIVATE",
                evidence_class="EVIDENCE_CLAIM")
    results = index.search("secret project", tenant_scope="tenant-a")
    assert [r["ref"] for r in results] == ["ev-a"]
    # explicit opt-in still works for governed cases
    cross = index.search("secret project", tenant_scope="tenant-a",
                         allow_cross_tenant=True)
    assert len(cross) >= 2


def test_graph_node_ids_derive_from_canonical_ids():
    proj = GraphProjection()
    proj.project(source_refs=["opp-rev-3"], canonical_nodes={
        "opp-rev-3": {"deadline": "2026-10-15"}}, edges=[])
    assert proj.canonical_node_ids() == ["opp-rev-3"]


def test_graph_only_mutation_never_canonical():
    proj = GraphProjection()
    proj.project(source_refs=["opp-rev-3"], canonical_nodes={
        "opp-rev-3": {"deadline": "2026-10-15"}}, edges=[])
    proj.mutate_graph_only("opp-rev-3", {"deadline": "2026-11-01"})
    node = proj._nodes["opp-rev-3"]
    assert node.get("graph_only_mutation") is True
    assert node["canonical_id"] == "opp-rev-3"


def test_exit_test_rebuild_without_semantic_loss():
    proj = GraphProjection()
    canonical = {"opp-rev-3": {"deadline": "2026-10-15"},
                 "fact-1": {"value": 75000}}
    edges = [{"from": "fact-1", "to": "opp-rev-3", "type": "SUPPORTS"}]
    proj.project(source_refs=["opp-rev-3", "fact-1"],
                 canonical_nodes=canonical, edges=edges)
    nodes, edge_count = proj.rebuild_from_canonical(canonical, edges)
    assert nodes == 2 and edge_count == 1
    assert proj.canonical_node_ids() == ["fact-1", "opp-rev-3"]


def test_validator_passes_on_live_configs():
    errors: list[str] = []
    validate(errors)
    assert errors == []


def test_validator_fails_on_missing_vector_rule():
    broken = dict(PROJ_CFG)
    broken["vector_index_rules"] = [
        r for r in PROJ_CFG["vector_index_rules"] if r["id"] != "VEC-001"]
    errors: list[str] = []
    validate(errors, projection=broken)
    assert any("VEC-001" in e for e in errors)
