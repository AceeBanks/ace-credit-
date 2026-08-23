# ACE Credit MVP Scope

## Purpose
Define the smallest safe product that can support real nonprofit program operations and prove the architecture before adding regulated credit automation, commercial complexity, or broad participant automation.

## MVP thesis
The first useful product should be a **staff-first nonprofit program operating system** with participant intake/education/progress capabilities, strict entity/security foundations, grant/outcome reporting, and an agent adapter. It should not begin as an autonomous credit-repair engine.

This creates value even if credit-service legal review takes longer, and it establishes the data, approval, audit, and program infrastructure that the credit module will need later.

---

# MVP users
Primary:
- Program Director;
- Financial Educator;
- Financial Coach/Case Manager;
- Program Coordinator;
- Grant/Data staff;
- Administrator;
- nonprofit applicant/participant through limited participant-facing surfaces.

Secondary/limited:
- Outreach/partner staff;
- agent workers through controlled capability APIs.

Not required for MVP:
- broad commercial client portal;
- unrestricted external partner portal;
- full payroll/accounting users;
- autonomous credit agent.

---

# MVP functional scope

## 1. Identity & access
Must have:
- staff authentication;
- user/account lifecycle;
- nonprofit entity context;
- role assignments;
- program/case scope where applicable;
- admin vs. operational permissions;
- audit of privileged changes;
- architecture ready for second legal entity even if pilot starts with nonprofit only.

Should have:
- MFA-capable identity provider;
- session revocation;
- least-privilege defaults.

## 2. Program configuration
Must have:
- program record;
- program version/status;
- eligibility rule description/version;
- program dates;
- target population/program description;
- service plan template;
- outcome/metric assignment;
- cohort support;
- assigned staff.

## 3. Applicant/intake
Must have:
- secure application form;
- safe contact preferences;
- minimal required fields;
- draft/submitted/review states;
- missing-information workflow;
- staff eligibility decision;
- decision reason categories;
- versioned consent/notice acknowledgment;
- enrollment creation after acceptance.

Non-goal:
- collect raw credit report during initial application.

## 4. Participant/enrollment
Must have:
- participant profile limited to needed program data;
- enrollment state;
- staff assignment;
- key dates;
- participant preferences;
- baseline/follow-up assessment support;
- program completion/exit state/reason.

## 5. Case/service management
Must have:
- case tied to enrollment;
- tasks;
- goals;
- structured service events;
- notes with visibility/data class;
- referrals;
- referral status;
- timeline/activity view;
- assigned staff/caseload.

## 6. Financial education
Must have:
- curriculum/module records;
- assignments;
- completion;
- assessments;
- pre/post score support;
- participant-facing module access or linkable delivery mechanism;
- curriculum versioning.

MVP content focus:
- budgeting;
- banking;
- savings;
- credit fundamentals;
- debt fundamentals;
- consumer rights;
- financial abuse/fraud/scams;
- financial goal planning.

## 7. Financial stabilization
Must support recording:
- financial goals;
- emergency savings milestone;
- banking access milestone;
- high-level debt action plan/status;
- housing/resource referral;
- employment/income goal;
- stability assessment indicators.

Non-goal:
- bank aggregation or transaction ingestion.

## 8. Credit readiness — limited MVP
MVP may include:
- credit education module completion;
- participant's self-reported credit status/goal if program chooses;
- task “obtain/review your own report”;
- credit pathway eligibility/status;
- referral or later-stage handoff;
- synthetic-data prototype of future credit domain for testing.

MVP production must NOT include unless Phase 4 legal/security gates are accelerated and approved:
- direct bureau/report provider pull;
- raw report ingestion;
- staff done-for-you disputes;
- automated dispute letters/submission;
- automated score recommendations;
- agent access to real credit reports.

## 9. Workforce/income basics
Must have:
- employment/income goal;
- workforce referral;
- training/job milestones;
- income baseline/follow-up source type.

Not required:
- employer ATS/integration;
- job board scraping platform.

## 10. Business/wealth pathway basics
Must have:
- entrepreneurship interest/readiness status;
- business goal;
- optional business profile;
- basic business milestones;
- referrals/resources.

Not required:
- business formation filing automation;
- lending/underwriting;
- automated grant applications on participant's behalf.

## 11. Grant intelligence & reporting
Must have or be build-ready in same application core:
- funder;
- funding program/opportunity;
- status/deadline;
- eligibility fields;
- personnel/payroll allowability field;
- previous award/source records;
- opportunity pursue decision;
- application status;
- award/reporting obligations;
- mapping internal metrics to funder requirements;
- report export/draft workflow.

MVP can begin grant intelligence as internal staff tooling before tying it to participant-facing app.

## 12. Outcomes & impact
Must have:
- versioned metric definitions;
- baseline/follow-up measurements;
- provenance/source type;
- program/cohort aggregation;
- data-quality flags;
- exportable impact summary;
- no unrestricted participant PII in routine funder export.

## 13. Documents
Must have:
- document metadata model;
- secure storage abstraction;
- classification/entity/context;
- access controls;
- signed/controlled download method;
- upload restrictions.

