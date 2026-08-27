"""G1 Wave 3 — bounded worker runtime.

Workers remain task-scoped and stateless-by-default. A worker:

1. atomically claims a durable task (one worker wins);
2. assembles a BOUNDED ContextBundle (intent ref + revision ref + evidence
   refs — never the raw client transcript, never full history);
3. invokes a governed handler (deterministic service, or the Model Gateway
   for drafting tasks — Wave 4 wiring);
4. writes a WorkerResult to the Store with material claims;
5. completes the task with a result ref.

Promoted from G0 (`prototype/g0/vslice/drafting.py` worker contract) with
durable task semantics from Wave 1 (`grant_platform.runtime.tasks`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from grant_platform.runtime.tasks import TaskRunner
from grant_platform.store.db import Store

from grant_platform.agents.personal import IntentContract


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ContextBundle:
    """Bounded context for one worker task. No transcripts, no full
    history, no model scratchpads — only governed refs."""
    task_id: str
    intent: IntentContract
    opportunity_revision_id: str
    evidence_refs: list[str] = field(default_factory=list)
    previous_section_summaries: dict = field(default_factory=dict)


@dataclass
class WorkerResult:
    result_id: str
    task_id: str
    tenant_id: str
    worker_principal: str
    capability_id: str
    summary: str
    project_id: str | None = None
    claims: list[dict] = field(default_factory=list)
    context_refs: list[str] = field(default_factory=list)
    model_ref: str | None = None


class WorkerRuntime:
    """Claims and runs durable worker tasks against registered handlers."""

    def __init__(self, store: Store, runner: TaskRunner,
                 worker_principal: str = "WORKER"):
        self.store = store
        self.runner = runner
        self.worker_principal = worker_principal
        self._handlers: dict[str, callable] = {}

    def register(self, capability_id: str, fn: callable) -> None:
        self._handlers[capability_id] = fn

    def build_bundle(self, intent: IntentContract, task_id: str,
                     revision_id: str) -> ContextBundle:
        """Bounded context assembly: intent + revision + governed evidence
        refs. Never the raw conversation."""
        refs = [f"ctx:intent-{intent.intent_id}",
                f"ctx:rev-{revision_id}"]
        return ContextBundle(task_id=task_id, intent=intent,
                             opportunity_revision_id=revision_id,
                             evidence_refs=refs)

    def run(self, task_id: str, tenant_id: str, intent: IntentContract,
            revision_id: str, project_id: str | None = None) -> dict:
        """Claim and execute one task. Returns the durable task row."""
        task = self.store.get_task(task_id, tenant_id)
        if task is None:
            raise ValueError(f"unknown task {task_id}")
        capability = task["capability_id"]
        if capability not in self._handlers:
            raise KeyError(f"no handler for capability {capability}")
        claimed = self.runner.claim(task_id, tenant_id, self.worker_principal)
        if not claimed:
            raise RuntimeError(f"task {task_id} not claimable (concurrent)")

        bundle = self.build_bundle(intent, task_id, revision_id)
        holder: dict = {}

        def body(h: dict) -> None:
            result: WorkerResult = self._handlers[capability](bundle)
            self.store.create_worker_result({
                "result_id": result.result_id, "task_id": result.task_id,
                "tenant_id": result.tenant_id, "project_id": project_id,
                "worker_principal": result.worker_principal,
                "capability_id": result.capability_id,
                "summary": result.summary,
                "claims": result.claims,
                "context_refs": result.context_refs,
                "model_ref": result.model_ref})
            h["result_ref"] = f"ref:result:{task_id}"

        outcome = self.runner.run(task_id, tenant_id,
                                  self.worker_principal, body)
        return {
            "task_id": task_id, "state": outcome.state,
            "result_ref": outcome.result_ref,
            "retry_count": outcome.retry_count,
        }
