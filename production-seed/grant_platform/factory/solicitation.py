"""G1-QUALITY-02 — Real solicitation decomposition engine.

Blueprints derive from actual solicitation documents, never a fixed
7-section template. Every requirement keeps locator/provenance back to
the source document (SourceSnapshot), and every section knows which
reviewer scoring criterion it serves.

Benchmark solicitation: FY2026 AmeriCorps State and National — Georgia
Formula Grant (Georgia Commission for Service and Volunteerism /
Georgia Serves, DCA). Source PDF stored at
docs/grant-sector/g1/solicitations/ga_dca_nofp_2026.pdf.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Source provenance -------------------------------------------------------


@dataclass(frozen=True)
class SourceSnapshot:
    """Exact provenance for a solicitation document."""
    source_id: str
    funder: str
    title: str
    source_url: str
    document_path: str          # repo-relative path to stored PDF
    retrieved_at: str = ""
    sha256: str = ""
    page_count: int = 0

    def compute_digest(self, repo_root: Path) -> str:
        p = repo_root / self.document_path
        if p.exists():
            self_sha = hashlib.sha256(p.read_bytes()).hexdigest()
            object.__setattr__(self, "sha256", self_sha)
        return self.sha256


# --- Scoring rubric ----------------------------------------------------------


@dataclass(frozen=True)
class ScoringCriterion:
    criterion_id: str           # e.g. "program_design.community_logic_model"
    name: str
    points: int
    parent_id: str | None = None
    reviewer_looks_for: str = ""
    requirement_ids: tuple[str, ...] = ()


# --- Requirements ------------------------------------------------------------


@dataclass(frozen=True)
class SolicitationRequirement:
    """One answerable requirement extracted from the solicitation, with
    locator/provenance back to the source document."""
    requirement_id: str
    section_id: str
    title: str
    prompt: str                  # exact funder prompt/question text
    required: bool = True
    response_type: str = "narrative"   # narrative | template | table | na
    page_limit: int | None = None       # section-local page limit, if any
    format_requirements: str = ""       # e.g. "double-spaced, 11 pages total"
    criterion_id: str | None = None     # scoring criterion served
    required_evidence: tuple[str, ...] = ()
    locator: str = ""                   # e.g. "NOFO E.1.b.1, p.19-20"


@dataclass(frozen=True)
class SolicitationProfile:
    """A decomposed solicitation: provenance + requirements + rubric."""
    snapshot: SourceSnapshot
    deadline: str
    funding_ceiling: str | None
    match_requirement: str | None
    narrative_page_limit: int | None
    eligibility: tuple[str, ...]
    funding_priorities: tuple[str, ...]
    requirements: tuple[SolicitationRequirement, ...]
    criteria: tuple[ScoringCriterion, ...]
    required_attachments: tuple[tuple[str, str], ...]

    def total_points(self) -> int:
        return sum(c.points for c in self.criteria if c.parent_id is None)


# --- The real FY2026 AmeriCorps Georgia benchmark ----------------------------

AMERICORPS_GA_2026 = SolicitationProfile(
    snapshot=SourceSnapshot(
        source_id="ga_dca_nofp_2026",
        funder="Georgia Commission for Service and Volunteerism (Georgia Serves) / AmeriCorps",
        title="Fiscal Year 2026 AmeriCorps State and National — Georgia Formula Grant",
        source_url=("https://dca.georgia.gov/document/document/"
                    "georgia-notice-funding-opportunity-2026/download"),
        document_path="docs/grant-sector/g1/solicitations/ga_dca_nofp_2026.pdf",
        retrieved_at="2026-08-28",
    ),
    deadline="February 27, 2026 3:00 PM EST",
    funding_ceiling=None,          # MSY-based allocation, not dollar ceiling
    match_requirement=("24% grantee match for first three-year funding "
                       "period (cost reimbursement grants)"),
    narrative_page_limit=11,
    eligibility=(
        "Indian Tribes", "institutions of higher education",
        "local governments including school districts",
        "nonprofit organizations", "State Service Commissions (sub-applicants)",
        "faith-based organizations"),
    funding_priorities=(
        "Georgia Serves funding priorities per NOFO section A.2"),
    requirements=(
        SolicitationRequirement(
            requirement_id="req.exec_summary",
            section_id="executive_summary",
            title="Executive Summary",
            prompt=("Fill in the blanks of the fixed template: \"The [Name of "
                    "the organization] will have [Number of] AmeriCorps "
                    "members in [locations]. AmeriCorps members will [service "
                    "activities]. At the end of the first program year, the "
                    "AmeriCorps members will be responsible for [anticipated "
                    "outcome]. In addition, the AmeriCorps members will "
                    "leverage [number] volunteers who will be engaged in "
                    "[what]. The AmeriCorps investment will be matched with "
                    "$[amount]...\" Do not deviate from this template."),
            response_type="template",
            criterion_id="exec_summary",
            locator="NOFO E.1.a, p.19"),
        SolicitationRequirement(
            requirement_id="req.community_logic_model",
            section_id="program_design",
            title="Community and Logic Model",
            prompt=("Provide a detailed summary of the community problem and "
                    "explain how the applicant's intervention(s) will lead to "
                    "the outcomes identified in the Logic Model. The Logic "
                    "Model must describe: inputs/resources necessary to "
                    "deliver the intervention (locations/sites, setting and "
                    "community condition); number of AmeriCorps members who "
                    "will deliver the intervention; characteristics of "
                    "members including specific knowledge, skills, and "
                    "abilities required; core activities members will "
                    "deliver including length of each activity (weeks, "
                    "sessions, months) and dosage (hours per session or "
                    "sessions per week); target population; measurable "
                    "outputs (number of beneficiaries served, types and "
                    "number of activities); and outcomes — meaningful "
                    "changes in knowledge/skill, attitude, behavior, or "
                    "condition — including short, medium, or long-term "
                    "outcomes."),
            criterion_id="program_design.community_logic_model",
            required_evidence=("community_condition",),
            locator="NOFO E.1.b.1, p.19-20"),
        SolicitationRequirement(
            requirement_id="req.evidence_base",
            section_id="program_design",
            title="Evidence Base (Tier and Quality)",
            prompt=("Summarize the study design and key findings of the "
                    "evidence documents submitted (up to two, plus the "
                    "evaluation report from the last three-year grant cycle "
                    "if applicable). Describe any other evidence supporting "
                    "the program, including past performance measure data "
                    "and/or other research studies that inform the program "
                    "design. Provide citations for the studies described. "
                    "The intervention evaluated must match the intervention "
                    "proposed. Rated into an evidence tier: Strong / "
                    "Moderate / Preliminary / Pre-Preliminary."),
            criterion_id="program_design.evidence_tier",
            required_evidence=("evidence_documents", "citations"),
            locator="NOFO E.1.b.2, p.20-21"),
        SolicitationRequirement(
            requirement_id="req.notice_priority",
            section_id="program_design",
            title="Notice Priority",
            prompt=("Describe whether one or more of the Georgia Serves "
                    "funding priorities is a significant part of the program "
                    "focus and intended outcomes (refer to NOFO A.2 Funding "
                    "Priorities)."),
            criterion_id="program_design.notice_priority",
            locator="NOFO E.1.b.3, p.21"),
        SolicitationRequirement(
            requirement_id="req.member_experience",
            section_id="program_design",
            title="Member Experience",
            prompt=("Describe how AmeriCorps members will be provided "
                    "opportunities for skill attainment, personal growth, "
                    "and connection to the community they are serving in "
                    "support of a lifetime of civic participation."),
            criterion_id="program_design.member_experience",
            locator="NOFO E.1.b.4, p.21"),
        SolicitationRequirement(
            requirement_id="req.org_background_staffing",
            section_id="organizational_capability",
            title="Organizational Background and Staffing",
            prompt=("Describe the roles, responsibilities, and structure of "
                    "the staff that will implement and provide oversight of "
                    "the program, including demonstrating the organization "
                    "has sufficient policies, procedures, and controls to "
                    "effectively implement a federal grant."),
            criterion_id="org_capability.background_staffing",
            required_evidence=("staff_structure", "financial_controls"),
            locator="NOFO E.1.c.1, p.21"),
        SolicitationRequirement(
            requirement_id="req.member_supervision",
            section_id="organizational_capability",
            title="Member Supervision",
            prompt=("Describe how AmeriCorps members will receive sufficient "
                    "guidance and support from their supervisor to provide "
                    "effective service, including structure for member "
                    "supervision: cadence and format of supervisor/member "
                    "check-ins, member and supervisor opportunities to "
                    "assess strengths and opportunities for growth, member "
                    "training plan."),
            criterion_id="org_capability.member_supervision",
            locator="NOFO E.1.c.2, p.21"),
        SolicitationRequirement(
            requirement_id="req.member_recruitment",
            section_id="cost_effectiveness",
            title="Member Recruitment",
            prompt=("Provide a description of budget expenses to support "
                    "recruitment of AmeriCorps members best suited to serve "
                    "the community."),
            criterion_id="cost_effect.recruitment",
            locator="NOFO E.1.d.1, p.22"),
        SolicitationRequirement(
            requirement_id="req.member_retention",
            section_id="cost_effectiveness",
            title="Member Retention",
            prompt=("Provide a description of budget expenses to support "
                    "retention of AmeriCorps members, e.g., additional "
                    "member benefits such as paying above the minimum living "
                    "allowance, supporting workforce pathways, "
                    "certifications, coaching, resume building, community "
                    "building, member recognition, alumni programming."),
            criterion_id="cost_effect.retention",
            locator="NOFO E.1.d.2, p.22"),
        SolicitationRequirement(
            requirement_id="req.data_collection",
            section_id="cost_effectiveness",
            title="Data Collection",
            prompt=("Provide a description of budget expenses that support "
                    "data collection and evaluation, including the process "
                    "for collecting and maintaining high-quality performance "
                    "data from your organization and community partners, how "
                    "data will be analyzed, and how this ensures timely and "
                    "accurate reporting to AmeriCorps."),
            criterion_id="cost_effect.data_collection",
            locator="NOFO E.1.d.3, p.22"),
        SolicitationRequirement(
            requirement_id="req.budget_adequacy",
            section_id="cost_effectiveness",
            title="Budget Adequacy",
            prompt=("Provide a detailed budget narrative of all the expenses "
                    "that will support the program (see NOFO H.1.a Budget "
                    "Preparation)."),
            criterion_id="cost_effect.budget_adequacy",
            required_evidence=("budget_line_items",),
            locator="NOFO E.1.d.4, p.22"),
        SolicitationRequirement(
            requirement_id="req.evaluation_summary",
            section_id="evaluation_summary",
            title="Evaluation Summary/Plan",
            prompt=("New applicants enter N/A in the Evaluation Summary or "
                    "Plan field. Required only for recompeting applicants "
                    "with three or more years of prior competitive funding "
                    "for the same project."),
            required=False,
            response_type="na",
            locator="NOFO E.1.e, p.22"),
    ),
    criteria=(
        ScoringCriterion("exec_summary", "Executive Summary", 0,
                         reviewer_looks_for="Exact fixed template, blanks filled",
                         requirement_ids=("req.exec_summary",)),
        ScoringCriterion("program_design", "Program Design", 50),
        ScoringCriterion("program_design.community_logic_model",
                         "Community and Logic Model", 20,
                         parent_id="program_design",
                         reviewer_looks_for=("Detailed community problem, "
                             "complete logic model inputs/activities/outputs/"
                             "outcomes with dosage and target population"),
                         requirement_ids=("req.community_logic_model",)),
        ScoringCriterion("program_design.evidence_tier", "Evidence Base", 20,
                         parent_id="program_design",
                         reviewer_looks_for=("Matched intervention, study "
                             "design summary, citations, tier qualification"),
                         requirement_ids=("req.evidence_base",)),
        ScoringCriterion("program_design.notice_priority", "Notice Priority", 4,
                         parent_id="program_design",
                         reviewer_looks_for="Georgia Serves priority alignment",
                         requirement_ids=("req.notice_priority",)),
        ScoringCriterion("program_design.member_experience",
                         "Member Experience", 6,
                         parent_id="program_design",
                         reviewer_looks_for=("Skill attainment, personal "
                             "growth, civic connection"),
                         requirement_ids=("req.member_experience",)),
        ScoringCriterion("org_capability", "Organizational Capability", 25),
        ScoringCriterion("org_capability.background_staffing",
                         "Organizational Background and Staffing", 15,
                         parent_id="org_capability",
                         reviewer_looks_for=("Staff roles/structure, federal "
                             "grant controls and policies"),
                         requirement_ids=("req.org_background_staffing",)),
        ScoringCriterion("org_capability.member_supervision",
                         "Member Supervision", 10,
                         parent_id="org_capability",
                         reviewer_looks_for=("Supervision structure, cadence, "
                             "training plan"),
                         requirement_ids=("req.member_supervision",)),
        ScoringCriterion("cost_effect",
                         "Cost-Effectiveness and Budget Adequacy", 25),
        ScoringCriterion("cost_effect.recruitment", "Member Recruitment", 5,
                         parent_id="cost_effect",
                         reviewer_looks_for="Recruitment budget expenses",
                         requirement_ids=("req.member_recruitment",)),
        ScoringCriterion("cost_effect.retention", "Member Retention", 5,
                         parent_id="cost_effect",
                         reviewer_looks_for="Retention budget expenses",
                         requirement_ids=("req.member_retention",)),
        ScoringCriterion("cost_effect.data_collection", "Data Collection", 5,
                         parent_id="cost_effect",
                         reviewer_looks_for="Data systems budget + process",
                         requirement_ids=("req.data_collection",)),
        ScoringCriterion("cost_effect.budget_adequacy", "Budget Adequacy", 10,
                         parent_id="cost_effect",
                         reviewer_looks_for="Detailed budget narrative",
                         requirement_ids=("req.budget_adequacy",)),
    ),
    required_attachments=(
        ("sf424", "Standard Form 424 FACE Sheet"),
        ("sf424a", "Standard Form 424A Budget"),
        ("logic_model", "Logic Model (max 8 pages)"),
        ("performance_measures", "Performance Measures"),
        ("continuation_changes", "Continuation Changes"),
        ("clarification", "Clarification"),
        ("certifications", "Authorization, Assurances, and Certifications"),
    ),
)


# --- Blueprint construction from a solicitation ------------------------------


def _section_points(profile: SolicitationProfile) -> dict[str, int]:
    """Aggregate scored points per blueprint section_id via requirements
    (keeps section ids and criteria names decoupled)."""
    pts_by_crit = {c.criterion_id: c.points for c in profile.criteria}
    by_section: dict[str, int] = {}
    for r in profile.requirements:
        if r.criterion_id and r.response_type != "na":
            by_section[r.section_id] = (by_section.get(r.section_id, 0)
                                        + pts_by_crit.get(r.criterion_id, 0))
    return by_section


def _words_for_points(total_words: int, profile: SolicitationProfile,
                      section_id: str, section_points: dict[str, int]) -> int:
    """Distribute the narrative word budget across scored sections in
    proportion to scoring weight (mission §14 — depth proportional to
    scoring importance, never padding)."""
    total_pts = sum(p for p in section_points.values() if p > 0) or 1
    share = max(0, section_points.get(section_id, 0)) / total_pts
    return max(150, round(total_words * share))


def build_blueprint_from_solicitation(
        profile: SolicitationProfile,
        *,
        total_narrative_words: int | None = None,
) -> "ApplicationBlueprint":
    """Build an ApplicationBlueprint whose sections, prompts, drafting
    notes, and word budgets derive from the decomposed solicitation.

    11 double-spaced pages ≈ 275 words/page ≈ 3,025 words; the caller may
    override the total budget.
    """
    from grant_platform.factory.blueprint import (
        ApplicationBlueprint, BlueprintSection)

    total = total_narrative_words or (
        (profile.narrative_page_limit or 11) * 275)

    # Group requirements by section, keep solicitation order
    section_reqs: dict[str, list[SolicitationRequirement]] = {}
    for r in profile.requirements:
        section_reqs.setdefault(r.section_id, []).append(r)

    sections: list[BlueprintSection] = []
    section_points = _section_points(profile)
    for sec_id, reqs in section_reqs.items():
        # Exact funder prompts become the section body instructions
        prompts = "\n\n".join(f"[{r.title}] {r.prompt}" for r in reqs)
        scored = section_points.get(sec_id, 0) > 0
        is_template = any(r.response_type == "template" for r in reqs)
        if scored:
            word_budget = _words_for_points(total, profile, sec_id,
                                            section_points)
        elif is_template:
            # Fixed funder templates (e.g. the AmeriCorps fill-in-the-blank
            # summary) run ~180-200 words when completed — the limit is
            # template-based, not share-based.
            word_budget = 200
        else:
            word_budget = 40
        sections.append(BlueprintSection(
            section_id=sec_id,
            title=reqs[0].title if len(reqs) == 1 else
            " & ".join(r.title for r in reqs),
            word_limit=word_budget,
            drafting_notes=prompts))

    first_req = profile.requirements[0]
    bp = ApplicationBlueprint(
        blueprint_id=f"bp-{profile.snapshot.source_id}",
        opportunity_revision_id=profile.snapshot.source_id,
        deadline=profile.deadline,
        funding_ceiling=profile.funding_ceiling or "0.00",
        # Terminology that MUST appear in narrative prose. Full commission
        # names and deadlines are provenance — enforced by their own gates,
        # not as prose terminology (G1-QUALITY-02).
        required_terminology=("AmeriCorps",),
        required_attachments=profile.required_attachments,
        sections=tuple(sections))
    # Attach the full profile for downstream planning/evidence work
    object.__setattr__(bp, "solicitation", profile)
    return bp


def coverage_matrix(draft_sections: dict, profile: SolicitationProfile
                    ) -> list[dict]:
    """Requirement coverage matrix (mission §16): for every requirement,
    is it covered in the draft, where, and how well."""
    matrix = []
    for r in profile.requirements:
        if r.response_type == "na":
            matrix.append({"requirement_id": r.requirement_id,
                           "title": r.title, "covered": True,
                           "status": "NOT_APPLICABLE",
                           "note": "N/A per NOFO for new applicants"})
            continue
        sec = draft_sections.get(r.section_id)
        if r.response_type == "template":
            # Fixed-form requirements (e.g. AmeriCorps exec summary) are
            # covered when their section exists with substantive content;
            # keyword matching against the template's own name is meaningless.
            covered = sec is not None and sec.word_count >= 60
        else:
            # Stem-tolerant keyword coverage: 'staffing' matches 'staff',
            # 'organizational' matches 'organization'.
            title_words = [w.lower() for w in r.title.split() if len(w) > 4]
            text = (sec.text.lower() if sec else "")
            hits = sum(1 for w in title_words
                       if w in text or text.count(w[:5]) > 0)
            covered = sec is not None and hits >= max(1, len(title_words) // 3)
        matrix.append({
            "requirement_id": r.requirement_id,
            "title": r.title,
            "section": r.section_id,
            "criterion": r.criterion_id,
            "points": next((c.points for c in profile.criteria
                            if c.criterion_id == r.criterion_id), 0),
            "covered": covered,
            "status": ("COVERED" if covered else "MISSING"),
            "locator": r.locator,
        })
    return matrix
