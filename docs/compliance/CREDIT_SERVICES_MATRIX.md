# Credit Services Matrix

## Purpose
Translate the planned credit-recovery model into discrete activities so legal review, product permissions, staff training, billing, data access, and agent automation can be decided activity by activity.

**Important:** nonprofit status or zero participant price does not automatically make every credit-related activity legally exempt. This matrix is an operational planning artifact. Applicable federal and state law must be reviewed for the exact entity, service, jurisdiction, marketing, compensation, and workflow.

## Status values
- `GREEN — EDUCATION MVP`: may be designed as educational capability, subject to ordinary consumer/privacy review.
- `YELLOW — COUNSEL REVIEW`: concept may be modeled/prototyped but not launched as an operational service until legal review.
- `RED — DO NOT AUTOMATE/LAUNCH`: prohibited by current project policy until explicit legal and owner approval.

---

| Activity | Nonprofit planned treatment | For-profit planned treatment | Current status | System control |
|---|---|---|---|---|
| Explain how credit reports/scores work | Core financial education | Core education | GREEN — EDUCATION MVP | Approved curriculum/version |
| Teach payment history/utilization/credit mix concepts | Core education | Core education | GREEN — EDUCATION MVP | No guaranteed score outcome |
| Teach consumer rights/dispute process generally | Core education | Core education | GREEN — EDUCATION MVP | Legal content version/source review |
| Help participant obtain own free reports through lawful consumer channels | Guided education/referral | Guided education/referral | GREEN/YELLOW depending implementation | Do not collect credentials; approved links/instructions |
| Participant uploads a copy of her own report | Potential program workflow | Potential client workflow | YELLOW — COUNSEL + SECURITY REVIEW | C4 storage, authorization, limited access |
| Staff reviews participant-provided report for educational discussion | Planned | Planned | YELLOW — COUNSEL REVIEW | Credit-specialist role, purpose, audit |
| Categorize report items | Potential support workflow | Potential support workflow | YELLOW | Staff review; not legal determination |
| Identify possible errors/inconsistencies for participant review | Potential support workflow | Potential support workflow | YELLOW | `DisputeCandidate`, not automatic dispute |
| Explain how participant can dispute inaccurate information herself | Planned education | Planned education | GREEN/YELLOW | Approved consumer-rights content |
| Draft a dispute letter with participant-specific facts | Potential no-cost assistance | Potential service | YELLOW — COUNSEL REVIEW | Draft only; versioned evidence; no auto-send |
| Staff submits dispute on participant's behalf | Desired possible service | Desired possible service | RED until exact federal/state review | Human approval + legal workflow required |
| Agent autonomously submits disputes | Not allowed in early design | Not allowed | RED | Capability absent/disabled |
| Send high-volume/template disputes without individualized review | Not planned | Not planned | RED | Prohibited project policy |
| Dispute accurate/timely information merely to seek deletion | Not permitted as program practice | Not permitted | RED | Staff/agent policy prohibits deceptive dispute purpose |
| Promise deletion of accurate negative items | Prohibited | Prohibited | RED | Marketing/content validation |
| Promise specific score increase | Prohibited | Prohibited | RED | No guaranteed outcomes |
| Track score over time using participant-reported score | Possible outcome measurement | Possible | YELLOW | Source tagged as self-reported |
| Pull score/report from third-party provider | Potential later | Potential later | RED until permissible purpose/provider/security review | Integration disabled until approved |
| Recommend on-time payment/utilization actions | Educational action plan | Educational action plan | GREEN/YELLOW depending personalization | Staff-reviewed plan; no guarantee |
| Recommend opening a specific credit product | Referral/education only initially | Referral/education only initially | YELLOW — compliance/affiliate review | Avoid individualized lending/financial product advice without review |
| Receive affiliate compensation for credit products | Not assumed | Possible future business model | RED until conflict/disclosure/compliance review | Separate commercial approval/integration |
| Credit builder loan/secured card educational directory | Potential resource directory | Potential resource directory | GREEN/YELLOW | Source/date; no endorsement unless reviewed |
| Add participant as authorized user/piggybacking arrangement | Not core program | Not core service | RED until legal/risk review | No marketplace or tradeline brokering |
| Sell tradelines | Not allowed | Not allowed | RED | Prohibited project scope |
| Create synthetic identity/CPN or advise identity manipulation | Not allowed | Not allowed | RED | Prohibited; fraud-risk control |
| Instruct participant to misstate facts to bureaus/creditors | Not allowed | Not allowed | RED | Prohibited |
| Debt budgeting/education | Core stabilization | Education | GREEN | Curriculum/coaching |
| Explain debt payoff strategies | Core education | Education | GREEN/YELLOW if individualized advice becomes regulated in jurisdiction | Approved scope |
| Negotiate creditor terms | Potential partner referral rather than direct service initially | Possible future service | RED until debt-management legal review | No negotiation capability in MVP |
| Enroll/manage debt management plan | Not in MVP | Not in MVP | RED | Out of scope |
| Debt settlement | Not planned | Not planned initially | RED | Out of scope/legal review |
| Hold/transmit participant funds to creditors | Not planned | Not planned | RED | No money-movement capability |
| Charge nonprofit participant for program credit assistance | Current mission intent is no-cost for qualifying participants | N/A | RED unless program model changes and legal/funder review | Nonprofit program price rules |
| Charge commercial client for consultation/education while credit-related assistance is included | N/A | Planned concept | YELLOW — COUNSEL REVIEW | Do not design around assumption this avoids CROA/TSR/state fee rules |
| Use grant funds to pay nonprofit credit specialists | Planned where grant permits | N/A | YELLOW by grant terms, not inherently prohibited | Award-specific cost allowability + payroll allocation |
| Use nonprofit grant-funded staff to service for-profit clients | Not permitted absent lawful documented arrangement and grant allowability | Could receive services only under approved related-party arrangement | RED by default | Entity/time/cost allocation controls |

