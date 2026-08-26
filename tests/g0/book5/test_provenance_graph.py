"""G0-B5-C2-C3 — ProvenanceRef + evidence graph semantics tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.models import (  # noqa: E402
    EvidenceGraph,
    EvidenceGraphError,
    make_ref,
)
from tools.g0.validate_provenance_graph import (  # noqa: E402
    validate,
)

EDGE_CFG = yaml.safe_load(
    (_ROOT / "config/g0/evidence/evidence_edge_types.yaml").read_text(
        encoding="utf-8"))


def _graph() -> EvidenceGraph:
    return EvidenceGraph(
        edge_types_config=EDGE_CFG,
        endpoint_rules=EDGE_CFG.get("edge_endpoint_rules", []))


def _refs(graph: EvidenceGraph):
    snap = make_ref(ref_id="snap-1", ref_type="SOURCE_SNAPSHOT",
                    entity_type="SourceSnapshot", entity_id="snap-1",
                    tenant_id="tenant-a", content_hash="a" * 8)
    ext = make_ref(ref_id="ext-1", ref_type="EXTRACTION_EVENT",
                   entity_type="ExtractionEvent", entity_id="ext-1",
                   tenant_id="tenant-a", content_hash="b" * 8)
    claim = make_ref(ref_id="claim-1", ref_type="EVIDENCE_CLAIM",
                     entity_type="EvidenceClaim", entity_id="claim-1",
                     tenant_id="tenant-a", content_hash="c" * 8)
    fact = make_ref(ref_id="fact-1", ref_type="CANONICAL_FACT",
                    entity_type="CanonicalFact", entity_id="fact-1",
                    tenant_id="tenant-a", content_hash="d" * 8)
    for r in (snap, ext, claim, fact):
        graph.put_ref(r)
    return snap, ext, claim, fact


def test_ref_resolves_and_hash_mismatch_detected():
    g = _graph()
    snap, _, _, _ = _refs(g)
    assert g.resolve_or_tombstone("snap-1")["content_hash"] == "a" * 8
    with pytest.raises(EvidenceGraphError, match="hash mismatch"):
        g.put_ref(make_ref(ref_id="snap-1", ref_type="SOURCE_SNAPSHOT",
                           entity_type="SourceSnapshot", entity_id="snap-1",
                           tenant_id="tenant-a", content_hash="e" * 8))


def test_unknown_ref_resolves_to_explicit_tombstone():
    g = _graph()
    resolved = g.resolve_or_tombstone("ghost-1")
    assert resolved["tombstoned"] is True


def test_support_chain_traces_to_source_snapshot():
    g = _graph()
    snap, ext, claim, fact = _refs(g)
    g.add_edge(edge_type="EXTRACTED_FROM", from_ref=ext, to_ref=snap,
               tenant_scope="tenant-a", created_by="extractor")
    g.add_edge(edge_type="NORMALIZED_FROM", from_ref=claim, to_ref=ext,
               tenant_scope="tenant-a", created_by="normalizer")
    g.add_edge(edge_type="SUPPORTS", from_ref=claim, to_ref=fact,
               tenant_scope="tenant-a", created_by="promotion-service")
    chain = g.claim_support_chain("fact-1")
    ids = [c["ref_id"] for c in chain]
    assert "claim-1" in ids and "ext-1" in ids and "snap-1" in ids


def test_cross_tenant_edge_denied():
    g = _graph()
    snap, ext, _, _ = _refs(g)
    other = make_ref(ref_id="snap-9", ref_type="SOURCE_SNAPSHOT",
                     entity_type="SourceSnapshot", entity_id="snap-9",
                     tenant_id="tenant-b", content_hash="f" * 8)
    g.put_ref(other)
    with pytest.raises(EvidenceGraphError, match="cross-tenant"):
        g.add_edge(edge_type="SUPPORTS", from_ref=snap, to_ref=other,
                   tenant_scope="tenant-a", created_by="tester")


def test_invalid_endpoint_combination_rejected():
    g = _graph()
    snap, _, _, fact = _refs(g)
    with pytest.raises(EvidenceGraphError, match="from type"):
        g.add_edge(edge_type="EXTRACTED_FROM", from_ref=fact, to_ref=snap,
                   tenant_scope="tenant-a", created_by="tester")


def test_unknown_edge_type_rejected():
    g = _graph()
    snap, _, _, fact = _refs(g)
    with pytest.raises(EvidenceGraphError, match="unknown edge type"):
        g.add_edge(edge_type="MAGIC_LINK", from_ref=snap, to_ref=fact,
                   tenant_scope="tenant-a", created_by="tester")


def test_tombstone_does_not_orphan_history():
    g = _graph()
    snap, ext, claim, fact = _refs(g)
    g.add_edge(edge_type="SUPPORTS", from_ref=claim, to_ref=fact,
               tenant_scope="tenant-a", created_by="svc")
    g.tombstone("claim-1")
    # historical replay still resolves the tombstoned endpoint explicitly
    resolved = g.resolve_or_tombstone("claim-1")
    assert resolved["tombstoned"] is True
    chain = g.claim_support_chain("fact-1")
    assert any(c.get("tombstoned") for c in chain)
    # and edges to tombstoned refs cannot be added
    with pytest.raises(EvidenceGraphError, match="tombstoned"):
        g.add_edge(edge_type="SUPPORTS", from_ref=claim, to_ref=fact,
                   tenant_scope="tenant-a", created_by="svc")


def test_validator_passes_on_live_config():
    errors: list[str] = []
    validate(errors)
    assert errors == []


def test_validator_fails_on_missing_family_edge():
    broken = dict(EDGE_CFG)
    broken["edge_families"] = [
        {**f, "edge_types": [t for t in f["edge_types"] if t != "SUPPORTS"]}
        if f["family"] == "evidence_semantics" else f
        for f in EDGE_CFG["edge_families"]]
    errors: list[str] = []
    validate(errors, cfg=broken)
    assert any("expected" in e for e in errors)


def test_validator_fails_on_missing_endpoint_rule():
    broken = dict(EDGE_CFG)
    broken["edge_endpoint_rules"] = [
        r for r in EDGE_CFG["edge_endpoint_rules"]
        if r["edge_type"] != "SUPPORTS"]
    errors: list[str] = []
    validate(errors, cfg=broken)
    assert any("SUPPORTS" in e for e in errors)
