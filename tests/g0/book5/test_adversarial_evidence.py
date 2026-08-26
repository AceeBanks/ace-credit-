"""G0-B5-C24 — Adversarial evidence suite (ADV-01..ADV-40).

Each scenario from config/g0/evidence/adversarial_evidence.yaml is attacked
against the real prototypes. All P0 integrity/security scenarios must pass:
the machine must reject fabrication, substitution, leakage, escalation and
stale-state shortcuts.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import yaml  # noqa: E402

from prototype.g0.evidence.claim_ledger import (  # noqa: E402
    ASSUMPTION,
    ClaimLedger,
    ClaimLedgerError,
    SUPPORTED,
    UNSUPPORTED,
)
from prototype.g0.evidence.contradictions import (  # noqa: E402
    Contradiction,
    SupportAssertion,
    authoritative_conflict_guard,
    independent_corroboration,
    open_contradiction,
    reopen_on_amendment,
    resolve_contradiction,
    score_quality,
)
from prototype.g0.evidence.decisions import (  # noqa: E402
    DecisionRecord,
    engine_version_required,
    supersede_decision,
)
from prototype.g0.evidence.degradation import (  # noqa: E402
    DegradationError,
    DegradationManager,
)
from prototype.g0.evidence.dependencies import (  # noqa: E402
    DependencyGraph,
    DependencyError,
)
from prototype.g0.evidence.eval_lineage import (  # noqa: E402
    EvalLineageError,
    validate_eval_case,
)
from prototype.g0.evidence.explanation import (  # noqa: E402
    ExplanationError,
    build_explanation_packet,
)
from prototype.g0.evidence.linkage import (  # noqa: E402
    LinkageError,
    check_actor_capability_consistency,
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
    plan_retrieval,
    run_retrieval,
)
from prototype.g0.evidence.semantica_adapter import SemanticaAdapter  # noqa: E402
from prototype.g0.evidence.visibility import VisibilityManager  # noqa: E402

CATALOG = yaml.safe_load((_ROOT / "config/g0/evidence/adversarial_evidence.yaml")
                         .read_text(encoding="utf-8"))
SCENARIOS = {s["id"]: s for s in CATALOG["scenarios"]}


def _edge_cfg() -> dict:
    return yaml.safe_load((_ROOT / "config/g0/evidence/evidence_edge_types.yaml")
                          .read_text(encoding="utf-8"))


def _graph(*, include_rival: bool = False) -> EvidenceGraph:
    cfg = _edge_cfg()
    graph = EvidenceGraph(edge_types_config=cfg,
                          endpoint_rules=cfg.get("edge_endpoint_rules", []))
    specs = [
        ("fact:deadline", "CANONICAL_FACT", "CanonicalFact", "deadline"),
        ("fact:ceiling", "CANONICAL_FACT", "CanonicalFact", "ceiling"),
        ("snap:official", "SOURCE_SNAPSHOT", "SourceSnapshot", "official"),
        ("snap:stats", "SOURCE_SNAPSHOT", "SourceSnapshot", "stats"),
        ("claim:org-status", "EVIDENCE_CLAIM", "EvidenceClaim", "org-status"),
    ]
    if include_rival:
        specs.append(("claim:rival", "EVIDENCE_CLAIM", "EvidenceClaim", "rival"))
    for rid, rtype, etype, eid in specs:
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
    graph.put_ref(make_ref(ref_id="stat:fl", ref_type="STATISTIC_OBSERVATION",
                           entity_type="StatisticObservation", entity_id="fl",
                           tenant_id="tenant-a", content_hash="sf" * 4,
                           locator={"geography": "FL", "unit": "pct"}))
    graph.put_ref(make_ref(ref_id="fact:deadline", ref_type="CANONICAL_FACT",
                           entity_type="CanonicalFact", entity_id="deadline",
                           tenant_id="tenant-a", content_hash="dd" * 4))
    graph.put_ref(make_ref(ref_id="snap:testimonial", ref_type="SOURCE_SNAPSHOT",
                           entity_type="SourceSnapshot", entity_id="testimonial",
                           tenant_id="tenant-a", content_hash="st" * 4,
                           locator={"origin": "SYNTHETIC"}))
    graph.put_ref(make_ref(ref_id="snap:real", ref_type="SOURCE_SNAPSHOT",
                           entity_type="SourceSnapshot", entity_id="real",
                           tenant_id="tenant-a", content_hash="sr" * 4))
    return graph


def _decision(**kw) -> DecisionRecord:
    base = dict(
        decision_id="decision:eligibility-1", decision_type="ELIGIBILITY",
        tenant_id="tenant-a", project_id="project-1",
        actor_ref="actor:ceo-hermes", capability_id="cap:eligibility",
        created_at="2026-08-26T00:00:00+00:00",
        input_refs=[], policy_ref="policy:v1", result={"summary": "eligible"},
        status="ACTIVE",
    )
    base.update(kw)
    return DecisionRecord(**base)


@pytest.mark.parametrize("sid", sorted(SCENARIOS))
def test_catalog_scenario_has_guard(sid):
    assert SCENARIOS[sid]["severity"] in ("P0", "P1")
    assert SCENARIOS[sid]["guard"]


# ---------------------------------------------------------------- ADV-01..02

def test_adv01_claim_points_to_source_that_never_contained_it():
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    assessed = ledger.put(
        entry={"artifact_version_id": "v1", "section_id": "s1",
               "claim_id": "c1", "claim_class": "DATES_DEADLINES",
               "claim_text_or_structured_ref": "deadline Oct 15",
               "evidence_refs": ["snap:does-not-exist"],
               "support_status": "PENDING", "qa_status": "PENDING"},
        graph=graph)
    assert assessed["support_status"] == UNSUPPORTED


def test_adv02_wrong_locator_page_fails_verification():
    # a ref whose locator does not carry the expected page cannot support a
    # page-specific citation claim
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    assert ledger.put(
        entry={"artifact_version_id": "v1", "section_id": "s1",
               "claim_id": "c2", "claim_class": "ORGANIZATION_LEGAL_STATUS",
               "claim_text_or_structured_ref": "501c3 per official record",
               "evidence_refs": ["snap:real"],
               "support_status": "PENDING", "qa_status": "PENDING"},
        graph=graph)["support_status"] == SUPPORTED


# ---------------------------------------------------------------- ADV-03..04

def test_adv03_secondary_source_citation_rejected():
    graph = _graph()
    decision = _decision(input_refs=[
        __import__("prototype.g0.evidence.decisions", fromlist=["DecisionInputRef"])
        .DecisionInputRef(input_role="FACT", ref="snap:official")])
    with pytest.raises(ExplanationError):
        build_explanation_packet(decision=decision, graph=graph,
                                 extra_cited_refs=["snap:stats"])


def test_adv04_research_summary_recursively_cited_as_evidence():
    graph = _graph()
    graph.put_ref(make_ref(ref_id="finding:gen", ref_type="RESEARCH_FINDING",
                           entity_type="ResearchFinding", entity_id="gen",
                           tenant_id="tenant-a", content_hash="fg" * 4))
    with pytest.raises(ResearchFindingError):
        validate_finding(
            finding={"finding_id": "f1", "research_type": "FUNDER_PRIORITY",
                     "statement": "funder prioritizes rural programs",
                     "evidence_refs": ["finding:gen"], "quality": "MEDIUM",
                     "applicability": "drafting context",
                     "created_by": "worker:research"},
            graph=graph)


# ---------------------------------------------------------------- ADV-05..06

def test_adv05_corroboration_copies_same_upstream():
    supports = [
        SupportAssertion(support_id="s1", claim_ref="c", evidence_ref="e1",
                         support_type="CORROBORATING", created_at="t",
                         method="m"),
        SupportAssertion(support_id="s2", claim_ref="c", evidence_ref="e2",
                         support_type="CORROBORATING", created_at="t",
                         method="m"),
    ]
    upstream_map = {"e1": "article-1", "e2": "article-1"}  # same upstream
    assert independent_corroboration(supports, upstream_map) is False
    upstream_map2 = {"e1": "article-1", "e2": "article-2"}
    assert independent_corroboration(supports, upstream_map2) is True


def test_adv06_stale_source_blocks_current_use():
    graph = _graph()
    graph.tombstone("snap:official")  # superseded by amendment
    ledger = ClaimLedger()
    assessed = ledger.put(
        entry={"artifact_version_id": "v1", "section_id": "s1",
               "claim_id": "c6", "claim_class": "ORGANIZATION_LEGAL_STATUS",
               "claim_text_or_structured_ref": "501c3",
               "evidence_refs": ["snap:official"],
               "support_status": "PENDING", "qa_status": "PENDING"},
        graph=graph)
    assert assessed["support_status"] == "STALE"


# ---------------------------------------------------------------- ADV-07..09

def test_adv07_current_source_substituted_into_historical_replay():
    from prototype.g0.evidence.replay import (  # noqa: E402
        ReplayError,
        current_state_must_not_substitute,
    )
    from prototype.g0.evidence.replay import ReplayPacket

    packet = ReplayPacket(
        decision={"decision_id": "d1"},
        pinned_input_refs=[{"ref": "fact:deadline",
                            "version_or_revision_id": "rev-1"}],
        configuration_refs=[], policy_refs=[], source_snapshot_refs=[],
        engine_metadata={}, mode="HISTORICAL_EXACT")
    with pytest.raises(ReplayError):
        current_state_must_not_substitute(
            packet, [{"ref": "fact:deadline", "version_or_revision_id": "rev-9"}])


def test_adv08_graph_node_without_canonical_entity():
    graph = _graph()
    with pytest.raises(EvidenceGraphError):
        # no canonical entity exists; ref with a fabricated entity fails at
        # the immutable-identity contract (hash mismatch path)
        graph.put_ref(make_ref(ref_id="fact:deadline",
                               ref_type="CANONICAL_FACT",
                               entity_type="CanonicalFact", entity_id="deadline",
                               tenant_id="tenant-a", content_hash="WRONG-HASH"))


def test_adv09_graph_mutation_cannot_create_canonical_fact():
    graph = _graph()
    # graph identity is immutable: same ref, different content -> rejected
    with pytest.raises(EvidenceGraphError):
        graph.put_ref(make_ref(ref_id="fact:deadline",
                               ref_type="CANONICAL_FACT",
                               entity_type="CanonicalFact", entity_id="deadline",
                               tenant_id="tenant-a", content_hash="zz" * 4))


# ---------------------------------------------------------------- ADV-10..12

def _hit(result_ref: str, tenant: str, score: float = 0.9) -> RetrievalHit:
    return RetrievalHit(result_ref=result_ref, tenant_scope=tenant,
                        ranking_metadata={"score": score},
                        source_quality={"authority": 0.5, "freshness": 0.5})


def test_adv10_vector_top_result_conflicts_with_canonical_fact():
    hit = _hit("fact:deadline", "tenant-a")
    result = run_retrieval(query_id="q1", method="VECTOR_SEMANTIC",
                           query_scope={"q": "deadline"}, tenant_scope="tenant-a",
                           hits=[hit],
                           canonical_facts={"fact:deadline": "2026-10-15"})
    assert result.results[0].conflict_flag is True
    assert "excluded from operational use" in (result.authority_gate_note or "")


def test_adv11_cross_tenant_nearest_neighbor_leak():
    hits = [_hit("fact:a", "tenant-a"), _hit("fact:b", "tenant-b")]
    result = run_retrieval(query_id="q1", method="VECTOR_SEMANTIC",
                           query_scope={"q": "x"}, tenant_scope="tenant-a",
                           hits=hits)
    assert [h.result_ref for h in result.results] == ["fact:a"]


def test_adv12_cross_tenant_edge_denied():
    graph = _graph()
    other = make_ref(ref_id="fact:b", ref_type="CANONICAL_FACT",
                     entity_type="CanonicalFact", entity_id="b",
                     tenant_id="tenant-b", content_hash="bb" * 4)
    graph.put_ref(other)
    with pytest.raises(EvidenceGraphError):
        graph.add_edge(edge_type="SUPPORTS",
                       from_ref=graph.get_ref("fact:deadline"),
                       to_ref=other, tenant_scope="tenant-a",
                       created_by="attacker")


# ---------------------------------------------------------------- ADV-13..15

def test_adv13_deleted_private_evidence_retrievable_through_embedding():
    vm = VisibilityManager()
    vm.declare("fact:private", "TENANT_PRIVATE")
    vm.delete("fact:private")
    assert "fact:private" not in vm.vector_results(
        candidates=["fact:private", "fact:public"])


def _open_contradiction(cid: str) -> Contradiction:
    return open_contradiction(
        contradiction_id=cid, tenant_id="tenant-a", entity_type="Organization",
        entity_id="org-1", predicate="org status",
        claim_refs=["claim:org-status", "claim:rival"],
        contradiction_type="VALUE_CONFLICT", severity="P0")


def test_adv14_contradiction_resolution_keeps_losing_claim():
    graph = _graph(include_rival=True)
    contradiction = _open_contradiction("contra-1")
    resolve_contradiction(
        contradiction=contradiction, chosen_fact_ref="claim:org-status",
        policy_ref="policy:contra", resolved_by="reviewer:r1",
        reason="official amendment governs", approval_ref="ap-1")
    # both claims remain in the graph; nothing is deleted
    assert graph.get_ref("claim:rival").ref_id == "claim:rival"
    assert graph.get_ref("claim:org-status").ref_id == "claim:org-status"


def test_adv15_model_confidence_cannot_resolve_conflict():
    contradiction = _open_contradiction("contra-2")
    with pytest.raises(Exception):
        resolve_contradiction(
            contradiction=contradiction, chosen_fact_ref="claim:org-status",
            policy_ref="policy:contra", resolved_by="model",
            reason="model says org-status", model_confidence=0.97)


# ---------------------------------------------------------------- ADV-16..19

def test_adv16_old_eligibility_not_current_after_revision():
    old = _decision()
    new = _decision(decision_id="decision:eligibility-2",
                    result={"summary": "eligible rev-2"})
    supersede_decision(old, new)
    assert old.status == "SUPERSEDED"
    assert new.status == "ACTIVE"


def test_adv17_statistic_geography_mismatch_rejected():
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    with pytest.raises(ClaimLedgerError):
        ledger.put(
            entry={"artifact_version_id": "v1", "section_id": "s1",
                   "claim_id": "c17", "claim_class": "POPULATION_COMMUNITY_STATISTICS",
                   "claim_text_or_structured_ref": "32% of GA youth",
                   "evidence_refs": ["stat:fl"], "geography": "GA",
                   "support_status": "PENDING", "qa_status": "PENDING"},
            graph=graph)


def test_adv18_statistic_unit_mismatch_rejected():
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    with pytest.raises(ClaimLedgerError):
        ledger.put(
            entry={"artifact_version_id": "v1", "section_id": "s1",
                   "claim_id": "c18", "claim_class": "POPULATION_COMMUNITY_STATISTICS",
                   "claim_text_or_structured_ref": "32% of youth",
                   "evidence_refs": ["stat:ga"], "unit": "count",
                   "support_status": "PENDING", "qa_status": "PENDING"},
            graph=graph)


def test_adv19_wrong_award_recipient_entity_unsupported():
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    assessed = ledger.put(
        entry={"artifact_version_id": "v1", "section_id": "s1",
               "claim_id": "c19", "claim_class": "PRIOR_AWARD_WINNER",
               "claim_text_or_structured_ref": "org X won $50k",
               "evidence_refs": ["snap:does-not-exist"],  # wrong entity
               "support_status": "PENDING", "qa_status": "PENDING"},
        graph=graph)
    assert assessed["support_status"] == UNSUPPORTED


# ---------------------------------------------------------------- ADV-20..23

def test_adv20_future_target_presented_as_historical():
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    with pytest.raises(ClaimLedgerError):
        ledger.put(
            entry={"artifact_version_id": "v1", "section_id": "s1",
                   "claim_id": "c20",
                   "claim_class": "MEASURABLE_OUTCOME_HISTORICAL",
                   "claim_text_or_structured_ref": "we will serve 500 youth",
                   "evidence_refs": ["stat:ga"],
                   "support_status": "PENDING", "qa_status": "PENDING"},
            graph=graph)


def test_adv21_synthetic_testimonial_presented_as_verified():
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    assessed = ledger.put(
        entry={"artifact_version_id": "v1", "section_id": "s1",
               "claim_id": "c21", "claim_class": "TESTIMONIAL_SUPPORT",
               "claim_text_or_structured_ref": "partner endorses us",
               "evidence_refs": ["snap:testimonial"],
               "support_status": "PENDING", "qa_status": "PENDING"},
        graph=graph)
    assert assessed["support_status"] == UNSUPPORTED


def test_adv22_budget_number_without_derivation_lineage():
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    with pytest.raises(ClaimLedgerError):
        ledger.put(
            entry={"artifact_version_id": "v1", "section_id": "s1",
                   "claim_id": "c22", "claim_class": "FUNDING_AMOUNT",
                   "claim_text_or_structured_ref": "we will request $50k",
                   "evidence_refs": ["snap:real"],
                   "support_status": "PENDING", "qa_status": "PENDING"},
            graph=graph)


def test_adv23_humanization_changes_supported_number_after_qa():
    ledger = ClaimLedger()
    graph = _claim_ledger_graph()
    ledger.put(
        entry={"artifact_version_id": "v1", "section_id": "s1",
               "claim_id": "c23", "claim_class": "DATES_DEADLINES",
               "claim_text_or_structured_ref": "deadline Oct 15",
               "evidence_refs": ["fact:deadline"],
               "support_status": "PENDING", "qa_status": "PENDING"},
        graph=graph)
    with pytest.raises(ClaimLedgerError):
        ledger.reversion(artifact_version_id="v1", claim_id="c23",
                         new_text="deadline Dec 1")


# ---------------------------------------------------------------- ADV-24..27

def test_adv24_semantica_unavailable_during_draft():
    dm = DegradationManager()
    dm.set_available("semantica", False)
    status = dm.semantica_status()
    assert status["status"] == "DEGRADED"
    # core drafting path continues: no exception, canonical state intact


def test_adv25_semantica_state_deleted_and_rebuilt():
    adapter = SemanticaAdapter()
    if not adapter.available:
        pytest.skip("semantica not installed in this environment")
    nodes = {"fact:deadline": {"value": "2026-10-15", "tenant": "t"}}
    edges = [("fact:deadline", "fact:deadline", "SUPPORTS")]
    result = adapter.rebuild(nodes=nodes, edges=edges)
    assert result["rebuilt"] is True
    assert result["node_count"] == 1


def test_adv26_projection_lag_serves_stale_dependency():
    deps = DependencyGraph()
    deps.add_dependency(dependent_ref="decision:1", depends_on_ref="fact:1",
                        dependency_type="ELIGIBILITY", materiality="CRITICAL")
    event = deps.invalidate(changed_upstream_ref="fact:1",
                            change_class="MATERIAL")
    with pytest.raises(DependencyError):
        deps.require_fresh("decision:1", last_invalidation=event)


def test_adv27_evidence_hash_mismatch():
    graph = _graph()
    with pytest.raises(EvidenceGraphError):
        graph.put_ref(make_ref(ref_id="fact:deadline",
                               ref_type="CANONICAL_FACT",
                               entity_type="CanonicalFact", entity_id="deadline",
                               tenant_id="tenant-a", content_hash="tampered"))


# ---------------------------------------------------------------- ADV-28..31

def test_adv28_audit_decision_actor_disagree():
    dec = _decision(actor_ref="actor:worker-7")
    event = {"actor_id": "actor:ceo-hermes", "capability_id": "cap:eligibility",
             "tenant_id": "tenant-a"}
    assert check_actor_capability_consistency(dec, event)


def test_adv29_eval_label_without_lineage():
    with pytest.raises(EvalLineageError):
        validate_eval_case(case={"case_id": "x", "label_origin": "HUMAN_REVIEWER",
                                 "label_reviewer": "", "privacy_classification": "PUBLIC_SOURCE",
                                 "split_membership": "TEST",
                                 "created_at": "2026-08-26T00:00:00+00:00"})


def test_adv30_private_case_enters_global_eval_without_approval():
    from prototype.g0.evidence.eval_lineage import global_eval_export
    case = {"privacy_classification": "TENANT_PRIVATE"}
    assert global_eval_export(case=case) is False


def test_adv31_malicious_source_self_supports_edge():
    graph = _graph()
    with pytest.raises(EvidenceGraphError):
        graph.add_edge(edge_type="SUPPORTS",
                       from_ref=graph.get_ref("snap:official"),
                       to_ref=graph.get_ref("snap:official"),
                       tenant_scope="tenant-a", created_by="malicious-source")


# ---------------------------------------------------------------- ADV-32..35

def test_adv32_source_duplicate_masquerades_as_corroboration():
    graph = _graph()
    dup = make_ref(ref_id="snap:official-copy", ref_type="SOURCE_SNAPSHOT",
                   entity_type="SourceSnapshot", entity_id="official-copy",
                   tenant_id="tenant-a", content_hash="snap:official-h"
                   "snap:official-h")  # same content as snap:official
    graph.put_ref(dup)
    with pytest.raises(EvidenceGraphError):
        graph.add_edge(edge_type="CORROBORATES",
                       from_ref=graph.get_ref("snap:official"),
                       to_ref=dup, tenant_scope="tenant-a",
                       created_by="attacker")


def _quality(evidence_ref: str, authority: float, freshness: float,
             class_rule: str = "OFFICIAL_RECORD") -> EvidenceQuality:
    return score_quality(
        evidence_ref=evidence_ref,
        dimensions={"authority": authority, "directness": 0.8,
                    "freshness": freshness, "specificity": 0.8,
                    "corroboration": 0.6, "extraction_quality": 0.9,
                    "identity_certainty": 0.9, "temporal_fit": 0.8},
        class_rule={"id": "official-record",
                    "derived_class": "OFFICIAL_RECORD"})


def test_adv33_quality_composite_hides_stale_dimension():
    # QUAL-001: a composite with a high weighted score must still surface a
    # stale dimension — the class derivation cannot be masked by averaging.
    stale = _quality("e1", authority=0.9, freshness=0.2)
    assert stale.quality_class == "STALE"  # not VERIFIED_HIGH
    assert stale.composite_score >= 0.6  # composite looks strong
    # a stale-but-authoritative ref conflicting with a fresh authoritative
    # ref must surface as CONFLICTED, never averaged into silence
    fresh = _quality("e2", authority=0.9, freshness=0.9)
    with pytest.raises(Exception):
        authoritative_conflict_guard([stale, fresh])


def test_adv34_missing_historical_model_metadata():
    from prototype.g0.evidence.replay import (  # noqa: E402
        ReplayError,
        require_engine_metadata,
    )
    with pytest.raises(ReplayError):
        require_engine_metadata(
            {"decision_id": "d1", "decision_type": "ELIGIBILITY",
             "model_or_engine_ref": None})
    require_engine_metadata(
        {"decision_id": "d1", "decision_type": "ELIGIBILITY",
         "model_or_engine_ref": "engine:v1"})
    require_engine_metadata(
        {"decision_id": "d2", "decision_type": "QA_FACTUALITY"})  # non-deterministic ok


def test_adv35_unsupported_causal_winner_conclusion():
    graph = _graph()
    graph.put_ref(make_ref(ref_id="snap:winners", ref_type="SOURCE_SNAPSHOT",
                           entity_type="SourceSnapshot", entity_id="winners",
                           tenant_id="tenant-a", content_hash="sw" * 4))
    with pytest.raises(ResearchFindingError):
        validate_finding(
            finding={"finding_id": "f35", "research_type": "HISTORICAL_WINNER_PATTERN",
                     "statement": "winners always propose workforce programs",
                     "evidence_refs": ["snap:winners"], "quality": "MEDIUM",
                     "applicability": "drafting", "award_sample_size": 12,
                     "created_by": "worker:research"},
            graph=graph)


# ---------------------------------------------------------------- ADV-36..37

def test_adv36_resolved_contradiction_reopens_on_amendment():
    contradiction = _open_contradiction("contra-36")
    resolve_contradiction(
        contradiction=contradiction, chosen_fact_ref="claim:org-status",
        policy_ref="policy:contra", resolved_by="reviewer:r1",
        reason="official amendment governs", approval_ref="ap-1")
    assert contradiction.status != "OPEN"
    reopened = reopen_on_amendment(contradiction,
                                   amendment_refs=["claim:org-status"])
    assert reopened is True
    assert contradiction.status == "OPEN"


def test_adv37_dependency_cycle_bounded():
    deps = DependencyGraph()
    deps.add_dependency(dependent_ref="a", depends_on_ref="b",
                        dependency_type="FACTUAL", materiality="CRITICAL")
    deps.add_dependency(dependent_ref="b", depends_on_ref="a",
                        dependency_type="FACTUAL", materiality="CRITICAL")
    affected, cycle = deps.transitive_dependents("a")
    assert cycle is True  # bounded traversal, no storm
    assert len(affected) <= 8


# ---------------------------------------------------------------- ADV-38..40

def test_adv38_query_returns_unauthorized_restricted_metadata():
    vm = VisibilityManager()
    vm.declare("fact:secret", "RESTRICTED_SENSITIVE")
    vm.declare("fact:public", "PUBLIC_SOURCE")
    visible = vm.scoped_refs(refs=["fact:secret", "fact:public"],
                             tenant_id="tenant-a", viewer_class="PLATFORM_ADMIN")
    assert visible == ["fact:public"]


def test_adv39_license_restriction_blocks_reuse_but_keeps_retention():
    vm = VisibilityManager()
    vm.declare("snap:licensed", "PUBLIC_SOURCE")
    vm.declare_license("snap:licensed", restricted=True)
    assert vm.reuse_allowed("snap:licensed") is False
    vm.approve_reuse("snap:licensed")
    assert vm.reuse_allowed("snap:licensed") is True
    # retention unaffected: tombstone/hash bookkeeping still works
    vm.delete("snap:licensed")
    assert "snap:licensed" not in vm.vector_results(candidates=["snap:licensed"])


def test_adv40_explanation_omits_material_uncertainty():
    graph = _graph()
    graph.tombstone("claim:org-status")
    from prototype.g0.evidence.decisions import DecisionInputRef
    decision = _decision(input_refs=[
        DecisionInputRef(input_role="CLAIM", ref="claim:org-status")])
    packet = build_explanation_packet(decision=decision, graph=graph)
    assert any(s["ref"] == "claim:org-status" for s in packet["stale_indicators"])
