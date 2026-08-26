"""G0-B5-C18 — Audit <-> Evidence <-> Decision linkage tests.

Required coverage (plan):
- orphaned consequential decision rejected;
- approval reference resolves;
- actor/capability consistent between audit and decision;
- sensitive payload redaction does not destroy lineage.
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
from prototype.g0.evidence.linkage import (  # noqa: E402
    LinkageError,
    backward_lineage,
    check_actor_capability_consistency,
    check_orphaned_consequential,
    forward_lineage,
    redact_payload,
)
from prototype.g0.evidence.models import EvidenceGraph, make_ref  # noqa: E402


def _decision(**kw) -> DecisionRecord:
    base = dict(
        decision_id="decision:eligibility-1", decision_type="ELIGIBILITY",
        tenant_id="tenant-a", project_id="project-1",
        actor_ref="actor:ceo-hermes", capability_id="cap:eligibility",
        created_at="2026-08-26T00:00:00+00:00",
        input_refs=[DecisionInputRef(input_role="FACT", ref="fact:deadline")],
        policy_ref="policy:eligibility-v1",
        result={"summary": "eligible", "result_class": "CANONICAL_MUTATION"},
        status="ACTIVE", output_refs=["art:eligibility-letter"],
    )
    base.update(kw)
    return DecisionRecord(**base)


def _audit(**kw) -> dict:
    base = dict(
        event_id="evt-1", timestamp="2026-08-26T00:01:00+00:00",
        actor_id="actor:ceo-hermes", actor_type="AGENT",
        tenant_id="tenant-a", project_id="project-1",
        capability_id="cap:eligibility", authority_level="L2",
        resource_type="DECISION", resource_id="decision:eligibility-1",
        request_id="req-1", approval_ref="ap-1",
        input_artifact_refs=["fact:deadline"],
        output_artifact_refs=["art:eligibility-letter"],
        source_refs=["snap:official"], result_status="SUCCESS",
        error_class=None, policy_decision_ref="pd:allow-eligibility",
    )
    base.update(kw)
    return base


def _graph() -> EvidenceGraph:
    import yaml
    edge_cfg = yaml.safe_load((_ROOT / "config/g0/evidence/"
                               "evidence_edge_types.yaml")
                              .read_text(encoding="utf-8"))
    graph = EvidenceGraph(edge_types_config=edge_cfg,
                          endpoint_rules=edge_cfg.get("edge_endpoint_rules", []))
    graph.put_ref(make_ref(ref_id="fact:deadline", ref_type="CANONICAL_FACT",
                           entity_type="CanonicalFact", entity_id="deadline",
                           tenant_id="tenant-a", content_hash="dd" * 4))
    return graph


def test_orphaned_consequential_decision_rejected():
    dec = _decision()
    violations = check_orphaned_consequential(
        decisions=[dec], audit_events=[])
    assert violations and "orphaned" in violations[0]
    violations = check_orphaned_consequential(
        decisions=[dec], audit_events=[_audit()])
    assert violations == []


def test_approval_reference_resolves():
    approvals = {"ap-1": {"approval_id": "ap-1", "status": "VALID"}}
    fwd = forward_lineage(audit_event=_audit(), decisions=[_decision()],
                          approvals=approvals, graph=_graph())
    assert fwd["approval_resolved"] is True
    with pytest.raises(LinkageError):
        forward_lineage(audit_event=_audit(), decisions=[_decision()],
                        approvals={}, graph=_graph())


def test_actor_capability_consistent():
    dec = _decision()
    event = _audit()
    assert check_actor_capability_consistency(dec, event) == []
    bad = _audit(actor_id="actor:worker-7")
    assert check_actor_capability_consistency(dec, bad)


def test_redaction_preserves_lineage():
    dec = _decision()
    event = _audit()
    fwd = forward_lineage(audit_event=event, decisions=[dec],
                          approvals={"ap-1": {"approval_id": "ap-1",
                                              "status": "VALID"}},
                          graph=_graph())
    redacted = redact_payload(fwd)
    assert redacted["decision_record_ref"] == "decision:eligibility-1"
    assert redacted["audit_event_id"] == "evt-1"
    assert redacted["capability_id"] == "cap:eligibility"
    assert redacted["evidence_inputs"][0]["ref"] == "fact:deadline"
    assert redacted["evidence_inputs"][0]["tombstoned"] is False
    assert redacted["output_artifacts"] == ["art:eligibility-letter"]


def test_forward_and_backward_traversal():
    dec = _decision()
    event = _audit()
    graph = _graph()
    approvals = {"ap-1": {"approval_id": "ap-1", "status": "VALID"}}
    fwd = forward_lineage(audit_event=event, decisions=[dec],
                          approvals=approvals, graph=graph)
    assert fwd["policy_decision_ref"] == "pd:allow-eligibility"
    assert fwd["evidence_inputs"][0]["ref"] == "fact:deadline"
    bwd = backward_lineage(artifact_ref="art:eligibility-letter",
                           decisions=[dec], audit_events=[event])
    assert bwd["audit_event_id"] == "evt-1"
    assert bwd["actor_id"] == "actor:ceo-hermes"
    assert bwd["evidence_inputs"] == ["fact:deadline"]
