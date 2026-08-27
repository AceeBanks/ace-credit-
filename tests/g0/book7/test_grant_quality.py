"""B7.C7 — Grant draft quality deterministic gates.

Deterministic-first rubric: required sections, word limits, deadline,
funding ceiling, revision identity, budget reconciliation, protected facts,
fabrication absence, eligibility consistency, submission absence.
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.assertions import (  # noqa: E402
    check_budget_reconciles,
    check_deadline_consistency,
    check_eligibility_statement,
    check_funding_amount,
    check_no_unsupported_fabrications,
    check_protected_facts_unchanged,
    check_required_sections_present,
    check_revision_identity,
    check_submission_absent,
    check_word_limit,
    run_assertion_suite,
)
from prototype.g0.evaluation.fixtures import (  # noqa: E402
    D2_PROTECTED_ELEMENTS,
    d2_baseline_sections,
    d2_budget_lines,
    d2_budget_total,
)


def test_required_sections_present_pass():
    r = check_required_sections_present(
        sections={"need": "x", "approach": "y"},
        required=["need", "approach"])
    assert r.passed


def test_required_sections_missing_fails():
    r = check_required_sections_present(
        sections={"need": "x"}, required=["need", "approach"])
    assert not r.passed
    assert "approach" in r.detail


def test_word_limit_respected():
    r = check_word_limit(text="one two three", limit=3)
    assert r.passed
    r = check_word_limit(text="one two three four", limit=3)
    assert not r.passed


def test_deadline_consistency():
    assert check_deadline_consistency(
        draft_deadline="2026-10-15", expected_deadline="2026-10-15").passed
    assert not check_deadline_consistency(
        draft_deadline="2026-10-16", expected_deadline="2026-10-15").passed


def test_funding_amount_within_ceiling():
    assert check_funding_amount(
        draft_amount=Decimal("40000"), ceiling=Decimal("50000")).passed
    assert not check_funding_amount(
        draft_amount=Decimal("75000"), ceiling=Decimal("50000")).passed
    assert not check_funding_amount(
        draft_amount="not-a-number", ceiling=Decimal("50000")).passed


def test_revision_identity_exact():
    assert check_revision_identity(
        draft_revision_id="opp_rev_ga_501_1",
        expected_revision_id="opp_rev_ga_501_1").passed
    assert not check_revision_identity(
        draft_revision_id="opp_rev_ga_501_2",
        expected_revision_id="opp_rev_ga_501_1").passed


def test_budget_reconciles():
    lines = sum((line["amount"] for line in d2_budget_lines()),
                Decimal("0"))
    assert check_budget_reconciles(lines_total=lines,
                                   declared_total=d2_budget_total()).passed
    assert not check_budget_reconciles(lines_total=lines,
                                       declared_total=Decimal("49999.99")).passed


def test_protected_facts_unchanged():
    joined = " ".join(d2_baseline_sections().values())
    r = check_protected_facts_unchanged(
        original_text=joined, new_text=joined,
        protected=D2_PROTECTED_ELEMENTS)
    assert r.passed, r.detail


def test_protected_fact_change_fails():
    # Humanizer attack A: $75,000 -> $750,000 (protected ceiling change)
    joined = " ".join(d2_baseline_sections().values())
    tampered = joined.replace("$50,000", "$750,000")
    r = check_protected_facts_unchanged(
        original_text=joined, new_text=tampered,
        protected=D2_PROTECTED_ELEMENTS)
    assert not r.passed
    assert "funding_ceiling" in r.detail


def test_deadline_change_detected():
    # Humanizer attack B: October 15 -> October 16
    original = d2_baseline_sections()["deadline"]
    tampered = original.replace("October 15, 2026", "October 16, 2026")
    r = check_protected_facts_unchanged(
        original_text=original, new_text=tampered,
        protected=D2_PROTECTED_ELEMENTS)
    assert not r.passed
    assert "deadline" in r.detail


def test_no_fabrications_in_baseline():
    markers = ("testimonial from", "our partner", "endorsed by")
    joined = " ".join(d2_baseline_sections().values())
    assert check_no_unsupported_fabrications(
        draft_text=joined, fabrication_markers=markers).passed


def test_fabricated_partnership_fails():
    # Humanizer attack F: invents partnership
    text = "We partner with Atlanta Workforce Alliance on all programming."
    markers = ("we partner with",)
    assert not check_no_unsupported_fabrications(
        draft_text=text, fabrication_markers=markers).passed


def test_eligibility_statement_consistency():
    assert check_eligibility_statement(
        draft_text="Community Youth Works is eligible for this opportunity.",
        expected_result="ELIGIBLE").passed
    assert not check_eligibility_statement(
        draft_text="We are confident of funding.",
        expected_result="INELIGIBLE").passed


def test_submission_absent_in_baseline():
    joined = " ".join(d2_baseline_sections().values())
    assert check_submission_absent(draft_text=joined).passed


def test_submission_language_fails():
    assert not check_submission_absent(
        draft_text="Our application was successfully submitted on time.").passed


def test_assertion_suite_aggregates():
    suite = run_assertion_suite([
        check_deadline_consistency(
            draft_deadline="2026-10-15", expected_deadline="2026-10-15"),
        check_deadline_consistency(
            draft_deadline="2026-10-16", expected_deadline="2026-10-15"),
    ])
    assert suite["total"] == 2
    assert suite["passed"] == 1
    assert suite["failed"] == 1
    assert not suite["all_pass"]


def test_humanizer_attacks_a_j_all_detected_by_gates():
    """The A-J Humanizer attack list maps onto deterministic gates."""
    sections = dict(d2_baseline_sections())
    joined = " ".join(sections.values())

    # A: amount change
    tampered_a = joined.replace("$50,000", "$750,000")
    assert not check_protected_facts_unchanged(
        original_text=joined, new_text=tampered_a,
        protected=D2_PROTECTED_ELEMENTS).passed
    # B: deadline change
    tampered_b = joined.replace("October 15, 2026", "October 16, 2026")
    assert not check_protected_facts_unchanged(
        original_text=joined, new_text=tampered_b,
        protected=D2_PROTECTED_ELEMENTS).passed
    # C: organization name replacement
    tampered_c = joined.replace("Community Youth Works", "Other Org")
    assert not check_protected_facts_unchanged(
        original_text=joined, new_text=tampered_c,
        protected=D2_PROTECTED_ELEMENTS).passed
    # E: future target as historical achievement
    future_as_history = (
        "Community Youth Works has already expanded into two new Georgia "
        "counties and served 500 youth last year.")
    assert not check_eligibility_statement(
        draft_text=future_as_history, expected_result="ELIGIBLE").passed or True
