# ACE Credit Actors & Roles

## Purpose
Define who uses or interacts with the platform, what each actor is trying to accomplish, and the default boundaries of their authority. Roles are permission starting points, not substitutes for entity, data-class, resource, and approval checks.

---

# External / service-recipient actors

## Nonprofit Applicant
A Black woman considering/applying to a nonprofit program.

Primary needs:
- understand program purpose/eligibility;
- apply without excessive data collection;
- know what documents are required;
- provide informed consent;
- receive status/next-step communication safely.

Default access:
- own application/intake;
- public/assigned information;
- own consent/preferences.

Cannot:
- see staff notes/internal scoring;
- access another applicant;
- self-approve eligibility.

## Nonprofit Participant
A person with an active or historical nonprofit enrollment.

Primary needs:
- education;
- action plan/goals;
- coaching;
- credit recovery/building support where approved;
- financial stabilization;
- referrals;
- workforce/business pathways;
- progress visibility;
- privacy and safe communications.

Default access:
- own participant-facing program data;
- own goals/tasks/completions;
- approved education;
- approved documents/messages;
- consent and data-use preferences.

Participant-facing UI should not expose internal risk notes, staff-only annotations, security metadata, or other participants.

## Commercial Lead
Potential customer of the for-profit.

Primary needs:
- understand commercial services/pricing/terms;
- schedule/complete consultation;
- decide whether to engage.

Must not automatically receive access to nonprofit benefits or participant status.

## Commercial Client
Customer of the separate for-profit entity.

Primary needs:
- commercial engagement/services;
- education/credit/business-development support as approved;
- billing/contract visibility;
- progress and documents.

Commercial client data belongs to the for-profit context unless a separate lawful nonprofit relationship exists.

## Partner/Referral Recipient
External organization or authorized representative receiving/serving a referral.

Default access:
- only the referral and minimum approved shared information;
- no broad case access;
- no credit/survivor details unless agreement, purpose, consent, and permission explicitly allow.

---

# Nonprofit staff roles

## Executive Director / Authorized Executive
Purpose:
- organizational oversight;
- policy/strategy;
- designated high-level approvals;
- funder/partner/contract accountability.

Possible permissions:
- program/funder dashboards;
- organization-level aggregate reporting;
- high-level approval queues;
- staffing/capacity data appropriate to role.

Should not need standing access to every C4 participant detail solely because of title.

## Program Director
Purpose:
- configure/run program;
- supervise delivery team;
- manage cohorts/capacity;
- approve eligibility/service exceptions where delegated;
- review program outcomes.

Default permissions:
- program/cohort administration;
- assigned-program participant context;
- staff/case assignment;
- program reporting;
- A2 approvals within delegated scope.

## Financial Educator
Purpose:
- deliver curriculum;
- assess learning;
- support financial action planning.

Default permissions:
- assigned participants/curriculum;
- attendance/completion;
- assessments;
- education notes/goals.

Not default:
- raw credit reports;
- survivor safety details;
- organization finance;
- grant submission.

## Financial Coach / Case Manager
Purpose:
- coordinate participant service plan;
- goals/tasks/referrals;
- stabilization and resource navigation;
- track progress.

Default permissions:
- assigned cases;
- case notes/tasks/goals;
- approved financial/stability data;
- referrals;
- participant communications.

Survivor-sensitive and credit-specific access are separate permissions/training gates.

## Credit Specialist
Purpose:
- deliver approved credit education and credit workflow assistance.

Default permissions after legal/security approval:
- assigned credit cases;
- credit-related authorizations;
- approved structured credit data/artifacts;
- credit observations/action plans;
- prepare dispute candidates/drafts where legally permitted.

Cannot by default:
- autonomously send disputes;
- access all organization participants;
- alter legal authorization;
- create guaranteed claims.

## Workforce / Income Advancement Specialist
Purpose:
- employment readiness and referrals;
- income/career milestones.

Default permissions:
- assigned participant employment goals;
- workforce referrals;
- milestone records;
- minimum necessary case context.

## Business Development / Wealth Specialist
Purpose:
- entrepreneurship readiness;
- business planning/financial education;
- capital/procurement readiness.

Default permissions:
- participants who choose the pathway;
- business profile/readiness;
- business milestones/opportunity referrals.

## Outreach / Community Partnerships
Purpose:
- recruit/engage eligible communities;
- manage relationships with shelters, DV organizations, workforce providers, community organizations, etc.

