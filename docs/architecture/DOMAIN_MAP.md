# ACE Credit Domain Map

## Purpose
This document defines the business domains and core records that the platform is allowed to reason about. It is intentionally runtime-neutral. Hermes, OpenClaw, coding agents, and future workers interact with these domains through controlled application capabilities rather than becoming the source of truth.

## Domain principles
1. Legal entity ownership is explicit on every operational record.
2. A `Person` is not a universal dossier; access is scoped through entity-specific relationships.
3. Programs, cases, services, goals, outcomes, grants, and agent actions have explicit lifecycle states.
4. Sensitive data is separated logically from general profile data and protected by authorization policy.
5. Domain events should be auditable and useful for impact/reporting without exposing unnecessary PII.
6. Credit, debt-management, and consumer-report workflows are modeled separately from generic coaching because they may carry distinct legal requirements.
7. Grant intelligence and grant administration are separate from participant-service delivery, but may consume aggregated approved outcomes.

---

# 1. Organization & Entity Governance

## Purpose
Represent the ecosystem without collapsing separate legal organizations.

## Core objects

### Ecosystem
Strategy-level umbrella. Not used as a legal owner of money, contracts, participant records, employees, or grants.

Fields/concepts:
- `ecosystem_id`
- name/brand
- mission
- governance version

### LegalEntity
A legally distinct organization.

Examples:
- nonprofit entity
- for-profit entity

Required concepts:
- `entity_id`
- legal name
- entity type
- tax/legal identifiers stored only in secure admin context
- status
- jurisdiction(s)
- policy profile
- accounting boundary
- data-controller/owner context

### EntityRelationship
Documents lawful relationships between entities.

Examples:
- services agreement
- IP license
- shared technology agreement
- referral agreement

Never infer a relationship simply because the entities share ownership/leadership.

### PolicyVersion
Versioned organizational policies that may affect workflows, approvals, data handling, or eligibility.

---

# 2. Identity, Access & Authorization

## Purpose
Identify people/services and determine what they may access or do.

## Core objects

### Person
Minimum canonical human identity anchor.

A Person can have multiple entity-specific relationships. Cross-entity linking does not grant cross-entity access.

### UserAccount
Login identity linked to a Person or service identity.

### StaffMembership
A person's authorized role within one legal entity.

Examples:
- program director
- financial educator
- credit specialist
- coach/case manager
- outreach staff
- data/evaluation staff
- grant staff
- administrator

### PartnerMembership
Authorized external partner access, limited to explicit resources.

### Role
Named permission bundle.

### Permission
Atomic capability, e.g.:
- `participant.read_basic`
- `participant.read_survivor_sensitive`
- `case.write`
- `credit.read`
- `credit.prepare_action`
- `credit.approve_action`
- `grant.submit`
- `admin.manage_roles`

### AccessGrant
Contextual authorization linking actor, entity, resource scope, permission, dates, and rationale.

### ServiceIdentity / AgentIdentity
Non-human identity for integrations or AI runtimes.

Rules:
- no shared credentials between agents;
- permissions are environment-specific;
- production write permissions are exceptional;
- revocation must be immediate.

---

# 3. Program & Enrollment Management

## Purpose
Represent nonprofit program delivery and, later, analogous commercial engagements without forcing them into the same business rules.

## Core objects

### Program
Belongs to one entity.

Fields/concepts:
- owner entity
- name/version
- purpose
- target population
- eligibility policy
- service catalog
- outcome framework
- funding restrictions
- enrollment window
- operating dates
- active/archive state

### Cohort
Operational grouping of enrollments.

### EligibilityRuleSet
Versioned rules used to assess qualification.

### Application / Intake
Pre-enrollment information and workflow.

Suggested states:
`draft → submitted → under_review → needs_information → eligible/ineligible → accepted/declined/withdrawn`

### Enrollment
Relationship between Participant and Program.

Suggested states:
`pending → active → paused → completed → exited → terminated`

Required concepts:
- dates
- eligibility decision/version
- consent/authorization state
- funding/reporting context
- assigned staff
- reason codes for exit

### ServicePlan
Structured plan of approved services/interventions.

---

# 4. Participant Support / Case Management

## Purpose
Coordinate services while minimizing unnecessary sensitive information.

## Core objects

### Case
A bounded record tied to one entity and generally one enrollment.

Do not create one permanent cross-program dossier by default.

### CaseAssignment
Maps staff to a case with role and dates.

### Note
Must include visibility class and purpose.

Avoid free-text duplication of sensitive structured data.

### Task
Action item with owner, due date, status, source, and escalation.

States:
`open → in_progress → blocked → completed/cancelled`

### Goal
Participant-centered objective.

Required:
- category
- baseline
- target
- target date
- participant ownership/acknowledgment where appropriate
- progress history
- evidence/source

### Referral
Internal/external service handoff.

