# ACE Credit Compliance Register

## Purpose
Maintain one explicit register of legal/regulatory/compliance topics that can constrain product, program, nonprofit, commercial, data, marketing, employment, grant, and agent workflows.

This is a planning/control document, not legal advice. `RESEARCH NEEDED` means the related implementation must not assume an answer.

## Status values
- `DECIDED CONTROL` — project control adopted regardless of exact legal scope.
- `RESEARCH NEEDED` — applicability/requirements need qualified review.
- `BLOCKS FEATURE` — feature may not enter production until resolved.
- `MONITOR` — requirements may change or become relevant later.

## Evidence standard
A compliance conclusion should eventually record:
- jurisdiction;
- legal/entity/service facts used;
- primary authority or official guidance;
- reviewer;
- date reviewed;
- decision/interpretation;
- required controls;
- revisit trigger.

---

# Register

## C-001 — Credit Repair Organizations Act (CROA)
**Area:** Credit services / for-profit / potentially other structures depending facts.

**Why relevant:** contemplated services may involve improving a consumer's credit record/history/rating. FTC materials identify CROA requirements including truthfulness, required disclosures/contracts/cancellation protections, and restrictions on advance payment for covered credit repair organizations.

**Status:** `RESEARCH NEEDED` + `BLOCKS FEATURE` for paid credit-repair launch and any operational design relying on an exemption/exclusion.

**Questions:**
- Which contemplated nonprofit and for-profit services meet the statutory definition?
- Does the proposed paid consultation + included credit assistance structure affect CROA treatment?
- What exact contract/disclosure/cancellation/payment timing is required for the commercial model?
- What records must be preserved?

**Controls now:**
- no misleading promise to remove accurate/timely negative information;
- no product architecture that assumes fees can be collected for covered credit-repair services before legally permitted;
- credit-related claims require substantiation/review;
- separate education from operational credit-service workflows.

**Primary source:** FTC, Credit Repair Organizations Act, 15 U.S.C. §§ 1679–1679j — https://www.ftc.gov/legal-library/browse/statutes/credit-repair-organizations-act

---

## C-002 — Fair Credit Reporting Act (FCRA) / Regulation V
**Area:** Consumer reports, credit data, disputes, permissible purpose.

**Why relevant:** future platform may review consumer reports or receive credit data. CFPB guidance emphasizes that users may not obtain/use a consumer report without a permissible purpose.

**Status:** `RESEARCH NEEDED` + `BLOCKS FEATURE` for direct report-provider/bureau integration.

**Questions:**
- Will participants supply their own reports, or will an entity obtain reports from a provider?
- What permissible purpose/authorization model applies to each method?
- What contractual certifications are required by a report provider?
- Which data qualifies as a consumer report vs. consumer-provided copy?
- How will disputes/communications interact with FCRA rights/processes?

**Controls now:**
- no automated pulling of consumer reports;
- no assumed permissible purpose;
- consumer authorization modeled as purpose/version/date specific;
- raw reports classified C4/CREDIT_DATA.

**Primary sources:** CFPB Regulation V and CFPB advisory opinion on permissible purposes — https://www.consumerfinance.gov/rules-policy/regulations/1022/ and https://www.consumerfinance.gov/rules-policy/final-rules/fair-credit-reporting-permissible-purposes-for-furnishing-using-and-obtaining-consumer-reports/

---

## C-003 — Telemarketing Sales Rule (TSR): credit repair
**Area:** Marketing/sales/payment timing.

**Why relevant:** FTC guidance identifies special payment restrictions for credit repair services sold through covered telemarketing and notes FCRA permissible-purpose requirements remain applicable.

**Status:** `RESEARCH NEEDED` + `BLOCKS FEATURE` if sales/marketing flows fall within TSR.

**Questions:**
- Will paid services be marketed/sold through covered interstate telephone campaigns, inbound calls resulting from advertising, or other covered patterns?
- How does the contemplated consultation model interact with TSR payment rules?
- What records/disclosures/do-not-call requirements apply?

**Primary source:** FTC, Complying with the Telemarketing Sales Rule — https://www.ftc.gov/business-guidance/resources/complying-telemarketing-sales-rule

---

## C-004 — Debt relief / debt management / credit counseling rules
**Area:** Debt services.

**Why relevant:** proposed scope includes debt-management education and may later include more active services. FTC TSR guidance has specific rules for covered for-profit debt relief services, and state laws/licensing can apply separately.

**Status:** `RESEARCH NEEDED` + `BLOCKS FEATURE` for creditor negotiation, debt management plans, settlement, payment administration, or representations that terms will be changed.

**Controls now:**
- MVP may provide general debt education and track participant goals/referrals;
- no negotiating creditor terms, handling dedicated accounts, transmitting debt payments, or debt-settlement workflow until legal scope is approved.

**Primary source:** FTC, Debt Relief Services & the Telemarketing Sales Rule: A Guide for Business — https://www.ftc.gov/business-guidance/resources/debt-relief-services-telemarketing-sales-rule-guide-business

---

## C-005 — State credit-services organization laws
**Area:** State licensing/registration/bond/contracts/fees.

