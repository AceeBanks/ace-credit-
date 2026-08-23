# ACE Credit Threat Model

## Purpose
Identify realistic threats early enough that architecture, permissions, agent tooling, and product workflows can be designed around them rather than patched later.

## Security objectives
1. Protect participant/client confidentiality and physical safety.
2. Preserve nonprofit/for-profit entity isolation.
3. Prevent unauthorized financial/credit actions.
4. Prevent agents from exceeding granted authority.
5. Preserve integrity of grant, impact, case, credit, and approval records.
6. Keep operations recoverable when an agent/vendor/integration fails.
7. Make consequential actions attributable and auditable.

## Primary assets
- participant/client identity and contact data;
- survivor-sensitive information;
- credit/consumer-report data;
- financial/debt/income/housing/employment data;
- consents and authorizations;
- case/coaching records;
- grant proposals, budgets, awards, reports;
- staff/HR information;
- contracts and partnership data;
- credentials/secrets;
- source code and infrastructure configuration;
- audit history;
- domain and policy configuration;
- agent tool permissions and runtime state.

## Trust boundaries
1. Internet/public edge.
2. Participant/client authenticated session.
3. Staff authenticated session.
4. Admin/high-privilege session.
5. Application/policy boundary.
6. Database/object storage.
7. External integrations.
8. Agent runtime/tool gateway.
9. Development/source-control environment.
10. Nonprofit/for-profit tenant boundary.

---

# Threat scenarios

## T01 — Cross-entity data leakage
**Scenario:** staff, API, background job, agent, or export accesses records from the wrong legal entity.

**Impact:** severe privacy, grant-compliance, contractual, and organizational risk.

**Controls:**
- mandatory entity context;
- default deny;
- server-side authorization;
- row-level or equivalent data isolation where practical;
- tenant-aware storage keys;
- cross-tenant tests;
- entity context in audit events;
- no global unrestricted agent tools.

**Priority:** Critical.

## T02 — Survivor-sensitive disclosure
**Scenario:** an ordinary case user, export, notification, or agent reveals protected address, shelter, abuser information, or safety details.

**Controls:**
- survivor-sensitive tag;
- narrower role/attribute authorization;
- field-level masking;
- no inclusion in routine dashboards/exports;
- safe-contact preferences;
- notification content minimization;
- high-priority access alerts/review.

**Priority:** Critical.

## T03 — Prompt injection through external content
**Scenario:** a grant webpage, uploaded document, email, or participant-provided text contains instructions that manipulate an AI agent into leaking data or taking unauthorized actions.

**Controls:**
- treat retrieved/user content as data, never authority;
- tool authorization outside prompts;
- separate system/task instructions from untrusted content;
- deny secret access to research agents;
- approval before consequential writes/sends;
- content/source provenance;
- sandbox document processing.

**Priority:** High.

## T04 — Agent privilege escalation
**Scenario:** agent modifies configuration, creates credentials, changes its own role, or calls a broader tool than intended.

**Controls:**
- agents cannot administer their own IAM/policy;
- separate admin plane;
- short-lived/scoped credentials;
- server-side capability enforcement;
- tool allowlist;
- production write access exceptional;
- rapid revocation/kill switch;
- audit and alerts on denied attempts.

**Priority:** Critical.

## T05 — Unauthorized credit action
**Scenario:** system/agent sends a dispute or credit-related communication without valid authorization, correct workflow, staff review, or legal basis.

**Controls:**
- separate credit workflow domain;
- compliance gate;
- participant authorization record;
- immutable draft/version reference;
- human approval tied to exact action;
- execution only through approved adapter;
- confirmation captured;
- no autonomous external submission in early phases.

**Priority:** Critical.

## T06 — Secret leakage
**Scenario:** API key/token/password enters GitHub, logs, prompt history, issue, screenshot, or analytics.

**Controls:**
- secret manager/environment variables;
- `.gitignore` and secret scanning;
- log redaction;
- never echo full `.env`/credential files;
- runtime isolation;
- rotation procedure;
- development credentials separated from production.

**Priority:** Critical.

## T07 — IDOR / object authorization bypass
**Scenario:** authenticated user changes an ID and retrieves another participant/client/document.

**Controls:**
- every object lookup includes authorization/entity check;
- opaque identifiers do not replace authorization;
- automated security tests;
- signed/short-lived download URLs;
- no direct predictable storage paths.

**Priority:** Critical.

## T08 — Unsafe file upload
**Scenario:** uploaded statement, identity file, or report contains malware, oversized payload, malicious format, or active content.

**Controls:**
- type/size allowlist;
- malware scanning where supported;
- quarantine before processing;
- generated storage names;
- no execution from upload location;
- isolate document parsers;
- limit agent/document tool access;
- sanitize previews.

**Priority:** High.

## T09 — Sensitive data in logs/telemetry
**Scenario:** full request/response bodies, reports, notes, identifiers, or tokens are logged.

**Controls:**
- structured logs with approved fields;
- request-body logging disabled for sensitive endpoints;
- redaction middleware;
- C3/C4 values prohibited from general analytics;
- periodic log sampling/review.

**Priority:** High.

## T10 — Fraudulent or fabricated impact data
**Scenario:** staff/agent invents outcomes, edits historical measurements, or generates a funder report without provenance.

