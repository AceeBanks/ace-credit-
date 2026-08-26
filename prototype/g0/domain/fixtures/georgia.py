"""B2.C17 Scenario GA-1 — Georgia nonprofit pursuing a state opportunity.

Organization + verified identifiers + Georgia opportunity/revision + eligibility
rules + requirements + ApplicationProject + proposal/business-plan artifacts.
Semantic example only — not a live adapter.
"""
from __future__ import annotations

from decimal import Decimal

from prototype.g0.domain.models import (
    ApplicationProject,
    Artifact,
    ArtifactStatus,
    ArtifactType,
    ArtifactVersion,
    CanonicalFact,
    ClaimStatus,
    EligibilityDecision,
    EligibilityRule,
    EligibilityRuleSet,
    EligibilityStatus,
    EntityStatus,
    EvidenceClaim,
    ExternalIdentifier,
    FactPromotionState,
    GrantOpportunity,
    OpportunityRevision,
    Organization,
    OrganizationKind,
    Requirement,
    VerificationState,
)

GA_NONPROFIT = Organization(
    organization_id="org_ga_1001",
    organization_kind=OrganizationKind.NONPROFIT,
    legal_name="Community Youth Works, Inc.",
    preferred_display_name="Community Youth Works",
    status=EntityStatus.ACTIVE,
    jurisdiction="Georgia",
    formation_date="2012-04-17",
    primary_location="Atlanta, GA",
)

GA_EIN = ExternalIdentifier(namespace="IRS_EIN", value="58-2345671",
                            entity_type="Organization",
                            verification_state=VerificationState.VERIFIED,
                            issuer="IRS", source_lineage="snap-ga-1")
GA_STATE_ID = ExternalIdentifier(namespace="GA_SECRETARY_OF_STATE",
                                 value="1234567", entity_type="Organization",
                                 verification_state=VerificationState.VERIFIED,
                                 issuer="GA SOS", source_lineage="snap-ga-2")

GA_OPP = GrantOpportunity(
    opportunity_id="opp_ga_501",
    program_id="prog_ga_9",
    title="Georgia Rural Community Impact Grant FY2026",
    status=EntityStatus.ACTIVE,
    funding_instrument="grant",
    funding_category="state",
)

GA_OPP_REV1 = OpportunityRevision(
    revision_id="opp_rev_ga_501_1",
    opportunity_id=GA_OPP.opportunity_id,
    revision_number=1,
    terms_hash="sha256:ga-opp-501-rev1",
    deadline="2026-10-15",
    funding_ceiling=Decimal("50000.00"),
    material_change=False,
)

GA_RULE_GEO = EligibilityRule(
    rule_id="rule_ga_1",
    rule_type="requirement",
    subject_type="Organization",
    operator="WITHIN_GEOGRAPHY",
    expected_value=["Georgia"],
    unit_or_namespace="state",
    required_fact_types=("primary_location",),
    source_requirement_ref="ga-solicitation-sec-3",
    severity="REQUIRED",
    explanation_template="Organization must operate within {expected_value}.",
)
GA_RULE_KIND = EligibilityRule(
    rule_id="rule_ga_2",
    rule_type="requirement",
    subject_type="Organization",
    operator="EQUALS",
    expected_value="nonprofit",
    unit_or_namespace=None,
    required_fact_types=("organization_kind",),
    source_requirement_ref="ga-solicitation-sec-3",
    severity="REQUIRED",
    explanation_template="Applicant must be a nonprofit.",
)

GA_RULE_SET = EligibilityRuleSet(
    rule_set_id="ruleset_ga_501",
    opportunity_revision_id=GA_OPP_REV1.revision_id,
    version=1,
    rules=(GA_RULE_GEO, GA_RULE_KIND),
)

GA_DECISION = EligibilityDecision(
    decision_id="eldec_ga_1",
    organization_id=GA_NONPROFIT.organization_id,
    opportunity_revision_id=GA_OPP_REV1.revision_id,
    rule_set_id=GA_RULE_SET.rule_set_id,
    rule_set_version=1,
    result=EligibilityStatus.ELIGIBLE,
    per_rule_results=(("rule_ga_1", EligibilityStatus.ELIGIBLE),
                      ("rule_ga_2", EligibilityStatus.ELIGIBLE)),
    explanation="rule_ga_1=ELIGIBLE; rule_ga_2=ELIGIBLE",
)

GA_REQ_NARRATIVE = Requirement(
    requirement_id="req_ga_1",
    opportunity_revision_id=GA_OPP_REV1.revision_id,
    requirement_type="narrative",
    source_location="ga-solicitation-sec-5a",
    mandatory=True,
    prompt="Describe the community impact of your program.",
    state="NORMALIZED",
    word_limit=2000,
)

GA_PROJECT = ApplicationProject(
    project_id="app_ga_1",
    organization_id=GA_NONPROFIT.organization_id,
    opportunity_id=GA_OPP.opportunity_id,
    opportunity_revision_id=GA_OPP_REV1.revision_id,
    state="DRAFTING",
)

GA_PROPOSAL = Artifact(
    artifact_id="artifact_ga_1",
    artifact_type=ArtifactType.GRANT_PROPOSAL,
    logical_name="FY2026 Rural Community Impact Proposal",
    status=ArtifactStatus.DRAFT,
    project_id=GA_PROJECT.project_id,
)
GA_PROPOSAL_V1 = ArtifactVersion(
    version_id="artver_ga_1",
    artifact_id=GA_PROPOSAL.artifact_id,
    version_number=1,
    content_hash="sha256:ga-proposal-v1",
    format="markdown",
)

GA_BUSINESS_PLAN = Artifact(
    artifact_id="artifact_ga_2",
    artifact_type=ArtifactType.BUSINESS_PLAN,
    logical_name="Community Youth Works Business Plan",
    status=ArtifactStatus.DRAFT,
    project_id=GA_PROJECT.project_id,
)

GA_CLAIM = EvidenceClaim(
    claim_id="claim_ga_1",
    proposition="Organization has 501(c)(3) status",
    subject=GA_NONPROFIT.organization_id,
    predicate="is_501c3",
    value="true",
    source_snapshot_id="snap-ga-1",
    status=ClaimStatus.VERIFIED,
    value_type="boolean",
)

GA_FACT = CanonicalFact(
    fact_id="fact_ga_1",
    subject=GA_NONPROFIT.organization_id,
    predicate="is_501c3",
    value="true",
    value_type="boolean",
    scope=GA_NONPROFIT.organization_id,
    promotion_state=FactPromotionState.PROMOTED,
    supporting_claim_ids=(GA_CLAIM.claim_id,),
)

GA_1 = {
    "name": "GA-1 Georgia nonprofit pursuing state opportunity",
    "organization": GA_NONPROFIT,
    "identifiers": [GA_EIN, GA_STATE_ID],
    "opportunity": GA_OPP,
    "revision": GA_OPP_REV1,
    "rule_set": GA_RULE_SET,
    "decision": GA_DECISION,
    "requirements": [GA_REQ_NARRATIVE],
    "project": GA_PROJECT,
    "artifacts": [GA_PROPOSAL, GA_BUSINESS_PLAN],
    "fact": GA_FACT,
    "claim": GA_CLAIM,
}
