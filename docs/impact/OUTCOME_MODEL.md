# ACE Credit Impact & Outcome Model

## Purpose
Create a measurable program architecture that can support participant care, program improvement, grant reporting, and credible impact claims without reducing success to a credit score.

## North-star transformation
**financial stability → financial capability → stronger credit → increased income → asset building → entrepreneurship where appropriate → wealth creation → economic independence**

This is a directional model, not a required linear path for every participant.

---

# Theory of change

## Inputs
Potential inputs include:
- trained financial educators/coaches/credit specialists;
- grant-funded personnel;
- curriculum;
- coaching/case management;
- safe referral network;
- technology;
- participant support such as allowable transportation/childcare;
- community partnerships;
- workforce/business-development partners;
- compliant credit-recovery resources;
- evaluation/data capacity.

## Activities
- financial education;
- financial goal/action planning;
- budgeting/banking/savings coaching;
- debt education/strategy;
- credit education and approved recovery/building services;
- resource/housing referrals;
- workforce/income advancement;
- entrepreneurship/business readiness;
- wealth/asset education;
- follow-up/coaching.

## Outputs
Immediate countable delivery:
- people enrolled;
- sessions delivered;
- modules completed;
- assessments completed;
- goals created;
- credit cases initiated where approved;
- referrals made/connections completed;
- workforce/business activities completed;
- follow-up contacts.

## Short-term outcomes
- increased financial knowledge;
- increased credit understanding;
- clear financial action plan;
- banking access/use improvement;
- savings behavior established;
- debt plan established;
- improved fraud/consumer-rights awareness;
- improved financial confidence/self-efficacy where measured responsibly.

## Intermediate outcomes
- emergency savings increased;
- debt reduced or delinquency stabilized;
- credit history/profile strengthened;
- housing retained/secured;
- employment obtained/retained;
- income increased;
- business readiness/formalization milestones;
- capital/procurement readiness;
- reduced reliance on high-cost financial products where measured.

## Long-term outcomes
- greater economic stability;
- asset accumulation;
- sustainable business ownership where chosen;
- increased financial resilience;
- wealth creation;
- economic independence.

---

# Measurement principles
1. Define every metric before reporting it.
2. Retain denominator as well as numerator.
3. Distinguish output from outcome.
4. Distinguish self-reported from verified data.
5. Capture measurement date/time window.
6. Keep metric versions; do not redefine history silently.
7. Do not imply causation from simple pre/post observation unless evaluation design supports it.
8. Use participant-level data only where necessary; funder reports should prefer aggregates.
9. Missing data is not zero.
10. Participant exit is not automatically failure.
11. Credit score change must be contextualized by baseline and measurement source/time.
12. Entrepreneurship metrics apply only to participants entering that pathway.

---

# Source/provenance types
Each `Measurement` should identify one:
- `SELF_REPORTED`
- `STAFF_OBSERVED`
- `DOCUMENT_VERIFIED`
- `SYSTEM_GENERATED`
- `PARTNER_CONFIRMED`
- `THIRD_PARTY_DATA`
- `DERIVED`

Also capture source date and recorder/system identity.

---

# Core metric catalog

## Participation

### Applicants
Count of distinct submitted applications in reporting period.

### Enrolled participants
Distinct people with enrollment start during period.

### Active participants
Distinct active enrollments at period checkpoint.

### Program completion rate
`completed enrollments / enrollments reaching an eligible completion/exit evaluation point`

Denominator methodology must be defined per program; do not automatically divide by every applicant.

### Attendance / engagement
Service events attended vs. scheduled/required according to program definition.

---

# Financial knowledge/capability

### Financial knowledge score
Pre/post score from versioned assessment.

Measures:
- baseline mean/median;
- follow-up mean/median;
- participant-level change where matched;
- percent meeting defined proficiency threshold.

### Credit knowledge score
Separate assessment if credit curriculum requires greater detail.

### Action-plan completion
Percent completing defined financial action plan milestones.

### Financial confidence/self-efficacy
Optional validated or program-defined scale. Label clearly as self-reported perception, not financial condition.

---

# Banking/access

### Banked status
Participant has an appropriate transaction account according to program definition.

### Banking access improvement
Examples:
- opened account;
- restored account access;
- moved from high-cost alternative service to lower-cost account;
- established direct deposit where participant chooses.

Do not assume bank account ownership alone equals financial health.

---

# Savings/resilience

### Emergency savings established
Participant moves from no designated emergency savings to positive designated amount or agreed milestone.

### Emergency savings amount/range
Prefer ranges if exact dollars are not necessary for program/funder reporting.

### Savings milestone achievement
Percent reaching participant-specific target or standard checkpoint.

### Emergency expense resilience
Optional self-report: ability to cover a defined emergency amount/timeframe. Wording and amount must be versioned.

---

# Debt

### Debt plan established
Participant completes debt inventory/priority plan.

### Debt reduction
Change in measured debt balance where reliable data exists.

Do not report debt reduction if baseline/follow-up definitions differ.

### Delinquency stabilization
Defined event such as bringing an account current, entering approved arrangement, or preventing new delinquency—only if data source supports claim.

---

# Credit

### Credit report understanding
Assessment or participant demonstration of ability to identify major report sections/rights.

### Credit profile established
Participant previously credit-invisible/thin-file reaches defined positive-history threshold according to approved measurement approach.

### Credit score change
`follow-up score - baseline score` using same score/model/source where practical.

Report:
- number with valid paired measurements;
- mean/median change;
- distribution;
- baseline bands;
- measurement interval;
- source/model.

Never present score increase among only successful cases as program-wide average.

### Utilization improvement
Change in utilization metric where valid account/limit data exists.

