"""G1 Wave 3 — production Dual Hermes tests.

Flow under test:
client message → Personal intent → CEO task plan → persistent tasks →
worker (claim, bounded ContextBundle, WorkerResult) → synthesis →
cold reconstruction (no raw-chat dependency).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from grant_platform.agents.ceo import CeoHermes, CeoExecution  # noqa: E402
from grant_platform.agents.personal import (  # noqa: E402
    PersonalHermes,
    SUBMISSION_CAPABILITIES,
)
from grant_platform.agents.reconstruction import reconstruct  # noqa: E402
from grant_platform.agents.workers import (  # noqa: E402
    ContextBundle,
    WorkerResult,
    WorkerRuntime,
)
from grant_platform.domain.records import (  # noqa: E402
    ApplicationProject,
    Opportunity,
    OpportunityRevision,
    Organization,
    Tenant,
)
from grant_platform.runtime.tasks import TaskRunner  # noqa: E402
from grant_platform.store.db import Store  # noqa: E402


def _seed(store: Store, tenant: str = "tenant-a",
           org: str = "org-a", project: str = "proj-1") -> dict:
    store.create_tenant(Tenant(tenant_id=tenant, display_name="T"))
    store.create_organization(Organization(
        organization_id=org, tenant_id=tenant,
        legal_name="Community Youth Works, Inc."))
    store.create_opportunity(Opportunity(
        opportunity_id="opp_ga_501", tenant_id=tenant,
        title="Georgia Rural Community Impact Grant FY2026",
        deadline="2026-10-15"))
    store.create_revision(OpportunityRevision(
        revision_id="opp_rev_ga_501_1", opportunity_id="opp_ga_501",
        revision_number=1))
    store.create_project(ApplicationProject(
        project_id=project, tenant_id=tenant, organization_id=org,
        opportunity_id="opp_ga_501", revision_id="opp_rev_ga_501_1"))
    return {"tenant": tenant, "org": org, "project": project}


def _conversation(store: Store, conv: str, tenant: str, client: str):
    store.create_conversation({
        "conversation_id": conv, "tenant_id": tenant,
        "client_actor_id": client, "title": "t"})


def test_client_message_to_persistent_intent():
    store = Store.open(":memory:")
    _seed(store)
    _conversation(store, "conv-1", "tenant-a", "client-1")
    ph = PersonalHermes(store)
    reply = ph.receive_message(
        conversation_id="conv-1", tenant_id="tenant-a",
        client_actor_id="client-1", organization_id="org-a",
        content="We need funding for an after-school STEM program in Atlanta.")
    assert reply.intent is not None
    assert reply.intent.intent_type == "BUILD_APPLICATION"
    assert reply.intent.authority_scope == "PREPARE_ONLY"
    # intent is durable
    row = store.get_intent(reply.intent.intent_id)
    assert row is not None
    assert row["tenant_id"] == "tenant-a"
    # both messages persisted
    assert len(store.messages_for("conv-1")) == 2
    store.close()


def test_submission_capability_normalized_fail_closed():
    store = Store.open(":memory:")
    _seed(store)
    _conversation(store, "conv-2", "tenant-a", "client-1")
    ph = PersonalHermes(store)
    reply = ph.receive_message(
        conversation_id="conv-2", tenant_id="tenant-a",
        client_actor_id="client-1", organization_id="org-a",
        content="Draft our proposal.",
        requested_capabilities=["submission.execute", "research.funder"])
    caps = reply.intent.requested_capabilities
    assert "submission.execute" not in caps
    assert "application.prepare_submission_package" in caps
    assert any("normalized" in n for n in reply.intent.normalization_notes)
    # Personal normalized it away, so CEO plans fine with prepare-only
    ceo = CeoHermes(store)
    exec_ = ceo.plan(reply.intent, project_id="proj-1")
    assert not any("submission" in t for t in exec_.task_ids)
    # CEO fails closed if a submission capability bypasses Personal
    from grant_platform.agents.personal import IntentContract
    poisoned = IntentContract(
        intent_id="int-poisoned", tenant_id="tenant-a",
        client_actor_id="client-1", organization_id="org-a",
        intent_type="BUILD_APPLICATION",
        objective="draft proposal", authority_scope="PREPARE_ONLY",
        confidence_state="MEDIUM", created_at="now",
        requested_capabilities=("submission.execute",))
    with pytest.raises(ValueError):
        ceo.plan(poisoned, project_id="proj-1")
    store.close()


def test_ceo_durable_task_plan_and_execution():
    store = Store.open(":memory:")
    _seed(store)
    _conversation(store, "conv-3", "tenant-a", "client-1")
    ph = PersonalHermes(store)
    reply = ph.receive_message(
        conversation_id="conv-3", tenant_id="tenant-a",
        client_actor_id="client-1", organization_id="org-a",
        content="Build our application for the Georgia grant.")
    intent = reply.intent
    ceo = CeoHermes(store)
    exec_: CeoExecution = ceo.plan(intent, project_id="proj-1")
    assert exec_.plan.plan_id == f"plan-{intent.intent_id}"
    assert len(exec_.task_ids) >= 8
    # plan persisted
    assert store.get_plan(exec_.plan.plan_id) is not None
    # all tasks durable and READY
    for tid in exec_.task_ids:
        row = store.get_task(tid, "tenant-a")
        assert row is not None and row["state"] == "READY"
    # worker executes the eligibility step with a bounded bundle
    runner = TaskRunner(store)
    runtime = WorkerRuntime(store, runner, worker_principal="WORKER-1")
    runtime.register("eligibility.extract_candidate_rules",
                     lambda b: WorkerResult(
                         result_id=f"r-{b.task_id}", task_id=b.task_id,
                         tenant_id="tenant-a",
                         worker_principal="WORKER-1",
                         capability_id="eligibility.extract_candidate_rules",
                         summary="ELIGIBLE",
                         claims=[{"claim": "organization is eligible",
                                  "support": "rule:501.1"}],
                         context_refs=b.evidence_refs))
    out = runtime.run(exec_.task_ids[1], "tenant-a", intent,
                      "opp_rev_ga_501_1", project_id="proj-1")
    assert out["state"] == "SUCCEEDED"
    result = store.get_worker_result(exec_.task_ids[1])
    assert result["summary"] == "ELIGIBLE"
    assert store.get_task(exec_.task_ids[1], "tenant-a")["state"] == \
        "SUCCEEDED"
    # synthesis reads durable results only
    syn = ceo.synthesize("proj-1")
    assert syn["completed_tasks"] == 1
    store.close()


def test_worker_bundle_never_contains_raw_transcript():
    store = Store.open(":memory:")
    _seed(store)
    _conversation(store, "conv-4", "tenant-a", "client-1")
    ph = PersonalHermes(store)
    reply = ph.receive_message(
        conversation_id="conv-4", tenant_id="tenant-a",
        client_actor_id="client-1", organization_id="org-a",
        content="Draft a proposal for youth STEM in rural Georgia.")
    intent = reply.intent
    runner = TaskRunner(store)
    runtime = WorkerRuntime(store, runner)
    bundle: ContextBundle = runtime.build_bundle(
        intent, "task-x", "opp_rev_ga_501_1")
    refs = " ".join(bundle.evidence_refs)
    assert "conv:" not in refs
    assert "chat" not in refs
    assert "ctx:intent-" in refs and "ctx:rev-" in refs
    store.close()


def test_cold_reconstruction_no_raw_chat_required():
    store = Store.open(":memory:")
    _seed(store)
    _conversation(store, "conv-5", "tenant-a", "client-1")
    ph = PersonalHermes(store)
    reply = ph.receive_message(
        conversation_id="conv-5", tenant_id="tenant-a",
        client_actor_id="client-1", organization_id="org-a",
        content="Research and draft our Georgia application.")
    intent = reply.intent
    ceo = CeoHermes(store)
    exec_ = ceo.plan(intent, project_id="proj-1")
    # simulate a process death: run a worker in a NEW runtime instance
    runner = TaskRunner(store)
    runtime = WorkerRuntime(store, runner, worker_principal="WORKER-2")
    runtime.register("research.community",
                     lambda b: WorkerResult(
                         result_id=f"r-{b.task_id}", task_id=b.task_id,
                         tenant_id="tenant-a",
                         worker_principal="WORKER-2",
                         capability_id="research.community",
                         summary="Dade County poverty 18.2%",
                         claims=[{"claim": "poverty 18.2%",
                                  "support": "census_2023"}],
                         context_refs=b.evidence_refs))
    # pick the research.community task by capability, not index
    research_task = next(t["task_id"] for t in store.tasks_for("tenant-a")
                         if t["capability_id"] == "research.community")
    runtime.run(research_task, "tenant-a", intent,
                "opp_rev_ga_501_1", project_id="proj-1")
    # cold reconstruct from durable state only
    report = reconstruct(store, tenant_id="tenant-a", project_id="proj-1")
    assert report.raw_chat_required is False
    assert report.organization["legal_name"] == "Community Youth Works, Inc."
    assert report.intent["intent_id"] == intent.intent_id
    assert report.revision["revision_id"] == "opp_rev_ga_501_1"
    assert report.plan is not None
    assert len(report.tasks) == len(exec_.task_ids)
    assert len(report.worker_results) == 1
    assert report.completeness["intent"] is True
    store.close()


def test_cross_tenant_isolation():
    store = Store.open(":memory:")
    _seed(store, tenant="tenant-a")
    _seed(store, tenant="tenant-b", org="org-b", project="proj-b")
    _conversation(store, "conv-b", "tenant-b", "client-b")
    ph = PersonalHermes(store)
    reply = ph.receive_message(
        conversation_id="conv-b", tenant_id="tenant-b",
        client_actor_id="client-b", organization_id="org-b",
        content="Draft a proposal.")
    assert reply.intent.tenant_id == "tenant-b"
    # tenant-a cannot see tenant-b's intent
    rows = store.intents_for("tenant-a", "org-a")
    assert all(r["intent_id"] != reply.intent.intent_id for r in rows)
    # each tenant sees only its own project
    assert store.get_project("proj-b", "tenant-b") is not None
    assert store.get_project("proj-b", "tenant-a") is None  # cross-tenant denied
    assert store.get_project("proj-1", "tenant-a") is not None  # own project
    store.close()


def test_concurrent_claim_one_winner():
    store = Store.open(":memory:")
    _seed(store)
    _conversation(store, "conv-6", "tenant-a", "client-1")
    ph = PersonalHermes(store)
    reply = ph.receive_message(
        conversation_id="conv-6", tenant_id="tenant-a",
        client_actor_id="client-1", organization_id="org-a",
        content="Draft a proposal.")
    ceo = CeoHermes(store)
    exec_ = ceo.plan(reply.intent, project_id="proj-1")
    tid = exec_.task_ids[0]
    runner = TaskRunner(store)
    assert runner.claim(tid, "tenant-a", "W1") is True
    assert runner.claim(tid, "tenant-a", "W2") is False
    store.close()
