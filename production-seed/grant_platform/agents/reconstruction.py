"""G1 Wave 3 — cold reconstruction (Book 8 C36).

After a Personal Hermes / CEO Hermes / worker process restart, the whole
project must be reconstructable from the Store alone:

  organization, intent, project, opportunity revision, plan, tasks,
  worker results, decisions, artifacts.

raw_chat_required must remain False: the raw conversation is never the
canonical Grant state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from grant_platform.store.db import Store


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ReconstructionReport:
    tenant_id: str
    project_id: str
    organization: dict | None
    intent: dict | None
    project: dict | None
    revision: dict | None
    plan: dict | None
    tasks: list[dict]
    worker_results: list[dict]
    decisions: list[dict]
    artifacts: list[dict]
    raw_chat_required: bool = False
    completeness: dict = field(default_factory=dict)
    generated_at: str = ""


def reconstruct(store: Store, *, tenant_id: str, project_id: str) -> ReconstructionReport:
    """Rebuild project state purely from durable rows."""
    project = store.get_project(project_id, tenant_id)
    org: dict | None = None
    revision: dict | None = None
    intent: dict | None = None
    plan: dict | None = None
    if project:
        org = store.get_organization(project["organization_id"], tenant_id)
        revision = store.get_revision(project["revision_id"])
    intents = store.intents_for(tenant_id, project["organization_id"] if project else "")
    if intents:
        intent = intents[-1]
    if intent:
        plan = store.get_plan(f"plan-{intent['intent_id']}")
    tasks = [t for t in store.tasks_for(tenant_id)
             if t.get("project_id") == project_id]
    results = store.worker_results_for(project_id)
    decisions = [d for d in store.audit_for(tenant_id)
                 if d.get("project_id") == project_id]

    report = ReconstructionReport(
        tenant_id=tenant_id, project_id=project_id,
        organization=org, intent=intent, project=project, revision=revision,
        plan=plan, tasks=tasks, worker_results=results,
        decisions=decisions, artifacts=store.artifacts_for(project_id),
        raw_chat_required=False, generated_at=_now())
    # completeness is derived, never asserted
    report.completeness = {
        "organization": org is not None,
        "intent": intent is not None,
        "project": project is not None,
        "revision": revision is not None,
        "plan": plan is not None,
        "tasks": len(tasks) > 0,
        "worker_results": len(results) > 0,
    }
    return report
