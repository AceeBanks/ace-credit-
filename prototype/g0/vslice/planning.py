"""G0-B8-C4 — CEO planning & work decomposition.

CEO receives ONLY the governed IntentContract + assembled canonical
context — never the raw client transcript. The plan is bounded and
authority-compliant: no submission capability, workers get bounded
context and bounded capability, and every step anchors to the exact
OpportunityRevision under evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from prototype.g0.agents.task_builder import (
    TaskContract,
    TaskPlan,
    build_plan,
    build_task_contract,
)

# (step_id, worker_role, capability, objective) — roles/capabilities must
# be registered delegables per the Book 4 worker delegation law
PLAN_STEPS = (
    ("discover", "DeterministicService", "opportunity.fetch",
     "Identify governed Georgia opportunity matching the intent"),
    ("eligibility", "DeterministicService",
     "eligibility.extract_candidate_rules",
     "Run deterministic eligibility against the exact revision"),
    ("match", "DeterministicService", "match.explain",
     "Explain match dimensions; hard eligibility dominates ranking"),
    ("research", "CommunityEvidenceWorker", "research.community",
     "Community statistics with lineage"),
    ("research_funder", "FunderResearchWorker", "research.funder",
     "Funder priorities from the solicitation revision"),
    ("research_org", "WinnerResearchWorker", "research.organization",
     "Organization verification from governed snapshots"),
    ("project", "DeterministicService", "application.create_draft_project",
     "Bind ApplicationProject to the exact OpportunityRevision"),
    ("requirements", "RequirementNormalizationWorker",
     "application.create_blueprint",
     "Normalize requirements from the revision"),
    ("blueprint", "RequirementNormalizationWorker",
     "application.create_blueprint",
     "Produce the application blueprint from requirements"),
    ("workers", "DeterministicService", "application.create_blueprint",
     "Decompose drafting into bounded worker tasks with ContextBundles"),
    ("draft", "ProposalSectionWorker", "application.draft_section",
     "Generate proposal sections via governed model runtime"),
    ("budget", "BudgetValidationWorker", "budget.create",
     "Reconcile budget within ceiling"),
    ("ledger", "CitationQAWorker", "evidence.extract_claim",
     "Complete Claim Ledger for material claims"),
    ("qa", "CitationQAWorker", "qa.requirement_coverage",
     "Deterministic QA + Book 7 evaluation"),
    ("review", "DeterministicService", "artifact.version",
     "Record human review packet"),
    ("package", "DeterministicService",
     "application.prepare_submission_package",
     "Assemble SUBMISSION_READY_MOCK package"),
    ("explain", "DeterministicService", "artifact.export",
     "Client ExplanationPacket"),
)


def _expiry() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()


@dataclass
class PlanningResult:
    plan: TaskPlan
    tasks: list[TaskContract]
    context_refs: list[str] = field(default_factory=list)

    def validate(self) -> None:
        for t in self.tasks:
            if "submission" in t.capability_id:
                raise ValueError("CEO plan must never include submission "
                                 "capability (B8.C4)")


def run_planning(*, plan_id: str, intent_id: str, tenant_id: str,
                 project_id: str, objective: str,
                 opportunity_revision_id: str,
                 hard_eligibility_verified: bool = True) -> PlanningResult:
    """Decompose the intent into an authority-compliant, revision-anchored
    plan with bounded worker tasks."""
    step_dicts = [dict(step_id=sid, step_type=stype,
                       objective=desc, required_capability=cap,
                       mock_or_research_only=False)
                  for sid, stype, cap, desc in PLAN_STEPS]
    dependencies = [(PLAN_STEPS[i][0], PLAN_STEPS[i + 1][0])
                    for i in range(len(PLAN_STEPS) - 1)]
    caps = [cap for _, _, cap, _ in PLAN_STEPS]
    plan = build_plan(
        plan_id=plan_id, intent_id=intent_id, objective=objective,
        steps=step_dicts, dependencies=dependencies,
        required_capabilities=caps,
        hard_eligibility_verified=hard_eligibility_verified,
        application_project_id=project_id)
    # CEO-owned capabilities execute in the CEO stage and are NOT delegated
    # to workers; only delegable capabilities produce worker TaskContracts.
    CEO_OWNED = {"application.create_draft_project",
                 "application.prepare_submission_package", "match.explain"}
    tasks = []
    for order, (sid, role, cap, desc) in enumerate(PLAN_STEPS):
        if cap in CEO_OWNED:
            continue
        tasks.append(build_task_contract(
            task_id=f"task-{sid}", plan_id=plan_id, tenant_id=tenant_id,
            project_id=project_id, worker_role=role,
            objective=desc, capability_id=cap,
            inputs_refs=[f"ctx:intent-{intent_id}",
                         f"ctx:rev-{opportunity_revision_id}"],
            allowed_context_refs=[f"ctx:intent-{intent_id}",
                                  f"ctx:rev-{opportunity_revision_id}"],
            required_outputs=[f"output:{sid}"], expires_at=_expiry(),
            side_effect_policy="READ_ONLY"))
    context_refs = [f"ctx:intent-{intent_id}",
                    f"ctx:rev-{opportunity_revision_id}",
                    f"ref:snap-ga-1", f"ref:snap-ga-2", f"ref:stat_ga_42"]
    result = PlanningResult(plan=plan, tasks=tasks, context_refs=context_refs)
    result.validate()
    return result
