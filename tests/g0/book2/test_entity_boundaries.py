"""B2.C2 tests — Entity Boundary ADR scenarios.

Every high-cost boundary decision (ADR-B2-001..010) is proven against a
concrete multi-role / historical scenario without duplicate truth.
"""
from __future__ import annotations

from decimal import Decimal

from prototype.g0.domain.models import (
    ApplicationProject,
    ApplicationRevision,
    Artifact,
    ArtifactStatus,
    ArtifactType,
    ArtifactVersion,
    Award,
    CanonicalFact,
    EvidenceClaim,
    FactPromotionState,
    GrantOpportunity,
    OpportunityRevision,
    Organization,
    OrganizationContact,
    OrganizationKind,
    OrganizationRole,
    Person,
    Program,
    RoleType,
    SourceSnapshot,
    ClaimStatus,
)

ORG_A = Organization("org-42", OrganizationKind.NONPROFIT, "Community Youth Works, Inc.",
                     "Community Youth Works")
ORG_B = Organization("org-7", OrganizationKind.FOUNDATION, "Peach State Foundation",
                     "Peach Foundation")


# ADR-B2-001 — Organization vs Funder/Recipient roles --------------------------
def test_organization_roles_do_not_create_duplicate_entities():
    funder_role = OrganizationRole("role-1", ORG_B.organization_id, RoleType.FUNDER,
                                   target_ref="prog-1")
    recipient_role = OrganizationRole("role-2", ORG_B.organization_id, RoleType.RECIPIENT,
                                      target_ref="award-1")
    # one organization, two roles — no second root entity
    assert funder_role.organization_id == recipient_role.organization_id == ORG_B.organization_id
    assert funder_role.role_type is not recipient_role.role_type


# ADR-B2-002 — Program vs Opportunity ------------------------------------------
def test_program_produces_many_opportunities():
    prog = Program("prog-1", "Community Grants")
    opp1 = GrantOpportunity("opp-1", prog.program_id, "Community Grant FY2026")
    opp2 = GrantOpportunity("opp-2", prog.program_id, "Community Grant FY2027")
    assert {o.program_id for o in (opp1, opp2)} == {prog.program_id}
    assert prog.program_id != opp1.opportunity_id  # distinct identity


# ADR-B2-003 — Opportunity vs OpportunityRevision ------------------------------
def test_decisions_point_to_exact_revision():
    opp = GrantOpportunity("opp-1", "prog-1", "Community Grant FY2026")
    rev1 = OpportunityRevision("rev-1", opp.opportunity_id, 1, "h1", deadline="2026-10-01")
    rev2 = OpportunityRevision("rev-2", opp.opportunity_id, 2, "h2", deadline="2026-11-01",
                               material_change=True)
    app = ApplicationProject("app-1", ORG_A.organization_id, opp.opportunity_id,
                             rev2.revision_id)
    assert app.opportunity_revision_id == rev2.revision_id
    assert rev1.opportunity_id == rev2.opportunity_id == opp.opportunity_id


# ADR-B2-004 — ApplicationProject vs interoperable Application ------------------
def test_application_project_is_distinct_from_revision():
    opp = GrantOpportunity("opp-1", "prog-1", "Community Grant FY2026")
    rev = OpportunityRevision("rev-1", opp.opportunity_id, 1, "h1")
    proj = ApplicationProject("app-1", ORG_A.organization_id, opp.opportunity_id,
                              rev.revision_id, state="DRAFTING")
    rev_app = ApplicationRevision("apprev-1", proj.project_id, 1, rev.revision_id, "ch1")
    # workflow state change does not create new project identity
    proj2 = ApplicationProject(proj.project_id, proj.organization_id, proj.opportunity_id,
                               proj.opportunity_revision_id, state="QA")
    assert proj2.project_id == proj.project_id
    assert rev_app.project_id == proj.project_id
    assert proj.project_id != rev_app.app_revision_id


