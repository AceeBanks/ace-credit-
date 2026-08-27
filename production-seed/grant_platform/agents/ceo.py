"""G1 Wave 3 — CEO Hermes durable orchestration.

Consumes a governed IntentContract (never the raw transcript), produces a
TaskPlan anchored to the exact OpportunityRevision, and enqueues durable
worker tasks in the Store. CEO-owned capabilities (project creation,
submission package) are NOT delegated to workers. A CEO process crash must
not lose the project: all plan/task state is persisted.

Promoted from G0 (`prototype/g0/vslice/planning.py`) with durable
persistence replacing in-memory planning.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from grant_platform.agents.personal import IntentContract
from grant_platform.domain.records import Task
from grant_platform.store.db import Store

# (step_id, worker_role, capability_id, objective) — delegable steps only.
# CEO-OWNED capabilities are executed by the CEO stage itself and never
# appear in this worker table.
PLAN_STEPS = (
    ("discover", "DeterministicService", "opportunity.fetch",
     "Identify governed Georgia opportunity matching the intent"),
    ("eligibility", "DeterministicService", "eligibility.extract_candidate_rules",
     "Run deterministic eligibility against the exact revision"),
    ("match", "DeterministicService", "match.explain",
     "Explain match dimensions; hard eligibility dominates ranking"),
    ("research", "CommunityEvidenceWorker", "research.community",
     "Community statistics with lineage"),
    ("research_funder", "FunderResearchWorker", "research.funder",
     "Funder priorities from the solicitation revision"),
    ("research_org", "WinnerResearchWorker", "research.organization",
     "Organization verification from governed snapshots"),
    ("requirements", "RequirementNormalizationWorker",
     "application.create_blueprint",
     "Normalize requirements from the revision"),
    ("draft", "ProposalSectionWorker", "application.draft_section",
     "Generate proposal sections via governed model runtime"),
    ("budget", "BudgetValidationWorker", "budget.create",
     "Reconcile budget within ceiling"),
    ("ledger", "CitationQAWorker", "evidence.extract_claim",
     "Complete Claim Ledger for material claims"),
    ("qa", "CitationQAWorker", "qa.requirement_coverage",
     "Deterministic QA + Book 7 evaluation"),
    ("package", "DeterministicService",
     "application.prepare_submission_package",
     "Assemble SUBMISSION_READY_MOCK package"),
)

CEO_OWNED = {"application.create_draft_project",
             "application.prepare_submission_package", "match.explain"}

DEFAULT_REVISION = "opp_rev_ga_501_1"  # governed Georgia fixture revision


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class TaskPlan:
    plan_id: str
    intent_id: str
    tenant_id: str
    project_id: str
    opportunity_revision_id: str
    objective: str
    steps: tuple[dict, ...] = ()

    def validate(self) -> None:
        for step in self.steps:
            if "submission" in step.get("capability_id", ""):
                raise ValueError("CEO plan must never include submission "
                                 "capability (B8.C4)")


@dataclass
class CeoExecution:
    plan: TaskPlan
    task_ids: list[str]
    blockers: list[str] = field(default_factory=list)


class CeoHermes:
    def __init__(self, store: Store, ceo_principal: str = "HERMES_CEO"):
        self.store = store
        self.ceo_principal = ceo_principal

    def plan(self, intent: IntentContract, *, project_id: str,
             opportunity_revision_id: str = DEFAULT_REVISION,
             plan_id: str | None = None) -> CeoExecution:
        """Turn the IntentContract into a durable TaskPlan + worker tasks."""
        # submission capability requests were already normalized to
        # prepare-only by Personal Hermes; double-check fail-closed
        if any(c.startswith("submission.") for c in intent.requested_capabilities):
            raise ValueError("CEO refuses submission capability")
        if intent.authority_scope not in ("PREPARE_ONLY", "RESEARCH_ONLY"):
            raise ValueError(f"authority scope {intent.authority_scope} "
                             "not executable by CEO")

        steps = [{"step_id": sid, "worker_role": role,
                  "capability_id": cap, "objective": desc}
                 for sid, role, cap, desc in PLAN_STEPS
                 if cap not in CEO_OWNED]
        plan = TaskPlan(
            plan_id=plan_id or f"plan-{intent.intent_id}",
            intent_id=intent.intent_id, tenant_id=intent.tenant_id,
            project_id=project_id,
            opportunity_revision_id=opportunity_revision_id,
            objective=intent.objective, steps=tuple(steps))
        plan.validate()
        self.store.create_plan({
            "plan_id": plan.plan_id, "intent_id": plan.intent_id,
            "tenant_id": plan.tenant_id, "project_id": plan.project_id,
            "opportunity_revision_id": plan.opportunity_revision_id,
            "objective": plan.objective,
            "steps": [dict(s) for s in plan.steps],
            "state": "PLANNED"})

        task_ids: list[str] = []
        for step in steps:
            task_id = f"task-{plan.plan_id}-{step['step_id']}"
            task_ids.append(task_id)
            self.store.create_task(Task(
                task_id=task_id, tenant_id=plan.tenant_id,
                task_type=step["capability_id"], state="READY",
                project_id=plan.project_id,
                capability_id=step["capability_id"]))
        return CeoExecution(plan=plan, task_ids=task_ids)

    def synthesize(self, project_id: str) -> dict:
        """Gather durable WorkerResults into an execution summary. Reads
        ONLY the Store — never Hermes memory (reconstruction law)."""
        results = self.store.worker_results_for(project_id)
        summary = {
            "project_id": project_id,
            "completed_tasks": len(results),
            "capabilities": [r["capability_id"] for r in results],
            "blockers": [r["summary"] for r in results
                         if r["summary"].startswith("BLOCKED")],
        }
        return summary