If secure production upload is not ready at pilot launch, document exchange remains outside app through an approved process rather than using insecure storage.

## 14. Audit & approvals
Must have:
- append-oriented audit events for privileged/consequential actions;
- approval request/decision model;
- grant submission approval support;
- privileged access change audit;
- future credit-action approval model even if not activated.

## 15. Agent integration
Must have:
- runtime-neutral capability/tool contract;
- agent identity;
- entity scope;
- run/correlation ID;
- allowlisted read/write capabilities;
- approval handoff;
- audit;
- global disable/kill mechanism.

First safe agent use cases:
- public grant research;
- repository/coding work;
- completeness checks;
- draft internal summaries;
- prepare aggregate program reports;
- create internal tasks from approved rules.

---

# Explicit MVP non-goals
1. Autonomous credit repair.
2. Direct consumer-report pulling.
3. Debt settlement/debt-management-plan administration.
4. Holding/moving participant money.
5. Payroll processing.
6. Full accounting/general ledger.
7. Loan origination/underwriting.
8. Automated business formation filings.
9. Open-ended AI access to all participant records.
10. Cross-entity marketing database.
11. Complex social/community network features.
12. Native mobile apps before responsive web proves the workflow.
13. Multi-language expansion unless pilot requires it.
14. Advanced predictive risk scoring.
15. Automated eligibility denial based solely on AI.
16. Funder-facing live portal before internal reporting is reliable.
17. Provider marketplace or tradeline marketplace.
18. Full enterprise CRM replacement.

---

# MVP release slices

## Slice A — Secure internal skeleton
- authentication;
- entity/role foundation;
- programs/cohorts;
- synthetic participants/enrollments;
- tasks/goals/referrals;
- audit;
- basic admin;
- automated tests for tenancy/permissions.

Exit: staff can simulate one program with synthetic data.

## Slice B — Intake & program delivery
- applicant flow;
- consent;
- enrollment;
- caseload;
- curriculum/assessment;
- service events;
- participant goals.

Exit: staff can run intake → enrollment → service delivery with test/pilot-ready workflow.

## Slice C — Outcomes & grant operations
- metric definitions;
- measurements;
- reporting;
- grant opportunity/award obligations;
- personnel allowability/restriction fields;
- report exports/drafts.

Exit: staff can produce an internally verified cohort impact/grant report.

## Slice D — Participant experience
- secure participant login;
- own tasks/goals/modules;
- safe communications/preferences;
- progress summary.

Exit: participant can complete core program workflow without seeing staff-only data.

## Slice E — Agent-assisted operations
- runtime adapter;
- grant research agent tools;
- internal task/report preparation;
- approval queue integration;
- run/audit history.

Exit: an agent can complete a bounded workflow without direct database access or bypassing policy.

---

# Acceptance criteria for MVP architecture

## Entity/security
- every entity-owned record has explicit entity ownership;
- cross-entity denial tests pass;
- authorization is server-side;
- no sensitive data in logs/source control;
- production secrets are externalized;
- high-risk exports/actions require separate permissions.

## Product
- staff can manage a participant from intake through program exit;
- participant can receive assigned education/goals;
- referrals/outcomes are measurable;
- staff can distinguish participant-facing vs. internal information;
- entrepreneurship is optional.

## Impact
- cohort completion and pre/post education metrics work;
- outcome provenance exists;
- credit score is not required as the sole/primary success measure;
- reports can aggregate without exposing unnecessary PII.

## Agents
- agent run has identity/scope/audit;
- agent cannot grant itself tools;
- denied action fails closed;
- high-risk external action is unavailable or approval-gated;
- platform still functions when runtime is offline.

## Operations
- documented backup/restore before real data;
- documented incident escalation;
- staff onboarding/role revocation process;
- data retention interim/final policy;
- synthetic test dataset;
- CI/tests on critical domain/security rules.

---

# MVP success metrics
Technical:
- cross-tenant authorization test pass rate 100%;
- critical workflow automated tests passing;
- no known critical/high security defects at pilot launch;
- restore drill succeeds;
- agent actions traceable to run/actor.

Operational:
- staff can complete core intake/enrollment/service/reporting without shadow spreadsheet for core records;
- staff can identify next action/caseload status;
- grant reporting metrics come from defined fields rather than manual reconstruction.

Participant:
- application completion;
- orientation/education completion;
- goals established;
- referrals connected;
- measurable financial capability/stability outcomes as defined in outcome model.

# Feature-entry rule
A feature may enter MVP only if it:
1. supports the pilot mission/operations;
2. has an owner/user;
3. has a defined domain object/state;
4. has data classification;
5. has authorization/approval rules;
6. has measurable acceptance criteria;
7. does not depend on unresolved legal assumptions.

# Status
`DECIDED`: staff-first nonprofit operating MVP with limited participant experience and no autonomous credit/debt actions.

`WORKING ASSUMPTION`: responsive web first; one first-party application core; nonprofit pilot before complex dual-entity production workflows.

`OPEN QUESTION`: pilot cohort size, exact launch program, first jurisdiction, implementation stack, participant-auth timing.