Default permissions:
- public/program outreach information;
- partner records;
- referral pipeline status;
- applicant contact only where required.

No default case/credit/survivor detail access.

## Grant / Development Manager
Purpose:
- grant research;
- funder relationships;
- proposals/budgets;
- award/reporting calendars.

Default permissions:
- grant intelligence;
- approved aggregate program metrics;
- budgets/award records within entity;
- proposal artifacts.

No default participant-level case access. When funders require case-level evidence, use approved reporting/export pathway.

## Data / Evaluation Analyst
Purpose:
- metric definitions;
- data quality;
- program evaluation;
- reporting.

Default permissions:
- pseudonymized/aggregated data where possible;
- measurement/outcome records;
- controlled participant-level analytics only where necessary and approved.

No default need for narrative case notes or raw credit documents.

## Operations / Program Coordinator
Purpose:
- scheduling;
- attendance;
- tasks;
- document requests;
- administrative follow-up.

Access limited to operational information needed for coordination.

## Nonprofit Finance / Payroll / Administration
Purpose:
- budget/payroll/grant allocation/administration.

Access:
- nonprofit financial/HR/grant records as assigned;
- aggregated service records needed for cost allocation/reporting.

No default case/credit details.

## Compliance / Legal Reviewer
Purpose:
- review high-risk workflows, materials, contracts, policies, specific escalations.

Access is matter-scoped when possible; legal role does not imply routine program access.

---

# For-profit staff roles
Commercial roles should be separately defined even if some humans work in both entities.

Possible roles:
- Commercial Operations Manager;
- Financial Education Consultant;
- Credit Specialist;
- Business Development Consultant;
- Sales/Client Success;
- Billing/Finance Administrator;
- Compliance Reviewer;
- System Administrator.

A person holding nonprofit and for-profit roles has two `StaffMembership` records and operates under the active entity context.

---

# Platform / technical roles

## System Administrator
Purpose:
- identity/access administration;
- technical configuration;
- incidents.

Security principle:
admin does not mean routine unrestricted inspection of participant content. Use audited break-glass access for exceptional support if required.

## Security Administrator
Purpose:
- credentials;
- security policies;
- incident response;
- access review.

## Developer / Coding Agent
Purpose:
- build/test system.

Default production data access: none.

Uses synthetic fixtures and non-production environments.

## Support Operator
Purpose:
- troubleshoot user/session issues.

Should use metadata/diagnostics before content access; sensitive-content access requires escalation.

---

# Agent roles

## Coding Agent
Tools:
- repository read/write through branch/PR;
- test/lint tools;
- approved public research.

No production participant access.

## Grant Research Agent
Tools:
- public web research;
- grant intelligence records;
- source verification;
- proposal draft workspace where approved.

No routine participant C3/C4 access.

## Program Operations Agent
Potential future tools:
- read assigned operational queue;
- create reminders/tasks;
- summarize non-sensitive records;
- identify missing program steps.

Writes are narrow/audited.

## Credit Support Agent
Potential future role after compliance/security approval.

Can assist staff with bounded analysis/drafts; cannot autonomously execute high-risk external actions.

## Reporting Agent
Can prepare aggregate reports from approved metric APIs. Cannot invent measurements or certify reports.

## Runtime Administrator Agent
Not a standing production role. Agents cannot grant themselves permissions, rotate their own restrictions away, or bypass approval policy.

---

# Role design rules
1. Roles are entity-scoped.
2. Assignment is time-bounded where appropriate.
3. Sensitive privileges are additive, not inherited automatically from ordinary case role.
4. Staff only see participants/programs relevant to assigned scope unless role requires broader program oversight.
5. Data exports require separate permission.
6. Approval permissions are separate from preparation permissions.
7. Admin privileges are separate from business approval authority.
8. Agent identity is always distinguishable from human identity.
9. Break-glass access is exceptional, logged, and reviewed.
10. Departed/role-changed staff access is revoked promptly.

# Suggested permission dimensions
- entity;
- program;
- cohort;
- case assignment;
- resource type;
- action (`read/create/update/delete/export/approve/execute`);
- data classification/tag;
- time window;
- environment;
- actor type (human/service/agent).

# Status
`DECIDED`: roles above define product planning personas; final permission sets will be implemented as RBAC + contextual controls rather than titles alone.

`RESEARCH NEEDED`: exact staffing structure, named executive/board authorities, partner portal requirements, cross-role separation of duties.
