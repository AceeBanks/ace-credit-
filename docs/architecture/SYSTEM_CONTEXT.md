# ACE Credit System Context

## Purpose
Define the major actors, systems, trust boundaries, data flows, and ownership boundaries before implementation architecture is selected.

## System of interest
**ACE Credit Platform** is the planned shared application infrastructure that supports separate nonprofit and for-profit operations while enforcing legal-entity, permission, data, audit, and policy boundaries.

It is not the same thing as Hermes WebUI, OpenClaw, a model provider, GitHub, or any one user-facing app.

## Primary human actors
- Participant — Black woman enrolled in a nonprofit program.
- Commercial Client — paying consumer/business customer of the for-profit.
- Program Director / Executive leadership.
- Financial Educator.
- Financial Coach / Case Manager.
- Credit Specialist.
- Outreach / Partnership staff.
- Workforce / Business Development staff.
- Grant / Development staff.
- Data / Evaluation staff.
- System Administrator.
- Authorized Partner user.
- Legal/Compliance reviewer.

## Non-human actors
- Hermes Agent runtime.
- OpenClaw runtime if adopted.
- Coding agents.
- Scheduled workers.
- Identity provider.
- Secure object/file storage.
- Email/SMS provider.
- Credit-data or consumer-report provider if later approved.
- Analytics/reporting services.
- Grant/funder research sources.
- Payroll/HR systems used by an entity.

---

# Logical system zones

## Zone A — Public / Participant Edge
Future surfaces:
- public website;
- program application/intake;
- participant portal/mobile experience;
- commercial client portal;
- approved messaging/reminders.

Trust level: untrusted external input.

Controls:
- authentication where required;
- rate limiting;
- input validation;
- anti-abuse protections;
- minimum disclosure of internal identifiers;
- secure upload policies;
- clear privacy/consent notices.

## Zone B — Staff Application
Authorized internal staff interface for:
- programs and cohorts;
- participant/client records;
- case management;
- education;
- goals/referrals;
- credit workflows where approved;
- outcomes;
- grants and reporting;
- approvals.

Trust level: authenticated but not universally trusted.

Controls:
- role and entity authorization;
- sensitive-field restrictions;
- session security;
- audit logs;
- export controls;
- least privilege.

## Zone C — Core Application / Policy Layer
Authoritative application services:
- domain rules;
- entity/tenant policy;
- authorization;
- workflow state machines;
- approval gates;
- validation;
- audit event creation;
- integration policy;
- data minimization rules.

No agent runtime may bypass this layer to mutate authoritative production business data.

## Zone D — Data Layer
Potential stores:
- relational transactional database;
- secure object storage;
- search/indexing store with redaction controls;
- analytics warehouse later;
- append-oriented audit/event storage.

Data is partitioned and classified. Runtime memory is not part of the authoritative data layer.

## Zone E — Integration Layer
Adapters for external services:
- identity;
- email/SMS;
- file scanning/storage;
- credit data;
- grants/funder feeds;
- partner systems;
- payroll/HR;
- reporting/export destinations.

Each integration has:
- owner entity;
- credentials;
- allowed operations;
- data classification;
- retry/error policy;
- logging/redaction requirements;
- kill switch.

## Zone F — Agent Operations Layer
Runtimes such as Hermes/OpenClaw and coding agents.

Allowed pattern:
`Agent → approved tool/capability → application/policy layer → domain/data`

Prohibited pattern:
`Agent → direct unrestricted production DB/files/credentials`

Agents may have isolated workspaces and memory but those are operational aids, not policy authority or the canonical participant record.

## Zone G — Development / Source Control
GitHub contains:
- application code;
- infrastructure definitions;
- governance docs;
- ADRs;
- tests;
- synthetic fixtures;
- templates.

GitHub must not contain:
- participant PII;
- credit reports;
- production exports;
- secrets/tokens;
- live passwords;
- confidential grant/contract material unless intentionally stored with an approved secure mechanism outside normal source control.

---

# Legal-entity boundary