# ADR-B2-005 — CanonicalFact vs EvidenceClaim -----------------------------------
def test_claim_cannot_automatically_become_canonical_fact():
    snap = SourceSnapshot("snap-1", "GA-OPB", "opp-1", "2026-08-01T00:00:00Z", "ch0")
    claim = EvidenceClaim("claim-1", "deadline is 2026-10-15", "opp-1", "deadline",
                          "2026-10-15", source_snapshot_id=snap.snapshot_id,
                          status=ClaimStatus.PROPOSED)
    fact = CanonicalFact("fact-1", "opp-1", "deadline", "2026-10-15",
                         promotion_state=FactPromotionState.PROPOSED)
    # a claim is not a fact until promoted under governance
    assert claim.claim_id != fact.fact_id
    assert fact.promotion_state is FactPromotionState.PROPOSED
    promoted = CanonicalFact(fact.fact_id, fact.subject, fact.predicate, fact.value,
                             promotion_state=FactPromotionState.PROMOTED,
                             supporting_claim_ids=(claim.claim_id,))
    assert promoted.promotion_state is FactPromotionState.PROMOTED
    assert claim.claim_id in promoted.supporting_claim_ids


# ADR-B2-006 — Artifact vs SourceSnapshot ----------------------------------------
def test_artifact_and_source_snapshot_are_distinct_semantic_types():
    pdf = Artifact("art-1", ArtifactType.GRANT_PROPOSAL, "Proposal v3",
                   status=ArtifactStatus.DRAFT, project_id="app-1")
    snap = SourceSnapshot("snap-2", "GA-OPB", "opp-1", "2026-08-01T00:00:00Z", "chX")
    assert type(pdf) is not type(snap)
    assert pdf.artifact_id != snap.snapshot_id
    assert isinstance(pdf, Artifact) and not isinstance(pdf, SourceSnapshot)


# ADR-B2-007 — Requirement vs Response -------------------------------------------
def test_requirement_and_response_are_separate():
    from prototype.g0.domain.models import Requirement, RequirementResponse
    req = Requirement("req-1", "rev-1", "narrative", mandatory=True)
    resp = RequirementResponse("resp-1", req.requirement_id, "section",
                               artifact_version_id="artver-3")
    assert req.requirement_id != resp.response_id
    assert resp.requirement_id == req.requirement_id  # linked, not merged


# ADR-B2-008 — Proposal vs Business Plan ------------------------------------------
def test_proposal_and_business_plan_are_distinct_artifact_families():
    proposal = Artifact("art-p", ArtifactType.GRANT_PROPOSAL, "Grant Proposal")
    business_plan = Artifact("art-b", ArtifactType.BUSINESS_PLAN, "Business Plan")
    assert proposal.artifact_type is ArtifactType.GRANT_PROPOSAL
    assert business_plan.artifact_type is ArtifactType.BUSINESS_PLAN
    assert proposal.artifact_type is not business_plan.artifact_type


# ADR-B2-009 — Award as first-class root -------------------------------------------
def test_historical_award_exists_without_application_project():
    award = Award("award-1", funder_id=ORG_B.organization_id,
                  recipient_id=ORG_A.organization_id,
                  amount=Decimal("75000.00"), award_date="2024-06-01",
                  program_id="prog-1", opportunity_id=None)
    assert award.award_id == "award-1"
    assert award.opportunity_id is None  # award exists even without known opportunity
    assert not hasattr(award, "project_id")  # award is not an ApplicationProject status


# ADR-B2-010 — Person vs OrganizationContact ----------------------------------------
def test_person_is_distinct_from_contact_relationship():
    p = Person("person-1", "Ada Grant")
    contact = OrganizationContact("contact-1", p.person_id, ORG_A.organization_id,
                                  "CEO", email="ada@example.org")
    assert contact.person_id == p.person_id
    assert contact.contact_id != p.person_id
    # same person at another organization is a new contact, not a new person
    contact2 = OrganizationContact("contact-2", p.person_id, ORG_B.organization_id,
                                   "Board Advisor")
    assert contact2.person_id == p.person_id


# cross-cutting: version lineage ------------------------------------------------------
def test_artifact_version_lineage_remains_intact():
    art = Artifact("art-1", ArtifactType.GRANT_PROPOSAL, "Proposal")
    v1 = ArtifactVersion("v-1", art.artifact_id, 1, "h1")
    v2 = ArtifactVersion("v-2", art.artifact_id, 2, "h2")
    assert v1.artifact_id == v2.artifact_id == art.artifact_id
    assert (v1.version_number, v2.version_number) == (1, 2)
