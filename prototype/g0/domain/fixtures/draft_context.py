"""B2.C19 — Georgia-first DraftContextBundle readiness fixture.

A schema-valid synthetic/manual bundle that Book 3 can later replace with
source-governed snapshots. Validates clean against the D0 rules.
"""
from __future__ import annotations

from decimal import Decimal

from prototype.g0.domain.draft_context import DraftContextBundle
from prototype.g0.domain.fixtures.community import COMMUNITY_1
from prototype.g0.domain.fixtures.georgia import (
    GA_BUSINESS_PLAN,
    GA_CLAIM,
    GA_DECISION,
    GA_FACT,
    GA_NONPROFIT,
    GA_OPP,
    GA_OPP_REV1,
    GA_PROPOSAL,
    GA_PROJECT,
    GA_REQ_NARRATIVE,
)
from prototype.g0.domain.models import (
    Budget,
    BudgetLine,
    Period,
    Program,
    ProposalSection,
)

GA_PROGRAM = Program(program_id="prog_ga_9", name="GA OPB Community Grants",
                     agency="Georgia Office of Planning and Budget",
                     status="ACTIVE")

GA_BUDGET = Budget(
    budget_id="budget_ga_1",
    project_id=GA_PROJECT.project_id,
    version=1,
    currency="USD",
    lines=(BudgetLine("line_ga_1", "personnel", Decimal("40000.00")),
           BudgetLine("line_ga_2", "program_supplies", Decimal("10000.00"))),
    period=Period("period_ga_1", "FY2026"),
)

GA_PROPOSAL_TEMPLATE = (
    ProposalSection("sec_ga_1", profile_section_key="org_background",
                    title="Organization Background", order=1),
    ProposalSection("sec_ga_2", profile_section_key="impact_narrative",
                    title="Impact Narrative", order=2),
)

GA_DRAFT_BUNDLE = DraftContextBundle(
    organization=GA_NONPROFIT,
    opportunity=GA_OPP,
    opportunity_revision=GA_OPP_REV1,
    canonical_facts=(GA_FACT,),
    eligibility_decision=GA_DECISION,
    requirements=(GA_REQ_NARRATIVE,),
    funder_program=GA_PROGRAM,
    evidence=(GA_CLAIM,),
    statistics=(COMMUNITY_1["statistic"],),
    budget=GA_BUDGET,
    research_findings=(GA_FACT,),
    proposal_template=GA_PROPOSAL_TEMPLATE,
    output_artifacts=(GA_PROPOSAL, GA_BUSINESS_PLAN),
)
