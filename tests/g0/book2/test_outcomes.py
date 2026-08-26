"""B2.C14 tests — Outcome & Learning Feedback Ontology.

Prepares the domain for later tracking/self-improvement without building
tracking now. Outcomes are evidence for Book 7 — never automatic doctrine.
"""
from __future__ import annotations

import copy
from decimal import Decimal

from prototype.g0.domain.models import Award, OutcomeFeedback, OutcomeType
from prototype.g0.domain.outcomes import (
    doctrine_unchanged,
    learning_evidence,
    link_outcome,
)
from tools.g0.validate_domain import load_outcome_policy, validate_outcome_policy

POLICY = load_outcome_policy()


def test_live_outcome_policy_passes():
    ok, report = validate_outcome_policy(POLICY)
    assert ok, report["errors"]
    assert report["outcome_type_count"] == 7


def test_historical_award_can_exist_without_application_project():
    award = Award("award-1", funder_id="org-7", recipient_id="org-42",
                  amount=Decimal("75000.00"), award_date="2024-06-01",
                  opportunity_id=None)
    assert award.award_id == "award-1"
    assert award.opportunity_id is None            # no project required
    assert not hasattr(award, "project_id")


def test_outcome_can_be_linked_later():
    outcome = OutcomeFeedback("outcome-1", OutcomeType.REJECTED,
                              "2025-09-01T00:00:00Z",
                              reason_codes=("incomplete_evidence",),
                              freeform_feedback="needed more financials")
    assert outcome.project_id is None and outcome.award_id is None
    linked = link_outcome(outcome, project_id="app-1", award_id="award-1")
    # the original object is untouched; linkage is a separate immutable op
    assert outcome.project_id is None
    assert linked.project_id == "app-1" and linked.award_id == "award-1"
    assert linked.outcome_id == outcome.outcome_id


def test_rejection_feedback_preserved_without_becoming_automatic_doctrine():
    outcome = OutcomeFeedback("outcome-2", OutcomeType.REJECTED,
                              "2025-09-01T00:00:00Z",
                              reason_codes=("incomplete_evidence",),
                              freeform_feedback="budget narrative was weak")
    evidence = learning_evidence(outcome)
    # feedback is preserved verbatim as evidence...
    assert evidence["freeform_feedback"] == "budget narrative was weak"
    assert "incomplete_evidence" in evidence["reason_codes"]
    # ...and recorded as doctrine_effect: none — no prompt/policy rewrite
    assert evidence["doctrine_effect"] == "none"
    assert evidence["evidence_kind"] == "outcome_feedback"


def test_learning_never_rewrites_doctrine():
    doctrine = {"prompt_policy_version": "3.1", "rules": ("a", "b")}
    outcome = OutcomeFeedback("outcome-3", OutcomeType.AWARDED,
                              "2026-01-15T00:00:00Z", project_id="app-1")
    evidence = learning_evidence(outcome)
    assert evidence["doctrine_effect"] == "none"
    # any honest learning pipeline leaves doctrine byte-identical
    assert doctrine_unchanged(doctrine, dict(doctrine)) is True
    assert doctrine_unchanged(doctrine, {**doctrine, "rules": ("a", "b", "c")}) is False


def test_outcome_carries_source_evidence_refs():
    outcome = OutcomeFeedback("outcome-4", OutcomeType.SUBMITTED,
                              "2026-02-01T00:00:00Z", project_id="app-1",
                              source_evidence_refs=("snap-9", "fact-4"))
    assert outcome.source_evidence_refs == ("snap-9", "fact-4")


# --- validator defect injection ------------------------------------------------

def test_missing_outcome_type_fails():
    data = copy.deepcopy(POLICY)
    data["outcome_types"] = [t for t in data["outcome_types"] if t != "AWARDED"]
    ok, report = validate_outcome_policy(data)
    assert not ok
    assert any("outcome_types" in e for e in report["errors"])


def test_automatic_doctrine_learning_fails():
    data = copy.deepcopy(POLICY)
    data["learning_rule"] = "outcome_rewrites_prompts"
    ok, report = validate_outcome_policy(data)
    assert not ok
    assert any("learning_rule" in e for e in report["errors"])
