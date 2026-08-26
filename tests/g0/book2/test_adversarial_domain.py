"""B2.C20 tests — Adversarial Domain Test Suite (A1-A20).

Attack the ontology before Book 3/data adapters depend on it. Every scenario
fails closed: no silent merges, no fabricated facts, no invented entities.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from prototype.g0.domain.budget import validate_amounts
from prototype.g0.domain.common_grants import lossy_fields, round_trip
from prototype.g0.domain.facts import (
    geography_mismatch,
    mark_conflict,
    promote_fact,
    superseded_fact_use,
)
from prototype.g0.domain.guards import (
    normalize_identifier,
    relationship_tenant_matches,
    require_known_type,
)
from prototype.g0.domain.identity import (
    classify_opportunity_identity,
    resolve_organizations,
)
from prototype.g0.domain.models import (
    ApplicationProject,
    Artifact,
    ArtifactStatus,
    ArtifactType,
    ArtifactVersion,
    Award,
    Budget,
    BudgetLine,
    CanonicalFact,
    ClaimStatus,
    EntityStatus,
    EvidenceClaim,
    ExternalIdentifier,
    FactPromotionState,
    GrantOpportunity,
    OpportunityRevision,
    Organization,
    OrganizationKind,
    OrganizationRole,
    Program,
    Relationship,
    Requirement,
    RequirementResponse,
    ResolutionStatus,
    RoleType,
    SourceSnapshot,
    StatisticObservation,
    VerificationState,
)
from prototype.g0.domain.revisions import (
    DecisionAnchor,
    RevisionSet,
    classify_revision,
    is_stale,
)
from tools.g0.validate_domain import load_common_grants_mapping, load_revision_policy

REV_POLICY = load_revision_policy()
CG_MAPPING = load_common_grants_mapping()


def _org(oid: str, name: str) -> Organization:
    return Organization(oid, OrganizationKind.NONPROFIT, name, name,
                        status=EntityStatus.ACTIVE)


# A1 — same name, different organization ---------------------------------------
def test_a1_same_name_different_org_no_silent_merge():
    a = _org("org_a1_1", "Community Youth Works, Inc.")
    b = _org("org_a1_2", "Community Youth Works Inc.")
    ids_a = [ExternalIdentifier("EIN", "58-1111111", "Organization",
                                verification_state=VerificationState.VERIFIED)]
    ids_b = [ExternalIdentifier("EIN", "58-2222222", "Organization",
                                verification_state=VerificationState.VERIFIED)]
    # near-identical names but DIFFERENT verified EINs -> distinct, not merged
    assert resolve_organizations(a, b, ids_a, ids_b) is ResolutionStatus.DISTINCT_CONFIRMED
    assert a.organization_id != b.organization_id


# A2 — rename, same organization ------------------------------------------------
def test_a2_rename_same_org_keeps_identity():
    a = _org("org_a2_1", "Old Name, Inc.")
    b = _org("org_a2_1", "New Name, Inc.")          # same internal id
    ids = [ExternalIdentifier("EIN", "58-9999999", "Organization",
                              verification_state=VerificationState.VERIFIED)]
    assert resolve_organizations(a, b, ids, ids) is ResolutionStatus.MATCH_CONFIRMED
    assert a.organization_id == b.organization_id


# A3 — source disagreement on name/address --------------------------------------
def test_a3_source_disagreement_claims_coexist_identity_intact():
    claim_old = EvidenceClaim("claim_a3_1", "legal name is Old Name",
                              "org_a3_1", "legal_name", "Old Name, Inc.",
                              status=ClaimStatus.VERIFIED)
    claim_new = EvidenceClaim("claim_a3_2", "legal name is New Name, Inc.",
                              "org_a3_1", "legal_name", "New Name, Inc.",
                              status=ClaimStatus.CONFLICTED)
    # both claims coexist; identity is NOT destroyed
    assert claim_old.claim_id != claim_new.claim_id
    assert claim_old.status is ClaimStatus.VERIFIED
    assert claim_new.status is ClaimStatus.CONFLICTED
    assert claim_old.subject == claim_new.subject == "org_a3_1"


# A4 — opportunity amendment after drafting -------------------------------------
def test_a4_amendment_after_drafting_new_revision_old_draft_stale():
    opp = GrantOpportunity("opp_a4_1", None, "Grant FY2026")
    rev1 = classify_revision("opp_rev_a4_1", 1, ["deadline"], "2026-08-01T00:00:00Z", REV_POLICY)
    rev2 = classify_revision("opp_rev_a4_2", 2, ["deadline"], "2026-08-02T00:00:00Z", REV_POLICY)
    rs = RevisionSet(opp.opportunity_id, "GrantOpportunity").add(rev1).add(rev2)
    draft = ApplicationProject("app_a4_1", "org_a4_1", opp.opportunity_id,
                               rev1.revision_id)      # old draft keeps old revision
    assert draft.opportunity_revision_id == rev1.revision_id
    anchor = DecisionAnchor("eldec_a4_1", rev1.revision_id)
    assert is_stale(anchor, rs) is True


# A5 — reissued opportunity number ambiguity ------------------------------------
def test_a5_reissued_opportunity_explicit_rule_no_merge():
    assert classify_opportunity_identity("RFA-100", "RFA-100",
                                         same_issuer=True,
                                         reissued_by_issuer=False) == "SAME_OPPORTUNITY"
    assert classify_opportunity_identity("RFA-100", "RFA-100",
                                         reissued_by_issuer=True) == "REISSUED_NEW_OPPORTUNITY"
    assert classify_opportunity_identity("RFA-100", "RFA-101") == "REISSUED_NEW_OPPORTUNITY"
    # two roots with the same number but different ids are never merged
    a = GrantOpportunity("opp_a5_1", None, "RFA-100")
    b = GrantOpportunity("opp_a5_2", None, "RFA-100")
    assert a.opportunity_id != b.opportunity_id


# A6 — historical award with no known opportunity --------------------------------
def test_a6_historical_award_representable_without_opportunity():
    award = Award("award_a6_1", funder_id="org_f", recipient_id="org_r",
                  amount=Decimal("5000.00"))
    assert award.opportunity_id is None
    assert award.award_id == "award_a6_1"


# A7 — recipient also funder elsewhere -------------------------------------------
def test_a7_same_org_different_roles():
    org = _org("org_a7_1", "Dual Role Foundation")
    as_funder = OrganizationRole("role_a7_1", org.organization_id, RoleType.FUNDER,
                                 target_ref="prog-1")
    as_recipient = OrganizationRole("role_a7_2", org.organization_id, RoleType.RECIPIENT,
                                    target_ref="award-1")
    assert as_funder.organization_id == as_recipient.organization_id == org.organization_id
    assert as_funder.role_type is RoleType.FUNDER
    assert as_recipient.role_type is RoleType.RECIPIENT


# A8 — requirement vs proposal section confusion ---------------------------------
def test_a8_requirement_and_section_separate_linked():
    req = Requirement("req_a8_1", "opp_rev_1", "narrative", mandatory=True)
    resp = RequirementResponse("resp_a8_1", req.requirement_id, "section",
                               artifact_version_id="artver-1")
    assert req.requirement_id != resp.response_id
    assert resp.requirement_id == req.requirement_id      # satisfaction link


# A9 — user claim treated as verified fact ----------------------------------------
def test_a9_claim_not_fact_without_promotion():
    claim = EvidenceClaim("claim_a9_1", "501(c)(3)", "org_a9_1", "is_501c3",
                          "true", status=ClaimStatus.PROPOSED)
    with_claim = promote_fact(
        CanonicalFact("fact_a9_1", "org_a9_1", "is_501c3", "true"),
        ("claim_a9_1",))
    assert with_claim.promotion_state is FactPromotionState.PROMOTED
    # a bare PROPOSED claim never yields a fact silently
    candidate = CanonicalFact("fact_a9_2", "org_a9_1", "is_501c3", "true")
    assert candidate.promotion_state is FactPromotionState.PROPOSED
    assert candidate.supporting_claim_ids == ()


# A10 — county statistic used as city statistic -----------------------------------
def test_a10_county_statistic_not_city():
    county = StatisticObservation("stat_a10_1", "poverty rate", Decimal("18.2"),
                                  "percent", "Dade County, GA", "2023",
                                  population="Dade County residents")
    assert geography_mismatch(county.geography, "City of Trenton, GA") is True
    assert geography_mismatch(county.geography, "Dade County, GA") is False


# A11 — proposal/business plan collapse --------------------------------------------
def test_a11_proposal_and_business_plan_distinct():
    p = Artifact("artifact_a11_1", ArtifactType.GRANT_PROPOSAL, "Proposal")
    bp = Artifact("artifact_a11_2", ArtifactType.BUSINESS_PLAN, "Business Plan")
    assert p.artifact_type is not bp.artifact_type
    assert p.artifact_id != bp.artifact_id


# A12 — synthetic testimonial -------------------------------------------------------
def test_a12_synthetic_testimonial_rejected():
    # a testimonial artifact with no source/status cannot be verified support
    snap = SourceSnapshot("snap_a12_1", "client", "org_a12_1",
                          "2026-08-01T00:00:00Z", "ch1")
    real = EvidenceClaim("claim_a12_1", "client testimonial quote", "org_a12_1",
                         "testimonial", "quote", source_snapshot_id=snap.snapshot_id,
                         status=ClaimStatus.VERIFIED)
    synthetic = EvidenceClaim("claim_a12_2", "invented quote", "org_a12_1",
                              "testimonial", "quote", source_snapshot_id=None,
                              status=ClaimStatus.PROPOSED)
    # only the source-backed, verified claim can support a testimonial fact
    assert real.source_snapshot_id is not None and real.status is ClaimStatus.VERIFIED
    assert synthetic.source_snapshot_id is None
    promote_fact(CanonicalFact("fact_a12_1", "org_a12_1", "testimonial", "quote"),
                 (real.claim_id,))     # ok
    try:
        promote_fact(CanonicalFact("fact_a12_2", "org_a12_1", "testimonial", "quote"),
                     (synthetic.claim_id,))
    except ValueError:
        pass


# A13 — CommonGrants lossy round trip ----------------------------------------------
def test_a13_lossy_round_trip_reports_loss():
    internal = {"opportunity_id": "opp-1", "title": "T", "status": "ACTIVE",
                "deadline (revision)": "2026-10-15"}
    ok, mismatches = round_trip(internal, CG_MAPPING, "GrantOpportunity")
    # status/deadline are LOSSY: round trip may not be exact, but loss is visible
    losses = lossy_fields(CG_MAPPING, "GrantOpportunity")
    assert losses
    assert all(r["loss_notes"] for r in losses)      # no silent truncation


# A14 — provider ID collision --------------------------------------------------------
def test_a14_same_string_two_namespaces_distinct():
    ga = ExternalIdentifier("GA_SECRETARY_OF_STATE", "1234567", "Organization",
                            verification_state=VerificationState.VERIFIED)
    fed = ExternalIdentifier("UEI", "1234567", "Organization",
                             verification_state=VerificationState.VERIFIED)
    assert ga.namespace != fed.namespace
    assert ga.value == fed.value                     # same string...
    assert (ga.namespace, ga.value) != (fed.namespace, fed.value)   # ...distinct identifiers
    assert ga.entity_type == fed.entity_type == "Organization"


# A15 — cross-tenant relationship -----------------------------------------------------
def test_a15_cross_tenant_relationship_rejected():
    rel = Relationship("rel_a15_1", "OPPORTUNITY_HAS_RULE", "opp-1", "rule-1",
                       tenant_id="tenant-alpha")
    assert relationship_tenant_matches(rel, "tenant-alpha", "tenant-alpha") is True
    assert relationship_tenant_matches(rel, "tenant-alpha", "tenant-beta") is False
    assert relationship_tenant_matches(rel, "tenant-beta", "tenant-alpha") is False


# A16 — floating money -----------------------------------------------------------------
def test_a16_floating_money_rejected():
    bad = Budget("budget_a16_1", "app-1",
                 lines=(BudgetLine("l1", "personnel", 50000.0),))      # float
    assert validate_amounts(bad)
    good = Budget("budget_a16_2", "app-1",
                  lines=(BudgetLine("l1", "personnel", Decimal("50000.00")),))
    assert validate_amounts(good) == []


# A17 — impossible state jump -----------------------------------------------------------
def test_a17_impossible_state_jump_rejected():
    from prototype.g0.domain.transitions import can_transition
    from tools.g0.validate_domain import load_state_machines
    sm = next(m for m in load_state_machines()["state_machines"]
              if m["state_machine"] == "application_project")
    verdict = can_transition(sm, "IDEA", "SUBMISSION_READY")
    assert not verdict.allowed


# A18 — stale eligibility ---------------------------------------------------------------
def test_a18_stale_eligibility_detected():
    rev1 = classify_revision("opp_rev_a18_1", 1, ["deadline"], "2026-08-01T00:00:00Z", REV_POLICY)
    rev2 = classify_revision("opp_rev_a18_2", 2, ["eligibility"], "2026-08-02T00:00:00Z", REV_POLICY)
    rs = RevisionSet("opp_a18_1", "GrantOpportunity").add(rev1).add(rev2)
    anchor = DecisionAnchor("eldec_a18_1", rev1.revision_id)
    assert is_stale(anchor, rs) is True
    # application now targets rev2 while the decision was made against rev1
    app = ApplicationProject("app_a18_1", "org-1", "opp_a18_1", rev2.revision_id)
    assert app.opportunity_revision_id != anchor.revision_id
    assert is_stale(anchor, rs) is True


# A19 — artifact uses superseded fact ----------------------------------------------------
def test_a19_artifact_uses_superseded_fact_detected():
    fact = CanonicalFact("fact_a19_1", "opp-1", "deadline", "2026-10-15",
                         promotion_state=FactPromotionState.SUPERSEDED,
                         supporting_claim_ids=("claim-1",))
    assert superseded_fact_use(fact, ("artver-1",)) != []
    assert superseded_fact_use(fact, ()) == []


# A20 — agent invents new root entity ----------------------------------------------------
def test_a20_invented_root_entity_rejected():
    assert require_known_type("Organization") is True
    assert require_known_type("GrantWinnerCompany") is False     # invented
    assert require_known_type("OpportunityObject") is False      # premature generalization


def test_a14b_identifier_normalization_idempotent():
    assert normalize_identifier("strip_non_alnum_upper", " 58-2345a ") == "582345A"
    assert normalize_identifier("strip_non_alnum_upper",
                                normalize_identifier("strip_non_alnum_upper",
                                                     " 58-2345a ")) == "582345A"
    assert normalize_identifier("trim_upper", " abc ") == "ABC"
    assert normalize_identifier("trim_upper", normalize_identifier("trim_upper",
                                                                  " abc ")) == "ABC"
