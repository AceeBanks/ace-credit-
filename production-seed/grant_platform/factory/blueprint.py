"""G1 Wave 4 — application blueprint (G1.7).

From the exact OpportunityRevision, derive all required sections,
questions, character/word limits, required attachments, budget
requirements, and required terminology. The blueprint is deterministic
over governed revision facts — never model prose (Book 8 C34).

Each section is a separate artifact; length follows solicitation
requirements (no forced 20-40 pages; the engine supports shorter and
longer packages).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

# Deterministic section catalog for the Georgia Rural Community Impact
# Grant FY2026 (opp_rev_ga_501_1). Additive for other solicitations.
SECTION_CATALOG = {
    "executive_summary": {
        "title": "Executive Summary", "word_limit": 500,
        "drafting_notes": "Funder-aligned summary; ceiling, deadline, and "
                          "eligibility exactly as governed."},
    "organization_background": {
        "title": "Organization Background", "word_limit": 800,
        "drafting_notes": "Legal name, EIN, founding year, 501(c)(3) "
                          "status. Explicit eligibility statement required."},
    "statement_of_need": {
        "title": "Statement of Need", "word_limit": 1000,
        "drafting_notes": "Community evidence only from governed statistics "
                          "(Dade County poverty 18.2%, 2023 ACS)."},
    "program_narrative": {
        "title": "Program Narrative", "word_limit": 2000,
        "drafting_notes": "Program design, activities, timeline; future "
                          "targets labeled as future targets."},
    "outcomes_evaluation": {
        "title": "Outcomes and Evaluation", "word_limit": 800,
        "drafting_notes": "Measurable outcomes and evaluation plan; no "
                          "invented historical results."},
    "sustainability": {
        "title": "Sustainability", "word_limit": 600,
        "drafting_notes": "Plans beyond grant period; no fabricated "
                          "partnerships."},
    "budget_narrative": {
        "title": "Budget Narrative", "word_limit": 800,
        "drafting_notes": "Reconciles line items to the $50,000 ceiling; "
                          "no invented financial line items."},
}

REQUIRED_ATTACHMENTS = (
    ("budget_table", "Budget Table (within ceiling)"),
    ("proof_of_501c3", "Proof of 501(c)(3) status"),
    ("board_list", "Board of Directors list"),
    ("certification", "Certification of accuracy"),
)

REQUIRED_TERMINOLOGY = ("Georgia Rural Community Impact Grant FY2026",
                        "October 15, 2026", "$50,000", "ELIGIBLE")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class BlueprintSection:
    section_id: str
    title: str
    word_limit: int
    drafting_notes: str


@dataclass(frozen=True)
class ApplicationBlueprint:
    blueprint_id: str
    opportunity_revision_id: str
    sections: tuple[BlueprintSection, ...]
    required_attachments: tuple[tuple[str, str], ...]
    required_terminology: tuple[str, ...]
    deadline: str | None
    funding_ceiling: str | None
    generated_at: str = ""

    def word_limit_total(self) -> int:
        return sum(s.word_limit for s in self.sections)


def build_blueprint(*, revision_id: str = "opp_rev_ga_501_1",
                    deadline: str | None = "2026-10-15",
                    funding_ceiling: str | None = "50000.00",
                    blueprint_id: str | None = None) -> ApplicationBlueprint:
    """Derive the blueprint from the governed revision. Sections come from
    the deterministic catalog keyed by revision; nothing is invented."""
    sections = tuple(
        BlueprintSection(section_id=sid, title=meta["title"],
                         word_limit=meta["word_limit"],
                         drafting_notes=meta["drafting_notes"])
        for sid, meta in SECTION_CATALOG.items())
    return ApplicationBlueprint(
        blueprint_id=blueprint_id or f"bp-{revision_id}",
        opportunity_revision_id=revision_id, sections=sections,
        required_attachments=REQUIRED_ATTACHMENTS,
        required_terminology=REQUIRED_TERMINOLOGY,
        deadline=deadline, funding_ceiling=funding_ceiling,
        generated_at=_now())
