"""G0 Book 2 — domain semantic model (provisional executable form).

Dependency-free frozen dataclasses matching the B2.C3 entity catalog.
Money is Decimal-only (B2.C12); identity uses opaque stable IDs (B2.C4);
semantic shape is authoritative here, persistence is a later book.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


class OrganizationKind(str, enum.Enum):
    NONPROFIT = "nonprofit"
    BUSINESS = "business"
    GOVERNMENT = "government_entity"
    EDUCATIONAL = "educational_institution"
    TRIBAL = "tribal_entity"
    FISCAL_SPONSOR = "fiscal_sponsor"
    FOUNDATION = "foundation"
    OTHER = "other_governed_extension"


class RoleType(str, enum.Enum):
    FUNDER = "funder"
    APPLICANT = "applicant"
    RECIPIENT = "recipient"
    PARTNER = "partner"
    FISCAL_SPONSOR = "fiscal_sponsor"


class EntityStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    SUPERSEDED = "SUPERSEDED"


class ResolutionStatus(str, enum.Enum):
    MATCH_CONFIRMED = "MATCH_CONFIRMED"
    MATCH_PROBABLE_REVIEW = "MATCH_PROBABLE_REVIEW"
    DISTINCT_CONFIRMED = "DISTINCT_CONFIRMED"
    UNRESOLVED = "UNRESOLVED"


class ClaimStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    VERIFIED = "VERIFIED"
    CONFLICTED = "CONFLICTED"
    RETRACTED = "RETRACTED"


class FactPromotionState(str, enum.Enum):
    PROPOSED = "PROPOSED"
    PROMOTED = "PROMOTED"
    CONFLICTED = "CONFLICTED"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"


class EligibilityStatus(str, enum.Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    CONDITIONAL = "CONDITIONAL"
    UNKNOWN = "UNKNOWN"


class ArtifactType(str, enum.Enum):
    RESEARCH_REPORT = "research_report"
    MATCH_EXPLANATION = "match_explanation"
    APPLICATION_BLUEPRINT = "application_blueprint"
    GRANT_PROPOSAL = "grant_proposal"
    BUSINESS_PLAN = "business_plan"
    PITCH_DECK = "pitch_deck"
    BUDGET_FINANCIAL = "budget_financial"
    PARTNERSHIP_MATERIAL = "partnership_material"
    TESTIMONIAL_MATERIAL = "testimonial_material"
    GOAL_SHEET = "goal_sheet"
    QA_REPORT = "qa_report"
    SUBMISSION_PACKAGE = "submission_package"
    CLIENT_EXPLANATION = "client_explanation"


class ArtifactStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    QA_PENDING = "QA_PENDING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED_INTERNAL = "APPROVED_INTERNAL"
    SUBMISSION_READY = "SUBMISSION_READY"
    SUPERSEDED = "SUPERSEDED"
    MOCK = "MOCK"                       # D0 shadow-draft artifacts


class OutcomeType(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    AWARDED = "AWARDED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    NOT_SUBMITTED = "NOT_SUBMITTED"
    UNKNOWN = "UNKNOWN"


class VerificationState(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    CLAIMED = "CLAIMED"
    VERIFIED = "VERIFIED"
    CONFLICTED = "CONFLICTED"


# --- Business actors ---------------------------------------------------------

@dataclass(frozen=True)
class Organization:
    organization_id: str
    organization_kind: OrganizationKind
    legal_name: str
    preferred_display_name: str
    status: EntityStatus = EntityStatus.ACTIVE
    jurisdiction: str | None = None
    formation_date: str | None = None
    primary_location: str | None = None


@dataclass(frozen=True)
class Person:
    person_id: str
    full_name: str
    # deliberately minimal PII in core schema (B2.C3)


@dataclass(frozen=True)
class OrganizationRole:
    """Contextual role binding an Organization to another object/period."""
    role_id: str
    organization_id: str
    role_type: RoleType
    target_ref: str | None = None      # e.g. program/project/award ref
    valid_from: str | None = None
    valid_to: str | None = None


@dataclass(frozen=True)
class OrganizationContact:
    """Contextual Person↔Organization link with role/reachability."""
    contact_id: str
    person_id: str
    organization_id: str
    role: str
    email: str | None = None


# --- Funding structure --------------------------------------------------------

@dataclass(frozen=True)
class Program:
    program_id: str
    name: str
    assistance_listing: str | None = None   # ALN where applicable
    agency: str | None = None
    status: EntityStatus = EntityStatus.ACTIVE


@dataclass(frozen=True)
class GrantOpportunity:
    opportunity_id: str
    program_id: str | None
    title: str
    status: EntityStatus = EntityStatus.ACTIVE
    funding_instrument: str | None = None
    funding_category: str | None = None


@dataclass(frozen=True)
class OpportunityRevision:
    revision_id: str
    opportunity_id: str
    revision_number: int
    terms_hash: str
    deadline: str | None = None
    funding_ceiling: Decimal | None = None
    material_change: bool = False


# --- Eligibility --------------------------------------------------------------

@dataclass(frozen=True)
class EligibilityRule:
    rule_id: str
    rule_type: str
    subject_type: str
    operator: str
    expected_value: Any
    unit_or_namespace: str | None = None
    required_fact_types: tuple[str, ...] = ()
    source_requirement_ref: str | None = None
    severity: str = "REQUIRED"
    explanation_template: str = ""


@dataclass(frozen=True)
class EligibilityRuleSet:
    rule_set_id: str
    opportunity_revision_id: str
    version: int
    rules: tuple[EligibilityRule, ...] = ()


@dataclass(frozen=True)
class EligibilityDecision:
    decision_id: str
    organization_id: str
    opportunity_revision_id: str
    rule_set_id: str
    rule_set_version: int
    result: EligibilityStatus
    per_rule_results: tuple[tuple[str, EligibilityStatus], ...] = ()
    explanation: str = ""


# --- Awards -------------------------------------------------------------------

@dataclass(frozen=True)
class Award:
    award_id: str
    funder_id: str
    recipient_id: str
    amount: Decimal
    currency: str = "USD"
    award_date: str | None = None
    program_id: str | None = None
    opportunity_id: str | None = None
    external_award_ids: tuple["ExternalIdentifier", ...] = ()


# --- Application --------------------------------------------------------------

@dataclass(frozen=True)
class ApplicationProject:
    project_id: str
    organization_id: str
    opportunity_id: str
    opportunity_revision_id: str       # exact revision targeted (B2.C8)
    state: str = "IDEA"


@dataclass(frozen=True)
class ApplicationRevision:
    app_revision_id: str
    project_id: str
    revision_number: int
    opportunity_revision_id: str
    content_hash: str


# --- Requirements / budget ----------------------------------------------------

@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    opportunity_revision_id: str
    requirement_type: str
    source_location: str | None = None
    mandatory: bool = True
    prompt: str = ""
    state: str = "IDENTIFIED"


@dataclass(frozen=True)
class RequirementResponse:
    response_id: str
    requirement_id: str
    response_type: str                 # section | form | budget | attachment | certification | support_letter
    artifact_version_id: str | None = None
    state: str = "IN_PROGRESS"


@dataclass(frozen=True)
class BudgetLine:
    line_id: str
    category: str
    amount: Decimal                    # Decimal only — no float money
    currency: str = "USD"
    period: str | None = None
    assumption_ref: str | None = None


@dataclass(frozen=True)
class Budget:
    budget_id: str
    project_id: str
    version: int = 1
    currency: str = "USD"
    lines: tuple[BudgetLine, ...] = ()

    @property
    def total(self) -> Decimal:
        return sum((line.amount for line in self.lines), Decimal("0"))


# --- Evidence ------------------------------------------------------------------

@dataclass(frozen=True)
class SourceSnapshot:
    snapshot_id: str
    source: str
    entity_ref: str
    captured_at: str
    content_hash: str


@dataclass(frozen=True)
class EvidenceClaim:
    claim_id: str
    proposition: str
    subject: str
    predicate: str
    value: Any
    source_snapshot_id: str | None = None
    status: ClaimStatus = ClaimStatus.PROPOSED
    value_type: str = "string"


@dataclass(frozen=True)
class CanonicalFact:
    fact_id: str
    subject: str
    predicate: str
    value: Any
    value_type: str = "string"
    scope: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None
    promotion_state: FactPromotionState = FactPromotionState.PROPOSED
    supporting_claim_ids: tuple[str, ...] = ()
    contradicting_claim_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class StatisticObservation:
    stat_id: str
    metric: str
    value: Decimal
    unit: str
    geography: str
    reference_period: str
    population: str | None = None
    dataset_version: str | None = None
    methodology: str | None = None


# --- Artifacts ------------------------------------------------------------------

@dataclass(frozen=True)
class ArtifactVersion:
    version_id: str
    artifact_id: str
    version_number: int
    content_hash: str
    format: str = "markdown"
    is_mock: bool = False


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    artifact_type: ArtifactType
    logical_name: str
    status: ArtifactStatus = ArtifactStatus.DRAFT
    project_id: str | None = None
    current_version_ref: str | None = None
    created_by: str | None = None
    created_at: str | None = None


@dataclass(frozen=True)
class SubmissionPackage:
    package_id: str
    project_id: str
    artifact_version_refs: tuple[str, ...] = ()
    readiness_state: str = "INCOMPLETE"   # never implies submitted


# --- Outcomes -------------------------------------------------------------------

@dataclass(frozen=True)
class OutcomeFeedback:
    outcome_id: str
    outcome_type: OutcomeType
    observed_at: str
    project_id: str | None = None
    award_id: str | None = None
    verified_at: str | None = None
    reason_codes: tuple[str, ...] = ()
    freeform_feedback: str | None = None


# --- Identity / relationships -------------------------------------------------------

@dataclass(frozen=True)
class ExternalIdentifier:
    namespace: str
    value: str
    entity_type: str
    issuer: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    verification_state: VerificationState = VerificationState.UNVERIFIED
    source_lineage: str | None = None


@dataclass(frozen=True)
class Relationship:
    relationship_id: str
    relationship_type: str
    source_ref: str
    target_ref: str
    tenant_id: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    provenance_required: bool = True