States:
`identified → offered → accepted/declined → sent → connected → outcome_known/unknown → closed`

### Resource
Verified organization/service available for referral.

### ParticipantSupport
Optional support provided to remove program participation barriers, e.g. approved transportation/childcare support. Financial disbursement is outside MVP unless separately designed.

---

# 5. Financial Education & Capability

## Purpose
Deliver education and track learning/application without representing education as individualized regulated financial advice.

## Core objects

### Curriculum
Versioned content collection.

### Module
Examples:
- budgeting
- banking
- savings
- credit
- debt
- consumer rights
- financial abuse
- fraud/scams
- financial planning

### Lesson
Instructional unit.

### Assessment
Pre/post or topic-level assessment.

### AssessmentAttempt
Stores participant responses/scores according to data-minimization rules.

### LearningAssignment
Maps required/recommended modules to an enrollment.

### Completion
Evidence that a lesson/module requirement was completed.

### FinancialActionPlan
Participant-specific, staff-reviewed plan derived from goals and education.

The plan must distinguish educational guidance from regulated recommendations where applicable.

---

# 6. Financial Stabilization

## Purpose
Track practical financial-stability goals and milestones without turning the platform into a bank/account aggregator by default.

## Core objects

### BudgetSnapshot
Optional participant-entered or staff-assisted snapshot. Prefer categories/ranges where exact values are unnecessary.

### SavingsGoal / SavingsMilestone
Tracks emergency-savings progress.

### BankingAccessMilestone
Examples:
- account opened
- account retained
- lower-cost banking established

### DebtSummary
High-level debt data for coaching/education where permitted. Detailed creditor/account data belongs in more restricted structures if needed.

### HousingStabilityMilestone
Examples:
- housing retained
- housing secured
- eviction prevention referral completed

### StabilityAssessment
Composite assessment using versioned indicators; never reducible to credit score alone.

---

# 7. Credit Recovery & Building

## Purpose
Separate credit-related operations from general education so legal permissions, authorizations, staff qualifications, and approvals can be enforced.

## Core objects

### CreditCase
Credit-specific subdomain record owned by one entity and linked to an eligible engagement/enrollment.

### ConsumerAuthorization
Versioned record of authorization/consent for specific credit-related actions or data access.

### CreditReportArtifact
Secure reference to a report or imported data; raw reports must not live in GitHub, logs, or agent memory.

### CreditProfileSnapshot
Structured, time-bound summary used for progress measurement.

### CreditItem
Account/public-record/inquiry/other item represented only where necessary.

### CreditObservation
Staff/participant/system observation such as utilization issue, late-payment pattern, possible inaccuracy, thin-file status, or positive tradeline.

### CreditActionPlan
Educational/rebuilding actions with staff review.

### DisputeCandidate
Potential issue requiring validation. A candidate is not a determination that information is legally disputable.

### CreditCommunicationDraft
Prepared external communication that cannot be sent without the required approval and legal workflow.

### CreditActionApproval
Human authorization tied to a specific action/draft/version.

### CreditOutcome
Examples:
- score movement
- credit established
- utilization change
- inaccurate item corrected/removed where documented
- payment behavior milestone

Outcome provenance and measurement source are required.

---

# 8. Workforce & Income Advancement

## Purpose
Support income growth without building a full applicant-tracking system in the first MVP.

## Core objects

### EmploymentProfile
Minimal information needed for program services.

### WorkforceGoal
Employment/career objective.

### WorkforceReferral
Referral to job training, employer, skills provider, or workforce agency.

### EmploymentMilestone
Examples:
- training enrolled/completed
- interview obtained
- job obtained
- job retained at checkpoint
- wage/income increase

### IncomeSnapshot
Participant-reported or verified measurement with source classification.

---

# 9. Business & Wealth Development

## Purpose
Offer entrepreneurship as an optional advancement pathway.

## Core objects

### EntrepreneurshipReadinessAssessment
Determines interest/readiness; must support `not interested` as a valid outcome.

### BusinessProfile
Participant-owned business or planned venture.

### BusinessMilestone
Examples:
- concept validated
- entity formation education completed
- business formed
- EIN/business bank account established
- bookkeeping system established
- business plan completed

### CapitalReadinessAssessment
Readiness for grants, loans, investment, procurement, or other capital.

### FundingOpportunityReferral
Business funding opportunity delivered as education/referral; does not guarantee eligibility or award.

### WealthMilestone
Later-stage asset-building milestones with careful definition and measurement.

---

# 10. Grant & Funding Intelligence

## Purpose
Institutionalize grant research and administration.

## Core objects

### Funder
Organization providing grants/sponsorships/contracts.

### FundingProgram
Specific program or RFP.

### Opportunity
One application cycle.

Required:
- official source
- status
- deadline
- geography
- eligible entity types
- target population/program priorities
- award range
- personnel/payroll eligibility
- indirect/admin rules
- match
- reporting
- evidence confidence/date checked

