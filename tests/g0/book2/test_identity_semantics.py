"""B2.C4 tests — Identity Constitution.

Rename continuity, duplicate-name separation, cross-source resolution,
source ID reuse/collision, amended vs reissued opportunity, historical
award dedupe, missing/conflicting external IDs.
"""
from __future__ import annotations

from decimal import Decimal

from prototype.g0.domain.identity import (
    award_dedupe_candidate,
    classify_opportunity_identity,
    resolve_organizations,
    validate_internal_id,
)
from prototype.g0.domain.models import (
    Award,
    ExternalIdentifier,
    Organization,
    OrganizationKind,
    ResolutionStatus,
    VerificationState,
)


def _org(oid, name):
    return Organization(oid, OrganizationKind.NONPROFIT, name, name)


def _ein(value, state=VerificationState.VERIFIED):
    return ExternalIdentifier("EIN", value, "Organization",
                              verification_state=state)


def test_rename_continuity_same_ein():
    """8.4 rename: same verified EIN -> same Organization (MATCH_CONFIRMED)."""
    old = _org("org-1", "Community Youth Works, Inc.")
    new = _org("org-1", "Georgia Youth Works, Inc.")
    assert resolve_organizations(old, new, [_ein("58-1234567")],
                                 [_ein("58-1234567")]) is ResolutionStatus.MATCH_CONFIRMED


def test_similar_name_different_ein_is_distinct():
    """8.4 similar names, different EINs -> distinct Organizations."""
    a = _org("org-2", "Atlanta Youth Initiative")
    b = _org("org-3", "Atlanta Youth Initiatives Inc.")
    assert resolve_organizations(a, b, [_ein("58-1111111")],
                                 [_ein("58-2222222")]) is ResolutionStatus.DISTINCT_CONFIRMED


def test_same_name_no_verified_id_is_probable_review():
    """Name similarity without verified shared ID proposes review, never merges."""
    a = _org("org-4", "Peach Tree Center")
    b = _org("org-5", "Peach Tree Center")
    assert resolve_organizations(a, b) is ResolutionStatus.MATCH_PROBABLE_REVIEW


def test_cross_source_organization_resolution():
    """IRS, SAM and USAspending records map to one internal Organization."""
    irs = _org("org-6", "Southside CDC")
    sam = _org("org-6", "Southside CDC")
    usasp = _org("org-6", "Southside Community Development Corp")
    ein = _ein("58-3333333")
    uei = ExternalIdentifier("UEI", "K1A2B3C4D5E6", "Organization",
                             verification_state=VerificationState.VERIFIED)
    assert resolve_organizations(irs, sam, [ein], [ein]) is ResolutionStatus.MATCH_CONFIRMED
    assert resolve_organizations(sam, usasp, [uei], [uei]) is ResolutionStatus.MATCH_CONFIRMED


def test_source_id_collision_across_namespaces_is_not_a_match():
    """Same value in two namespaces is not a shared identity."""
    a = _org("org-7", "Alpha")
    b = _org("org-8", "Beta")
    id_a = ExternalIdentifier("GA_PORTAL", "XYZ-1", "GrantOpportunity",
                              verification_state=VerificationState.VERIFIED)
    id_b = ExternalIdentifier("PROVIDER", "XYZ-1", "Organization",
                              verification_state=VerificationState.VERIFIED)
    assert resolve_organizations(a, b, [id_a], [id_b]) is not ResolutionStatus.MATCH_CONFIRMED


def test_missing_external_id_is_unresolved():
    a = _org("org-9", "Gamma Collective")
    b = _org("org-10", "Delta Initiative")
    assert resolve_organizations(a, b) is ResolutionStatus.UNRESOLVED


def test_conflicting_verified_eins_are_distinct():
    a = _org("org-11", "Omega Fund")
    b = _org("org-12", "Omega Fund")
    assert resolve_organizations(a, b, [_ein("58-4444444")],
                                 [_ein("58-5555555")]) is ResolutionStatus.DISTINCT_CONFIRMED


def test_unverified_ein_does_not_confirm_identity():
    a = _org("org-13", "Sigma")
    b = _org("org-14", "Sigma")
    assert resolve_organizations(a, b, [_ein("58-6666666", VerificationState.CLAIMED)],
                                 [_ein("58-6666666", VerificationState.CLAIMED)]) \
        is not ResolutionStatus.MATCH_CONFIRMED


def test_amended_opportunity_is_same_opportunity():
    assert classify_opportunity_identity("OPP-2026-01", "OPP-2026-01") == "SAME_OPPORTUNITY"


def test_reissued_opportunity_is_new_opportunity():
    assert classify_opportunity_identity("OPP-2026-01", "OPP-2026-01",
                                         reissued_by_issuer=True) \
        == "REISSUED_NEW_OPPORTUNITY"
    assert classify_opportunity_identity("OPP-2026-01", "OPP-2027-01") \
        == "REISSUED_NEW_OPPORTUNITY"


def test_historical_award_not_merged_on_similarity_alone():
    a = {"issuer_award_id": None, "recipient": "org-1", "funder": "org-2",
         "amount": Decimal("50000.00")}
    b = {"issuer_award_id": None, "recipient": "org-1", "funder": "org-2",
         "amount": Decimal("50000.00")}
    assert award_dedupe_candidate(a, b) is False  # never merge on coincidence


def test_award_dedupe_by_issuer_id():
    a = {"issuer_award_id": "FAIN-2026-0001"}
    b = {"issuer_award_id": "FAIN-2026-0001"}
    assert award_dedupe_candidate(a, b) is True


def test_internal_id_prefix_scheme():
    assert validate_internal_id("Organization", "org_42")
    assert validate_internal_id("GrantOpportunity", "opp_ga-2026-01")
    assert not validate_internal_id("Organization", "opp_42")      # wrong prefix
    assert not validate_internal_id("Organization", "42")          # no prefix
    assert validate_internal_id("OpportunityRevision", "opp_rev_3")
    assert validate_internal_id("StatisticObservation", "stat_acs-2022")
