"""B2.C19 tests — D0 Shadow Draft Readiness Contract.

Book 2 defines the minimum domain bundle the D0 harness must consume; the
Georgia-first DraftContextBundle fixture validates clean, and each D0 rule
violation is proven fail-closed.
"""
from __future__ import annotations

import copy
from dataclasses import replace

from prototype.g0.domain.draft_context import (
    DraftContextBundle,
    validate_draft_context,
)
from prototype.g0.domain.fixtures.draft_context import GA_DRAFT_BUNDLE
from prototype.g0.domain.fixtures.georgia import (
    GA_DECISION,
    GA_OPP,
    GA_OPP_REV1,
)
from prototype.g0.domain.models import (
    Artifact,
    ArtifactStatus,
    ArtifactType,
    CanonicalFact,
    EligibilityStatus,
    FactPromotionState,
    OpportunityRevision,
)
from tools.g0.validate_domain import (
    load_draft_context_policy,
    validate_draft_context_policy,
)

POLICY = load_draft_context_policy()


def test_live_draft_context_policy_passes():
    ok, report = validate_draft_context_policy(POLICY)
    assert ok, report["errors"]
    assert report["d0_rule_count"] == 7


def test_georgia_first_bundle_is_ready():
    violations = validate_draft_context(GA_DRAFT_BUNDLE)
    assert violations == [], violations


def test_bundle_is_representable_without_agent_memory():
    # a plain frozen dataclass: reconstructable from fields alone
    b = DraftContextBundle(
        organization=GA_DRAFT_BUNDLE.organization,
        opportunity=GA_DRAFT_BUNDLE.opportunity,
        opportunity_revision=GA_DRAFT_BUNDLE.opportunity_revision,
        canonical_facts=GA_DRAFT_BUNDLE.canonical_facts,
        eligibility_decision=GA_DRAFT_BUNDLE.eligibility_decision,
        requirements=GA_DRAFT_BUNDLE.requirements,
        proposal_template=GA_DRAFT_BUNDLE.proposal_template,
    )
    rebuilt = replace(b)
    assert rebuilt == b                      # no hidden state, no memory needed


def test_missing_opportunity_revision_fails():
    b = replace(GA_DRAFT_BUNDLE, opportunity_revision=None)
    violations = validate_draft_context(b)
    assert any("missing opportunity revision" in v for v in violations)


def test_mismatched_eligibility_revision_fails():
    other_rev = OpportunityRevision("opp_rev_ga_501_9", GA_OPP.opportunity_id, 9,
                                    "sha256:other", deadline="2027-01-01")
    b = replace(GA_DRAFT_BUNDLE, opportunity_revision=other_rev)
    violations = validate_draft_context(b)
    assert any("belongs to a different opportunity" in v for v in violations) or \
        any("different revision" in v for v in violations)


def test_ineligible_eligibility_fails():
    decision = replace(GA_DECISION, result=EligibilityStatus.INELIGIBLE)
    b = replace(GA_DRAFT_BUNDLE, eligibility_decision=decision)
    violations = validate_draft_context(b)
    assert any("INELIGIBLE" in v for v in violations)


def test_missing_mandatory_requirement_list_marks_incomplete():
    b = replace(GA_DRAFT_BUNDLE, requirements=())
    violations = validate_draft_context(b)
    assert any("no requirements" in v for v in violations)
    # non-mandatory-only list is also incomplete
    b2 = replace(GA_DRAFT_BUNDLE,
                 requirements=(replace(GA_DRAFT_BUNDLE.requirements[0],
                                       mandatory=False),))
    violations = validate_draft_context(b2)
    assert any("no mandatory requirements" in v for v in violations)


def test_unsupported_organization_fact_flagged():
    unsupported = CanonicalFact("fact_ga_x", "org_ga_1001", "founding_year",
                                "2012", value_type="string",
                                promotion_state=FactPromotionState.PROPOSED)
    b = replace(GA_DRAFT_BUNDLE,
                canonical_facts=(GA_DRAFT_BUNDLE.canonical_facts[0], unsupported))
    violations = validate_draft_context(b)
    assert any("unsupported fact" in v for v in violations)


def test_output_artifact_state_must_be_draft_or_mock():
    bad = Artifact("artifact_ga_9", ArtifactType.GRANT_PROPOSAL, "Proposal",
                   status=ArtifactStatus.SUBMISSION_READY)
    b = replace(GA_DRAFT_BUNDLE, output_artifacts=(bad,))
    violations = validate_draft_context(b)
    assert any("not DRAFT/MOCK" in v for v in violations)
    # submission-family artifact is rejected even in DRAFT
    pkg = Artifact("artifact_ga_10", ArtifactType.SUBMISSION_PACKAGE, "Pkg",
                   status=ArtifactStatus.DRAFT)
    b2 = replace(GA_DRAFT_BUNDLE, output_artifacts=(pkg,))
    violations = validate_draft_context(b2)
    assert any("submission artifact" in v for v in violations)


def test_proposal_and_business_plan_contexts_distinguishable():
    # the bundle's proposal template is ProposalSection-based; the business
    # plan artifact is a distinct ArtifactType — never collapsed
    from prototype.g0.domain.models import ArtifactType
    types = {a.artifact_type for a in GA_DRAFT_BUNDLE.output_artifacts}
    assert ArtifactType.GRANT_PROPOSAL in types
    assert ArtifactType.BUSINESS_PLAN in types
    assert types == {ArtifactType.GRANT_PROPOSAL, ArtifactType.BUSINESS_PLAN}


# --- validator defect injection ------------------------------------------------

def test_missing_d0_rule_fails():
    data = copy.deepcopy(POLICY)
    data["d0_rules"] = [r for r in data["d0_rules"]
                        if r["rule"] != "no_submission_state"]
    ok, report = validate_draft_context_policy(data)
    assert not ok
    assert any("no_submission_state" in e for e in report["errors"])
