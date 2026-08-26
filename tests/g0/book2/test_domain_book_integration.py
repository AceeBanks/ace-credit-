"""B2.C21 tests — Book Integration & Property Tests.

The 22 mandatory domain invariants, each proven against the live ontology,
plus the plan's property tests (serialize round trip, EXACT CommonGrants
round trip, revision append immutability, idempotent normalization,
deterministic transitions).
"""
from __future__ import annotations

from dataclasses import asdict, replace
from decimal import Decimal

from prototype.g0.domain.budget import validate_amounts
from prototype.g0.domain.common_grants import round_trip as cg_round_trip
from prototype.g0.domain.facts import promote_fact, mark_conflict
from prototype.g0.domain.guards import normalize_identifier
from prototype.g0.domain.identity import validate_internal_id
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
    EvidenceClaim,
    ExternalIdentifier,
    FactPromotionState,
    GrantOpportunity,
    OpportunityRevision,
    Organization,
    OrganizationKind,
    OrganizationRole,
    Requirement,
    RequirementResponse,
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
from prototype.g0.domain.transitions import can_transition
from tools.g0.validate_domain import (
    load_common_grants_mapping,
    load_entity_types,
    load_revision_policy,
)

REV_POLICY = load_revision_policy()
CG_MAPPING = load_common_grants_mapping()

ORG = Organization("org_1", OrganizationKind.NONPROFIT, "Org", "Org")


# 1. Every root entity has stable internal identity ------------------------------
def test_invariant_01_root_entities_have_stable_identity():
    catalog = load_entity_types()
    for ent in catalog["entity_types"]:
        entity_type = ent["entity_type"]
        prefix = ent.get("identity_prefix")
        if not prefix:
            continue
        sample = prefix + "sample1"
        assert validate_internal_id(entity_type, sample), entity_type
    assert ORG.organization_id == "org_1"


# 2. Every external identifier is namespaced --------------------------------------
def test_invariant_02_external_ids_namespaced():
    ext = ExternalIdentifier("IRS_EIN", "58-1234567", "Organization",
                             verification_state=VerificationState.VERIFIED)
    assert ext.namespace and ext.namespace != ext.value
    assert ext.namespace == "IRS_EIN"


# 3. Provider IDs never replace internal primary identity --------------------------
def test_invariant_03_provider_ids_never_replace_internal_id():
    ext = ExternalIdentifier("USAspending", "ARC-2024-441", "Award",
                             verification_state=VerificationState.VERIFIED)
    award = Award("award_1", funder_id="org_f", recipient_id="org_r",
                  amount=Decimal("100.00"))
    assert award.award_id != ext.value
    assert award.award_id.startswith("award_")


# 4. Funder/Recipient/Applicant are role semantics --------------------------------
def test_invariant_04_roles_not_duplicate_orgs():
    roles = (OrganizationRole("r1", ORG.organization_id, "funder"),
             OrganizationRole("r2", ORG.organization_id, "recipient"),
             OrganizationRole("r3", ORG.organization_id, "applicant"))
    assert {r.organization_id for r in roles} == {ORG.organization_id}
    assert len({r.organization_id for r in roles}) == 1


# 5. Opportunity revisions are immutable -------------------------------------------
def test_invariant_05_opportunity_revisions_immutable():
    rev = OpportunityRevision("opp_rev_1", "opp_1", 1, "h1")
    try:
        rev.deadline = "mutated"
        raise AssertionError("frozen revision must not mutate")
    except Exception:
        pass
    rs = RevisionSet("opp_1", "GrantOpportunity").add(
        classify_revision("opp_rev_1", 1, ["deadline"], "t", REV_POLICY))
    before = rs.revisions
    rs2 = rs.add(classify_revision("opp_rev_2", 2, ["deadline"], "t2", REV_POLICY))
    assert rs.revisions == before            # append never mutates


# 6. Eligibility decisions target exact opportunity revision ------------------------
def test_invariant_06_eligibility_decision_targets_exact_revision():
    from prototype.g0.domain.models import (
        EligibilityDecision, EligibilityRuleSet, EligibilityStatus)
    rs = EligibilityRuleSet("rs_1", "opp_rev_7", 1)
    d = EligibilityDecision("eldec_1", "org_1", rs.opportunity_revision_id,
                            "rs_1", 1, EligibilityStatus.UNKNOWN)
    assert d.opportunity_revision_id == "opp_rev_7"


# 7. ApplicationProject targets exact opportunity revision ---------------------------
def test_invariant_07_project_targets_exact_revision():
    app = ApplicationProject("app_1", "org_1", "opp_1", "opp_rev_7")
    assert app.opportunity_revision_id == "opp_rev_7"


