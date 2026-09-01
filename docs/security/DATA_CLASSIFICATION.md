# ACE Credit Data Classification Standard

## Purpose
Define how ACE Credit categorizes information so application design, staff access, agent permissions, logging, storage, exports, and retention can be designed consistently.

This standard is a technical/operational baseline and should be reviewed against applicable law, contracts, funder requirements, insurance requirements, and vendor agreements before production use.

## Core principles
- Collect the minimum data needed for a defined purpose.
- Entity ownership and data sensitivity are separate dimensions; every protected record needs both.
- The fact that staff can see a participant does not imply access to every sensitive field.
- Survivor-related information is treated with heightened care because unauthorized disclosure can create physical as well as financial harm.
- Raw credit reports and identity verification materials require tighter controls than ordinary coaching notes.
- Agents receive the minimum data necessary for the bounded task.
- Sensitive values must not be placed in source control, ordinary application logs, analytics events, issue trackers, or agent memory by default.

---

# Classification levels

## C0 — Public
Information intentionally available to the public.

Examples:
- public website copy;
- published curriculum samples;
- public grant announcements;
- public resource-directory information;
- published impact reports after review;
- public contact information for organizations.

Controls:
- integrity/version control;
- publication approval where organizational claims are made;
- no assumption that public source data is accurate forever; record source/date for research data.

## C1 — Internal
Low-sensitivity organizational information not intended for public release.

Examples:
- internal project plans;
- generic workflow documentation;
- non-sensitive meeting notes;
- synthetic test data;
- draft grant research using public information;
- non-sensitive vendor evaluation notes.

Controls:
- authenticated staff access as appropriate;
- may be available to approved coding/operations agents;
- avoid unnecessary external publication.

## C2 — Confidential
Information whose disclosure could materially harm operations, privacy, partnerships, or competitive position.

Examples:
- non-public grant proposals/budgets;
- internal financial projections;
- employee operational information that is not highly sensitive;
- non-public partner/contract negotiations;
- internal policies before publication;
- participant names/contact information in ordinary program context;
- case scheduling and basic service status;
- commercial client information.

Controls:
- entity-scoped authorization;
- encrypted transport;
- protected storage;
- access/audit logging for material operations;
- controlled exports;
- no public agent prompts or third-party tools without approved data-processing terms.

## C3 — Restricted
Highly sensitive personal, financial, legal, or operational information.

Examples:
- detailed income/debt information;
- bank-account information if ever collected;
- detailed employment/housing records;
- case notes containing significant private circumstances;
- participant documents;
- tax/business financial documents;
- credit profile details;
- consumer-report derived data;
- signed consents/authorizations;
- government identifiers where collected;
- HR/payroll records;
- authentication recovery information;
- executed confidential contracts.

Controls:
- explicit need-to-know authorization;
- stronger field/object permissions;
- encryption at rest in production;
- access logging;
- download/export restrictions;
- retention schedule;
- secure deletion process;
- no source control;
- no ordinary analytics payloads;
- agent access only where task-specific and approved.

## C4 — Critical / Safety-Sensitive
Information where unauthorized access/disclosure could create severe identity, financial, legal, security, or physical-safety risk.

Examples:
- raw consumer/credit reports containing extensive personal data;
- Social Security numbers or equivalent high-risk identifiers;
- identity verification document images;
- credentials, API keys, private keys, password hashes/recovery secrets;
- survivor safety plans, protected addresses, shelter location, abuser-related details, or other information whose exposure could create physical danger;
- highly sensitive legal records;
- unrestricted production database backups.

Controls:
- collect only if necessary;
- separate/segmented storage where practical;
- very limited roles;
- short-lived access where possible;
- explicit access audit;
- secrets stored in a secrets manager, never normal DB text fields when avoidable;
- no agent memory persistence;
- no copied values in tickets/chat/docs/logs;
- download disabled or highly restricted where feasible;
- incident alerting for suspicious access;
- formal retention/deletion rules;
- periodic access review.

---

# Special handling tags
Classification level is combined with handling tags.

## `ENTITY:NONPROFIT`
Owned/controlled by nonprofit context.

## `ENTITY:FORPROFIT`
Owned/controlled by for-profit context.

## `SURVIVOR_SENSITIVE`
Access requires a narrower purpose/role than ordinary case access. Default dashboards should not expose safety-sensitive details.

## `CREDIT_DATA`
Consumer-report/credit-related data. Access, retention, provider contracts, and permissible uses require specific compliance review.

