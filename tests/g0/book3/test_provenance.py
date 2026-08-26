"""B3.C21 tests — Provenance Chain Specification.

Fail-closed: given a material proposal sentence/assertion, the product must
trace to source capture; a missing critical hop is a FAIL.
"""
from __future__ import annotations

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_retention_provenance import (
    REQUIRED_CHAIN_STAGES,
    REQUIRED_RELATIONSHIPS,
    validate_provenance,
)
from prototype.g0.source.provenance import (
    CRITICAL_HOPS,
    ProvenanceEdge,
    ProvenanceGraph,
    Relationship,
    trace_to_capture,
)

CFG = SOURCE_CONFIG_DIR / "provenance_chain.yaml"


def _material_trace_graph() -> ProvenanceGraph:
    """Full chain for a proposal section claim:
    SourceSnapshot -> ExtractionEvent -> NormalizationEvent -> EvidenceClaim
    -> CanonicalFact -> ProposalSection."""
    g = ProvenanceGraph()
    g.add(ProvenanceEdge("e1", "SourceSnapshot", "snap_1",
                         "CaptureEvent_SourceSnapshot", "snap_1",
                         Relationship.CAPTURED_FROM, "adapter-1.0",
                         created_at="2026-08-01T00:00:00Z"))
    g.add(ProvenanceEdge("e2", "CaptureEvent_SourceSnapshot", "snap_1",
                         "ExtractionEvent", "extract_1",
                         Relationship.EXTRACTED_FROM, "parser-2.1",
                         created_at="2026-08-01T00:00:01Z"))
    g.add(ProvenanceEdge("e3", "ExtractionEvent", "extract_1",
                         "NormalizationEvent", "norm_1",
                         Relationship.NORMALIZED_FROM, "normalizer-1.3",
                         created_at="2026-08-01T00:00:02Z"))
    g.add(ProvenanceEdge("e4", "NormalizationEvent", "norm_1",
                         "EvidenceClaim_ExternalIdentifier_StatisticObservation",
                         "claim_1", Relationship.SUPPORTED_BY,
                         created_at="2026-08-01T00:00:03Z"))
    g.add(ProvenanceEdge("e5",
                         "EvidenceClaim_ExternalIdentifier_StatisticObservation",
                         "claim_1", "PromotionEvent_CanonicalFact", "fact_1",
                         Relationship.GENERATED_FROM, "promotion-2.0",
                         created_at="2026-08-01T00:00:04Z"))
    g.add(ProvenanceEdge("e6", "PromotionEvent_CanonicalFact", "fact_1",
                         "RequirementResponse_ProposalSection_BudgetLine",
                         "section_1", Relationship.USED_IN,
                         created_at="2026-08-01T00:00:05Z"))
    return g


def test_validator_live_config_passes():
    errors: list[str] = []
    validate_provenance(load_yaml(CFG), errors)
    assert errors == []


def test_chain_stages_and_relationships_match_config():
    cfg = load_yaml(CFG)
    assert cfg["chain_stages"] == REQUIRED_CHAIN_STAGES
    assert set(cfg["relationships"]) == REQUIRED_RELATIONSHIPS


def test_material_claim_traces_to_source_capture():
    g = _material_trace_graph()
    ok, hops = trace_to_capture(g, "RequirementResponse_ProposalSection_BudgetLine",
                                "section_1")
    assert ok, hops
    assert any("CAPTURED_FROM" in h for h in hops)
    assert any("NORMALIZED_FROM" in h for h in hops)


def test_missing_extraction_hop_fails():
    g = _material_trace_graph()
    # drop the extraction hop: section -> ... -> capture still reachable but the
    # critical EXTRACTED_FROM hop is gone
    g._edges["ExtractionEvent:extract_1"] = []
    ok, hops = trace_to_capture(g, "RequirementResponse_ProposalSection_BudgetLine",
                                "section_1")
    assert ok is False
    # the trace must FAIL (missing hop), with a diagnostic explaining why
    assert hops and any("without source capture" in h or "missing critical" in h
                        for h in hops)


def test_orphan_claim_fails():
    g = ProvenanceGraph()
    ok, hops = trace_to_capture(g, "RequirementResponse_ProposalSection_BudgetLine",
                                "section_9")
    assert ok is False
    assert any("no provenance edges" in h for h in hops)


def test_claim_without_capture_terminal_fails():
    g = ProvenanceGraph()
    g.add(ProvenanceEdge("x1", "NormalizationEvent", "norm_9",
                         "EvidenceClaim_ExternalIdentifier_StatisticObservation",
                         "claim_9", Relationship.SUPPORTED_BY))
    # no path continues to a CAPTURED_FROM snapshot
    ok, hops = trace_to_capture(g,
                                "EvidenceClaim_ExternalIdentifier_StatisticObservation",
                                "claim_9")
    assert ok is False
    assert any("without source capture" in h for h in hops)


def test_critical_hops_defined():
    assert {"CaptureEvent_SourceSnapshot", "NormalizationEvent",
            "EvidenceClaim_ExternalIdentifier_StatisticObservation"} == set(CRITICAL_HOPS)


def test_contradicted_by_edge_is_expressible():
    g = ProvenanceGraph()
    g.add(ProvenanceEdge("c1", "PromotionEvent_CanonicalFact", "fact_2",
                         "PromotionEvent_CanonicalFact", "fact_1",
                         Relationship.CONTRADICTED_BY))
    incoming = g.incoming("PromotionEvent_CanonicalFact", "fact_1")
    assert any(e.relationship is Relationship.CONTRADICTED_BY for e in incoming)