**Status:** `RESEARCH NEEDED` + `BLOCKS FEATURE`.

**Trigger:** before serving residents of any state with covered credit-services activity.

**Required action:** create a jurisdiction matrix for every launch/service state covering:
- definition of credit-services organization;
- nonprofit exclusions/exemptions, if any;
- registration/license;
- surety bond;
- contract language;
- cancellation rights;
- fee timing/caps;
- prohibited practices;
- record retention;
- regulator;
- penalties/private actions.

**Open decision:** first launch jurisdiction(s) must be explicitly selected before this matrix can be finalized.

---

## C-006 — State debt-adjusting/debt-management laws
**Area:** Debt management/licensing.

**Status:** `RESEARCH NEEDED` + `BLOCKS FEATURE` for active debt-management services.

**Required action:** jurisdiction-by-jurisdiction review before any negotiation, debt-management plan administration, creditor payment handling, settlement, or fee-based debt-adjusting service.

---

## C-007 — Federal/state unfair or deceptive acts and practices (UDAP/UDAP-like laws)
**Area:** Marketing, program claims, service representations.

**Status:** `DECIDED CONTROL` + `RESEARCH NEEDED` for jurisdiction specifics.

**Controls:**
- no guaranteed score increase, deletion, grant award, funding, housing, job, business revenue, or credit outcome;
- material limitations disclosed;
- outcome statistics retain methodology/source;
- testimonials/endorsements reviewed;
- agent-generated marketing claims require human review.

---

## C-008 — Electronic signatures / electronic disclosures
**Area:** Contracts, consent, authorizations.

**Status:** `RESEARCH NEEDED`.

**Questions:**
- Which disclosures/contracts may be delivered/signed electronically?
- What consumer consent and retention requirements apply?
- Are any credit/debt forms subject to special formatting or delivery rules?

**Implementation control:** version, timestamp, signer identity, document hash/reference, acceptance event, and withdrawal/revocation where applicable.

---

## C-009 — Privacy notice, consent, data use & state privacy laws
**Area:** Personal information.

**Status:** `RESEARCH NEEDED` + `BLOCKS REAL DATA` until launch-state requirements are mapped.

**Questions:**
- states of residence/service;
- applicable comprehensive privacy statutes and exemptions;
- notice/rights obligations;
- sensitive-data consent;
- service provider/processor contracts;
- data sale/share/targeted advertising implications;
- data subject access/correction/deletion processes.

**Controls now:** data minimization, entity/purpose scoping, classification, synthetic development data, no cross-entity marketing reuse by default.

---

## C-010 — Data breach/security notification laws
**Area:** Security incident response.

**Status:** `RESEARCH NEEDED` + `BLOCKS REAL DATA` until incident plan includes launch jurisdictions.

**Required deliverable later:** incident response runbook with detection, containment, counsel escalation, evidence preservation, insurer/vendor notification, regulator/consumer timelines by applicable jurisdiction.

---

## C-011 — Gramm-Leach-Bliley Act / Safeguards Rule applicability
**Area:** Financial information/security.

**Status:** `RESEARCH NEEDED`.

**Reason:** depending on final activities, one or more entities could potentially fall within definitions applicable to financial institutions/services. Do not assume applicability or exemption.

**Required review:** business activity mapping against current FTC/other regulator scope before production credit/debt/financial-service data architecture is finalized.

---

## C-012 — Nonprofit 501(c)(3) exempt purpose/private benefit/inurement
**Area:** Nonprofit structure and relationship with for-profit.

**Status:** `DECIDED CONTROL` + `RESEARCH NEEDED` for entity-specific transactions.

**Controls:**
- nonprofit operates for exempt/charitable purposes;
- no automatic subsidy of for-profit;
- related-party contracts documented and reviewed;
- conflicts disclosed;
- interested persons do not control approval of their own arrangements;
- fair/reasonable terms supported where required;
- nonprofit resources/participant data are not diverted for private benefit.

**Primary sources:** IRS exemption requirements and private benefit guidance — https://www.irs.gov/charities-non-profits/charitable-organizations/exemption-requirements-501c3-organizations and https://www.irs.gov/charities-non-profits/charitable-organizations/inurement-private-benefit-charitable-organizations

---

## C-013 — Nonprofit compensation & conflicts of interest
**Area:** Payroll/governance.

**Status:** `DECIDED CONTROL` + `RESEARCH NEEDED` for final governance process.

**Controls:**
- nonprofit may pay employees for services;
- compensation is approved through appropriate conflict-free governance;
- reasonableness/comparability documented for key compensation;
- related-party compensation/contracts identified;
- grants may fund personnel only according to each award's terms.

**Primary sources:** IRS Form 1023 compensation/conflict guidance and Form 990 instructions — https://www.irs.gov/charities-non-profits/form-1023-required-information-about-compensation-and-other-financial-information and https://www.irs.gov/instructions/i990

---

## C-014 — Related-party/shared-services arrangements
**Area:** Nonprofit ↔ for-profit.

**Status:** `RESEARCH NEEDED` + `BLOCKS FEATURE` for shared employee/vendor/IP/data arrangements that are not routine arms-length purchases.