### On-time payment behavior
Participant-reported or verified milestone. Source must be explicit.

### Credit-report correction outcome
Count/percent of documented inaccuracies corrected/updated/removed through approved process. Do not count deletion of accurate data as intended success.

### Credit-building action completion
Examples:
- autopay/reminder system established;
- balance-reduction milestone;
- positive account established where appropriate;
- secured/card/credit-builder educational action completed.

---

# Housing stability

### Housing retained
Participant at documented risk retains housing through program-defined follow-up window.

### Housing secured
Participant experiencing homelessness/housing instability enters stable housing according to program definition.

### Housing referral connection
Referral accepted + connection confirmed.

Safety-sensitive location information is never required in aggregate reporting.

---

# Employment/income

### Job obtained
Participant reports/verification shows new employment after program/workforce engagement.

### Job retention
Employment retained at defined checkpoint(s), e.g. 30/90/180 days where program methodology uses those intervals.

### Income increase
Comparable baseline/follow-up income measure.

Report source, time basis (hourly/monthly/annual), and whether gross/net. Prefer derived standardized measure only when assumptions are explicit.

### Training completion
Workforce/credential training completed.

---

# Entrepreneurship/business

Denominator only includes participants who enter entrepreneurship pathway.

### Business-readiness plan completed
Versioned readiness requirements completed.

### Business formalized
Business legal/administrative milestone based on documented definition.

### Business bank account established
Participant reports/verification of separate business banking.

### Bookkeeping/financial system established
Defined system/process in use.

### Business plan completed
Plan meets program completion criteria.

### Business credit readiness
Educational/readiness milestone, not guaranteed credit approval.

### Capital readiness
Required documents/systems completed for targeted funding type.

### Capital secured
Actual grant/loan/investment/other capital confirmed. Report type and source; do not attribute solely to program without appropriate evaluation evidence.

### Procurement readiness/award
Separate readiness from actual contract award.

---

# Economic stability composite

## Purpose
Avoid equating one financial measure with stability.

A future **Economic Stability Index** may combine versioned indicators such as:
- stable/sufficient income trend;
- housing stability;
- essential bill payment stability;
- emergency savings;
- banking access;
- manageable debt/delinquency trajectory;
- credit access/health where relevant;
- reduced financial crisis frequency;
- progress toward participant-defined goals.

## Rule
Do not calculate a composite score until:
- indicators are defined;
- weighting method is justified;
- missing-data treatment is specified;
- interpretation is tested;
- score is not used for punitive eligibility/denial without explicit review.

MVP may display indicators individually instead.

---

# Safety and dignity metrics
Potential process measures:
- percent with safe-contact preference recorded when applicable;
- participant-reported sense of control/understanding;
- referral connection rate;
- time from application to decision;
- unresolved service barrier count;
- complaint/grievance resolution;
- participant data correction requests completed.

Do not require survivors to disclose violence details merely to improve program metrics.

---

# Grant reporting architecture

## FunderMetricMapping
Each funder-required metric maps to:
- internal metric ID/version;
- funder wording;
- period;
- inclusion/exclusion rules;
- numerator/denominator;
- verification level;
- reporting format;
- responsible reviewer.

If a funder definition differs from ACE's standard metric, create mapping/derived metric rather than silently redefining the standard.

## Reporting review
Before external impact reporting:
1. completeness check;
2. duplicate check;
3. denominator verification;
4. source/provenance check;
5. outlier/anomaly review;
6. privacy/aggregation review;
7. narrative claim consistency;
8. authorized approval/certification.

---

# Suggested measurement checkpoints
Programs may select:
- intake/baseline;
- 30-day;
- 90-day;
- program completion;
- 6-month;
- 12-month.

Do not collect every metric at every checkpoint. Use minimum data required for service/evaluation.

---

# Data model requirements
`MetricDefinition`:
- metric ID/name;
- domain;
- definition;
- unit;
- formula;
- eligible population/denominator;
- source requirements;
- verification class;
- privacy classification;
- aggregation rules;
- effective dates/version;
- owner.

`Measurement`:
- metric version;
- entity/program/enrollment context;
- subject pseudonymous ID/reference;
- value/category;
- measurement date;
- source type;
- evidence reference where appropriate;
- recorded by;
- data-quality status.

---

# Data-quality statuses
- `VALID`
- `SELF_REPORTED_UNVERIFIED`
- `MISSING`
- `STALE`
- `CONFLICTING`
- `CORRECTED`
- `EXCLUDED_FROM_REPORTING`

Corrections should preserve audit history.

# Impact claims policy
Prohibited without adequate evidence:
- “ACE causes X-point credit increases” from simple averages;
- “graduates become financially independent” without defined measure/follow-up;
- “X% obtained jobs because of ACE” without causal evaluation support;
- selecting only successful participants for program-wide outcome claims;
- fabricated estimates to satisfy a grant report.

Preferred language matches evidence, e.g. “Among participants with paired baseline and follow-up measurements…”

# MVP outcome set
At minimum, configure:
- enrollment/completion;
- financial knowledge pre/post;
- goals established/completed;
- emergency savings milestone;
- banking access milestone;
- debt action plan;
- workforce referral/job milestones;
- housing/resource referral connections where relevant;
- entrepreneurship pathway opt-in/readiness where relevant;
- credit education completion; credit score/profile outcomes only when lawful/reliable data workflow exists.

# Status
`DECIDED`: outcome provenance/versioning, output vs. outcome distinction, no credit-score-only success definition, pathway-specific denominators.

`RESEARCH NEEDED`: validated stability instrument selection, exact pilot targets, grant-specific metric definitions, long-term evaluation design.
