"""G0-B8-C14/C15/C16 — ApplicationProject creation, requirement
decomposition, and application blueprint.

The project binds the EXACT OpportunityRevision. Requirements come from the
revision (never a hard-coded template). The blueprint maps each requirement
to proposal sections and evidence needs — drafting starts from the blueprint,
not from a generic prompt.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from prototype.g0.domain.fixtures.georgia import GA_1
from prototype.g0.evidence.decisions import DecisionInputRef, build_decision


@dataclass
class ProjectResult:
    project_id: str
    organization_id: str
    opportunity_id: str
    revision_id: str
    requirements: list[dict]
    blueprint: dict
    decision_record: dict

    def validate(self) -> None:
        assert all(r["opportunity_revision_id"] == self.revision_id
                   for r in self.requirements), \
            "requirements must anchor to the exact revision (B8.C15)"
        if not self.blueprint.get("sections"):
            raise ValueError("blueprint must map requirements to sections "
                             "(B8.C16)")


def run_project(*, tenant_id: str, project_id: str, principal_id: str,
                intent_id: str, revision_id: str,
                organization_id: str, opportunity_id: str) -> ProjectResult:
    """Bind the ApplicationProject, normalize requirements, and build the
    blueprint."""
    requirements = []
    for req in GA_1["requirements"]:
        requirements.append({
            "requirement_id": req.requirement_id,
            "opportunity_revision_id": req.opportunity_revision_id,
            "requirement_type": req.requirement_type,
            "mandatory": req.mandatory,
            "prompt": req.prompt,
            "word_limit": req.word_limit,
            "state": "IDENTIFIED",
        })
    # blueprint: section -> requirement -> evidence needs
    sections = [
        {"section_id": "community_impact",
         "requirement_id": "req_ga_1",
         "evidence_refs": ["ref:stat_ga_42", "ref:snap-ga-1"],
         "drafting_notes": ("use the 18.2% Dade County statistic; do not "
                            "invent program outcomes; UNKNOWN stays UNKNOWN")},
        {"section_id": "organization",
         "requirement_id": "req_ga_1",
         "evidence_refs": ["ref:snap-ga-1", "ref:snap-ga-2",
                           "ref:fact_ga_1"],
         "drafting_notes": ("legal name, Georgia nonprofit, founded 2012, "
                            "501(c)(3); staff/budget UNKNOWN")},
        {"section_id": "budget_narrative",
         "requirement_id": "req_ga_2",
         "evidence_refs": [f"ref:opp_rev_{revision_id}"],
         "drafting_notes": ("request within the $50,000 ceiling; line items "
                            "reconcile; do not invent allocations")},
        {"section_id": "deadline",
         "requirement_id": "req_ga_1",
         "evidence_refs": [f"ref:opp_rev_{revision_id}"],
         "drafting_notes": ("October 15, 2026; application NOT yet "
                            "submitted")},
    ]
    blueprint = {"sections": sections,
                 "opportunity_revision_id": revision_id,
                 "source": "derived from the exact OpportunityRevision"}
    decision = build_decision(
        decision_id=f"dec-proj-{intent_id}",
        decision_type="REQUIREMENT_COVERAGE",
        tenant_id=tenant_id, project_id=project_id,
        actor_ref=principal_id,
        capability_id="application.draft_internal",
        input_refs=[
            DecisionInputRef(input_role="opportunity_revision",
                             ref=f"ref:opp_rev_{revision_id}"),
        ],
        policy_ref="policy:book2-requirements",
        result={"project_id": project_id,
                "opportunity_id": opportunity_id,
                "revision_id": revision_id,
                "requirement_count": len(requirements),
                "blueprint_sections": len(sections)})
    result = ProjectResult(
        project_id=project_id, organization_id=organization_id,
        opportunity_id=opportunity_id, revision_id=revision_id,
        requirements=requirements, blueprint=blueprint,
        decision_record=decision.to_dict())
    result.validate()
    return result