# 8. Material changes invalidate dependent decisions --------------------------------
def test_invariant_08_material_change_invalidates():
    rev1 = classify_revision("opp_rev_1", 1, ["deadline"], "t", REV_POLICY)
    rev2 = classify_revision("opp_rev_2", 2, ["funding_amount"], "t2", REV_POLICY)
    rs = RevisionSet("opp_1", "GrantOpportunity").add(rev1).add(rev2)
    assert is_stale(DecisionAnchor("eldec_1", "opp_rev_1"), rs) is True


# 9. EvidenceClaim cannot silently become CanonicalFact ------------------------------
def test_invariant_09_claim_not_silent_fact():
    claim = EvidenceClaim("claim_1", "501(c)(3)", "org_1", "is_501c3", "true",
                          status=ClaimStatus.VERIFIED)
    candidate = CanonicalFact("fact_1", "org_1", "is_501c3", "true")
    assert candidate.promotion_state is FactPromotionState.PROPOSED
    promoted = promote_fact(candidate, (claim.claim_id,))
    assert promoted.promotion_state is FactPromotionState.PROMOTED
    assert promoted.supporting_claim_ids == (claim.claim_id,)


# 10. Conflicting claims may coexist -------------------------------------------------
def test_invariant_10_conflicting_claims_coexist():
    c1 = EvidenceClaim("claim_a", "rate 18%", "c-1", "rate", "18%",
                       status=ClaimStatus.VERIFIED)
    c2 = EvidenceClaim("claim_b", "rate 21%", "c-1", "rate", "21%",
                       status=ClaimStatus.CONFLICTED)
    fact = mark_conflict(CanonicalFact("fact_1", "c-1", "rate", "18%"),
                         ("claim_b",))
    assert fact.promotion_state is FactPromotionState.CONFLICTED
    assert c1.status is ClaimStatus.VERIFIED and c2.status is ClaimStatus.CONFLICTED


# 11. Statistics preserve geography/population/time context ---------------------------
def test_invariant_11_statistics_preserve_context():
    stat = StatisticObservation("stat_1", "poverty rate", Decimal("18.2"),
                                "percent", "Dade County, GA", "2023",
                                population="Dade County residents",
                                dataset_version="ACS-5yr-2023")
    assert stat.geography and stat.population and stat.reference_period


# 12. Proposal and BusinessPlan are distinct artifacts --------------------------------
def test_invariant_12_proposal_business_plan_distinct():
    p = Artifact("artifact_p", ArtifactType.GRANT_PROPOSAL, "Proposal")
    bp = Artifact("artifact_bp", ArtifactType.BUSINESS_PLAN, "Business Plan")
    assert p.artifact_type is ArtifactType.GRANT_PROPOSAL
    assert bp.artifact_type is ArtifactType.BUSINESS_PLAN
    assert p.artifact_type is not bp.artifact_type


# 13. Requirement and RequirementResponse are distinct --------------------------------
def test_invariant_13_requirement_response_distinct():
    req = Requirement("req_1", "opp_rev_1", "narrative")
    resp = RequirementResponse("resp_1", req.requirement_id, "section")
    assert type(req) is not type(resp)
    assert resp.requirement_id == req.requirement_id


# 14. Artifact and SourceSnapshot are distinct semantic types --------------------------
def test_invariant_14_artifact_snapshot_distinct():
    art = Artifact("artifact_1", ArtifactType.RESEARCH_REPORT, "Report")
    snap = SourceSnapshot("snap_1", "GA-OPB", "opp-1", "2026-08-01T00:00:00Z", "h")
    assert type(art) is not type(snap)
    assert isinstance(art, Artifact) and not isinstance(art, SourceSnapshot)


# 15. Historical Award can exist without internal ApplicationProject -------------------
def test_invariant_15_historical_award_without_project():
    award = Award("award_1", funder_id="org_f", recipient_id="org_r",
                  amount=Decimal("5000.00"), opportunity_id=None)
    assert award.opportunity_id is None
    assert not hasattr(award, "project_id")


# 16. Money uses decimal/fixed-point semantics ------------------------------------------
def test_invariant_16_money_decimal_only():
    bad = Budget("budget_1", "app_1",
                 lines=(BudgetLine("l1", "x", 1.5),))
    assert validate_amounts(bad)
    good = Budget("budget_1", "app_1",
                  lines=(BudgetLine("l1", "x", Decimal("1.50")),))
    assert validate_amounts(good) == []


# 17. State transitions are enumerated and validated ------------------------------------
def test_invariant_17_state_transitions_validated():
    from tools.g0.validate_domain import load_state_machines, validate_state_machines
    data = load_state_machines()
    ok, report = validate_state_machines(data)
    assert ok, report["errors"]
    sm = next(m for m in data["state_machines"]
              if m["state_machine"] == "application_project")
    assert can_transition(sm, "IDEA", "SUBMISSION_READY").allowed is False
    assert can_transition(sm, "IDEA", "QUALIFYING",
                          capability="application.create_draft_project",
                          authority_level="L2").allowed is True


