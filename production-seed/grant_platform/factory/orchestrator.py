"""G1 Wave 4 — full Grant factory orchestrator (G1.7/G1.8).

End-to-end: blueprint -> section drafting -> synthesis -> budget -> full QA
-> DOCX/PDF rendering -> SUBMISSION_READY_MOCK package.

The orchestrator is the composition boundary the Wave 5 API drives. It
takes an optional governed model_invoke callable; None selects the honest
deterministic lane (labeled as such, never passed off as model output).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from grant_platform.factory.blueprint import ApplicationBlueprint, build_blueprint
from grant_platform.factory.budget import BudgetReport, build_budget
from grant_platform.factory.drafting import DraftingReport, draft_sections
from grant_platform.factory.qa import FullQAReport, run_full_qa
from grant_platform.factory.render import render_docx, render_pdf
from grant_platform.factory.synthesis import SynthesisReport, synthesize

SUBMISSION_READY_MOCK = "SUBMISSION_READY_MOCK"
BLOCKED = "BLOCKED"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class FactoryPackage:
    blueprint: ApplicationBlueprint
    draft: DraftingReport
    synthesis: SynthesisReport
    budget: BudgetReport
    qa: FullQAReport
    docx: object
    pdf: object
    project_id: str
    revision_id: str
    status: str
    model_runs: list[dict] = field(default_factory=list)
    generated_at: str = ""

    @property
    def readiness_state(self) -> str:
        """Explicit readiness outcome: never claim READY when gaps remain."""
        unresolved = self.draft.unsupported_material_claims()
        if self.qa.failures:
            return "QA_BLOCKED"
        if unresolved:
            return "NEEDS_CLIENT_INPUT"
        return "READY_FOR_REVIEW"

    def summary(self) -> dict:
        unresolved = self.draft.unsupported_material_claims()
        claim_counts: dict[str, int] = {}
        for c in self.draft.claims:
            claim_counts[c.classification] = claim_counts.get(c.classification, 0) + 1
        return {
            "project_id": self.project_id,
            "revision_id": self.revision_id,
            "status": self.status,
            "readiness_state": self.readiness_state,
            "generation_mode": self.draft.generation_mode,
            "sections": len(self.draft.sections),
            "word_count": sum(s.word_count
                              for s in self.draft.sections.values()),
            "claims": len(self.draft.claims),
            "claim_counts": claim_counts,
            "unsupported": len(unresolved),
            "qa_pass": self.qa.pass_count,
            "qa_fail": len(self.qa.failures),
            "budget_total": self.budget.total,
            "ceiling": self.budget.ceiling,
            "within_ceiling": self.budget.within_ceiling,
            "docx_pages": self.docx.page_count_estimate,
            "pdf_pages": self.pdf.page_count_estimate,
            "submission_enabled": False,
            "generated_at": self.generated_at,
        }


def run_factory(*, project_id: str = "proj-1",
                revision_id: str = "opp_rev_ga_501_1",
                deadline: str | None = "2026-10-15",
                ceiling: str | None = "50000.00",
                model_invoke: Callable | None = None,
                model_id: str | None = None,
                client_budget_lines: list | None = None,
                blueprint: ApplicationBlueprint | None = None,
                fact_pack=None,
                profile=None) -> FactoryPackage:
    """Run the full factory. Returns a SUBMISSION_READY_MOCK package when
    all QA hard gates pass, BLOCKED otherwise (never fake-ready).

    Quality path (G1-QUALITY): when a solicitation profile and organization
    fact pack are supplied with a live model_invoke, sections are planned,
    drafted, critiqued, and revised against the REAL funder requirements
    (draft_sections_quality). Otherwise the plain lane applies."""
    bp = blueprint or build_blueprint(
        revision_id=revision_id, deadline=deadline,
        funding_ceiling=ceiling)
    effective_revision = bp.opportunity_revision_id or revision_id
    effective_deadline = bp.deadline or deadline
    if profile is not None and fact_pack is not None and model_invoke is not None:
        from grant_platform.factory.quality_drafting import draft_sections_quality
        research = getattr(bp, "research_block", "")
        draft = draft_sections_quality(
            bp, fact_pack=fact_pack, profile=profile,
            research_block=research,
            model_invoke=model_invoke, model_id=model_id)
    else:
        draft = draft_sections(bp, model_invoke=model_invoke,
                               model_id=model_id)
    synthesis = synthesize(bp, draft)
    budget = build_budget(ceiling=ceiling or "50000.00",
                          client_lines=client_budget_lines)
    qa = run_full_qa(blueprint=bp, draft=draft, budget=budget,
                     synthesis=synthesis,
                     expected_deadline=effective_deadline or "",
                     expected_revision=effective_revision)
    # per-section protected facts are a hard gate for LIVE_MODEL sections
    model_sections = [s for s in draft.sections.values()
                      if s.generation_mode == "LIVE_MODEL"]
    if any(not s.protected_facts_preserved for s in model_sections):
        qa.results.append(type(qa.results[0])(
            "protected_facts_live_lane", "FAIL",
            "live lane altered a protected fact"))

    if qa.submission_ready_mock:
        status = SUBMISSION_READY_MOCK
    else:
        status = BLOCKED

    docx = render_docx(draft.sections,
                       artifact_version_id=f"av-{project_id}-{_now()}",
                       project_ref=project_id, revision_ref=effective_revision)
    pdf = render_pdf(draft.sections,
                     artifact_version_id=f"av-{project_id}-{_now()}",
                     project_ref=project_id, revision_ref=effective_revision)

    return FactoryPackage(
        blueprint=bp, draft=draft, synthesis=synthesis, budget=budget,
        qa=qa, docx=docx, pdf=pdf, project_id=project_id,
        revision_id=revision_id, status=status,
        model_runs=draft.model_runs, generated_at=_now())
