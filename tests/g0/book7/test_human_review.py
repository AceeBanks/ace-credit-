"""B7.C23 — Human review protocol tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.human_review import (  # noqa: E402
    HumanReviewError,
    disagreement_is_data,
    human_review_required,
    record_review,
    review_packet,
)


def test_human_review_required_for_subjective_high_impact():
    assert human_review_required(
        reason="rubric_dimension_materially_subjective_and_high_impact")
    assert human_review_required(
        reason="candidate_changes_client_facing_grant_strategy")
    assert human_review_required(reason="security boundary change")
    assert not human_review_required(reason="trivial wording tweak")


def test_record_review_requires_identity():
    with pytest.raises(HumanReviewError):
        record_review(reviewer_identity="", reviewer_role="reviewer",
                      subject_ref="s", decision="APPROVE",
                      reason_codes=[])


def test_record_review_requires_valid_decision():
    with pytest.raises(HumanReviewError):
        record_review(reviewer_identity="r1", reviewer_role="grant-expert",
                      subject_ref="s", decision="MAYBE", reason_codes=[])


def test_record_review_attributable():
    review = record_review(reviewer_identity="r1", reviewer_role="grant-expert",
                           subject_ref="draft-1", decision="REQUEST_EDITS",
                           reason_codes=["NEED_MORE_EVIDENCE"],
                           comments="add census citation")
    assert review["reviewer_identity"] == "r1"
    assert review["decision"] == "REQUEST_EDITS"
    assert review["reviewed_at"]


def test_review_packet_bounded_not_raw_logs():
    packet = review_packet(
        subject_ref="draft-1",
        opportunity_revision_id="opp_rev_ga_501_1",
        eligibility_summary={"result": "ELIGIBLE"},
        draft_artifact_ref="art-1",
        requirement_coverage={"coverage": 0.8},
        claim_ledger_issues=["d2-c9 unsupported"],
        budget_validation={"reconciles": True},
        uncertainties=["cost share unconfirmed"],
        qa_eval_results={"all_pass": False},
        confirmation_items=["confirm EIN"])
    assert packet["opportunity_revision_id"] == "opp_rev_ga_501_1"
    assert "d2-c9 unsupported" in packet["claim_ledger_issues"]
    assert "confirm EIN" in packet["confirmation_items"]
    # no raw transcript field exists in the packet contract
    assert "raw_transcript" not in packet


def test_disagreement_is_data():
    reviews = [
        record_review(reviewer_identity="r1", reviewer_role="expert",
                      subject_ref="d", decision="APPROVE", reason_codes=[]),
        record_review(reviewer_identity="r2", reviewer_role="expert",
                      subject_ref="d", decision="REQUEST_EDITS",
                      reason_codes=["STYLE"]),
    ]
    r = disagreement_is_data(reviews=reviews)
    assert r["disagreement"] is True
    assert r["decisions"] == ["APPROVE", "REQUEST_EDITS"]


def test_agreement_reported():
    reviews = [
        record_review(reviewer_identity="r1", reviewer_role="expert",
                      subject_ref="d", decision="APPROVE", reason_codes=[]),
        record_review(reviewer_identity="r2", reviewer_role="expert",
                      subject_ref="d", decision="APPROVE", reason_codes=[]),
    ]
    assert disagreement_is_data(reviews=reviews)["disagreement"] is False


def test_single_review_note():
    reviews = [
        record_review(reviewer_identity="r1", reviewer_role="expert",
                      subject_ref="d", decision="APPROVE", reason_codes=[]),
    ]
    assert disagreement_is_data(reviews=reviews)["disagreement"] is False
