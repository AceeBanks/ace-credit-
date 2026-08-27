"""G0-B8-C3..C27 — vertical slice orchestrator.

Runs the production-shaped Georgia vertical slice end-to-end through the
existing governed contracts and the Book 7 model runtime:

  client intent -> Personal (IntentContract) -> CEO (TaskPlan)
  -> selection -> eligibility -> match -> research -> project
  -> requirements -> blueprint -> drafting (governed model) -> budget
  -> claim ledger -> QA -> human review -> SUBMISSION_READY_MOCK
  -> explanation

Every stage emits a durable SliceRecord so the run can be reconstructed
without chat memory. Submission stays structurally impossible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from prototype.g0.vslice.assurance import run_assurance
from prototype.g0.vslice.drafting import run_drafting
from prototype.g0.vslice.fixture import build_client_profile
from prototype.g0.vslice.intake import run_intake
from prototype.g0.vslice.models import SliceRecord
from prototype.g0.vslice.package import build_package
from prototype.g0.vslice.planning import run_planning
from prototype.g0.vslice.project import run_project
from prototype.g0.vslice.qualify import run_qualify
from prototype.g0.vslice.research import run_research
from prototype.g0.vslice.selection import run_selection

TENANT = "tenant-a"
PROJECT = "proj-slice"
ACTOR = "client-ga-1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SliceRun:
    run_id: str
    records: list[SliceRecord]
    package: object
    generation_mode: str = ""

    def record(self, stage: str) -> dict:
        return next((r.payload for r in self.records
                     if r.stage == stage), {})

    def state(self) -> dict:
        return {"run_id": self.run_id,
                "stages": [r.stage for r in self.records],
                "package_state": self.package.state,
                "label": self.package.label,
                "submission_enabled": self.package.submission_enabled,
                "generation_mode": self.generation_mode}


def run_slice(*, run_id: str, client_intent: str,
              draft_live: bool | None = None) -> SliceRun:
    """Execute the full vertical slice; returns durable records + package."""
    records: list[SliceRecord] = []
    profile = build_client_profile()

    # C3 intake
    intake = run_intake(tenant_id=TENANT, client_actor_id=ACTOR,
                        organization_id=profile.organization_id,
                        client_intent_text=client_intent, profile=profile)
    records.append(SliceRecord(
        stage="intent", record_id=f"rec-{run_id}-intent", tenant_id=TENANT,
        project_id=PROJECT, payload={
            "intent_id": intake.intent.intent_id,
            "objective": intake.intent.objective,
            "readiness_state": intake.readiness_state,
            "open_questions": intake.intent.open_questions,
            "used_raw_transcript": intake.used_raw_transcript,
            "fabricated_eligibility": intake.fabricated_eligibility,
        }, created_at=_now()))

    # C4 CEO planning
    intent_id = intake.intent.intent_id
    selection = run_selection(tenant_id=TENANT, project_id=PROJECT,
                              principal_id=ACTOR, intent_id=intent_id)
    revision_id = selection.revision_id
    planning = run_planning(
        plan_id=f"plan-{run_id}", intent_id=intent_id, tenant_id=TENANT,
        project_id=PROJECT, objective=intake.intent.objective,
        opportunity_revision_id=revision_id)
    records.append(SliceRecord(
        stage="plan", record_id=f"rec-{run_id}-plan", tenant_id=TENANT,
        project_id=PROJECT, payload={
            "plan_id": planning.plan.plan_id,
            "task_ids": [t.task_id for t in planning.tasks],
            "step_count": len(planning.plan.steps),
            "submission_capabilities": [],
        }, created_at=_now()))

    # C5 selection
    records.append(SliceRecord(
        stage="selection", record_id=f"rec-{run_id}-selection",
        tenant_id=TENANT, project_id=PROJECT,
        payload=selection.to_dict(),
        decision_refs=[selection.decision_record["decision_id"]],
        created_at=_now()))

    # C7-C9 eligibility + match
    qualify = run_qualify(tenant_id=TENANT, project_id=PROJECT,
                          principal_id=ACTOR, intent_id=intent_id,
                          selection_revision_id=revision_id)
    records.append(SliceRecord(
        stage="eligibility", record_id=f"rec-{run_id}-eligibility",
        tenant_id=TENANT, project_id=PROJECT,
        payload=qualify.eligibility_decision,
        decision_refs=[qualify.eligibility_decision["decision_id"]],
        created_at=_now()))
    records.append(SliceRecord(
        stage="match", record_id=f"rec-{run_id}-match",
        tenant_id=TENANT, project_id=PROJECT,
        payload=qualify.match_decision,
        decision_refs=[qualify.match_decision["decision_id"]],
        created_at=_now()))

    # C10-C13 research + synthesis
    research = run_research(tenant_id=TENANT, project_id=PROJECT,
                            principal_id=ACTOR, intent_id=intent_id,
                            revision_id=revision_id)
    records.append(SliceRecord(
        stage="research", record_id=f"rec-{run_id}-research",
        tenant_id=TENANT, project_id=PROJECT,
        payload={"findings": research.findings,
                 "synthesis": research.synthesis},
        created_at=_now()))

    # C14-C16 project + requirements + blueprint
    project = run_project(tenant_id=TENANT, project_id=PROJECT,
                          principal_id=ACTOR, intent_id=intent_id,
                          revision_id=revision_id,
                          organization_id=profile.organization_id,
                          opportunity_id=selection.opportunity_id)
    records.append(SliceRecord(
        stage="project", record_id=f"rec-{run_id}-project",
        tenant_id=TENANT, project_id=PROJECT,
        payload={"project_id": project.project_id,
                 "requirements": project.requirements,
                 "blueprint": project.blueprint},
        decision_refs=[project.decision_record["decision_id"]],
        created_at=_now()))

    # C17-C20 drafting + budget
    drafting = run_drafting(blueprint=project.blueprint,
                            revision_id=revision_id,
                            ceiling=str(D2_CEILING), live=draft_live)
    records.append(SliceRecord(
        stage="drafting", record_id=f"rec-{run_id}-drafting",
        tenant_id=TENANT, project_id=PROJECT,
        payload={"sections": drafting.sections,
                 "generation_mode": drafting.generation_mode,
                 "budget_total": drafting.budget_total,
                 "ceiling": drafting.ceiling},
        created_at=_now()))

    # C21-C24 assurance (ledger + QA + human review)
    assurance = run_assurance(
        sections=drafting.sections, revision_id=revision_id,
        deadline=selection.deadline or "2026-10-15",
        ceiling=drafting.ceiling)
    records.append(SliceRecord(
        stage="assurance", record_id=f"rec-{run_id}-assurance",
        tenant_id=TENANT, project_id=PROJECT,
        payload={"claim_metrics": assurance.claim_metrics,
                 "deterministic_qa": assurance.deterministic_qa,
                 "hard_gate_pass": assurance.hard_gate_pass,
                 "human_review": assurance.human_review},
        created_at=_now()))

    # C25-C26 package + explanation
    eligibility_result = qualify.eligibility_decision["result"]["result"]
    decisions = [
        qualify.eligibility_decision, qualify.match_decision,
        project.decision_record, selection.decision_record,
    ]
    package = build_package(
        package_id=f"pkg-{run_id}", project_id=PROJECT, tenant_id=TENANT,
        sections=drafting.sections, claim_ledger=assurance.claim_ledger,
        budget_lines=drafting.budget_lines,
        budget_total=drafting.budget_total,
        qa_report=assurance.deterministic_qa,
        human_review=assurance.human_review,
        revision_id=revision_id, eligibility_result=eligibility_result,
        explanation_decisions=[_decision_from_dict(d) for d in decisions])
    records.append(SliceRecord(
        stage="package", record_id=f"rec-{run_id}-package",
        tenant_id=TENANT, project_id=PROJECT,
        payload={"package_id": package.package_id,
                 "state": package.state, "label": package.label,
                 "submission_enabled": package.submission_enabled},
        created_at=_now()))

    run = SliceRun(run_id=run_id, records=records, package=package,
                   generation_mode=drafting.generation_mode)
    return run


from prototype.g0.domain.fixtures.georgia import GA_1  # noqa: E402
from prototype.g0.vslice.package import _decision_from_dict  # noqa: E402

D2_CEILING = GA_1["revision"].funding_ceiling