---

# Nonprofit credit program design target

The desired nonprofit program can be described operationally as **Credit Recovery & Building**, not merely “free credit repair.”

Potential approved flow after legal review:
1. participant is eligible/enrolled in nonprofit program;
2. financial/credit education prerequisites completed;
3. participant chooses credit-support pathway;
4. required consent/authorization collected;
5. participant supplies or authorizes approved access to credit information;
6. trained staff reviews information;
7. participant receives educational explanation/action plan;
8. possible inaccuracies are documented as candidates;
9. any participant-specific dispute assistance follows the approved legal workflow;
10. external communication requires human approval and valid authorization;
11. results are tracked without promises/guarantees;
12. grant-funded staff time is allocated only when award terms allow.

## Staffing concept
Potential roles:
- Credit Program Manager;
- Credit Specialist;
- Financial Educator;
- Financial Coach/Case Manager;
- Compliance Reviewer/consulting counsel;
- Data/Evaluation staff.

Role design does not itself establish legal eligibility to perform a regulated activity.

---

# Commercial credit program design target

The commercial model may combine:
- paid consultation/education;
- individualized credit education;
- approved done-for-you assistance;
- business-development pathways.

**Critical legal design question:** do not assume characterizing credit assistance as “free with a paid consultation” removes federal/state credit-repair or advance-fee requirements. Counsel must review the substance of the offer, sales/marketing representations, contract, timing, pricing, and actual services before implementation.

System architecture therefore must support flexible billing/service separation rather than hard-coding an unreviewed fee structure.

---

# Credit workflow state machine

Suggested states:
`not_started → education_required → authorized → report_received → under_staff_review → action_plan_ready → participant_review → dispute_candidate_review → approval_required → approved/rejected → external_action_pending → sent/confirmed → monitoring → outcome_recorded → closed`

Not every participant uses every state.

## Transition rules
- `authorized` requires a valid authorization version and effective date.
- `report_received` requires secure storage and data classification.
- `dispute_candidate_review` cannot be created from an agent conclusion alone.
- `approved` references the exact communication/action version.
- any edit after approval invalidates prior approval unless change is proven non-material under later policy.
- `sent/confirmed` requires destination confirmation/event.
- outcomes distinguish correction/removal, score movement, utilization change, and other metrics.

---

# Agent policy for credit domain

## May eventually assist
- explain approved curriculum;
- summarize structured credit observations for staff;
- identify missing documentation;
- prepare action-plan drafts from approved rules;
- draft participant communications for review;
- compare snapshots;
- track deadlines/tasks;
- prepare internal outcome summaries.

## Cannot autonomously do in early phases
- determine legal disputability;
- submit disputes;
- impersonate participant;
- obtain report using participant credentials;
- advise false statements;
- promise deletion/score increase;
- enroll participant in credit products;
- charge/collect credit-service fees;
- change authorizations;
- override staff/legal approval.

---

# Required legal review package before operational launch
For each entity/jurisdiction, provide counsel with:
- exact service catalog;
- free vs. paid structure;
- marketing copy and claims;
- intake flow;
- contracts/disclosures;
- cancellation/refund policy;
- when payment is requested/collected;
- consumer-report acquisition method;
- authorization language;
- staff vs. agent responsibilities;
- dispute workflow;
- communications channels;
- record-retention plan;
- referral/affiliate arrangements;
- nonprofit/for-profit relationship;
- grant-funded staffing/cost allocation where relevant.

# Status
`DECIDED`: education-first design, no deceptive claims, no autonomous disputes, no direct report pull until approved, no debt settlement/money movement in MVP.

`RESEARCH NEEDED`: exact nonprofit and commercial credit-services legal scope, launch jurisdictions, billing/contract model, report-provider access, dispute-assistance rules.
