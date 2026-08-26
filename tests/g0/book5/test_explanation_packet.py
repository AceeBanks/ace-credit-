"""G0-B5-C15 — ExplanationPacket tests.

Required coverage (plan):
- explanation matches DecisionRecord;
- conflicts are not hidden;
- stale evidence indicated;
- unsupported rationale rejected.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
import sys

if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.decisions import DecisionRecord, DecisionInputRef  # noqa: E402
from prototype.g0.evidence.explanation import (  # noqa: E402
    ExplanationError,
    build_explanation_packet,
)
from prototype.g0.evidence.models import EvidenceGraph, make_ref  # noqa: E402


def _graph() -> EvidenceGraph:
    import yaml
    edge_cfg = yaml.safe_load((_ROOT / "config/g0/evidence/"
                               "evidence_edge_types.yaml")
                              .read_text(encoding="utf-8"))
    graph = EvidenceGraph(edge_types_config=edge_cfg,
                          endpoint_rules=edge_cfg.get("edge_endpoint_rules", []))
    for rid, rtype, eid in (
        ("fact:deadline", "CANONICAL_FACT", "deadline"),
        ("claim:org-status", "EVIDENCE_CLAIM", "org-status"),
        ("claim:rival-status", "EVIDENCE_CLAIM", "rival-status"),
    ):
        graph.put_ref(make_ref(ref_id=rid, ref_type=rtype,
                               entity_type="CanonicalFact" if rtype == "CANONICAL_FACT" else "EvidenceClaim",
                               entity_id=eid, tenant_id="tenant-a",
                               content_hash=f"{rid}-h" * 2))
    graph.add_edge(edge_type="CONTRADICTS",
                   from_ref=graph.get_ref("claim:rival-status"),
                   to_ref=graph.get_ref("claim:org-status"),
                   tenant_scope="tenant-a", created_by="test")
    return graph


def _decision(input_refs: list[DecisionInputRef], **kw) -> DecisionRecord:
    base = dict(
        decision_id="decision:eligibility-1", decision_type="ELIGIBILITY",
        tenant_id="tenant-a", project_id="project-1", actor_ref="actor:ceo-hermes",
        capability_id="cap:eligibility", created_at="2026-08-26T00:00:00+00:00",
        input_refs=input_refs, policy_ref="policy:eligibility-v1",
        result={"summary": "Eligible on 3/3 hard rules", "outcome": "ELIGIBLE"},
        status="ACTIVE",
    )
    base.update(kw)
    return DecisionRecord(**base)


def test_explanation_matches_decision_record():
    graph = _graph()
    decision = _decision([
        DecisionInputRef(input_role="FACT", ref="fact:deadline"),
        DecisionInputRef(input_role="CLAIM", ref="claim:org-status"),
    ])
    packet = build_explanation_packet(decision=decision, graph=graph)
    assert packet["decision_record_ref"] == decision.decision_id
    assert packet["summary"] == decision.result["summary"]
    # every cited ref is a decision input
    inputs = {i.ref for i in decision.input_refs}
    assert set(packet["cited_evidence_refs"]) <= inputs


def test_conflict_not_hidden():
    graph = _graph()
    decision = _decision([
        DecisionInputRef(input_role="FACT", ref="fact:deadline"),
        DecisionInputRef(input_role="CLAIM", ref="claim:org-status"),
        DecisionInputRef(input_role="CLAIM", ref="claim:rival-status"),
    ])
    packet = build_explanation_packet(decision=decision, graph=graph)
    pairs = {frozenset((d["ref_a"], d["ref_b"]))
             for d in packet["conflict_disclosures"]}
    assert frozenset(("claim:org-status", "claim:rival-status")) in pairs


def test_stale_evidence_indicated():
    graph = _graph()
    graph.tombstone("claim:org-status")
    decision = _decision([
        DecisionInputRef(input_role="CLAIM", ref="claim:org-status"),
    ])
    packet = build_explanation_packet(decision=decision, graph=graph)
    assert any(s["ref"] == "claim:org-status" and s["stale_class"] == "TOMBSTONED"
               for s in packet["stale_indicators"])


def test_unsupported_rationale_rejected():
    graph = _graph()
    decision = _decision([
        DecisionInputRef(input_role="FACT", ref="fact:deadline"),
    ])
    with pytest.raises(ExplanationError):
        build_explanation_packet(decision=decision, graph=graph,
                                 extra_cited_refs=["claim:org-status"])
    # an explicit assumption is allowed to carry untraced rationale
    packet = build_explanation_packet(
        decision=decision, graph=graph,
        explicit_assumptions=["client attestation pending (ASSUMPTION)"])
    assert packet["assumptions"]


def test_packet_conforms_to_schema():
    graph = _graph()
    decision = _decision([
        DecisionInputRef(input_role="FACT", ref="fact:deadline"),
    ])
    packet = build_explanation_packet(decision=decision, graph=graph)
    import jsonschema
    schema = json.loads((_ROOT / "schemas/g0/evidence/"
                         "explanation_packet.schema.json")
                        .read_text(encoding="utf-8"))
    jsonschema.validate(packet, schema)