The platform may be shared infrastructure, but every production request that touches operational data should resolve:
1. actor identity;
2. active legal entity/tenant;
3. role/permissions;
4. target resource entity;
5. data classification;
6. contextual restrictions;
7. approval requirement;
8. audit requirement.

A shared human owner or staff member is not sufficient reason for cross-entity access.

## Nonprofit data
Examples:
- program applications;
- participant enrollments;
- grant-funded service records;
- case/coaching data;
- impact outcomes;
- grant reporting.

## For-profit data
Examples:
- paid consultations;
- commercial client records;
- commercial service agreements;
- invoices/payment references;
- business-development engagements.

## Shared/reference data candidates
Only after explicit design:
- public curriculum content;
- public resource directory;
- common software configuration;
- generic templates;
- non-sensitive reference data;
- shared identity anchor with entity-scoped relationships.

Shared does not mean unrestricted.

---

# Key data flows

## Flow 1 — Nonprofit participant intake
`Applicant → intake form → validation → eligibility review → consent/authorization → human decision where required → enrollment → program/case setup → audit`

Sensitive details not needed for eligibility should not be collected during initial intake.

## Flow 2 — Program service delivery
`Enrollment → service plan → education/coaching/referral/tasks → progress evidence → outcome measurements → program reporting`

## Flow 3 — Credit-related support
`Authorized participant → credit workflow eligibility → required authorization → secure report/data acquisition → staff review → educational/action plan → approval-gated external actions if legally permitted → progress measurement`

Agents may assist with preparation but not bypass authorization, legal boundaries, or approval.

## Flow 4 — Grant research
`Sources → agent/human research → source verification → structured opportunity record → qualification → pursue decision → proposal workflow`

Public grant research generally contains no participant PII.

## Flow 5 — Grant reporting
`Approved internal metrics → aggregation → data-quality review → grant-specific mapping → report draft → human approval/certification → submission`

No agent may fabricate outcomes or certify reports.

## Flow 6 — Commercial client service
`Lead/client → commercial intake/contract → payment/commercial engagement → approved services → outcomes → commercial record`

Commercial services cannot be recorded as nonprofit grant-funded delivery unless a lawful documented arrangement explicitly permits it.

## Flow 7 — Agent-assisted operation
`Human/system trigger → IACER/task → agent policy resolution → scoped context → tool calls → draft/action → approval if consequential → execution → audit`

---

# Runtime context

## Hermes
Current repository includes Hermes WebUI and a local Hermes setup. It may be used as an operator interface and automation runtime, but ACE Credit policy/business state remains outside runtime-specific memory/config.

## OpenClaw
Potential second runtime. If evaluated, use a dedicated workspace/config adapter. Do not duplicate the constitution into divergent copies that can silently drift; runtime bootstrap files should reference or be generated from canonical project governance where practical.

## Coding agents
May modify source code through GitHub workflows under branch/PR controls. They do not receive production participant data by default.

---

# Required platform security properties
- entity isolation;
- least privilege;
- MFA-capable staff authentication in production;
- revocable sessions/tokens;
- secure secret management;
- input validation;
- encrypted transport;
- protected sensitive storage;
- access logging;
- audit event integrity;
- backup/recovery;
- environment separation;
- dependency/security update process;
- safe file upload handling;
- configurable retention/deletion;
- agent tool policies and kill switches.

# Failure principles
- fail closed on authorization ambiguity;
- do not report an external action as complete without confirmation;
- retries must be idempotent where possible;
- no sensitive values in exception logs;
- agent failure must not corrupt workflow state;
- human staff must be able to continue operations if an agent runtime is unavailable.

# Status
`DECIDED`: shared platform may exist, but entity boundaries are enforced at policy/data layers; agents access authoritative state through controlled capabilities.

`WORKING ASSUMPTION`: a relational application core plus secure object storage will be appropriate, subject to later ADR.

`RESEARCH NEEDED`: final hosting, identity provider, production file storage, credit-data integrations, messaging provider, analytics architecture.
