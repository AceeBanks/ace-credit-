"""G1 Wave 1 — scheduler tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from grant_platform.domain.records import Tenant  # noqa: E402
from grant_platform.runtime.scheduler import JobSpec, Scheduler  # noqa: E402
from grant_platform.runtime.tasks import TaskRunner  # noqa: E402
from grant_platform.store.db import Store  # noqa: E402


@pytest.fixture
def scheduler():
    store = Store.open(":memory:")
    store.create_tenant(Tenant(tenant_id="tenant-a", display_name="A"))
    runner = TaskRunner(store)
    sch = Scheduler(store, runner, service_principal="svc-refresh")
    yield sch, store, runner
    store.close()


def test_enqueue_and_dispatch(scheduler):
    sch, store, _ = scheduler
    sch.enqueue(JobSpec(job_type="source_refresh", tenant_id="tenant-a",
                        capability_id="source.fetch"))
    assert sch.pending_count("tenant-a") == 1
    result = sch.dispatch_once(
        "tenant-a", "source_refresh",
        lambda h: h.update({"result_ref": "ref:snap-1"}))
    assert result["dispatched"] is True
    assert result["state"] == "SUCCEEDED"
    assert result["result_ref"] == "ref:snap-1"
    # idempotent: nothing left to dispatch
    again = sch.dispatch_once("tenant-a", "source_refresh",
                              lambda h: h.update({"result_ref": "x"}))
    assert again["dispatched"] is False


def test_retry_on_failure(scheduler):
    sch, _, _ = scheduler
    sch.enqueue(JobSpec(job_type="revision_watch", tenant_id="tenant-a"))
    calls = {"n": 0}

    def flaky(h):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("transient network")
        h.update({"result_ref": "ref:rev-2"})

    for _ in range(4):
        r = sch.dispatch_once("tenant-a", "revision_watch", flaky)
        if r["state"] == "SUCCEEDED":
            break
    assert calls["n"] == 3
    assert r["state"] == "SUCCEEDED"


def test_dispatch_none_when_empty(scheduler):
    sch, _, _ = scheduler
    r = sch.dispatch_once("tenant-a", "source_refresh",
                          lambda h: None)
    assert r["dispatched"] is False


def test_job_tenant_scoped(scheduler):
    sch, _, _ = scheduler
    sch.enqueue(JobSpec(job_type="research", tenant_id="tenant-a"))
    # tenant-b dispatch cannot see tenant-a's job
    r = sch.dispatch_once("tenant-b", "research", lambda h: None)
    assert r["dispatched"] is False
    assert sch.pending_count("tenant-b") == 0
