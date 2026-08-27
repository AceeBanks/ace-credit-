"""G0-B7-C7 — Deterministic assertion engine.

EVAL-LAW-004: where correctness can be tested deterministically, use
deterministic evaluation. Every check returns a structured PASS/FAIL with a
reason code. Hard failures (deadline, funding amount, revision identity,
budget reconciliation, protected facts, submission capability) are never
overridable by subjective scores.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any


class AssertionResult:
    def __init__(self, check_id: str, passed: bool, detail: str = ""):
        self.check_id = check_id
        self.passed = passed
        self.detail = detail

    def to_dict(self) -> dict:
        return {"check_id": self.check_id, "passed": self.passed,
                "detail": self.detail}


def _to_decimal(value) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def check_required_sections_present(*, sections: dict, required: list[str],
                                    check_id: str = "req_sections") -> AssertionResult:
    missing = [r for r in required if r not in sections or not sections[r]]
    return AssertionResult(check_id, not missing,
                           f"missing: {missing}" if missing else "")


def check_word_limit(*, text: str, limit: int,
                     check_id: str = "word_limit") -> AssertionResult:
    words = len(re.findall(r"\S+", text))
    return AssertionResult(check_id, words <= limit,
                           f"{words} words (limit {limit})")


def check_deadline_consistency(*, draft_deadline: str,
                               expected_deadline: str,
                               check_id: str = "deadline") -> AssertionResult:
    return AssertionResult(
        check_id, draft_deadline == expected_deadline,
        f"draft={draft_deadline!r} expected={expected_deadline!r}")


def check_funding_amount(*, draft_amount: Decimal | str,
                         ceiling: Decimal | str,
                         check_id: str = "funding_amount") -> AssertionResult:
    a, c = _to_decimal(draft_amount), _to_decimal(ceiling)
    if a is None or c is None:
        return AssertionResult(check_id, False, "non-numeric amount/ceiling")
    return AssertionResult(check_id, a <= c,
                           f"draft={a} ceiling={c}")


def check_revision_identity(*, draft_revision_id: str, expected_revision_id: str,
                            check_id: str = "revision_identity") -> AssertionResult:
    return AssertionResult(
        check_id, draft_revision_id == expected_revision_id,
        f"draft={draft_revision_id!r} expected={expected_revision_id!r}")


def check_budget_reconciles(*, lines_total: Decimal | str,
                            declared_total: Decimal | str,
                            check_id: str = "budget_reconcile") -> AssertionResult:
    a, b = _to_decimal(lines_total), _to_decimal(declared_total)
    if a is None or b is None:
        return AssertionResult(check_id, False, "non-numeric budget value")
    return AssertionResult(check_id, a == b,
                           f"lines={a} declared={b}")


def _protected_aliases(value) -> list[str]:
    """A protected value may be a single string or a list of aliases
    (e.g. ISO date and prose form); any alias present in the original must
    survive the transform."""
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def check_protected_facts_unchanged(*, original_text: str, new_text: str,
                                    protected: dict[str, str | list[str]],
                                    check_id: str = "protected_facts") -> AssertionResult:
    """HZR-007: diff protected facts (names, dates, amounts, statistics,
    citations, deadlines, ceilings) between the original and the transformed
    artifact. Every protected alias present in the original must remain
    present and unchanged in the new text; a value the original carried can
    never be altered or dropped by a style transform."""
    changed = []
    for key, value in protected.items():
        for alias in _protected_aliases(value):
            if alias in original_text and alias not in new_text:
                changed.append(key)
                break
    return AssertionResult(check_id, not changed,
                           f"changed/dropped: {changed}" if changed else "")


def check_no_unsupported_fabrications(*, draft_text: str,
                                      fabrication_markers: tuple[str, ...],
                                      check_id: str = "fabrications") -> AssertionResult:
    """C7-15: forbidden fabrication absence — no invented testimonial,
    partnership, past performance, or historical outcome."""
    lowered = draft_text.lower()
    hits = [m for m in fabrication_markers if m in lowered]
    return AssertionResult(check_id, not hits,
                           f"fabrication markers: {hits}" if hits else "")


def check_eligibility_statement(*, draft_text: str,
                                expected_result: str,
                                check_id: str = "eligibility") -> AssertionResult:
    """The draft must not contradict the deterministic eligibility result."""
    lowered = draft_text.lower()
    if expected_result == "INELIGIBLE":
        ok = "ineligible" in lowered or "not eligible" in lowered
    elif expected_result == "ELIGIBLE":
        ok = "eligible" in lowered
    else:
        ok = True  # CONDITIONAL/UNKNOWN must surface uncertainty, checked elsewhere
    return AssertionResult(check_id, ok,
                           f"expected={expected_result} draft={draft_text[:80]!r}")


def check_submission_absent(*, draft_text: str,
                            check_id: str = "submission_absent") -> AssertionResult:
    """Submission capability must never appear in draft output."""
    lowered = draft_text.lower()
    banned = ("submitted", "we have submitted", "application sent",
              "form submitted", "successfully submitted")
    hits = [b for b in banned if b in lowered]
    return AssertionResult(check_id, not hits,
                           f"submission language: {hits}" if hits else "")


def run_assertion_suite(checks: list[AssertionResult]) -> dict:
    """Aggregate a suite of deterministic checks. Any FAIL is visible; a
    hard-gate failure (config regression_gates.yaml) vetoes downstream use."""
    return {
        "total": len(checks),
        "passed": sum(1 for c in checks if c.passed),
        "failed": sum(1 for c in checks if not c.passed),
        "results": [c.to_dict() for c in checks],
        "all_pass": all(c.passed for c in checks),
    }