**Controls:**
- metric definitions/versioning;
- source/provenance on measurements;
- correction events rather than silent overwrite where material;
- report review/approval;
- aggregation from canonical data;
- audit trail;
- data-quality flags.

**Priority:** High.

## T11 — Grant submission without authority
**Scenario:** agent or staff submits/attests to a proposal with unapproved budget, claims, certifications, or terms.

**Controls:**
- submission permission separate from drafting;
- owner/authorized approver gate;
- locked submission version/hash;
- evidence for claims;
- status transition only after confirmation;
- audit record.

**Priority:** High.

## T12 — Insecure runtime workspace
**Scenario:** Hermes/OpenClaw workspace contains credentials or protected participant data and is copied/backed up/synced unexpectedly.

**Controls:**
- runtime workspace considered non-authoritative;
- no C4 persistence by default;
- secrets outside workspace;
- sandbox where appropriate;
- runtime-specific `.gitignore`;
- separate private repo only for safe runtime config if used;
- periodic review of memory/context files.

**Priority:** High.

## T13 — Model/provider data exposure
**Scenario:** sensitive prompts/documents are sent to a model/provider whose terms, retention, region, or security posture is not approved.

**Controls:**
- provider inventory;
- data-processing/vendor review;
- classify which providers can receive which data levels;
- redact/minimize context;
- disable training/retention where contractually available;
- route C3/C4 tasks only to approved providers or keep them human-only until approved.

**Priority:** High.

## T14 — Compromised dependency/supply chain
**Scenario:** malicious package, action, container, browser extension, or imported runtime code executes in development/production.

**Controls:**
- pinned/locked dependencies where supported;
- dependency/security scanning;
- review new dependencies;
- minimal CI permissions;
- trusted action versions;
- SBOM later;
- upstream tracking for imported Hermes component;
- isolated build credentials.

**Priority:** High.

## T15 — Background job scope drift
**Scenario:** scheduled worker processes all entities/participants when intended to process one cohort/entity.

**Controls:**
- explicit entity/job scope;
- dry-run capability;
- max batch size;
- idempotency;
- audit correlation;
- canary/test mode;
- stop/kill switch;
- alert on unexpected volume.

**Priority:** High.

## T16 — Excessive exports
**Scenario:** authorized user downloads a broad CSV/report containing more sensitive data than necessary.

**Controls:**
- export-specific permissions;
- field allowlists;
- entity/program scope;
- export audit;
- warning/justification for sensitive exports;
- short-lived download URLs;
- future watermarking/data-loss controls if needed.

**Priority:** High.

## T17 — Account takeover
**Scenario:** attacker compromises staff/admin account.

**Controls:**
- MFA-capable identity provider;
- secure session management;
- passwordless/OIDC options later;
- step-up auth for high-risk admin actions;
- device/session revocation;
- suspicious-login alerting where supported;
- least privilege limits blast radius.

**Priority:** Critical.

## T18 — Data deletion/ransomware
**Scenario:** malicious user/agent/integration deletes or corrupts records/files.

**Controls:**
- backups;
- tested restore;
- deletion approval for protected records;
- soft-delete/tombstone where appropriate;
- immutable/versioned object storage where practical;
- separate backup credentials;
- audit;
- rate/volume anomaly detection later.

**Priority:** Critical.

## T19 — Consent/authorization mismatch
**Scenario:** system uses data for a purpose not covered by the recorded authorization or uses an expired/revoked authorization.

**Controls:**
- versioned purpose-specific consent/authorization;
- effective/revoked dates;
- policy checks at point of use;
- no generic 'consent=true' flag for all purposes;
- audit of consent basis.

**Priority:** High.

## T20 — Business-rule drift between app and agent
**Scenario:** agent memory says one rule while application policy or constitution says another.

**Controls:**
- repository/application policy authoritative;
- runtime bootstrap references canonical governance;
- agents query current policy for consequential workflows;
- policy version recorded in audit/decision where relevant.

**Priority:** High.

---

# Abuse cases
- staff searches a participant for curiosity rather than service need;
- founder/admin uses nonprofit participant data to market for-profit services without lawful basis;
- agent exports a full cohort to analyze one metric;
- partner user accesses data beyond referred participant scope;
- applicant intentionally uploads another person's credit report;
- user manipulates agent through uploaded text to reveal internal files;
- staff copies sensitive data into public AI/chat tools;
- automated reminder discloses sensitive program/violence/credit context on a shared phone.

# Security acceptance gates before real participant data
- authentication architecture accepted;
- entity authorization implemented and tested;
- data classes represented in schema/policy;
- secure secrets management;
- secure document storage/upload path;
- audit model operational;
- backups/restores tested;
- production logging reviewed for redaction;
- vendor/provider inventory reviewed;
- incident-response runbook created;
- high-risk agent actions disabled or approval-gated;
- privacy/retention/compliance review completed for launch jurisdiction.

# Status
`DECIDED`: threat model is part of architecture review and must be updated when new high-risk domains/integrations are added.

`RESEARCH NEEDED`: formal privacy impact assessment, vendor risk criteria, incident notification obligations, penetration testing scope, and production security monitoring stack.