### FunderContact
Relationship record with source/provenance.

### HistoricalAward
Verified prior grant with amount, recipient, project, and source.

### Application
ACE Credit's submission process.

States:
`identified → qualification → pursue/decline → LOI → invited/full_application → internal_review → approved_to_submit → submitted → awarded/declined/withdrawn`

### ProposalArtifact
Narrative, budget, attachment, or versioned submission document.

### Award
Executed award record belonging to one entity.

### GrantRestriction
Allowable/unallowable cost or program condition.

### ReportingObligation
Due date, required metrics, narrative, financial report, attachment, certification.

### GrantBudgetLine
Approved use of funds. Personnel lines must identify grant-specific allowability.

---

# 11. Impact, Evaluation & Reporting

## Purpose
Measure mission outcomes and grant obligations using traceable data.

## Core objects

### MetricDefinition
Versioned definition, formula, unit, denominator, source rules, and aggregation restrictions.

### Measurement
A value tied to participant/enrollment/program/time period with provenance.

### OutcomeEvent
A meaningful milestone with evidence.

### Baseline / FollowUp
Time-indexed assessments.

### ProgramReport
Aggregated report generated from approved metrics.

### FunderMetricMapping
Maps internal metrics to external funder definitions without redefining the underlying source data.

### DataQualityFlag
Missing, stale, conflicting, unverifiable, or corrected measurement state.

---

# 12. Partnerships & Contracts

## Core objects

### PartnerOrganization
External organization.

### PartnershipAgreement
Scope, entity, dates, permitted data sharing, services, contacts.

### ReferralAgreement
Controls data exchange and handoff.

### Contract
Metadata/reference to executed document; approval/signature workflow remains human-controlled.

---

# 13. Documents & Evidence

## Core objects

### Document
Metadata record only; binary content stored through secure storage abstraction.

Required metadata:
- entity
- owner/context
- data class
- purpose
- storage key
- checksum/version
- retention class
- access restrictions
- uploaded-by/source

### EvidenceLink
Associates a document or external evidence to an outcome, decision, eligibility finding, credit action, or grant requirement.

---

# 14. Workflow, Approval & Audit

## Core objects

### WorkflowDefinition
Versioned process definition.

### WorkflowInstance
Execution tied to a domain record.

### ApprovalRequest
Requested human authorization.

States:
`pending → approved/rejected/expired/cancelled`

### ApprovalDecision
Immutable decision event with approver, time, scope, version, and rationale where required.

### AuditEvent
Append-oriented record of consequential system activity.

### IntegrationEvent
Outbound/inbound integration record with correlation, retry, status, and redaction rules.

---

# 15. Agent & Automation Operations

## Core objects

### AgentRuntime
Runtime type/version/config reference, e.g. Hermes or OpenClaw.

### AgentProfile
Approved purpose, tool policy, model policy, environment, and owner.

### AgentRun
One bounded operation.

Required:
- initiating human/event
- IACER/task reference
- entity context
- tool permissions
- inputs classified/redacted as needed
- outputs
- approvals requested/received
- status
- cost/usage where available
- audit correlation

### ToolCapability
Approved callable capability such as `grant.read`, `participant.task.create`, or `report.prepare`.

### AgentMemoryReference
Optional pointer to runtime memory. Runtime memory is not authoritative business state.

### ScheduledJob
Bounded scheduled operation with owner, frequency, permissions, alerting, and kill switch.

---

# Cross-domain relationship rules

1. `LegalEntity` owns Programs, Awards, Contracts, StaffMemberships, AgentProfiles, and operational data.
2. `Person` may be linked to multiple entity relationships, but access is evaluated per relationship/resource.
3. `Participant` exists through a nonprofit Enrollment, not merely because a Person record exists.
4. `Client` exists through a commercial engagement, not through nonprofit enrollment.
5. `Case` belongs to one entity and should normally be tied to one enrollment/engagement.
6. `Outcome` is tied to an entity/program/enrollment context and cannot silently migrate between entities.
7. Grant reports consume approved aggregated metrics, not unrestricted case notes.
8. Agent runs operate in explicit entity context; no implicit global participant access.

# Domains explicitly outside early MVP
- direct money movement;
- payroll processing;
- automated underwriting/lending;
- autonomous credit dispute submission;
- automated debt settlement;
- legal representation;
- unrestricted cross-entity CRM;
- open-ended agent access to all participant documents;
- direct bureau integration until compliance/security approval.

# Status
`DECIDED`: bounded-context architecture, entity ownership, runtime-neutral source of truth, separate credit domain, grant intelligence as structured domain, approval/audit domains.

`WORKING ASSUMPTION`: shared identity service may link a person across entities while preserving entity-specific access.

`RESEARCH NEEDED`: exact credit/debt-service boundaries and minimum data required for each approved workflow.
