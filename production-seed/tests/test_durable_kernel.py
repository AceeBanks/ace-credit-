"""G1 Wave 1 — durable platform kernel tests.

Lifecycle: empty-DB migration -> tenant -> organization -> opportunity/
revision -> application project -> task -> worker claim -> checkpoint ->
simulated process death -> resume -> finish -> reconstruct.

Plus: concurrent task claims, cross-tenant isolation, retry, object store.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from grant_platform.domain.records import (  # noqa: E402
    ApplicationProject,
    AuditEvent,
    Capability,
    Grant,
    Opportunity,
    OpportunityRevision,
    Organization,
    Principal,
    Task,
    Tenant,
)
from grant_platform.runtime.tasks import TaskRunner  # noqa: E402
from grant_platform.store.db import Store  # noqa: E402
from grant_platform.store.objects import LocalObjectStore  # noqa: E402


def _seed(store: Store, tenant: str = "tenant-a"):
    store.create_tenant(Tenant(tenant_id=tenant, display_name="T"))
    store.create_principal(Principal(principal_id="p-ceo",
                                     tenant_id=tenant,
                                     principal_type="HERMES_CEO",
                                     authority_level=4))
    store.create_capability(Capability(capability_id="application.draft_internal",
                                       required_level=3))
    store.create_grant(Grant(grant_id="g1", principal_id="p-ceo",
                             capability_id="application.draft_internal",
                             authority_level=4, tenant_id=tenant))
    store.create_organization(Organization(organization_id="org-1",
                                           tenant_id=tenant,
                                           legal_name="Community Youth Works",
                                           jurisdiction="Georgia"))
    store.create_opportunity(Opportunity(opportunity_id="opp-1",
                                         tenant_id=tenant,
                                         title="GA Rural Impact",
                                         funding_ceiling=Decimal("50000"),
                                         deadline="2026-10-15"))
    store.create_revision(OpportunityRevision(revision_id="rev-1",
                                              opportunity_id="opp-1",
                                              revision_number=1))
    store.create_project(ApplicationProject(project_id="proj-1",
                                            tenant_id=tenant,
                                            organization_id="org-1",
                                            opportunity_id="opp-1",
                                            revision_id="rev-1"))


# ---------------------------------------------------------------------------
# persistence lifecycle
# ---------------------------------------------------------------------------

def test_empty_db_migration_and_lifecycle():
    store = Store.open(":memory:")
    _seed(store)
    org = store.get_organization("org-1", "tenant-a")
    assert org["legal_name"] == "Community Youth Works"
    proj = store.get_project("proj-1", "tenant-a")
    assert proj["revision_id"] == "rev-1"
    assert proj["state"] == "DRAFTING"
    store.close()


def test_revision_append_only_chain():
    store = Store.open(":memory:")
    _seed(store)
    store.create_revision(OpportunityRevision(revision_id="rev-2",
                                              opportunity_id="opp-1",
                                              revision_number=2,
                                              changed_terms=("deadline",),
                                              material=True))
    revs = store.revisions_for("opp-1")
    assert [r["revision_number"] for r in revs] == [1, 2]
    assert revs[1]["material"] == 1
    store.close()


def test_cross_tenant_isolation():
    store = Store.open(":memory:")
    _seed(store, "tenant-a")
    # tenant-b seeds its OWN org/project (distinct ids)
    store.create_tenant(Tenant(tenant_id="tenant-b", display_name="B"))
    store.create_principal(Principal(principal_id="p-b",
                                     tenant_id="tenant-b",
                                     principal_type="HERMES_CEO",
                                     authority_level=4))
    store.create_organization(Organization(organization_id="org-b",
                                           tenant_id="tenant-b",
                                           legal_name="Org B"))
    store.create_opportunity(Opportunity(opportunity_id="opp-x",
                                         tenant_id="tenant-b",
                                         title="Opp B"))
    store.create_revision(OpportunityRevision(revision_id="rev-x",
                                              opportunity_id="opp-x",
                                              revision_number=1))
    store.create_project(ApplicationProject(project_id="proj-b",
                                            tenant_id="tenant-b",
                                            organization_id="org-b",
                                            opportunity_id="opp-x",
                                            revision_id="rev-x"))
    # tenant-b cannot read tenant-a org or project (scoped queries)
    assert store.get_organization("org-1", "tenant-b") is None
    assert store.get_project("proj-1", "tenant-b") is None
    # tenant-a still can
    assert store.get_organization("org-1", "tenant-a") is not None
    assert store.get_project("proj-1", "tenant-a") is not None
    # tenant-a cannot read tenant-b's
    assert store.get_organization("org-b", "tenant-a") is None
    store.close()


def test_decision_and_audit_persist():
    store = Store.open(":memory:")
    _seed(store)
    store.create_decision(
        __import__("grant_platform.domain.records",
                   fromlist=["DecisionRecord"]).DecisionRecord(
            decision_id="dec-1", decision_type="ELIGIBILITY",
            tenant_id="tenant-a", project_id="proj-1", actor_ref="p-ceo",
            capability_id="eligibility.execute_deterministic",
            result={"result": "ELIGIBLE"}, created_at="2026-01-01T00:00:00Z"))
    store.create_audit(AuditEvent(audit_id="aud-1", tenant_id="tenant-a",
                                  project_id="proj-1", actor_ref="p-ceo",
                                  event_type="decision_recorded",
                                  decision_ref="dec-1",
                                  created_at="2026-01-01T00:00:00Z"))
    dec = store.get_decision("dec-1")
    assert dec["result"].startswith('{"result": "ELIGIBLE"}') or "ELIGIBLE" in dec["result"]
    assert len(store.audit_for("tenant-a")) == 1
    store.close()


# ---------------------------------------------------------------------------
# durable task lifecycle
# ---------------------------------------------------------------------------

def test_task_claim_run_complete_reconstruct():
    store = Store.open(":memory:")
    _seed(store)
    runner = TaskRunner(store)
    runner.enqueue(Task(task_id="t1", tenant_id="tenant-a",
                        task_type="research", project_id="proj-1",
                        capability_id="research.execute"))
    assert runner.claim("t1", "tenant-a", "worker-1") is True
    outcome = runner.run("t1", "tenant-a", "worker-1",
                         lambda h: h.update({"result_ref": "ref:r1"}))
    assert outcome.state == "SUCCEEDED"
    assert outcome.result_ref == "ref:r1"
    # reconstruct project + task from durable state
    task = store.get_task("t1", "tenant-a")
    assert task["state"] == "SUCCEEDED"
    proj = store.get_project("proj-1", "tenant-a")
    assert proj is not None
    store.close()


def test_process_death_then_resume():
    """Simulate a crash mid-run: task stays RUNNING; lease expires -> STALE
    -> recoverable; a new worker re-runs it."""
    store = Store.open(":memory:")
    _seed(store)
    runner = TaskRunner(store)
    runner.enqueue(Task(task_id="t1", tenant_id="tenant-a",
                        task_type="research", project_id="proj-1"))
    assert runner.claim("t1", "tenant-a", "worker-1") is True
    # worker dies: no completion. mark stale with immediate expiry
    store.conn.execute(
        "UPDATE tasks SET created_at = datetime('now', '-1 hour')"
        " WHERE task_id='t1'")
    store.conn.commit()
    recovered = runner.recover_stale(stale_after_seconds=60)
    assert recovered == 1
    task = store.get_task("t1", "tenant-a")
    assert task["state"] == "READY"
    # new worker claims and finishes
    assert runner.claim("t1", "tenant-a", "worker-2") is True
    outcome = runner.run("t1", "tenant-a", "worker-2",
                         lambda h: h.update({"result_ref": "ref:r2"}))
    assert outcome.state == "SUCCEEDED"
    store.close()


def test_concurrent_claim_only_one_wins():
    store = Store.open(":memory:")
    _seed(store)
    runner = TaskRunner(store)
    runner.enqueue(Task(task_id="t1", tenant_id="tenant-a",
                        task_type="research", project_id="proj-1"))
    assert runner.claim("t1", "tenant-a", "worker-1") is True
    assert runner.claim("t1", "tenant-a", "worker-2") is False
    store.close()


def test_idempotent_completion_no_reexecute():
    store = Store.open(":memory:")
    _seed(store)
    runner = TaskRunner(store)
    runner.enqueue(Task(task_id="t1", tenant_id="tenant-a",
                        task_type="research"))
    assert runner.claim("t1", "tenant-a", "w1") is True
    runner.run("t1", "tenant-a", "w1", lambda h: h.update({"result_ref": "r"}))
    calls = []
    outcome = runner.run("t1", "tenant-a", "w1",
                         lambda h: calls.append(1) or h.update(
                             {"result_ref": "r"}))
    assert outcome.state == "SUCCEEDED"
    assert calls == []          # never re-executed


def test_retry_then_fail():
    store = Store.open(":memory:")
    _seed(store)
    runner = TaskRunner(store, max_retries=1)
    runner.enqueue(Task(task_id="t1", tenant_id="tenant-a",
                        task_type="research"))
    assert runner.claim("t1", "tenant-a", "w1") is True

    def boom(h):
        raise RuntimeError("transient")

    first = runner.run("t1", "tenant-a", "w1", boom)
    assert first.state == "READY"          # retried
    assert first.retry_count == 1
    assert runner.claim("t1", "tenant-a", "w1") is True
    second = runner.run("t1", "tenant-a", "w1", boom)
    assert second.state == "FAILED"        # max retries exhausted
    store.close()


def test_task_scope_enforced_by_store():
    """Tasks are tenant-scoped: a tenant cannot touch another tenant's task."""
    store = Store.open(":memory:")
    _seed(store, "tenant-a")
    _seed(store, "tenant-b")
    runner = TaskRunner(store)
    runner.enqueue(Task(task_id="t1", tenant_id="tenant-a",
                        task_type="research"))
    assert runner.claim("t1", "tenant-b", "w1") is False
    assert store.get_task("t1", "tenant-b") is None
    store.close()


# ---------------------------------------------------------------------------
# object storage
# ---------------------------------------------------------------------------

def test_local_object_store_roundtrip(tmp_path):
    store = LocalObjectStore(tmp_path / "objects")
    h = store.put("artifacts/proj-1/v1.md", b"# draft", "text/markdown")
    assert h == store.put("artifacts/proj-1/v1.md", b"# draft",
                          "text/markdown")  # content-addressed
    data = store.get("artifacts/proj-1/v1.md")
    assert data == b"# draft"
    assert store.get("missing/key") is None


def test_object_store_rejects_traversal(tmp_path):
    store = LocalObjectStore(tmp_path / "objects")
    with pytest.raises(ValueError):
        store.put("../escape.md", b"x")


def test_checkpoint_is_durable():
    store = Store.open(":memory:")
    _seed(store)
    runner = TaskRunner(store)
    runner.enqueue(Task(task_id="t1", tenant_id="tenant-a",
                        task_type="research"))
    runner.claim("t1", "tenant-a", "w1")
    runner.checkpoint("t1", "tenant-a", "drafted section 3 of 7")
    events = store.audit_for("tenant-a")
    assert any(e["event_type"] == "task_checkpoint" for e in events)
    store.close()
