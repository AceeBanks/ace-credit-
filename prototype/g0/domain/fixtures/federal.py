"""B2.C17 Scenarios FED-1 + AWARD-1 — federal opportunity with assistance
listing; historical winner intelligence. Semantic examples only.
"""
from __future__ import annotations

from decimal import Decimal

from prototype.g0.domain.models import (
    ApplicationProject,
    Award,
    EligibilityRule,
    EligibilityRuleSet,
    EntityStatus,
    ExternalIdentifier,
    GrantOpportunity,
    OpportunityRevision,
    Organization,
    OrganizationKind,
    Program,
    VerificationState,
)

# FED-1 ------------------------------------------------------------------------

FED_PROGRAM = Program(
    program_id="prog_fed_93",
    name="Community Services Block Grant",
    assistance_listing="93.569",
    agency="HHS/ACF",
    status=EntityStatus.ACTIVE,
)

FED_OPP = GrantOpportunity(
    opportunity_id="opp_fed_7001",
    program_id=FED_PROGRAM.program_id,
    title="CSBG Formula Grant FY2026",
    status=EntityStatus.ACTIVE,
    funding_instrument="grant",
    funding_category="federal",
)

FED_OPP_REV1 = OpportunityRevision(
    revision_id="opp_rev_fed_7001_1",
    opportunity_id=FED_OPP.opportunity_id,
    revision_number=1,
    terms_hash="sha256:fed-opp-7001-rev1",
    deadline="2026-06-30",
    funding_ceiling=Decimal("1500000.00"),
    material_change=False,
)

FED_RULE = EligibilityRule(
    rule_id="rule_fed_1",
    rule_type="requirement",
    subject_type="Organization",
    operator="NOT_EXISTS",
    expected_value=None,
    unit_or_namespace=None,
    required_fact_types=("debarment_flag",),
    source_requirement_ref="fed-2cfr200",
    severity="REQUIRED",
    explanation_template="Applicant must not be debarred or suspended.",
)

FED_RULE_SET = EligibilityRuleSet(
    rule_set_id="ruleset_fed_7001",
    opportunity_revision_id=FED_OPP_REV1.revision_id,
    version=1,
    rules=(FED_RULE,),
)

FED_PROJECT = ApplicationProject(
    project_id="app_fed_1",
    organization_id="org_fed_1",
    opportunity_id=FED_OPP.opportunity_id,
    opportunity_revision_id=FED_OPP_REV1.revision_id,
    state="RESEARCH",
)

FED_1 = {
    "name": "FED-1 Federal opportunity with assistance listing",
    "program": FED_PROGRAM,
    "opportunity": FED_OPP,
    "revision": FED_OPP_REV1,
    "rule_set": FED_RULE_SET,
    "project": FED_PROJECT,
}

# AWARD-1 ----------------------------------------------------------------------

AWARD_FUNDER = Organization(
    organization_id="org_fed_2",
    organization_kind=OrganizationKind.GOVERNMENT,
    legal_name="Appalachian Regional Commission",
    preferred_display_name="ARC",
    status=EntityStatus.ACTIVE,
)

AWARD_RECIPIENT = Organization(
    organization_id="org_ga_2002",
    organization_kind=OrganizationKind.NONPROFIT,
    legal_name="North Georgia Food Bank, Inc.",
    preferred_display_name="North Georgia Food Bank",
    status=EntityStatus.ACTIVE,
    jurisdiction="Georgia",
)

AWARD_OPP = GrantOpportunity(
    opportunity_id="opp_arc_88",
    program_id="prog_arc_1",
    title="ARC POWER Initiative",
    status=EntityStatus.ACTIVE,
)

AWARD_RECORD = Award(
    award_id="award_arc_441",
    funder_id=AWARD_FUNDER.organization_id,
    recipient_id=AWARD_RECIPIENT.organization_id,
    amount=Decimal("750000.00"),
    currency="USD",
    award_date="2024-09-30",
    program_id="prog_arc_1",
    opportunity_id=AWARD_OPP.opportunity_id,
    external_award_ids=(
        ExternalIdentifier(namespace="USAspending", value="ARC-2024-441",
                           entity_type="Award",
                           verification_state=VerificationState.VERIFIED,
                           issuer="USAspending", source_lineage="snap-fed-9"),
    ),
)

AWARD_1 = {
    "name": "AWARD-1 Historical winner intelligence",
    "funder": AWARD_FUNDER,
    "recipient": AWARD_RECIPIENT,
    "opportunity": AWARD_OPP,
    "award": AWARD_RECORD,
}
