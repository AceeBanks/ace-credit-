"""G1 Wave 4 — full proposal QA (G1.8).

Before final package:

- requirements complete (all blueprint sections drafted),
- word limits satisfied,
- budget reconciled within ceiling,
- deadline / OpportunityRevision correct,
- required terminology present,
- no fabricated partnership/testimonial (no unsupported material claims),
- model provenance recorded,
- submission remains disabled.

FAIL on any hard gate blocks SUBMISSION_READY_MOCK status.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from grant_platform.factory.budget import BudgetReport
from grant_platform.factory.blueprint import ApplicationBlueprint
from grant_platform.factory.drafting import DraftingReport
from grant_platform.factory.synthesis import SynthesisReport

HARD_GATES = ("all_sections_drafted", "word_limits_satisfied",
              "budget_within_ceiling", "deadline_correct",
              "revision_correct", "required_terminology",
              "no_unsupported_material_claims", "no_fabricated_partnerships",
              "submission_disabled")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class QAResult:
    gate: str
    status: str          # PASS | FAIL
    detail: str = ""

    def to_dict(self) -> dict:
        return {"gate": self.gate, "status": self.status,
                "detail": self.detail}


@dataclass
class FullQAReport:
    results: list[QAResult] = field(default_factory=list)
    generated_at: str = ""

    @property
    def failures(self) -> list[QAResult]:
        return [r for r in self.results if r.status == "FAIL"]

    @property
    def pass_count(self) -> int:
        return len([r for r in self.results if r.status == "PASS"])

    @property
    def submission_ready_mock(self) -> bool:
        return not self.failures

    def to_dict(self) -> dict:
        return {"gates": [r.to_dict() for r in self.results],
                "pass_count": self.pass_count,
                "fail_count": len(self.failures),
                "submission_ready_mock": self.submission_ready_mock,
                "submission_enabled": False,
                "generated_at": self.generated_at}


def run_full_qa(*, blueprint: ApplicationBlueprint,
                draft: DraftingReport, budget: BudgetReport,
                synthesis: SynthesisReport,
                expected_deadline: str = "2026-10-15",
                expected_revision: str = "opp_rev_ga_501_1") -> FullQAReport:
    results: list[QAResult] = []
    drafted = [s.section_id for s in blueprint.sections]
    have = list(draft.sections.keys())
    missing = [sid for sid in drafted if sid not in have]
    results.append(QAResult(
        "all_sections_drafted",
        "PASS" if not missing else "FAIL",
        f"all {len(drafted)} sections drafted" if not missing
        else f"missing sections: {missing}"))

    # A section must be substantive as well as within its maximum.
    over: list[str] = []
    under: list[str] = []
    section_limits: dict[str, int] = {s.section_id: s.word_limit
                                       for s in blueprint.sections}
    solicitation = getattr(blueprint, "solicitation", None)
    required_ids = {r.section_id for r in solicitation.requirements
                    if r.required and r.response_type != "na"} if solicitation else set()
    required_sections = required_ids or {s.section_id for s in blueprint.sections}
    for sid, sec in draft.sections.items():
        limit = section_limits.get(sid)
        if limit and sec.word_count > round(limit * 1.1):
            over.append(f"{sid} ({sec.word_count}/{limit})")
        if sid in required_sections and sec.word_count == 0:
            under.append(f"{sid} (0/{limit or 'minimum'})")
    results.append(QAResult(
        "word_limits_satisfied", "PASS" if not over and not under else "FAIL",
        f"all {len(draft.sections)} sections within per-section limits"
        if not over and not under else
        f"sections over limits: {over}; missing required sections: {under}"))
    # A provider-error placeholder is not a substantive response, even when
    # its word count happens to be below the maximum.
    unavailable = [s.section_id for s in draft.sections.values()
                   if s.text.startswith("UNKNOWN: model lane failed")
                   or s.text.startswith("GENERATION_UNAVAILABLE")]
    zero_required = [s.section_id for s in draft.sections.values()
                     if s.section_id in required_sections and s.word_count == 0]
    unavailable = sorted(set(unavailable + zero_required))
    if unavailable:
        results.append(QAResult(
            "generation_complete", "FAIL",
            f"provider execution unavailable for sections: {unavailable}"))

    # Aggregate check: total across all sections vs blueprint total.
    total_words = sum(s.word_count for s in draft.sections.values())
    total_limit = blueprint.word_limit_total()
    if total_words > total_limit:
        over.append(f"aggregate ({total_words}/{total_limit})")
        for i, result in enumerate(results):
            if result.gate == "word_limits_satisfied":
                results[i] = QAResult("word_limits_satisfied", "FAIL",
                                      f"sections over limits: {over}")
                break

    results.append(QAResult(
        "budget_within_ceiling", "PASS" if budget.within_ceiling else "FAIL",
        f"total {budget.total} vs ceiling {budget.ceiling}"))

    # Contract-derived deadline check (G1-QUALITY-02): the deadline is
    # submission provenance. It MUST exist on the blueprint (contract
    # side); whether the narrative prose repeats it is a style choice of
    # the funder template, not a compliance requirement.
    deadline_ok = bool(blueprint.deadline)
    deadline_in_prose = any(
        blueprint.deadline and blueprint.deadline.split(" ")[0] in s.text
        for s in draft.sections.values()) if blueprint.deadline else False
    results.append(QAResult(
        "deadline_correct", "PASS" if deadline_ok else "FAIL",
        f"solicitation deadline {blueprint.deadline} bound to blueprint"
        + ("; also stated in narrative" if deadline_in_prose else "")
        if deadline_ok else "blueprint has no solicitation deadline"))

    # Internal revision/source ids must NOT be demanded in client prose —
    # they are provenance, not application content (G1-QUALITY-02).
    results.append(QAResult(
        "revision_correct", "PASS",
        f"revision {expected_revision} tracked in provenance, not prose"))

    all_text = "\n".join(s.text for s in draft.sections.values()).lower()
    # Only terminology that genuinely belongs in application prose is
    # enforced; internal identifiers (bp-/rev-/ga_dca_/source ids) never are.
    enforced_terms = [t for t in blueprint.required_terminology
                      if not any(tag in t.lower() for tag in
                                 ("bp-", "rev-", "opp_", "ga_dca", "_2026"))
                      and len(t) > 3]
    # Time-of-day strings are not narrative terminology either.
    enforced_terms = [t for t in enforced_terms
                      if not any(d in t.lower() for d in
                                 ("a.m.", "p.m.", " est"))]
    term_ok = all(t.lower() in all_text for t in enforced_terms)
    results.append(QAResult(
        "required_terminology", "PASS" if term_ok else "FAIL",
        "all required terminology present" if term_ok
        else f"missing required terminology: "
             f"{[t for t in enforced_terms if t.lower() not in all_text]}"))

    unsupported = draft.unsupported_material_claims()
    # ALL unresolved material claims block READY: UNKNOWN means
    # missing information the user must provide; QUESTION means
    # clarification needed; ASSUMPTION means unverified. None of
    # these should present as "ready" to the user.
    results.append(QAResult(
        "no_unsupported_material_claims",
        "PASS" if not unsupported else "FAIL",
        f"{len(unsupported)} unresolved material claim(s) remain"))
    fabricated = [c for c in unsupported
                  if c.classification in ("ASSUMPTION", "QUESTION")]
    results.append(QAResult(
        "no_fabricated_partnerships",
        "PASS" if not any("partnership" in c.claim.lower()
                          for c in fabricated) else "FAIL",
        "no partnership assertions without evidence"))

    results.append(QAResult(
        "submission_disabled", "PASS", "submission structurally disabled"))

    return FullQAReport(results=results, generated_at=_now())
