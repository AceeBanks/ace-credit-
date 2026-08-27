"""B7.C9 — Eligibility & match evaluation tests.

Deterministic eligibility classification, false-eligible severity, unknown
handling, revision sensitivity, match-never-overrides-eligibility,
match dimension bundles.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.domain_eval import (  # noqa: E402
    evaluate_eligibility_cases,
    match_dimension_bundle,
    match_never_overrides_eligibility,
)


def test_eligibility_accuracy_perfect():
    cases = [
        {"expected": "ELIGIBLE", "predicted": "ELIGIBLE"},
        {"expected": "INELIGIBLE", "predicted": "INELIGIBLE"},
        {"expected": "UNKNOWN", "predicted": "UNKNOWN"},
    ]
    r = evaluate_eligibility_cases(cases)
    assert r.accuracy == 1.0
    assert r.unknown_handled == 1


def test_false_eligible_counted():
    cases = [
        {"expected": "INELIGIBLE", "predicted": "ELIGIBLE"},
        {"expected": "ELIGIBLE", "predicted": "ELIGIBLE"},
    ]
    r = evaluate_eligibility_cases(cases)
    assert r.false_eligible == 1
    assert r.accuracy == 0.5


def test_false_ineligible_counted():
    cases = [{"expected": "ELIGIBLE", "predicted": "INELIGIBLE"}]
    r = evaluate_eligibility_cases(cases)
    assert r.false_ineligible == 1


def test_unknown_handled_as_separate_class():
    cases = [{"expected": "CONDITIONAL", "predicted": "CONDITIONAL"}]
    r = evaluate_eligibility_cases(cases)
    assert r.unknown_handled == 1
    assert r.accuracy == 1.0


def test_match_cannot_promote_ineligible():
    r = match_never_overrides_eligibility(match_score=0.99,
                                          eligibility="INELIGIBLE")
    assert r["allowed"] is False
    assert r["effective_status"] == "INELIGIBLE"


def test_match_conditional_surfaces_facts():
    r = match_never_overrides_eligibility(match_score=0.8,
                                          eligibility="UNKNOWN")
    assert r["allowed"] is True
    assert r["effective_status"] == "CONDITIONAL"


def test_match_dimensions_not_opaque():
    bundle = match_dimension_bundle(dimensions={
        "mission_alignment": 0.9, "geography": 1.0, "funding_fit": 0.5,
        "competition_risk": 0.2})
    assert set(bundle["dimensions"]) == {"mission_alignment", "geography",
                                         "funding_fit", "competition_risk"}
    assert bundle["ranked_recommendation"] is not None
    # competition_risk and application_burden excluded from the mean
    assert bundle["ranked_recommendation"] == round((0.9 + 1.0 + 0.5) / 3, 3)


def test_eligibility_domain_engine_deterministic():
    """Reuse the Book 2 deterministic engine: same inputs -> same decision."""
    from prototype.g0.domain.fixtures.georgia import GA_1
    from prototype.g0.domain.eligibility import evaluate_rule_set

    facts = {"primary_location": "Georgia",
             "organization_kind": "nonprofit"}
    d1 = evaluate_rule_set(GA_1["rule_set"], facts, "d-1", "org")
    d2 = evaluate_rule_set(GA_1["rule_set"], facts, "d-2", "org")
    assert d1.result == d2.result
    assert d1.explanation == d2.explanation


def test_missing_fact_is_unknown_not_eligible():
    from prototype.g0.domain.eligibility import evaluate_rule_set
    from prototype.g0.domain.fixtures.georgia import GA_1
    from prototype.g0.domain.models import EligibilityStatus
    decision = evaluate_rule_set(
        GA_1["rule_set"], {"primary_location": "Georgia"}, "d-3", "org")
    assert decision.result is EligibilityStatus.CONDITIONAL  # UNKNOWN -> CONDITIONAL
