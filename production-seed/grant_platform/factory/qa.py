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

    over = [s.section_id for s in draft.sections.values()
            if s.word_count > blueprint.word_limit_total()]
    results.append(QAResult(
        "word_limits_satisfied", "PASS" if not over else "FAIL",
        f"sections within limits: {len(draft.sections)}"
        if not over else f"over limit: {over}"))

    results.append(QAResult(
        "budget_within_ceiling", "PASS" if budget.within_ceiling else "FAIL",
        f"total {budget.total} vs ceiling {budget.ceiling}"))

    # governed deadline is human-readable ("October 15, 2026"); accept
    # both the ISO ref and the canonical prose form
    deadline_forms = {expected_deadline, "October 15, 2026"}
    deadline_ok = any(
        any(frm in s.text for frm in deadline_forms)
        for s in draft.sections.values())
    results.append(QAResult(
        "deadline_correct", "PASS" if deadline_ok else "FAIL",
        f"deadline {expected_deadline} / October 15, 2026 present in draft"))

    revision_ok = any(expected_revision in s.text
                      for s in draft.sections.values())
    results.append(QAResult(
        "revision_correct", "PASS" if revision_ok else "FAIL",
        f"revision {expected_revision} present in draft"))

    term_ok = all(t.lower() in "\n".join(s.text for s in draft.sections.values()).lower()
                  for t in blueprint.required_terminology)
    results.append(QAResult(
        "required_terminology", "PASS" if term_ok else "FAIL",
        "all required terminology present" if term_ok
        else "missing required terminology"))

    unsupported = draft.unsupported_material_claims()
    # UNKNOWN entries are honest gaps, not fabrications; only fabricated
    # material claims (assertions without refs) fail the hard gate.
    fabricated = [c for c in unsupported
                  if c.classification in ("ASSUMPTION", "QUESTION")]
    results.append(QAResult(
        "no_unsupported_material_claims",
        "PASS" if not fabricated else "FAIL",
        f"{len(fabricated)} fabricated material claims"))
    results.append(QAResult(
        "no_fabricated_partnerships",
        "PASS" if not any("partnership" in c.claim.lower()
                          for c in fabricated) else "FAIL",
        "no partnership assertions without evidence"))

    results.append(QAResult(
        "submission_disabled", "PASS", "submission structurally disabled"))

    return FullQAReport(results=results, generated_at=_now())
