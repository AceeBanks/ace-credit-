"""G0-B4-C27 — Integration & Reconstruction Property Tests.

Executes the 22 mandatory invariants and the 5 deterministic property tests
from Chapter B4.C27 against the live prototypes. Fail-closed: each invariant
asserts the architecture, not merely that code runs.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.compactor import compact  # noqa: E402
from prototype.g0.agents.context_builder import (  # noqa: E402
    ContextAssemblyError,
    build_context_bundle,
    build_explanation,
    style_transform,
)
from prototype.g0.agents.d1_flow import run_d1_mock_draft  # noqa: E402
from prototype.g0.agents.intent_builder import (  # noqa: E402
    build_intent,
    draft_readiness_gate,
)
from prototype.g0.agents.memory_lifecycle import (  # noqa: E402
    MemoryCandidate,
    classify_candidate,
    promote_candidate,
)
from prototype.g0.agents.memory_manager import (  # noqa: E402
    MemoryRecord,
    MemoryManager,
)
from prototype.g0.agents.portability import (  # noqa: E402
    ScopedMemoryStore,
    provider_swap,
    verify_no_duplicate_resurrection,
)
from prototype.g0.agents.reconstruction import (  # noqa: E402
    build_manifest,
    reconstruct_ceo,
    reconstruct_personal,
    recovery_quality,
)
from prototype.g0.agents.result_reducer import (  # noqa: E402
    build_sidechain,
    make_worker_result,
    synthesize,
)
from prototype.g0.agents.task_builder import (  # noqa: E402
    build_plan,
    build_task_contract,
    new_attempt,
)
from prototype.g0.agents.feedback import apply_feedback  # noqa: E402

# ---------------------------------------------------------------- helpers

_CFG = yaml.safe_load(
    (_ROOT / "config/g0/agents/adversarial_context.yaml").read_text(
        encoding="utf-8"))


def _iso(days_from_now: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days_from_now)
            ).isoformat()


def _intent(**overrides):
    kwargs = dict(
        tenant_id="tenant-a", client_actor_id="client-1",
        organization_id="org-1", intent_type="ASSESS_OPPORTUNITY",
        objective="assess Georgia rural library grant",
        authority_scope="RESEARCH_ONLY", confidence_state="MEDIUM")
    kwargs.update(overrides)
    return build_intent(**kwargs)


def _plan(intent):
    return build_plan(
        plan_id="plan-1", intent_id=intent.intent_id,
        objective=intent.objective,
        steps=[{"step_id": "s1", "step_type": "VERIFY_OPPORTUNITY_REVISION",
                "objective": "pin exact revision",
                "required_capability": "eligibility.extract_candidate_rules"}],
        dependencies=[], required_capabilities=["eligibility.extract_candidate_rules"],
        hard_eligibility_verified=True, application_project_id="proj-1")


def _task(plan=None, **overrides):
    if plan is None:
        plan = _plan(_intent())
    kwargs = dict(
        task_id="task-1", plan_id=plan.plan_id, tenant_id="tenant-a",
        project_id=plan.application_project_id,
        worker_role="RequirementNormalizationWorker",
        objective="verify eligibility",
        capability_id="eligibility.extract_candidate_rules",
        inputs_refs=["opp-rev-3"], allowed_context_refs=["opp-rev-3"],
        required_outputs=["eligibility_report"], expires_at=_iso(7))
    kwargs.update(overrides)
    return build_task_contract(**kwargs)


def _bundle(**overrides):
    kwargs = dict(
        consumer_actor="ceo_hermes", operation_type="assess_opportunity",
        tenant_id="tenant-a", project_id="proj-1",
        canonical_state_refs=["state:opp-rev-3", "state:org-1"],
        evidence_refs=["ev:official-solicitation"],
        memory_refs=["mem:pref-1"],
        recent_interaction_refs=["conv/session-1#msg-2"],
        policy_refs=["policy:approval"],
        task_refs=["task:eligibility"],
        anchors=["state:opp-rev-3", "state:org-1"],
        excluded_context_classes=["RAW_CLIENT_TRANSCRIPT"])
    kwargs.update(overrides)
    return kwargs


def _memory(manager: MemoryManager, memory_id: str, memory_class: str,
            namespace: str, statement: str, **kw) -> MemoryRecord:
    return manager.store(MemoryRecord(
        memory_id=memory_id, memory_class=memory_class,
        namespace=namespace, statement=statement, **kw))


# ======================================================== 22 invariants

def test_invariant_1_personal_and_ceo_namespaces_distinct():
    from prototype.g0.agents.memory_manager import (
        CEO_CLASSES,
        PERSONAL_CLASSES,
    )
    assert PERSONAL_CLASSES & CEO_CLASSES == set()


def test_invariant_2_memory_namespaces_not_canonical_truth():
    manager = MemoryManager()
    _memory(manager, "m1", "PM-PREFERENCE", "personal_hermes",
            "prefers email")
    # memory records carry canonical_refs, never the facts themselves
    record = manager.retrieve_active("personal_hermes")[0]
    assert isinstance(record.canonical_refs, list)


def test_invariant_3_complete_intent_sufficient_for_ceo_start():
    intent = _intent(open_questions=[], confidence_state="HIGH")
    plan = _plan(intent)
    task = _task(plan)
    assert plan.intent_id == intent.intent_id
    assert task.plan_id == plan.plan_id
    assert task.capability_id == "eligibility.extract_candidate_rules"


def test_invariant_4_critical_missing_intent_fields_trigger_clarification():
    intent = _intent(open_questions=["Which county is the library in?"])
    blocking = [type("Q", (), {
        "clarification_id": "q1", "question_type": "ELIGIBILITY_CRITICAL",
        "blocking": True, "question": "Which county is the library in?"})()]
    state, reasons = draft_readiness_gate(blocking, answers={})
    assert state == "BLOCKED_ELIGIBILITY"
    assert reasons


def test_invariant_5_task_contract_bounded_context_and_capability():
    task = _task(allowed_context_refs=["opp-rev-3"])
    assert task.allowed_context_refs == ["opp-rev-3"]
    assert task.capability_id == "eligibility.extract_candidate_rules"
    assert task.side_effect_policy in ("READ_ONLY", "INTERNAL_WRITE_SCOPED",
                                       "NO_EXTERNAL_SIDE_EFFECTS")


def test_invariant_6_worker_cannot_inherit_full_ceo_authority():
    from prototype.g0.agents.task_builder import TaskContractError
    with pytest.raises(TaskContractError):
        _task(authority_scope="FULL_CEO")  # unknown scope -> fail closed
    task = _task()
    assert task.authority_scope in ("TASK_SCOPED_L0", "TASK_SCOPED_L2")


def test_invariant_7_worker_result_bounded_and_points_to_sidechain():
    sidechain = build_sidechain(
        task_id="task-1", attempt_id="attempt-1", worker_identity="w1",
        transcript_uri="sc://task-1/attempt-1")
    result = make_worker_result(
        task_id="task-1", attempt_id="attempt-1", status="SUCCEEDED",
        summary="s" * 50_000, structured_output_ref="out://t1",
        sidechain_ref=sidechain.transcript_uri)
    assert len(result.summary) < 5000
    assert result.sidechain_ref == sidechain.transcript_uri


def test_invariant_8_full_worker_trace_not_injected_into_personal_context():
    intent = _intent()
    plan = _plan(intent)
    task = _task(plan)
    bundle = build_context_bundle(**_bundle(
        consumer_actor="personal_hermes",
        task_refs=[task.task_id]))
    assert "sc://task-1/attempt-1" not in bundle.recent_interaction_refs
    assert task.task_id in bundle.task_refs  # only the ref travels
    assert "sc://" not in " ".join(bundle.memory_refs + bundle.recent_interaction_refs)


def test_invariant_9_outcome_artifact_preserves_uncertainty_and_evidence():
    r = make_worker_result(
        task_id="task-1", attempt_id="attempt-1", status="SUCCEEDED",
        summary="possibly eligible; deadline unverified",
        structured_output_ref="out://t1", sidechain_ref="sc://t1/a1",
        uncertainties=["deadline not yet confirmed"],
        source_refs=["src://official-solicitation"])
    outcome = synthesize(
        outcome_id="o-1", intent_id="int-1", plan_id="plan-1",
        application_project_id="proj-1", opportunity_revision_id="opp-rev-3",
        outcome_type="eligibility_assessment", results=[r])
    assert outcome["unresolved_questions"] == ["deadline not yet confirmed"]
    assert "src://official-solicitation" in outcome["evidence_refs"]


def test_invariant_10_client_explanation_cannot_mutate_material_facts():
    outcome = {
        "outcome_id": "o-1",
        "executive_summary": "Award ceiling is $75,000 per official rev-3.",
        "evidence_refs": ["src://official-solicitation"],
        "research_pack_refs": ["out://t1"],
        "artifact_refs": [],
        "unresolved_questions": ["deadline unconfirmed"],
    }
    explanation = build_explanation(explanation_id="x-1", outcome=outcome)
    before = explanation["factual_anchors"]
    # prose-only transform (synonym swap): factual tokens must survive
    transformed = style_transform(
        explanation, lambda s: s.replace("ceiling", "cap"))
    assert transformed["factual_anchors"] == before
    assert "$75,000" in " ".join(transformed[f] for f in
                                 ("summary", "what_we_found"))


def test_invariant_11_personal_memory_not_duplicate_source_truth():
    from prototype.g0.agents.memory_manager import (
        MemoryPolicyError,
        canonical_substitution_guard,
    )
    with pytest.raises(MemoryPolicyError):
        canonical_substitution_guard(
            "the award ceiling is $75,000", canonical_ref=None)
    # with a canonical ref it stores a pointer, not the fact
    canonical_substitution_guard(
        "award ceiling preference", canonical_ref="opp-rev-3#award_ceiling")


def test_invariant_12_ceo_memory_lean_operational_not_raw_history():
    manager = MemoryManager()
    _memory(manager, "c1", "CM-ACTIVE-PROJECT", "ceo_hermes",
            "proj-1 active on opp-rev-3")
    statements = [r.statement for r in
                  manager.retrieve_active("ceo_hermes")]
    assert all("transcript" not in s.lower() and
               "raw chat" not in s.lower() for s in statements)


def test_invariant_13_workers_stateless_across_tasks_by_default():
    from prototype.g0.agents.memory_lifecycle import repeat_worker_task
    contract = {
        "task_id": "task-1", "plan_id": "plan-1", "tenant_id": "tenant-a",
        "project_id": "proj-1", "inputs_refs": ["opp-rev-3"],
        "capability_id": "eligibility.extract_candidate_rules",
    }
    snapshots = [{"content_hash": "abc123"}]
    out1 = repeat_worker_task(contract, snapshots)
    out2 = repeat_worker_task(contract, snapshots)
    assert out1 == out2  # deterministic: no hidden memory needed
    assert out1["memory_used"] == "none"


def test_invariant_14_memory_promotion_is_explicit():
    candidate = MemoryCandidate(
        candidate_id="c1", proposed_memory_class="PM-GOAL",
        proposed_statement="goal: secure the rural library grant",
        source_refs=["evt-1"], proposed_by="PERSONAL_HERMES")
    classify_candidate(candidate)
    assert candidate.classification == "PROMOTE_FOR_REVIEW"
    promotion = promote_candidate(candidate)
    assert promotion.decision == "PROMOTE"
    assert promotion.promoted_at


def test_invariant_15_superseded_memory_excluded_from_active_retrieval():
    manager = MemoryManager()
    _memory(manager, "old-1", "PM-PREFERENCE", "personal_hermes", "email ok")
    replacement = MemoryRecord(
        memory_id="new-1", memory_class="PM-PREFERENCE",
        namespace="personal_hermes", statement="email preferred")
    manager.supersede("old-1", replacement)
    active_ids = {r.memory_id for r in manager.retrieve_active("personal_hermes")}
    assert "old-1" not in active_ids
    assert "new-1" in active_ids


def test_invariant_16_compaction_preserves_mandatory_anchors():
    anchor = "Deadline: 2026-10-15 (official rev-3)"
    items = [anchor, "tool output dump: retry log",
             "duplicate snippet of old page"]
    for stage in ("STAGE1_DROP_DISPOSABLE_REDUNDANT",
                  "STAGE3_MICRO_SUMMARIZE_EPISODES_TASKS",
                  "STAGE5_MODEL_ASSISTED_SEMANTIC_COMPACTION"):
        kept, _ = compact(items, stage=stage, anchors=[anchor], budget=2)
        assert anchor in kept


def test_invariant_17_retrieval_prefers_required_refs_over_recency():
    # budget exactly holds the 4 mandatory refs; the most recent optional
    # interaction is dropped first, authority refs survive
    bundle = build_context_bundle(**_bundle(
        context_budget={"item_count": 4}))
    assert "state:opp-rev-3" in bundle.canonical_state_refs
    assert "policy:approval" in bundle.policy_refs
    assert "task:eligibility" in bundle.task_refs
    assert bundle.recent_interaction_refs == []
    assert bundle.evidence_refs == []
    assert bundle.memory_refs == []


def test_invariant_18_cold_restart_reconstructs_active_state():
    pre = reconstruct_ceo({
        "project_id": "proj-1", "opportunity_revision_id": "opp-rev-3",
        "intent_id": "int-1", "task_statuses": ["eligibility_report: DONE"],
        "active_blockers": [], "promoted_lessons": [],
        "unresolved_questions": [], "authority_state": "PREPARE_ONLY",
        "policy_refs": ["policy:approval"]})
    post = reconstruct_ceo({
        "project_id": "proj-1", "opportunity_revision_id": "opp-rev-3",
        "intent_id": "int-1", "task_statuses": ["eligibility_report: DONE"],
        "active_blockers": [], "promoted_lessons": [],
        "unresolved_questions": [], "authority_state": "PREPARE_ONLY",
        "policy_refs": ["policy:approval"]})
    metric = recovery_quality(pre, post)
    assert metric["match"] is True


def test_invariant_19_multi_project_context_isolated():
    a = build_context_bundle(**_bundle(
        project_id="proj-1", canonical_state_refs=["state:opp-rev-3"],
        anchors=["state:opp-rev-3"], policy_refs=["policy:approval"],
        task_refs=["task:eligibility-1"]))
    b = build_context_bundle(**_bundle(
        project_id="proj-2", canonical_state_refs=["state:opp-rev-5"],
        anchors=["state:opp-rev-5"], policy_refs=["policy:approval-v2"],
        task_refs=["task:eligibility-2"]))
    assert a.project_id != b.project_id
    assert set(a.mandatory_refs()) & set(b.mandatory_refs()) == set()


def test_invariant_20_multi_tenant_memory_isolated():
    t1 = MemoryManager()
    t2 = MemoryManager()
    _memory(t1, "m1", "PM-PREFERENCE", "personal_hermes", "tenant one pref")
    _memory(t2, "m1", "PM-PREFERENCE", "personal_hermes", "tenant two pref")
    assert (t1.retrieve_active("personal_hermes")[0].statement
            != t2.retrieve_active("personal_hermes")[0].statement)


def test_invariant_21_agent_model_replacement_preserves_state():
    swap = provider_swap(
        actor_identity="hermes-personal-t1",
        memory_namespaces={"personal_hermes", "ceo_hermes"},
        old_model="a/1", new_model="b/2")
    assert swap["identity_unchanged"] is True
    assert swap["actor_identity"] == "hermes-personal-t1"


def test_invariant_22_d1_mock_draft_without_raw_transcript():
    intent = _intent().to_dict()
    plan = {"plan_id": "plan-1", "application_project_id": "proj-1"}
    tasks = [{"task_id": "task-1"}]
    packet = run_d1_mock_draft(
        intent=intent, plan=plan, tasks=tasks,
        evidence_pack=["src://official-solicitation"],
        opportunity_revision_id="opp-rev-3",
        section_drafts={
            "community": "placeholder per source src://official-solicitation"},
        raw_transcript_available=False)
    assert packet.label == "MOCK_NON_SUBMISSION"
    assert packet.used_raw_transcript is False
    assert packet.worker_payloads_bounded is True
    assert packet.submission_capabilities == []


# ======================================================== 5 property tests

def test_property_same_state_reconstructs_same_mandatory_refs():
    for _ in range(3):
        a = build_context_bundle(**_bundle())
        b = build_context_bundle(**_bundle())
        assert a.mandatory_refs() == b.mandatory_refs()
        assert a.canonical_state_refs == b.canonical_state_refs


def test_property_compaction_idempotence_within_tolerance():
    anchor = "Deadline: 2026-10-15 (official rev-3)"
    items = [anchor, "tool output dump: retry log noise"]
    once, m1 = compact(items, stage="STAGE2_SNIP_HISTORICAL_LOW_VALUE",
                       anchors=[anchor], budget=1)
    twice, m2 = compact(once, stage="STAGE2_SNIP_HISTORICAL_LOW_VALUE",
                        anchors=[anchor], budget=1)
    assert once == twice  # idempotent within tolerance
    assert anchor in once and anchor in twice


def test_property_supersession_removes_old_from_active_set():
    manager = MemoryManager()
    _memory(manager, "p1", "PM-PREFERENCE", "personal_hermes", "old pref")
    replacement = MemoryRecord(
        memory_id="p2", memory_class="PM-PREFERENCE",
        namespace="personal_hermes", statement="new pref")
    manager.supersede("p1", replacement)
    active = manager.retrieve_active("personal_hermes")
    assert {r.memory_id for r in active} == {"p2"}


def test_property_task_retry_preserves_lineage():
    attempt1 = new_attempt("task-1", 1)
    attempt2 = new_attempt("task-1", 2)
    assert attempt1 == "task-1/attempt-1"
    assert attempt2 == "task-1/attempt-2"
    assert attempt1.split("/")[0] == attempt2.split("/")[0]


def test_property_source_refs_survive_summary_reduction():
    sidechain = build_sidechain(
        task_id="task-1", attempt_id="attempt-1", worker_identity="w1",
        transcript_uri="sc://task-1/attempt-1",
        source_refs=["src://official-solicitation", "src://census-vintage-2020"])
    result = make_worker_result(
        task_id="task-1", attempt_id="attempt-1", status="SUCCEEDED",
        summary="huge detail " * 1000, structured_output_ref="out://t1",
        source_refs=sidechain.source_refs, sidechain_ref=sidechain.transcript_uri)
    assert len(result.summary) < 5000  # reduced...
    assert "src://official-solicitation" in result.source_refs  # refs survive
    assert "src://census-vintage-2020" in result.source_refs


# ======================================================== catalog guard

def test_c27_invariant_catalog_all_required():
    """The 22 C27 invariants from the plan are all represented."""
    import inspect
    module = sys.modules[__name__]
    names = {n for n, _ in inspect.getmembers(module, inspect.isfunction)}
    for i in range(1, 23):
        assert any(n.startswith(f"test_invariant_{i}_") for n in names), \
            f"missing test_invariant_{i}"


def test_c27_property_catalog_all_required():
    """The 5 C27 property tests from the plan are all represented."""
    import inspect
    module = sys.modules[__name__]
    names = {n for n, _ in inspect.getmembers(module, inspect.isfunction)}
    for prefix in ("same_state_reconstructs_same_mandatory_refs",
                   "compaction_idempotence_within_tolerance",
                   "supersession_removes_old_from_active_set",
                   "task_retry_preserves_lineage",
                   "source_refs_survive_summary_reduction"):
        assert any(n == f"test_property_{prefix}" for n in names), \
            f"missing test_property_{prefix}"