**Required records:**
- conflict disclosure;
- board/authorized approval where appropriate;
- scope and pricing methodology;
- comparability/fair-market evidence where appropriate;
- data-sharing terms;
- grant restriction review;
- accounting treatment;
- legal/tax review.

---

## C-015 — Charitable solicitation registration
**Area:** Donations/fundraising.

**Status:** `RESEARCH NEEDED` before public fundraising across jurisdictions.

**Questions:** where the nonprofit solicits, online solicitation treatment, exemptions/thresholds, renewal/reporting, fundraising vendor rules.

---

## C-016 — Grant compliance
**Area:** Restricted funds, personnel, reporting.

**Status:** `DECIDED CONTROL`.

**Controls:** every award stores allowable/unallowable costs, personnel rules, indirect rate, match, period of performance, procurement/approval conditions, reporting due dates, outcome definitions, record retention, and certifications.

No assumption that a cost allowed by one grant is allowed by another.

---

## C-017 — Employment/payroll/workforce law
**Area:** Staff.

**Status:** `RESEARCH NEEDED` before hiring in each jurisdiction.

**Scope:** worker classification, wage/hour, payroll taxes, unemployment/workers compensation, leave, anti-discrimination/harassment, background checks if used, remote work, benefits, personnel records.

Payroll processor grants/credits or philanthropic programs do not alter employer obligations.

---

## C-018 — Accessibility
**Area:** Web/app/curriculum/program delivery.

**Status:** `DECIDED CONTROL` for accessibility-by-design; `RESEARCH NEEDED` for exact legal scope.

**Target:** use WCAG 2.2 AA as product design target unless superseded by a stronger applicable requirement.

Controls include keyboard access, semantic structure, captions/transcripts, contrast, form errors, readable language, assistive-technology testing, accessible documents.

---

## C-019 — Communications: TCPA/Do-Not-Call/CAN-SPAM/state rules
**Area:** SMS, calls, email, reminders, marketing.

**Status:** `RESEARCH NEEDED` + `BLOCKS AUTOMATION` for marketing/outreach automation.

**Controls now:** transactional/program communications separated from marketing; consent/source/preferences stored; opt-out respected; sensitive program details minimized in messages.

---

## C-020 — Record retention & legal holds
**Area:** All domains.

**Status:** `RESEARCH NEEDED` + `BLOCKS FINAL DELETION POLICY`.

Retention must reconcile:
- legal requirements;
- grant/contract requirements;
- tax/accounting records;
- employment records;
- credit/debt-service records;
- participant privacy/minimization;
- litigation/legal hold.

Do not use one indefinite retention period for all data.

---

## C-021 — Vendor/model provider contracts & data processing
**Area:** SaaS, cloud, AI.

**Status:** `RESEARCH NEEDED` + `BLOCKS C3/C4 THIRD-PARTY PROCESSING`.

Required review:
- data received;
- training/use of customer data;
- retention;
- subprocessors;
- breach terms;
- security standards;
- location/residency;
- deletion/export;
- audit/compliance reports;
- contractual confidentiality;
- business continuity.

---

## C-022 — Consumer financial education vs. individualized professional advice
**Area:** Curriculum/coaching.

**Status:** `RESEARCH NEEDED`.

**Purpose:** define when general education/coaching could cross into regulated legal, tax, investment, lending, debt-adjusting, or other professional services.

**Control:** content/service taxonomy must label what staff/agents may educate, what requires credentialed partner referral, and what is prohibited.

---

## C-023 — Business development / grants / funding representations
**Area:** Entrepreneur services.

**Status:** `DECIDED CONTROL` + `RESEARCH NEEDED` where business opportunity or funding-broker rules may apply.

Controls:
- no guaranteed business funding, grants, revenue, procurement awards, or credit limits;
- distinguish education/readiness from brokering or arranging regulated financing;
- record source/date for opportunities;
- disclose that funder eligibility/decisions belong to third parties.

---

## C-024 — Insurance
**Area:** Organizational risk transfer.

**Status:** `RESEARCH NEEDED` before operations.

Potential coverage review:
- general liability;
- professional/E&O;
- cyber/privacy;
- D&O for nonprofit;
- employment practices;
- workers compensation;
- crime/fidelity where handling funds;
- special coverage required by grants/contracts.

---

# Production launch compliance gate
No production credit-services or participant-data launch until:
1. launch entity/entities are legally formed/approved;
2. launch jurisdiction(s) are selected;
3. state credit-services/debt-management matrix is completed for the actual service catalog;
4. CROA/FCRA/TSR applicability is reviewed for the exact workflows;
5. privacy/security/retention requirements are mapped;
6. consumer-facing agreements/disclosures/consents are reviewed;
7. nonprofit/for-profit related-party structure is documented;
8. appropriate insurance/vendor contracts are reviewed;
9. staff training and escalation procedures exist;
10. applicable controls are represented in product acceptance tests.

# Status
This register is a living control artifact. Every resolved item should be converted from an open question into a dated decision with source/reviewer and linked implementation controls.
