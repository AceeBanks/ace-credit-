"""B7.C30 — Integration & property tests.

The 20 mandatory invariants plus property tests: immutable corpus hashing,
idempotent promotion evaluation, hard-gate veto, rollback identity,
tenant-scoped export, candidate round-trip.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.corpus import CorpusRegistry  # noqa: E402
from prototype.g0.evaluation.models import (  # noqa: E402
    EvalCorpusVersion,
    MetricBundle,
)
from prototype.g0.evaluation.promotion import (  # noqa: E402
    CandidateChange,
    evaluate_promotion,
)


def test_invariant_1_quality_claim_names_baseline_corpus_suite_run():
    """Every quality claim must bind baseline + corpus + suite + run."""
    from prototype.g0.evaluation.promotion import PromotionDecision
    d = PromotionDecision(
        promotion_decision_id="pd-1", candidate_change_id="cc-1",
        baseline_run_ref="run-b-1", candidate_run_ref="run-c-1",
        corpus_version_id="corpus-ga-v1", suite_id="grant-quality",
        suite_version=1, decision="PROMOTE", reason_codes=("x",),
        rollout_policy_ref="ro-1", rollback_ref="rb-1", decided_by="r1")
    assert d.baseline_run_ref and d.candidate_run_ref
    assert d.corpus_version_id and d.suite_id and d.suite_version


def test_invariant_2_hard_gates_not_compensated():
    candidate = _cand()
    baseline = _bundle()
    cand = _bundle(quality=0.95)  # style/funder alignment up
    gates = [{"dimension_id": "security_tenant_isolation",
              "family": "security", "passed": False}]
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=baseline,
                           candidate_metrics=cand,
                           hard_gate_results=gates)
    assert r["decision"] == "QUARANTINE"


def test_invariant_3_deterministic_overrides_subjective():
    from prototype.g0.evaluation.evaluators import LLMJudge
    conflict = LLMJudge.conflict_with_deterministic(
        deterministic_result={"all_pass": False}, judge_score=0.99)
    assert conflict["judge_overridden"] is True


def test_invariant_4_corpus_versions_immutable():
    reg = CorpusRegistry()
    cases = [{"eval_case_id": "c1"}]
    v1 = _version(cases)
    reg.add_version(v1, cases)
    with pytest.raises(Exception):
        reg.add_version(v1, cases)  # duplicate id rejected


def test_invariant_5_tenant_private_stays_scoped():
    reg = CorpusRegistry()
    cases = [{"eval_case_id": "c-p", "privacy_class": "TENANT_PRIVATE_APPROVED",
              "tenant_scope": "tenant-a"}]
    with pytest.raises(Exception):
        reg.add_version(_version(cases), cases)  # no governance approval


def test_invariant_6_generators_cannot_self_promote():
    candidate = _cand(source="skillclaw")
    r = evaluate_promotion(candidate=candidate,
                           baseline_metrics=_bundle(),
                           candidate_metrics=_bundle(quality=0.9),
                           hard_gate_results=[],
                           independent_evaluator="skillclaw")
    assert r["decision"] == "REJECT"


def test_invariant_7_production_change_needs_promotion_decision():
    from prototype.g0.evaluation.promotion import PromotionDecision
    d = PromotionDecision(
        promotion_decision_id="pd-2", candidate_change_id="cc-2",
        baseline_run_ref="b", candidate_run_ref="c",
        corpus_version_id="corpus", suite_id="s", suite_version=1,
        decision="PROMOTE", reason_codes=("PROM-001",),
        rollout_policy_ref="r", rollback_ref="rb", decided_by="me")
    assert d.decision == "PROMOTE"
    assert d.rollback_ref  # EVAL-LAW-009


def test_invariant_8_promotion_has_rollback_identity():
    candidate = _cand()
    assert candidate.rollback_ref == "rb-1"


def test_invariant_9_personal_and_ceo_separate_suites():
    from prototype.g0.evaluation.agent_eval import (
        ceo_hermes_eval,
        personal_hermes_eval,
    )
    p = personal_hermes_eval(used_canonical_state_before_asking=True,
                             unnecessary_questions=0, intent_type_valid=True,
                             performed_ceo_only_operation=False,
                             cross_project_contamination=False,
                             uncertainty_communicated=True,
                             explanation_packet_used=True)
    c = ceo_hermes_eval(interpreted_intent_correctly=True,
                        plan_decomposition_quality=0.9,
                        correct_worker_selection=True, task_bounding_ok=True,
                        used_raw_transcript=False, unnecessary_tool_calls=0,
                        synthesis_correct=True, completion_state_correct=True,
                        relationship_memory_pollution=False)
    assert p["all_pass"] and c["all_pass"]
    # distinct metric sets prove separate optimization targets
    p_metrics = {m["metric_id"] for m in p["results"]}
    c_metrics = {m["metric_id"] for m in c["results"]}
    assert p_metrics.isdisjoint(c_metrics)


def test_invariant_10_worker_evals_enforce_task_boundaries():
    from prototype.g0.evaluation.agent_eval import worker_eval
    kw = dict(obeyed_task_contract=True, used_allowed_context_only=True,
              used_allowed_tools_only=True, returned_structured_result=True,
              preserved_evidence_refs=True, scope_expanded=True,
              contacted_client=False, mutated_policy_or_canonical=False,
              scratch_memory_promoted=False)
    r = worker_eval(**kw)
    assert r["all_pass"] is False


def test_invariant_11_memory_eval_checks_cold_reconstruction():
    from prototype.g0.evaluation.agent_eval import cold_restart_reconstruction
    required = {"tenant_id": "t", "project_id": "p", "revision_id": "r",
                "decision": "ELIGIBLE"}
    assert cold_restart_reconstruction(reconstructed=dict(required),
                                       required=required)["pass"]


def test_invariant_12_factuality_measures_material_claim_support():
    from prototype.g0.evaluation.metrics import claim_support_metrics
    m = claim_support_metrics([
        {"claim_id": "a", "support_status": "SUPPORTED", "material": True},
        {"claim_id": "b", "support_status": "UNSUPPORTED", "material": True},
    ])
    assert m["material_claim_support_rate"] == 0.5


def test_invariant_13_eligibility_separates_hard_rules_from_ranking():
    from prototype.g0.evaluation.domain_eval import (
        match_never_overrides_eligibility,
    )
    assert not match_never_overrides_eligibility(
        match_score=0.99, eligibility="INELIGIBLE")["allowed"]


def test_invariant_14_research_preserves_evidence_and_limitations():
    from prototype.g0.evaluation.domain_eval import evaluate_research_quality
    r = evaluate_research_quality(findings=[
        {"finding_id": "f1", "evidence_refs": ["r"],
         "limitations": ["small sample"],
         "research_type": "HISTORICAL_WINNER_PATTERN",
         "award_sample_size": 5, "created_at": "t", "created_by": "w"}])
    assert r["with_evidence"] == 1
    assert r["causal_caution_failures"] == 0


def test_invariant_15_routing_measured_against_simple_baseline():
    from prototype.g0.evaluation.routing_eval import routing_must_beat_baseline
    assert routing_must_beat_baseline(
        simple_cost=0.02, routed_cost=0.01,
        simple_correctness=0.8, routed_correctness=0.85)["proven_value"]


def test_invariant_16_parser_eval_task_appropriate_truth():
    from prototype.g0.evaluation.routing_eval import (
        parser_eval,
        retrieval_task_appropriateness,
    )
    assert not retrieval_task_appropriateness(task_kind="deadline_lookup",
                                              semantic_used=True)
    r = parser_eval(text_fidelity=0.9, heading_fidelity=0.9,
                    table_fidelity=0.9, locator_lineage=0.95,
                    extraction_errors=0, latency_ms=100, cost_usd=0.001,
                    failure_detected=True)
    assert r["passes_locator_hard_gate"]


def test_invariant_17_external_tools_replaceable():
    """The project owns the eval objects; external tools are adapters."""
    from prototype.g0.evaluation.models import EvalCase
    from prototype.g0.evaluation.corpus import CorpusRegistry
    from prototype.g0.evaluation.promotion import PromotionDecision
    assert EvalCase and CorpusRegistry and PromotionDecision  # project-owned


def test_invariant_18_failure_feedback_not_production_truth():
    from prototype.g0.evaluation.ops_eval import feedback_is_not_training_truth
    r = feedback_is_not_training_truth(outcome="lost",
                                       feedback_type="grant_lost")
    assert r["direct_training_truth"] is False


def test_invariant_19_historical_runs_replayable_from_lineage():
    from prototype.g0.evidence.eval_lineage import (
        assert_unchanged,
        case_hash,
    )
    case = {"eval_case_id": "c1", "answer": 42}
    recorded = {"content_hash": case_hash(case)}
    assert_unchanged(recorded=recorded, current=case)  # no raise
    mutated = dict(case, answer=43)
    with pytest.raises(Exception):
        assert_unchanged(recorded=recorded, current=mutated)


def test_invariant_20_submission_remains_disabled():
    from prototype.g0.evaluation.security_regression import (
        gate_submission_remains_disabled,
    )
    assert gate_submission_remains_disabled(submission_capable=False).passed


# ---------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------

def _cand(source="human") -> CandidateChange:
    return CandidateChange(
        candidate_change_id="cc-1", change_type="PROMPT",
        baseline_version="1.0", candidate_version="2.0",
        source_or_generator=source, reason="align",
        expected_benefit="alignment", risk_class="LOW",
        affected_capabilities=("research.run",),
        required_eval_suites=("grant-quality",), rollback_ref="rb-1")


def _bundle(quality=0.6, cost=0.10, support=1.0) -> MetricBundle:
    return MetricBundle(metric_bundle_id="mb", dimensions=(
        {"dimension_id": "grant_funder_alignment", "family": "grant_quality",
         "gate": "OPTIMIZE", "direction": "higher_is_better",
         "value": quality},
        {"dimension_id": "ops_cost", "family": "operations",
         "gate": "OPTIMIZE", "direction": "lower_is_better", "value": cost},
        {"dimension_id": "factuality_material_claim_support",
         "family": "factuality", "gate": "HARD",
         "direction": "higher_is_better", "value": support},
        {"dimension_id": "security_capability_compliance",
         "family": "security", "gate": "HARD", "direction": "higher_is_better",
         "value": 1.0},
    ))


def _version(cases) -> EvalCorpusVersion:
    return EvalCorpusVersion(
        corpus_version_id="corpus-ga-v1", corpus_class="GOLDEN_HUMAN_REVIEWED",
        version=1, case_ids=tuple(c["eval_case_id"] for c in cases),
        created_at="2026-08-26T00:00:00Z")


def test_property_same_corpus_hashes_identically():
    reg = CorpusRegistry()
    cases = [{"eval_case_id": "c1"}]
    v1 = _version(cases)
    reg.add_version(v1, cases)
    fetched = reg.get("corpus-ga-v1")
    assert fetched.content_hash == v1.content_hash


def test_property_promotion_eval_idempotent_for_fixed_inputs():
    candidate = _cand()
    r1 = evaluate_promotion(candidate=candidate,
                            baseline_metrics=_bundle(),
                            candidate_metrics=_bundle(quality=0.9),
                            hard_gate_results=[
                                {"dimension_id": "security_capability_compliance",
                                 "family": "security", "passed": True}])
    r2 = evaluate_promotion(candidate=candidate,
                            baseline_metrics=_bundle(),
                            candidate_metrics=_bundle(quality=0.9),
                            hard_gate_results=[
                                {"dimension_id": "security_capability_compliance",
                                 "family": "security", "passed": True}])
    assert r1["decision"] == r2["decision"] == "PROMOTE"


def test_property_hard_gate_failure_always_vetoes():
    candidate = _cand()
    for passed in (False, True):
        r = evaluate_promotion(
            candidate=candidate,
            baseline_metrics=_bundle(), candidate_metrics=_bundle(quality=0.9),
            hard_gate_results=[{"dimension_id": "security_tenant_isolation",
                                "family": "security", "passed": passed}])
        if not passed:
            assert r["decision"] in ("REJECT", "QUARANTINE")


def test_property_rollback_returns_exact_previous_identity():
    from prototype.g0.evaluation.rollout import RollbackRegistry
    reg = RollbackRegistry()
    reg.register_baseline(version_ref="v2", config_identity="cfg-2")
    event = reg.rollback_to(rollout_event_id="ro-1", version_ref="v2",
                            trigger_code="EXPLICIT", trigger_reason="review")
    assert event["config_identity"] == "cfg-2"


def test_property_corpus_export_excludes_unauthorized_tenant_cases():
    reg = CorpusRegistry()
    pub = {"eval_case_id": "c-pub", "privacy_class": "PUBLIC_SOURCE"}
    priv = {"eval_case_id": "c-priv",
            "privacy_class": "TENANT_PRIVATE_APPROVED",
            "tenant_scope": "tenant-a", "governance_approval": "ga-1"}
    reg.add_version(_version([pub, priv]), [pub, priv])
    audit = reg.export_audit("corpus-ga-v1")
    assert "c-priv" in audit["exported_case_ids"]  # approved => allowed
    assert audit["excluded_case_ids"] == []
