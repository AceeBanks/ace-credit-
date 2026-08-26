"""B2.C9 tests — Fact, Claim, Evidence & Statistic Semantic Model.

Claims never auto-promote; facts must reference support; conflicting claims
coexist; statistics keep context; artifacts trace assertions to evidence.
"""
from __future__ import annotations

import copy
from decimal import Decimal

import pytest

from prototype.g0.domain.facts import (
    assertion_lineage,
    claim_to_fact_candidate,
    mark_conflict,
    promote_fact,
    validate_statistic,
)
from prototype.g0.domain.models import (
    CanonicalFact,
    ClaimStatus,
    EvidenceClaim,
    FactPromotionState,
    SourceSnapshot,
    StatisticObservation,
)
from tools.g0.validate_domain import load_fact_semantics, validate_fact_semantics

POLICY = load_fact_semantics()


def _claim(cid: str, proposition: str = "county poverty rate is 18%",
           subject: str = "county-121", predicate: str = "poverty_rate",
           value: str = "18%", snap: str | None = "snap-1",
           status: ClaimStatus = ClaimStatus.PROPOSED) -> EvidenceClaim:
    return EvidenceClaim(cid, proposition, subject, predicate, value,
                         source_snapshot_id=snap, status=status)


def test_live_fact_semantics_passes():
    ok, report = validate_fact_semantics(POLICY)
    assert ok, report["errors"]


def test_claim_cannot_automatically_become_canonical_fact():
    verified = _claim("claim-1", status=ClaimStatus.VERIFIED)
    # even a VERIFIED claim is not a fact — only a PROPOSED candidate at best
    candidate = claim_to_fact_candidate(verified, "fact-1")
    assert candidate.promotion_state is FactPromotionState.PROPOSED
    assert candidate.supporting_claim_ids == ()
    assert candidate.fact_id != verified.claim_id
    # promotion is an explicit, separate action with support
    promoted = promote_fact(candidate, ("claim-1",))
    assert promoted.promotion_state is FactPromotionState.PROMOTED


def test_fact_must_reference_support():
    with pytest.raises(ValueError):
        CanonicalFact("fact-1", "opp-1", "deadline", "2026-10-15",
                      promotion_state=FactPromotionState.PROMOTED)
    # and the explicit promotion path rejects empty support too
    candidate = CanonicalFact("fact-2", "opp-1", "deadline", "2026-10-15")
    with pytest.raises(ValueError):
        promote_fact(candidate, ())


def test_conflicting_claims_coexist_without_deletion():
    c1 = _claim("claim-a", proposition="poverty rate is 18%", value="18%",
                status=ClaimStatus.VERIFIED)
    c2 = _claim("claim-b", proposition="poverty rate is 21%", value="21%",
                status=ClaimStatus.CONFLICTED)
    candidate = claim_to_fact_candidate(c1, "fact-1")
    fact = mark_conflict(candidate, ("claim-b",))
    # both claims still exist; the fact is CONFLICTED, not resolved
    assert fact.promotion_state is FactPromotionState.CONFLICTED
    assert fact.contradicting_claim_ids == ("claim-b",)
    assert c1.status is ClaimStatus.VERIFIED          # untouched
    assert c2.status is ClaimStatus.CONFLICTED        # untouched
    assert fact.supporting_claim_ids == ()            # never auto-promoted


def test_conflict_requires_contradicting_claims():
    candidate = CanonicalFact("fact-1", "opp-1", "deadline", "2026-10-15")
    with pytest.raises(ValueError):
        mark_conflict(candidate, ())


def test_statistic_requires_geography_context():
    ok_stat = StatisticObservation("stat-1", "county poverty rate", Decimal("18.0"),
                                   "percent", "county-121", "2025")
    assert validate_statistic(ok_stat, POLICY) == []
    missing_geo = StatisticObservation("stat-2", "county poverty rate", Decimal("18.0"),
                                       "percent", "", "2025")
    errors = validate_statistic(missing_geo, POLICY)
    assert any("geography" in e for e in errors)


def test_statistic_population_required_where_relevant():
    served = StatisticObservation("stat-3", "program served 240 participants",
                                  Decimal("240"), "people", "county-121", "FY2025",
                                  population=None)
    errors = validate_statistic(served, POLICY)
    assert any("population" in e for e in errors)
    with_pop = StatisticObservation("stat-4", "program served 240 participants",
                                    Decimal("240"), "people", "county-121", "FY2025",
                                    population="county-121 residents")
    assert validate_statistic(with_pop, POLICY) == []


def test_artifact_can_trace_assertion_back_to_evidence():
    snap = SourceSnapshot("snap-1", "GA-OPB", "county-121",
                          "2026-08-01T00:00:00Z", "ch0")
    claim = _claim("claim-1", snap="snap-1", status=ClaimStatus.VERIFIED)
    candidate = claim_to_fact_candidate(claim, "fact-1")
    fact = promote_fact(candidate, ("claim-1",))
    chain = assertion_lineage("artver-3", fact, {"claim-1": claim}, {"snap-1": snap})
    assert chain["artifact_version_ref"] == "artver-3"
    assert chain["fact_id"] == "fact-1"
    assert chain["supporting_claims"][0]["claim_id"] == "claim-1"
    assert chain["supporting_claims"][0]["snapshot_resolved"] is True
    assert chain["supporting_claims"][0]["source_snapshot_id"] == "snap-1"


def test_lineage_fails_closed_on_unresolvable_claim():
    claim = _claim("claim-1")
    candidate = claim_to_fact_candidate(claim, "fact-1")
    fact = promote_fact(candidate, ("claim-1",))
    with pytest.raises(ValueError):
        assertion_lineage("artver-3", fact, {}, {})


# --- validator defect injection ------------------------------------------------

def test_non_explicit_promotion_rule_fails():
    data = copy.deepcopy(POLICY)
    data["claim_to_fact_rule"] = "auto_promote_on_verify"
    ok, report = validate_fact_semantics(data)
    assert not ok
    assert any("explicit_promotion_required" in e for e in report["errors"])


def test_promotion_without_support_fails():
    data = copy.deepcopy(POLICY)
    data["fact_promotion_requires_support"] = False
    ok, report = validate_fact_semantics(data)
    assert not ok
    assert any("fact_promotion_requires_support" in e for e in report["errors"])


def test_missing_statistic_context_field_fails():
    data = copy.deepcopy(POLICY)
    data["required_statistic_context"] = ["geography", "unit"]
    ok, report = validate_fact_semantics(data)
    assert not ok
    assert any("reference_period" in e for e in report["errors"])
