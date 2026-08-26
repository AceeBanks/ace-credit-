"""G0 Book 2 — B2.C19 D0 Shadow Draft Readiness Contract.

Book 2 does NOT build the drafting harness; it defines the minimum domain
bundle the D0 harness must consume. DraftContextBundle is representable
without agent memory — it is a plain immutable dataclass assembled from
canonical domain objects.

validate_draft_context() applies the D0 rules fail-closed:
  - exact opportunity revision required
  - eligibility cannot be INELIGIBLE (unresolved -> incomplete)
  - mandatory requirement list present
  - unsupported facts flagged, never silently filled
  - material assertions link evidence where practical
  - output artifact state DRAFT/MOCK; no submission state/capability
"""
from __future__ import annotations

from dataclasses import dataclass

from prototype.g0.domain.models import (
    Artifact,
    ArtifactStatus,
    Budget,
    CanonicalFact,
    EligibilityDecision,
    EligibilityStatus,
    EvidenceClaim,
    GrantOpportunity,
    OpportunityRevision,
    Organization,
    Program,
    ProposalSection,
    Requirement,
    StatisticObservation,
)


@dataclass(frozen=True)
class DraftContextBundle:
    organization: Organization
    opportunity: GrantOpportunity
    opportunity_revision: OpportunityRevision
    canonical_facts: tuple[CanonicalFact, ...] = ()
    eligibility_decision: EligibilityDecision | None = None
    requirements: tuple[Requirement, ...] = ()
    funder_program: Program | None = None
    evidence: tuple[EvidenceClaim, ...] = ()
    statistics: tuple[StatisticObservation, ...] = ()
    budget: Budget | None = None
    research_findings: tuple[CanonicalFact, ...] = ()
    proposal_template: tuple[ProposalSection, ...] = ()
    output_artifacts: tuple[Artifact, ...] = ()


def validate_draft_context(bundle: DraftContextBundle) -> list[str]:
    """D0 rules, fail closed. Returns a list of violations (empty = ready)."""
    violations: list[str] = []

    # exact opportunity revision required
    if bundle.opportunity_revision is None:
        violations.append("missing opportunity revision")
    elif bundle.opportunity_revision.opportunity_id != bundle.opportunity.opportunity_id:
        violations.append("opportunity revision belongs to a different opportunity")

    # eligibility cannot be INELIGIBLE; unresolved marks mock incomplete
    if bundle.eligibility_decision is None:
        violations.append("incomplete: mandatory eligibility unresolved")
    elif bundle.eligibility_decision.result is EligibilityStatus.INELIGIBLE:
        violations.append("eligibility is INELIGIBLE")
    elif bundle.opportunity_revision is not None \
            and bundle.eligibility_decision.opportunity_revision_id \
            != bundle.opportunity_revision.revision_id:
        violations.append("eligibility decision targets a different revision")

    # mandatory requirement list present
    if not bundle.requirements:
        violations.append("incomplete: no requirements in bundle")
    elif not any(r.mandatory for r in bundle.requirements):
        violations.append("incomplete: no mandatory requirements present")

    # unsupported facts flagged, never silently filled
    for fact in bundle.canonical_facts:
        if not fact.supporting_claim_ids:
            violations.append(f"unsupported fact '{fact.fact_id}' (no supporting claims)")

    # material assertions link evidence where practical
    for finding in bundle.research_findings:
        if finding.promotion_state.value == "PROMOTED" and not finding.supporting_claim_ids:
            violations.append(f"material assertion '{finding.fact_id}' lacks evidence links")

    # output state DRAFT/MOCK; no submission state/capability
    for artifact in bundle.output_artifacts:
        if artifact.status not in (ArtifactStatus.DRAFT, ArtifactStatus.MOCK):
            violations.append(f"artifact '{artifact.artifact_id}' state "
                              f"{artifact.status.value} is not DRAFT/MOCK")
        if "submission" in (artifact.artifact_type.value or ""):
            violations.append(f"submission artifact '{artifact.artifact_id}' in D0 bundle")

    return violations
