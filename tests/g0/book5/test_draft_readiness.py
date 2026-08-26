"""G0-B5-C20 — D0/D1 evidence readiness tests.

Required coverage (plan):
- D0 claim ledger coverage threshold measured;
- D1 context excludes unrelated tenant/project evidence;
- Personal Hermes explanation reflects CEO decision packet;
- missing evidence surfaces as gap rather than hallucinated support.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.decisions import (  # noqa: E402
    DecisionInputRef,
    DecisionRecord,
)
from prototype.g0.evidence.draft_readiness import (  # noqa: E402
    assess_d0_coverage,
    build_d0_shadow_draft,
    build_d1_context_bundle,
    explanation_reflects_decision,
    worker_result,
)
from prototype.g0.evidence.models import EvidenceGraph, make_ref  # noqa: E402


def _graph() -> EvidenceGraph:
    import yaml
    edge_cfg = yaml.safe_load((_ROOT / "config/g0/evidence/"
                               "evidence_edge_types.yaml")
                              .read_text(encoding="utf-8"))
    graph = EvidenceGraph(edge_types_config=edge_cfg,
                          endpoint_rules=edge_cfg.get("edge_endpoint_rules", []))
    for rid, tenant, eid in (
        ("fact:requirement-1", "tenant-a", "requirement-1"),
        ("fact:requirement-2", "tenant-a", "requirement-2"),
        ("fact:other-tenant", "tenant-b", "other-tenant"),
    ):
        graph.put_ref(make_ref(ref_id=rid, ref_type="CANONICAL_FACT",
                               entity_type="CanonicalFact", entity_id=eid,
                               tenant_id=tenant, content_hash=f"{rid}-h" * 2))
    return graph


def _entries(n_supported: int, n_total: int) -> list[dict]:
    out = []
    for i in range(n_total):
        out.append({"claim_id": f"c{i}", "support_status": "SUPPORTED"
                    if i < n_supported else "UNSUPPORTED"})
    return out


def test_d0_coverage_threshold_measured():
    low = assess_d0_coverage(claim_ledger_entries=_entries(1, 4))
    assert low["evidence_label"] == "EVIDENCE_INCOMPLETE"
    assert low["meets_threshold"] is False
    high = assess_d0_coverage(claim_ledger_entries=_entries(4, 5))
    assert high["evidence_label"] == "EVIDENCE_COMPLETE"
    assert high["meets_threshold"] is True


def test_d0_draft_never_submission_ready():
    packet = build_d0_shadow_draft(
        artifact_version_id="art-v1", tenant_id="tenant-a",
        project_id="project-1", claim_ledger_entries=_entries(4, 5),
        research_findings=[], evidence_refs=["fact:requirement-1"],
        qa_factuality={"status": "PASS_MOCK"},
        explanation_packet={"summary": "draft"},
    )
    assert packet["label"] == "MOCK_NON_SUBMISSION"
    assert packet["submission_ready"] is False
    assert packet["evidence_label"] == "EVIDENCE_COMPLETE"


def test_d1_context_excludes_unrelated_evidence():
    graph = _graph()
    bundle = build_d1_context_bundle(
        tenant_id="tenant-a", project_id="project-1",
        requirements=["requirement-1"],
        graph=graph,
        all_refs=["fact:requirement-1", "fact:requirement-2",
                  "fact:other-tenant"])
    assert "fact:requirement-1" in bundle["evidence_refs"]
    assert "fact:other-tenant" not in bundle["evidence_refs"]
    assert "fact:requirement-2" not in bundle["evidence_refs"]
    assert bundle["bounded"] is True


def test_personal_explanation_reflects_ceo_decision():
    decision = DecisionRecord(
        decision_id="decision:d1-1", decision_type="ELIGIBILITY",
        tenant_id="tenant-a", project_id="project-1",
        actor_ref="actor:ceo-hermes", capability_id="cap:eligibility",
        created_at="2026-08-26T00:00:00+00:00",
        input_refs=[DecisionInputRef(input_role="FACT",
                                     ref="fact:requirement-1")],
        policy_ref="policy:v1",
        result={"summary": "Eligible on 2/2 rules", "outcome": "ELIGIBLE"})
    good = {"decision_record_ref": "decision:d1-1",
            "summary": "Eligible on 2/2 rules",
            "cited_evidence_refs": ["fact:requirement-1"]}
    assert explanation_reflects_decision(explanation_packet=good,
                                         decision=decision) is True
    bad = {"decision_record_ref": "decision:other",
           "summary": "Eligible on 2/2 rules",
           "cited_evidence_refs": ["fact:requirement-1"]}
    assert explanation_reflects_decision(explanation_packet=bad,
                                         decision=decision) is False


def test_missing_evidence_surfaces_as_gap():
    result = worker_result(
        draft_content_or_artifact_ref="art:draft-1",
        claims_created=["the program serves 500 youth annually"],
        evidence_used=["fact:requirement-1"],
        assumptions=["funding assumed at $50k"],
        sidechain_ref="sc:1")
    assert result["unresolved_evidence_gaps"]
    assert "no evidence ref" in result["unresolved_evidence_gaps"][0]
    ok = worker_result(
        draft_content_or_artifact_ref="art:draft-2",
        claims_created=["[TODO] verify partnership"],
        evidence_used=["fact:requirement-1"],
        assumptions=[], sidechain_ref="sc:2")
    assert ok["unresolved_evidence_gaps"] == []
