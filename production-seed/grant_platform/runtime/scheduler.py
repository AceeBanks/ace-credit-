"""G1 Wave 1 — scheduler / background job queue.

Smallest justified background execution layer (Book 9 OCE_NATIVE): jobs are
rows in the durable task system, claimed and executed by the TaskRunner.
No Kafka/Kubernetes-scale infrastructure (no measured evidence).

Job types planned: source_refresh, revision_watch, research, drafting,
evaluation. Scheduler semantics: enqueue periodic jobs as READY tasks with
a capability bound to a service principal; a worker loop claims + runs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from grant_platform.domain.records import Task
from grant_platform.runtime.tasks import TaskRunner
from grant_platform.store.db import Store


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class JobSpec:
    job_type: str
    tenant_id: str
    project_id: str | None = None
    capability_id: str | None = None
    cron_like: str = ""        # informational; not a cron engine yet
    payload: dict = field(default_factory=dict)


class Scheduler:
    """Enqueue + dispatch background jobs on the durable task system."""

    def __init__(self, store: Store, runner: TaskRunner,
                 service_principal: str):
        self.store = store
        self.runner = runner
        self.service = service_principal

    def enqueue(self, spec: JobSpec, job_id: str | None = None) -> str:
        tid = job_id or f"job-{spec.job_type}-{_now()}"
        self.runner.enqueue(Task(
            task_id=tid, tenant_id=spec.tenant_id,
            project_id=spec.project_id, task_type=spec.job_type,
            state="READY", capability_id=spec.capability_id))
        return tid

    def dispatch_once(self, tenant_id: str, job_type: str,
                      fn) -> dict:
        """Claim the next READY job of a type and run it (idempotent)."""
        rows = self.store.conn.execute(
            "SELECT * FROM tasks WHERE tenant_id=? AND task_type=? AND"
            " state='READY' ORDER BY created_at LIMIT 1",
            (tenant_id, job_type)).fetchall()
        if not rows:
            return {"dispatched": False, "job_id": None}
        job = rows[0]
        tid = job["task_id"]
        if not self.runner.claim(tid, tenant_id, self.service):
            return {"dispatched": False, "job_id": tid}
        outcome = self.runner.run(tid, tenant_id, self.service, fn)
        return {"dispatched": True, "job_id": tid,
                "state": outcome.state,
                "result_ref": outcome.result_ref}

    def pending_count(self, tenant_id: str) -> int:
        row = self.store.conn.execute(
            "SELECT COUNT(*) AS n FROM tasks WHERE tenant_id=? AND state"
            " IN ('READY','RUNNING')", (tenant_id,)).fetchone()
        return int(row["n"])
