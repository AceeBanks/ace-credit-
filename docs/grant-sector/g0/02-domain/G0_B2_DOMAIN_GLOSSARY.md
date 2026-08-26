# G0 Book 2 — Domain Glossary & Ubiquitous Language (B2.C1)

**Source of truth:** `config/g0/domain/glossary.yaml` (machine-readable; this
doc renders its structure)
**Validator:** `tools/g0/validate_domain.py::validate_glossary`
**Tests:** `tests/g0/book2/test_domain_glossary.py`

## Purpose

Freeze the vocabulary used by humans, agents, code, tests and UI so the same
word can never mean different things across the system. Book 2 eliminates the
failure class where Hermes calls a funding program an opportunity while an
adapter calls the same object a grant.

## Glossary classes (42 canonical terms)

| Class | Terms |
|---|---|
| Business actors & organizations | Organization, Person, OrganizationRole, Funder, Recipient, Applicant, Partner, Contact |
| Funding structure | Program, AssistanceListing, GrantOpportunity, OpportunityRevision, Award, FundingInstrument, FundingCategory |
| Eligibility | EligibilityRule, EligibilityRuleSet, EligibilityDecision, EligibilityEvidence, EligibilityStatus |
| Application production | ApplicationProject, ApplicationRevision, Requirement, RequirementResponse, ProposalSection, BusinessPlanSection, Budget, BudgetLine, Artifact, ArtifactVersion, SubmissionPackage |
| Evidence | SourceSnapshot, EvidenceClaim, CanonicalFact, StatisticObservation, EvidenceLink, ConflictState |
| Outcomes | OutcomeFeedback, AwardOutcome, RejectionOutcome, RevisionRequest |

Every entry carries: `term`, `definition`, `what_it_is_not`,
`identity_scope`, `mutable_attributes`, `source_of_truth_book`, `examples`,
`common_confusions`.

## Mandatory distinctions (enforced by test)

- Program ≠ GrantOpportunity ≠ OpportunityRevision ≠ Award
- ApplicationProject ≠ ApplicationRevision ≠ SubmissionPackage
- Requirement ≠ ProposalSection; RequirementResponse is the satisfaction mechanism
- EvidenceClaim ≠ CanonicalFact; StatisticObservation ≠ generic Fact
- Artifact ≠ SourceSnapshot
- Organization ≠ Funder/Recipient/Applicant/Partner (those are **roles**)
- Proposal ≠ BusinessPlan; Draft ≠ Approved Final; Submission-ready ≠ Submitted

## Banned ambiguous aliases

`grant`, `grant_application`, `solicitation`, `awardee`, `grantee`, `rfp`,
`nofo` — ambiguous aliases that must be replaced with the canonical term
(GrantOpportunity, Award, ApplicationProject, Recipient). Never used as
canonical terms (enforced).

## Book 1 linkage

Every capability resource type from Book 1's capability registry maps to a
glossary term (e.g. `opportunity` → GrantOpportunity, `evidence_record` →
EvidenceClaim, `submission_package` → SubmissionPackage). Verified by
`test_every_book1_capability_resource_type_maps_to_glossary`.