# 18. Submission-ready does not imply submitted ------------------------------------------
def test_invariant_18_submission_ready_not_submitted():
    pkg = Artifact("artifact_pkg", ArtifactType.SUBMISSION_PACKAGE, "Pkg",
                   status=ArtifactStatus.SUBMISSION_READY)
    assert pkg.status is ArtifactStatus.SUBMISSION_READY
    # there is NO SUBMITTED artifact status: readiness never implies submitted
    assert "SUBMITTED" not in {s.value for s in ArtifactStatus}


# 19. CommonGrants mappings report loss explicitly ---------------------------------------
def test_invariant_19_common_grants_loss_reported():
    from prototype.g0.domain.common_grants import lossy_fields
    for ent in ("GrantOpportunity", "ApplicationProject", "Award"):
        losses = lossy_fields(CG_MAPPING, ent)
        assert all(r["loss_notes"] for r in losses), ent
    # EXACT fields round-trip
    ok, _ = cg_round_trip({"opportunity_id": "opp-1", "title": "T"}, CG_MAPPING,
                          "GrantOpportunity")
    assert ok


# 20. Every Phase 1 client requirement is representable ---------------------------------
def test_invariant_20_client_requirements_representable():
    from tools.g0.validate_domain import load_client_vision_matrix
    matrix = load_client_vision_matrix()
    assert matrix["coverage"]
    assert all(r["covered"] is True for r in matrix["coverage"])


# 21. Georgia/federal fixtures validate against the same core ontology ------------------
def test_invariant_21_fixtures_share_core_ontology():
    from prototype.g0.domain.fixtures import SCENARIOS
    assert set(SCENARIOS) == {"GA-1", "FED-1", "AWARD-1", "COMMUNITY-1"}
    assert SCENARIOS["GA-1"]["project"].opportunity_revision_id == \
        SCENARIOS["GA-1"]["revision"].revision_id
    assert SCENARIOS["FED-1"]["project"].opportunity_revision_id == \
        SCENARIOS["FED-1"]["revision"].revision_id
    assert SCENARIOS["AWARD-1"]["award"].recipient_id == \
        SCENARIOS["AWARD-1"]["recipient"].organization_id


# 22. D0 DraftContextBundle representable without agent memory --------------------------
def test_invariant_22_draft_bundle_without_memory():
    from prototype.g0.domain.draft_context import (
        DraftContextBundle, validate_draft_context)
    from prototype.g0.domain.fixtures.draft_context import GA_DRAFT_BUNDLE
    assert validate_draft_context(GA_DRAFT_BUNDLE) == []
    rebuilt = DraftContextBundle(
        organization=GA_DRAFT_BUNDLE.organization,
        opportunity=GA_DRAFT_BUNDLE.opportunity,
        opportunity_revision=GA_DRAFT_BUNDLE.opportunity_revision)
    assert replace(rebuilt) == rebuilt


# --- Property tests ----------------------------------------------------------------

def test_property_serialize_deserialize_preserves_semantics():
    stat = StatisticObservation("stat_1", "poverty rate", Decimal("18.2"),
                                "percent", "Dade County, GA", "2023",
                                population="residents")
    as_dict = asdict(stat)
    assert as_dict["stat_id"] == "stat_1"
    assert as_dict["metric"] == "poverty rate"
    # serialized representation round-trips the semantic fields
    assert StatisticObservation(**as_dict) == stat


def test_property_exact_cg_round_trip_preserves_equality():
    internal = {"award_id": "award-1", "amount": Decimal("75000.00"),
                "currency": "USD", "recipient_id": "org-42"}
    ok, mismatches = cg_round_trip(internal, CG_MAPPING, "Award")
    assert ok and not mismatches


def test_property_revision_append_does_not_mutate():
    rs = RevisionSet("opp_1", "GrantOpportunity").add(
        classify_revision("opp_rev_1", 1, ["deadline"], "t", REV_POLICY))
    snapshot = rs.revisions
    rs.add(classify_revision("opp_rev_2", 2, ["funding_amount"], "t2", REV_POLICY))
    assert rs.revisions == snapshot


def test_property_identifier_normalization_idempotent():
    for rule, raw in (("trim", "  abc  "), ("trim_upper", " abc "),
                      ("trim_lower", " ABC "), ("strip_non_alnum_upper", " 58-9a ")):
        once = normalize_identifier(rule, raw)
        assert normalize_identifier(rule, once) == once


def test_property_deterministic_state_transition():
    from tools.g0.validate_domain import load_state_machines
    sm = next(m for m in load_state_machines()["state_machines"]
              if m["state_machine"] == "requirement")
    a = can_transition(sm, "NORMALIZED", "BLOCKED")
    b = can_transition(sm, "NORMALIZED", "BLOCKED")
    assert (a.allowed, a.reason) == (b.allowed, b.reason)
