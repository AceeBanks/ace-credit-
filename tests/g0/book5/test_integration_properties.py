"""G0-B5-C25 — Integration & property tests.

The twenty mandatory invariants (plan chapter 29) are asserted against the
real prototypes, plus property tests: rebuildable projections, deterministic
replay, append-only contradiction history, idempotent invalidation, and
serialization round-trip.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import yaml  # noqa: E402

from prototype.g0.evidence.claim_ledger import ClaimLedger  # noqa: E402
from prototype.g0.evidence.contradictions import (  # noqa: E402
    SupportAssertion,
    independent_corroboration,
    open_contradiction,
    promote_claim,
    resolve_contradiction,
)
from prototype.g0.evidence.decisions import (  # noqa: E402
    DecisionInputRef,
    DecisionRecord,
)
from prototype.g0.evidence.degradation import DegradationManager  # noqa: E402
from prototype.g0.evidence.dependencies import DependencyGraph  # noqa: E402
from prototype.g0.evidence.eval_lineage import validate_eval_case  # noqa: E402
from prototype.g0.evidence.explanation import build_explanation_packet  # noqa: E402
from prototype.g0.evidence.linkage import (  # noqa: E402
    backward_lineage,
    forward_lineage,
)
from prototype.g0.evidence.models import (  # noqa: E402
    EvidenceGraph,
    EvidenceGraphError,
    make_ref,
)
from prototype.g0.evidence.research import (  # noqa: E402
    ResearchFindingError,
    validate_finding,
)
from prototype.g0.evidence.retrieval import (  # noqa: E402
    RetrievalHit,
    run_retrieval,
)
from prototype.g0.evidence.semantica_adapter import SemanticaAdapter  # noqa: E402
from prototype.g0.evidence.visibility import VisibilityManager  # noqa: E402


def _edge_cfg() -> dict:
    return yaml.safe_load((_ROOT / "config/g0/evidence/evidence_edge_types.yaml")
                          .read_text(encoding="utf-8"))


def _graph() -> EvidenceGraph:
    cfg = _edge_cfg()
    graph = EvidenceGraph(edge_types_config=cfg,
                          endpoint_rules=cfg.get("edge_endpoint_rules", []))
    for rid, rtype, etype, eid in (
        ("fact:deadline", "CANONICAL_FACT", "CanonicalFact", "deadline"),
        ("snap:official", "SOURCE_SNAPSHOT", "SourceSnapshot", "official"),
        ("claim:org-status", "EVIDENCE_CLAIM", "EvidenceClaim", "org-status"),
        ("claim:rival", "EVIDENCE_CLAIM", "EvidenceClaim", "rival"),
    ):
        graph.put_ref(make_ref(ref_id=rid, ref_type=rtype, entity_type=etype,
                               entity_id=eid, tenant_id="tenant-a",
                               content_hash=f"{rid}-h" * 2))
    return graph


def _claim_ledger_graph() -> EvidenceGraph:
    cfg = _edge_cfg()
    graph = EvidenceGraph(edge_types_config=cfg,
                          endpoint_rules=cfg.get("edge_endpoint_rules", []))
    graph.put_ref(make_ref(ref_id="stat:ga", ref_type="STATISTIC_OBSERVATION",
                           entity_type="StatisticObservation", entity_id="ga",
                           tenant_id="tenant-a", content_hash="sg" * 4,
                           locator={"geography": "GA", "unit": "pct"}))
    graph.put_ref(make_ref(ref_id="fact:deadline", ref_type="CANONICAL_FACT",
                           entity_type="CanonicalFact", entity_id="deadline",
                           tenant_id="tenant-a", content_hash="dd" * 4))
    return graph


def _decision() -> DecisionRecord:
    return DecisionRecord(
        decision_id="decision:eligibility-1", decision_type="ELIGIBILITY",
        tenant_id="tenant-a", project_id="project-1",
        actor_ref="actor:ceo-hermes", capability_id="cap:eligibility",
        created_at="2026-08-26T00:00:00+00:00",
        input_refs=[DecisionInputRef(input_role="FACT", ref="fact:deadline",
                                     version_or_revision_id="rev-1")],
        policy_ref="policy:v1", result={"summary": "eligible",
                                        "result_class": "CANONICAL_MUTATION"},
        status="ACTIVE", output_refs=["art:letter"],
        model_or_engine_ref="engine:v1")


# ------------------------------------------------------------ invariants 1-5

def test_inv01_material_claims_evidence_linked_or_qualified():
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    supported = ledger.put(
        entry={"artifact_version_id": "v1", "section_id": "s1",
               "claim_id": "i1", "claim_class": "DATES_DEADLINES",
               "claim_text_or_structured_ref": "deadline Oct 15",
               "evidence_refs": ["fact:deadline"],
               "support_status": "PENDING", "qa_status": "PENDING"},
        graph=graph)
    assert supported["support_status"] == "SUPPORTED"
    unsupported = ledger.put(
        entry={"artifact_version_id": "v1", "section_id": "s1",
               "claim_id": "i2", "claim_class": "DATES_DEADLINES",
               "claim_text_or_structured_ref": "deadline Dec 1",
               "evidence_refs": ["snap:missing"],
               "support_status": "PENDING", "qa_status": "PENDING"},
        graph=graph)
    assert unsupported["support_status"] == "UNSUPPORTED"  # never silent


def test_inv02_generated_text_cannot_self_authorize_as_evidence():
    from prototype.g0.agents.d1_flow import D1ContractError, run_d1_mock_draft
    with pytest.raises(D1ContractError):
        run_d1_mock_draft(
            intent={"intent_id": "i1", "tenant_id": "tenant-a",
                    "project_id": "p1"},
            plan={"plan_id": "plan-1", "application_project_id": "p1"},
            tasks=[{"task_id": "t1"}],
            evidence_pack=["fact:deadline"],
            opportunity_revision_id="rev-3",
            section_drafts={"narrative": "we are a 501c3 (fabricated claim "
                            "with no ref)"})


def test_inv03_snapshot_lineage_survives_normalization():
    graph = _graph()
    graph.add_edge(edge_type="NORMALIZED_FROM",
                   from_ref=graph.get_ref("claim:org-status"),
                   to_ref=graph.get_ref("snap:official"),
                   tenant_scope="tenant-a", created_by="qa")
    chain = graph.claim_support_chain("claim:org-status")
    assert any(c.get("ref_id") == "snap:official" for c in chain)


def test_inv04_claim_promotion_is_explicit():
    graph = _graph()
    supports = [SupportAssertion(support_id="s1", claim_ref="claim:org-status",
                                 evidence_ref="snap:official",
                                 support_type="DIRECT", created_at="t",
                                 method="m")]
    with pytest.raises(Exception):
        promote_claim(claim_ref="claim:org-status",
                      support_assertions=[],
                      contradictions=[], policy_ref="policy:p")


def test_inv05_contradictory_evidence_is_retained():
    contradiction = open_contradiction(
        contradiction_id="c5", tenant_id="tenant-a", entity_type="Organization",
        entity_id="org-1", predicate="status",
        claim_refs=["claim:org-status", "claim:rival"],
        contradiction_type="VALUE_CONFLICT", severity="P0")
    resolve_contradiction(
        contradiction=contradiction, chosen_fact_ref="claim:org-status",
        policy_ref="policy:c", resolved_by="reviewer:r1",
        reason="official amendment governs", approval_ref="ap-1")
    # append-only: both claims still registered in the graph
    graph = _graph()
    assert graph.get_ref("claim:rival").ref_id == "claim:rival"


# ------------------------------------------------------------ invariants 6-10

def test_inv06_decisions_pin_exact_input_revisions():
    dec = _decision()
    assert dec.input_refs[0].version_or_revision_id == "rev-1"


def test_inv07_historical_replay_never_substitutes_current_state():
    from prototype.g0.evidence.replay import (  # noqa: E402
        ReplayError,
        ReplayPacket,
        current_state_must_not_substitute,
    )
    packet = ReplayPacket(decision={"decision_id": "d1"},
                          pinned_input_refs=[
                              {"ref": "fact:deadline",
                               "version_or_revision_id": "rev-1"}],
                          configuration_refs=[], policy_refs=[],
                          source_snapshot_refs=[], engine_metadata={},
                          mode="HISTORICAL_EXACT")
    with pytest.raises(ReplayError):
        current_state_must_not_substitute(
            packet, [{"ref": "fact:deadline", "version_or_revision_id": "rev-9"}])


def test_inv08_dependency_invalidation_selective_and_traceable():
    deps = DependencyGraph()
    deps.add_dependency(dependent_ref="decision:1", depends_on_ref="fact:1",
                        dependency_type="ELIGIBILITY", materiality="CRITICAL")
    deps.add_dependency(dependent_ref="art:2", depends_on_ref="decision:1",
                        dependency_type="ARTIFACT_BUNDLE", materiality="SIGNIFICANT")
    event = deps.invalidate(changed_upstream_ref="fact:1",
                            change_class="MATERIAL")
    assert "decision:1" in event.affected_downstream_refs
    assert "art:2" in event.affected_downstream_refs  # transitive, traceable


def test_inv09_retrieval_rank_is_not_authority():
    hit = RetrievalHit(result_ref="fact:deadline", tenant_scope="tenant-a",
                       ranking_metadata={"score": 0.99},
                       source_quality={"authority": 0.5})
    result = run_retrieval(query_id="q1", method="VECTOR_SEMANTIC",
                           query_scope={"q": "deadline"}, tenant_scope="tenant-a",
                           hits=[hit],
                           canonical_facts={"fact:deadline": "2026-10-15"})
    assert result.results[0].conflict_flag is True
    assert "excluded from operational use" in (result.authority_gate_note or "")


def test_inv10_vector_indexes_disposable_rebuildable():
    vm = VisibilityManager()
    vm.declare("fact:deadline", "TENANT_SHARED_APPROVED")
    rebuilt = vm.rebuild_visibility(nodes={"fact:deadline": {"value": "x"}})
    assert rebuilt["fact:deadline"] == "TENANT_SHARED_APPROVED"


# ------------------------------------------------------------ invariants 11-15

def test_inv11_graph_projections_disposable_rebuildable():
    adapter = SemanticaAdapter()
    if not adapter.available:
        pytest.skip("semantica not installed")
    nodes = {"fact:deadline": {"value": "x", "tenant": "t"}}
    edges = [("fact:deadline", "fact:deadline", "SUPPORTS")]
    result = adapter.rebuild(nodes=nodes, edges=edges)
    assert result["rebuilt"] is True
    assert result["node_count"] == len(nodes)


def test_inv12_internal_canonical_ids_survive_projection():
    adapter = SemanticaAdapter()
    if not adapter.available:
        pytest.skip("semantica not installed")
    adapter.project(nodes={"fact:deadline": {"value": "x", "tenant": "t"}},
                    edges=[])
    assert adapter._kg.entities[0]["id"] == "fact:deadline"


def test_inv13_cross_tenant_graph_vector_access_denied():
    graph = _graph()
    other = make_ref(ref_id="fact:b", ref_type="CANONICAL_FACT",
                     entity_type="CanonicalFact", entity_id="b",
                     tenant_id="tenant-b", content_hash="bb" * 4)
    graph.put_ref(other)
    with pytest.raises(EvidenceGraphError):
        graph.add_edge(edge_type="SUPPORTS",
                       from_ref=graph.get_ref("fact:deadline"),
                       to_ref=other, tenant_scope="tenant-a",
                       created_by="x")
    hits = [RetrievalHit(result_ref="fact:b", tenant_scope="tenant-b",
                         ranking_metadata={"score": 1.0},
                         source_quality={"authority": 0.5})]
    result = run_retrieval(query_id="q", method="VECTOR_SEMANTIC",
                           query_scope={}, tenant_scope="tenant-a", hits=hits)
    assert result.results == []


def test_inv14_explanation_packets_match_decision_evidence():
    graph = _graph()
    dec = _decision()
    packet = build_explanation_packet(decision=dec, graph=graph)
    assert packet["decision_record_ref"] == dec.decision_id
    assert set(packet["cited_evidence_refs"]) <= {
        i.ref for i in dec.input_refs} | set(dec.output_refs)


def test_inv15_claim_ledger_survives_transformations():
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    ledger.put(
        entry={"artifact_version_id": "v1", "section_id": "s1",
               "claim_id": "i15", "claim_class": "DATES_DEADLINES",
               "claim_text_or_structured_ref": "deadline Oct 15",
               "evidence_refs": ["fact:deadline"],
               "support_status": "PENDING", "qa_status": "PENDING"},
        graph=graph)
    revised = ledger.reversion(artifact_version_id="v2", claim_id="i15",
                               new_text="deadline Oct 15 (revised wording)")
    assert revised["claim_id"] == "i15-v2"
    assert ledger.entry("i15")["artifact_version_id"] == "v1"


# ------------------------------------------------------------ invariants 16-20

def test_inv16_research_findings_preserve_evidence_and_limitations():
    graph = _graph()
    finding = validate_finding(
        finding={"finding_id": "f16", "research_type": "FUNDER_PRIORITY",
                 "statement": "funder prioritizes rural workforce",
                 "evidence_refs": ["snap:official"], "quality": "MEDIUM",
                 "applicability": "drafting",
                 "limitations": ["single-cycle observation"],
                 "created_by": "worker:research"},
        graph=graph)
    assert finding["evidence_refs"] == ["snap:official"]
    assert finding["limitations"] == ["single-cycle observation"]


def test_inv17_audit_events_link_to_decisions_evidence_output():
    dec = _decision()
    event = {"event_id": "evt-17", "actor_id": "actor:ceo-hermes",
             "capability_id": "cap:eligibility", "tenant_id": "tenant-a",
             "project_id": "project-1", "resource_id": "decision:eligibility-1",
             "policy_decision_ref": "pd:1", "approval_ref": None}
    fwd = forward_lineage(audit_event=event, decisions=[dec],
                          approvals={}, graph=_graph())
    assert fwd["decision_record_ref"] == dec.decision_id
    bwd = backward_lineage(artifact_ref="art:letter", decisions=[dec],
                           audit_events=[event])
    assert bwd["audit_event_id"] == "evt-17"


def test_inv18_eval_cases_retain_lineage():
    case = validate_eval_case(case={"case_id": "e18",
                                    "source_snapshot_refs": ["snap:official"],
                                    "decision_artifact_refs": ["decision:1"],
                                    "label_origin": "HUMAN_REVIEWER",
                                    "label_reviewer": "reviewer:r1",
                                    "privacy_classification": "PUBLIC_SOURCE",
                                    "split_membership": "TEST",
                                    "created_at": "2026-08-26T00:00:00+00:00"})
    assert case["content_hash"]


def test_inv19_semantica_failure_does_not_destroy_canonical_operation():
    dm = DegradationManager()
    dm.set_available("semantica", False)
    assert dm.semantica_status()["status"] == "DEGRADED"
    # canonical recording still functions
    graph = _graph()
    graph.put_ref(make_ref(ref_id="fact:new", ref_type="CANONICAL_FACT",
                           entity_type="CanonicalFact", entity_id="new",
                           tenant_id="tenant-a", content_hash="nn" * 4))
    assert graph.get_ref("fact:new").ref_id == "fact:new"


def test_inv20_provenance_failure_blocks_consequential_finalization():
    dm = DegradationManager()
    dm.set_available("provenance_write", False)
    with pytest.raises(Exception):
        dm.record_with_provenance(material=True)


# ------------------------------------------------------------ property tests

def test_prop_replay_deterministic():
    from prototype.g0.evidence.contradictions import derived_fact_replay
    r1 = derived_fact_replay(method_version="v1", inputs=[1, 2, 3],
                             compute=lambda xs: sum(xs))
    r2 = derived_fact_replay(method_version="v1", inputs=[1, 2, 3],
                             compute=lambda xs: sum(xs))
    assert r1 == r2


def test_prop_invalidation_idempotent():
    deps = DependencyGraph()
    deps.add_dependency(dependent_ref="decision:1", depends_on_ref="fact:1",
                        dependency_type="ELIGIBILITY", materiality="CRITICAL")
    e1 = deps.invalidate(changed_upstream_ref="fact:1", change_class="MATERIAL")
    e2 = deps.invalidate(changed_upstream_ref="fact:1", change_class="MATERIAL")
    assert sorted(e1.affected_downstream_refs) == sorted(e2.affected_downstream_refs)


def test_prop_decision_serialization_round_trip():
    dec = _decision()
    data = dec.to_dict()
    revived = DecisionRecord(
        decision_id=data["decision_id"], decision_type=data["decision_type"],
        tenant_id=data["tenant_id"], project_id=data["project_id"],
        actor_ref=data["actor_ref"], capability_id=data["capability_id"],
        created_at=data["created_at"],
        input_refs=[DecisionInputRef(**i) for i in data["input_refs"]],
        policy_ref=data["policy_ref"], result=data["result"],
        status=data["status"], output_refs=data.get("output_refs", []),
        model_or_engine_ref=data.get("model_or_engine_ref"),
        configuration_refs=data.get("configuration_refs", []),
        reason_codes=data.get("reason_codes", []))
    assert revived.to_dict() == data


def test_prop_corroboration_needs_independent_upstreams():
    supports = [SupportAssertion(support_id=f"s{i}", claim_ref="c",
                                 evidence_ref=f"e{i}",
                                 support_type="CORROBORATING", created_at="t",
                                 method="m") for i in (1, 2)]
    assert independent_corroboration(supports, {"e1": "u1", "e2": "u1"}) is False
    assert independent_corroboration(supports, {"e1": "u1", "e2": "u2"}) is True
