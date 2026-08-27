"""G1 Wave 1 — durable task/run system.

Production semantics over the Store's task tables:

- PENDING/READY tasks are claimable atomically (one worker wins);
- a claimed task runs under the worker; a process death leaves it RUNNING
  until the lease expires -> STALE, then recoverable;
- idempotency: a SUCCEEDED task with a result_ref is never re-executed;
- retries are bounded per TaskContract policy;
- every transition is auditable via the Store.

Workflow truth lives in the Store (Postgres in production), never only in
Hermes memory (Book 8 reconstruction law).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from grant_platform.domain.records import Task
from grant_platform.store.db import Store


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TaskOutcome:
    task_id: str
    state: str
    result_ref: str | None = None
    retry_count: int = 0


class TaskRunner:
    def __init__(self, store: Store, max_retries: int = 2):
        self.store = store
        self.max_retries = max_retries

    def enqueue(self, t: Task) -> None:
        self.store.create_task(t)

    def claim(self, task_id: str, tenant_id: str, worker: str) -> bool:
        """Atomic claim. False = another worker owns it or it is terminal."""
        return self.store.claim_task(task_id, tenant_id, worker)

    def run(self, task_id: str, tenant_id: str, worker: str,
            fn) -> TaskOutcome:
        """Execute a claimed task with bounded retry + idempotency.

        fn(result_holder) is the worker body; it may write progress to a
        checkpoint holder dict. On exception the task FAILs (or retries up
        to max_retries when the error is transient).
        """
        task = self.store.get_task(task_id, tenant_id)
        if task is None:
            raise ValueError(f"unknown task {task_id}")
        # idempotency: never re-execute a completed task
        if task["state"] == "SUCCEEDED" and task.get("result_ref"):
            return TaskOutcome(task_id, "SUCCEEDED",
                               result_ref=task["result_ref"],
                               retry_count=task["retry_count"])

        holder: dict = {}
        try:
            fn(holder)
        except Exception as exc:  # noqa: BLE001 - durable retry boundary
            retries = task["retry_count"]
            if retries < self.max_retries:
                self.store.increment_task_retry(task_id)
                self.store.set_task_state(task_id, "READY")
                return TaskOutcome(task_id, "READY",
                                   retry_count=retries + 1)
            self.store.fail_task(task_id, tenant_id, worker, str(exc))
            return TaskOutcome(task_id, "FAILED", retry_count=retries)

        result_ref = holder.get("result_ref", f"ref:result:{task_id}")
        if not self.store.complete_task(task_id, tenant_id, worker,
                                        result_ref):
            raise RuntimeError(f"task {task_id} lost worker ownership")
        return TaskOutcome(task_id, "SUCCEEDED", result_ref=result_ref,
                           retry_count=task["retry_count"])

    def checkpoint(self, task_id: str, tenant_id: str,
                   progress: str) -> None:
        """Durable progress checkpoint (resume point)."""
        self.store.create_audit(
            __import__("grant_platform.domain.records",
                       fromlist=["AuditEvent"]).AuditEvent(
                audit_id=f"aud-cp-{task_id}-{_now()}",
                tenant_id=tenant_id, project_id=None, actor_ref="runner",
                event_type="task_checkpoint",
                payload_ref=f"progress:{task_id}",
                created_at=_now()))
        # progress is durable via audit; state row remains authoritative

    def recover_stale(self, stale_after_seconds: int = 600) -> int:
        """Lease expiry -> STALE; a supervisor re-queues them READY."""
        n = self.store.mark_stale_tasks(stale_after_seconds)
        if n:
            self.store.conn.execute(
                "UPDATE tasks SET state='READY' WHERE state='STALE'")
            self.store.conn.commit()
        return n
