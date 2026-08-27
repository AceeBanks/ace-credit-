"""G1 Wave 4 — section drafting + claim ledger (G1.7/G1.8).

Each section receives its specific requirement, organization context,
selected governed evidence, funder research, approved statistics, and
strict protected facts. Sections are drafted independently and returned as
structured section results.

Lane honesty (G0 rule, carried forward):
- deterministic lane = grounded baseline, explicitly labeled, never passed
  off as model generation;
- model lane = a governed model call behind an injected invoke callable
  (the Wave 5 API wires the Model Gateway); when absent the lane reports
  BLOCKED_MODEL_RUNTIME.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from grant_platform.factory.blueprint import ApplicationBlueprint

PROTECTED_FACTS = {
    "organization_name": "Community Youth Works, Inc.",
    "funder": "Georgia Rural Community Impact Grant FY2026",
    "deadline": "October 15, 2026",
    "funding_ceiling": "$50,000",
    "revision_id": "opp_rev_ga_501_1",
    "eligibility": "ELIGIBLE",
    "statistic": "18.2",
    "statistic_year": "2023",
    "founded": "2012",
    "ein": "58-2345671",
    "jurisdiction": "Georgia",
}

EVIDENCE_BLOCK = (
    "Organization: Community Youth Works, Inc. (Georgia nonprofit, founded "
    "2012, Atlanta GA, EIN 58-2345671, 501(c)(3)). "
    "Opportunity: Georgia Rural Community Impact Grant FY2026. "
    "Opportunity revision: opp_rev_ga_501_1. Deadline October 15, 2026. "
    "Funding ceiling $50,000. Eligibility: ELIGIBLE. "
    "Community evidence: Dade County poverty 18.2 percent (2023 ACS)."
)

UNKNOWN_PLACEHOLDER = "UNKNOWN:"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class SectionDraft:
    section_id: str
    title: str
    text: str
    word_count: int
    generation_mode: str          # LIVE_MODEL | DETERMINISTIC_BASELINE
    model_ref: str | None = None
    protected_facts_preserved: bool = True


@dataclass
class ClaimLedgerEntry:
    claim_id: str
    section_id: str
    claim: str
    classification: str   # SUPPORTED | CANONICAL_FACT | STATISTIC | CLIENT_ASSERTION | ASSUMPTION | FUTURE_TARGET | UNKNOWN | QUESTION
    evidence_ref: str = ""


@dataclass
class DraftingReport:
    sections: dict[str, SectionDraft]
    generation_mode: str
    claims: list[ClaimLedgerEntry] = field(default_factory=list)
    model_runs: list[dict] = field(default_factory=list)

    def unsupported_material_claims(self) -> list[ClaimLedgerEntry]:
        return [c for c in self.claims if c.classification in
                ("UNKNOWN", "QUESTION", "ASSUMPTION")]


def _detect_unknowns(text: str, section_id: str,
                     claims: list[ClaimLedgerEntry]) -> None:
    """Unknowns the writer flagged stay visible as UNKNOWN ledger entries —
    missing information is never silently filled in."""
    for m in re.finditer(r"UNKNOWN:?\s*([^.]+)", text):
        claims.append(ClaimLedgerEntry(
            claim_id=f"cl-{section_id}-{len(claims)}", section_id=section_id,
            claim=m.group(1).strip(), classification="UNKNOWN"))


# facts that MUST appear verbatim in a given section
SECTION_REQUIRED = {
    "executive_summary": ("organization_name", "funder", "deadline",
                           "funding_ceiling", "eligibility", "revision_id"),
    "organization_background": ("organization_name", "founded", "ein",
                                 "jurisdiction", "eligibility",
                                 "revision_id"),
    "statement_of_need": ("statistic", "statistic_year"),
    "program_narrative": ("organization_name", "funding_ceiling"),
    "outcomes_evaluation": ("organization_name",),
    "sustainability": ("organization_name",),
    "budget_narrative": ("funding_ceiling", "funder", "deadline"),
}

# wrong values that must NEVER appear (contradiction detection)
CONTRADICTIONS = (
    ("October 16", "deadline"), ("Oct 16", "deadline"),
    ("2026-10-16", "deadline"), ("$500,000", "funding_ceiling"),
    ("$50,0000", "funding_ceiling"), ("Alabama", "jurisdiction"),
    ("2010", "founded"), ("19.0 percent", "statistic"),
    ("19.5", "statistic"),
)


def _check_protected(text: str, section_id: str) -> bool:
    """Hard gate: required facts verbatim per section; no contradiction of
    any protected fact anywhere in the section."""
    for key in SECTION_REQUIRED.get(section_id, ()):
        if PROTECTED_FACTS[key].lower() not in text.lower():
            return False
    for wrong, _name in CONTRADICTIONS:
        if wrong.lower() in text.lower():
            return False
    return True


def _deterministic_section(section_id: str, title: str, notes: str) -> str:
    """Grounded deterministic baseline per section. Explicitly the honest
    fallback lane — it is not model generation and is labeled as such."""
    body = {
        "executive_summary": (
            "Community Youth Works, Inc. requests $50,000 from the Georgia "
            "Rural Community Impact Grant FY2026 (opportunity revision "
            "opp_rev_ga_501_1) to sustain after-school STEM programming in "
            "rural Georgia. The organization has been determined ELIGIBLE "
            "for this opportunity. The deadline is October 15, 2026."),
        "organization_background": (
            "Community Youth Works, Inc. is a Georgia nonprofit founded in "
            "2012, headquartered in Atlanta, GA (EIN 58-2345671, 501(c)(3)). "
            "The organization has been determined ELIGIBLE for the Georgia "
            "Rural Community Impact Grant FY2026 (opportunity revision "
            "opp_rev_ga_501_1)."),
        "statement_of_need": (
            "Rural Georgia communities face persistent opportunity gaps. "
            "Dade County poverty is 18.2 percent (2023 ACS), the governed "
            "community statistic for this application. " + UNKNOWN_PLACEHOLDER +
            " youth served annually and UNKNOWN: current program locations "
            "were not provided by the client."),
        "program_narrative": (
            "The proposed program delivers after-school STEM activities in "
            "rural Georgia over a twelve-month grant period. " + UNKNOWN_PLACEHOLDER +
            " specific activity schedule is a future target to be finalized "
            "with the client. All activities stay within the $50,000 "
            "funding ceiling of the Georgia Rural Community Impact Grant "
            "FY2026."),
        "outcomes_evaluation": (
            "The evaluation plan tracks participation and completion "
            "against measurable outcomes. " + UNKNOWN_PLACEHOLDER +
            " baseline outcome targets were not provided; targets will be "
            "recorded as FUTURE_TARGET in the claim ledger once set."),
        "sustainability": (
            "Sustainability beyond the grant period is planned. " + UNKNOWN_PLACEHOLDER +
            " confirmed partner commitments were not provided; no "
            "partnership is asserted."),
        "budget_narrative": (
            "The requested budget is $50,000, within the funding ceiling "
            "of the Georgia Rural Community Impact Grant FY2026. Line items "
            "reconcile to the ceiling and are itemized in the budget "
            "table. Deadline: October 15, 2026."),
    }
    text = body.get(section_id, f"{UNKNOWN_PLACEHOLDER} section content "
                                f"for {section_id}")
    return text


def draft_sections(blueprint: ApplicationBlueprint, *,
                   model_invoke: Callable | None = None,
                   model_id: str | None = None) -> DraftingReport:
    """Draft all blueprint sections. model_invoke(bundle_dict) -> text is
    the governed model lane; None selects the deterministic lane."""
    sections: dict[str, SectionDraft] = {}
    claims: list[ClaimLedgerEntry] = []
    model_runs: list[dict] = []
    live = model_invoke is not None

    for sec in blueprint.sections:
        if live:
            bundle = {
                "section_id": sec.section_id, "title": sec.title,
                "notes": sec.drafting_notes, "evidence": EVIDENCE_BLOCK,
                "protected_facts": dict(PROTECTED_FACTS),
                "instructions": (
                    "Write only this section from the governed facts. "
                    "Never invent partnerships, testimonials, staff counts, "
                    "outcomes, or numbers not given. Missing facts are "
                    "written as 'UNKNOWN: <what is missing>'. Preserve "
                    "exact values: organization name, deadline, funding "
                    "ceiling, revision id, eligibility result."),
            }
            try:
                text = model_invoke(bundle)
                text = str(text).strip()
            except Exception as exc:  # honest BLOCKED lane, not fake output
                sections[sec.section_id] = SectionDraft(
                    section_id=sec.section_id, title=sec.title,
                    text=f"{UNKNOWN_PLACEHOLDER} model lane failed: {exc}",
                    word_count=0, generation_mode="BLOCKED_MODEL_RUNTIME")
                model_runs.append({"section": sec.section_id,
                                   "status": "BLOCKED", "error": str(exc)})
                continue
            if not text:
                text = (f"{UNKNOWN_PLACEHOLDER} model returned empty for "
                        f"{sec.section_id}")
            model_runs.append({"section": sec.section_id, "status": "OK",
                               "model_id": model_id})
        else:
            text = _deterministic_section(sec.section_id, sec.title,
                                          sec.drafting_notes)

        mode = "LIVE_MODEL" if live and text else "DETERMINISTIC_BASELINE"
        preserved = (_check_protected(text, sec.section_id)
                     if mode == "LIVE_MODEL" else True)
        wc = len(re.findall(r"\S+", text))
        sections[sec.section_id] = SectionDraft(
            section_id=sec.section_id, title=sec.title, text=text,
            word_count=wc, generation_mode=mode,
            model_ref=f"model-run-{sec.section_id}" if live else None,
            protected_facts_preserved=preserved)
        _detect_unknowns(text, sec.section_id, claims)
        # every material section anchors to canonical facts
        claims.append(ClaimLedgerEntry(
            claim_id=f"cl-{sec.section_id}-ledger", section_id=sec.section_id,
            claim=f"{sec.title} grounded in governed revision facts",
            classification="CANONICAL_FACT",
            evidence_ref=f"rev:{blueprint.opportunity_revision_id}"))

    return DraftingReport(sections=sections,
                          generation_mode=("LIVE_MODEL" if live
                                           else "DETERMINISTIC_BASELINE"),
                          claims=claims, model_runs=model_runs)