## `IDENTITY_HIGH_RISK`
SSN, identity docs, identity verification artifacts, or equivalent.

## `HR_CONFIDENTIAL`
Employee/payroll/HR data.

## `GRANT_RESTRICTED`
Information controlled by award/application terms.

## `LEGAL_PRIVILEGED_OR_REVIEW`
Potentially privileged/legal-review material. Do not assume privilege merely by applying a tag.

## `SECRET`
Credential material. Must use secrets-management controls.

---

# Data-type baseline

| Data | Default class | Notes |
|---|---|---|
| Public curriculum | C0 | Versioned content |
| Public funder research | C0/C1 | Source/date required |
| Synthetic fixtures | C1 | Must be genuinely synthetic |
| Staff project plans | C1 | Increase if sensitive |
| Participant name/contact | C2 | Entity-scoped |
| Program/enrollment status | C2 | Avoid public exposure |
| General coaching note | C2/C3 | Structured data preferred |
| Income/debt details | C3 | Minimize exact values where unnecessary |
| Housing instability | C3 | May become C4 with safety detail |
| DV/IPV history | C3/C4 | Use survivor-sensitive tag |
| Safe address/shelter details | C4 | Extremely limited access |
| Credit score/history summary | C3 | CREDIT_DATA |
| Raw credit report | C4 | Secure artifact reference |
| SSN/identity document | C4 | IDENTITY_HIGH_RISK |
| Bank routing/account number | C4 | Avoid collection unless necessary |
| Grant proposal/budget draft | C2 | Entity + grant context |
| Executed grant agreement | C3 | Restricted terms may apply |
| Payroll/HR record | C3/C4 | HR_CONFIDENTIAL |
| Password/API key/token | C4 | SECRET; never DB/log/Git by default |
| Audit metadata | C2/C3 | Must not copy protected payload values |

---

# Environment rules

## Local development
Allowed:
- C0/C1;
- synthetic versions of C2–C4 data.

Not allowed by default:
- real participant data;
- real credit reports;
- production credentials;
- real identity documents;
- real survivor-sensitive details.

## Test / staging
Should use synthetic data. Production data copies are prohibited unless a specific secured testing procedure is approved.

## Production
May process approved classes needed for live operations. Production access is role/entity/task scoped.

---

# Agent data-access policy

## Coding agent
Default: C0/C1 and synthetic fixtures only.

## Research/grant agent
Default: C0/C1, selected C2 proposal material if explicitly needed. No participant C3/C4 data for ordinary grant research.

## Program operations agent
May receive narrow C2/C3 context only through application tools for a specific task. It should receive derived/minimized fields rather than a full case whenever possible.

## Credit support agent
No direct raw C4 report access until compliance/security design is approved. If later allowed, use task-bound access, redacted/structured representations where possible, no persistent memory, and full audit.

## Administrator agent
No standing unrestricted production access. Admin automation should use narrow capabilities and approval.

---

# Logging and observability
Never log by default:
- SSN/high-risk IDs;
- passwords/tokens/API keys;
- raw credit-report content;
- bank account numbers;
- identity document images;
- survivor safety details;
- full sensitive form payloads.

Use identifiers/correlation IDs instead. Audit logs record the action and object, not a duplicate copy of every protected field.

# Analytics
Product analytics should use pseudonymous identifiers and event metadata. Do not send C3/C4 fields to general analytics tools unless specifically approved through privacy/security/vendor review.

# Documents
Document metadata carries:
- entity;
- data classification;
- handling tags;
- owner/context;
- retention class;
- access policy;
- malware/scan status where uploads are supported.

Binary documents are stored outside the relational database when appropriate and outside source control.

# Retention
A final schedule is `RESEARCH NEEDED`. Until adopted:
- do not promise indefinite retention;
- do not design irreversible deletion without audit/tombstone strategy;
- separate operational retention from legal/contract/grant retention;
- preserve approvals/audit records according to later policy even if underlying content is deleted where lawful.

# Incident priorities
A suspected exposure of C4 or survivor-sensitive data is treated as highest priority and escalated immediately under the future incident-response plan.

# Status
`DECIDED`: five-level classification, special handling tags, synthetic-only development, no secret/PII in GitHub, task-scoped agent access.

`RESEARCH NEEDED`: statutory/contractual retention periods, breach-notification requirements by jurisdiction, final vendor/hosting controls, direct credit-data handling requirements.
