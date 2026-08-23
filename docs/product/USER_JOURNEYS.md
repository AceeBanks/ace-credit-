# ACE Credit User Journeys

## Purpose
Define the intended end-to-end experience before screens, APIs, or automation are built. Journeys include state changes, data requirements, safety points, staff responsibility, agent opportunities, and exit conditions.

---

# Journey 1 — Nonprofit applicant → enrolled participant

## Intent
Make it possible for an eligible Black woman to enter the program with dignity, understand what is being asked of her, and avoid supplying unnecessary sensitive information before it is needed.

## Flow
1. Applicant learns about program from website/community/referral partner.
2. Applicant sees purpose, population focus, available services, expected participation, privacy/safety information, and eligibility basics.
3. Applicant starts an application using minimal contact information.
4. Applicant chooses safe communication preferences.
5. System presents required privacy/consent notices and purpose-specific questions.
6. Applicant completes eligibility questions.
7. Application moves to `submitted`.
8. Staff reviews using configured eligibility rule set.
9. If information is missing, applicant receives a safe request for only the missing items.
10. Authorized staff records `eligible` or `ineligible` decision with rule/version and reason category.
11. If accepted, applicant reviews program agreement/consents.
12. Enrollment is created.
13. Staff assignment and initial orientation tasks are created.
14. Baseline assessments are scheduled/completed.
15. Participant enters active program journey.

## Data minimization
Do not collect raw credit report, SSN, detailed DV narrative, bank account numbers, or full debt inventory during basic intake unless a specific approved reason requires it.

## Agent role
May:
- answer approved FAQ;
- flag incomplete fields;
- route application to correct staff queue;
- prepare non-sensitive follow-up.

May not:
- make final eligibility decision unless later policy explicitly delegates a strictly mechanical rule;
- infer survivor details;
- use application data for commercial marketing.

## Success
Applicant reaches a clear outcome and knows next step without unnecessary friction or unsafe communication.

---

# Journey 2 — Participant onboarding → individualized financial recovery plan

## Flow
1. Participant completes orientation.
2. Participant completes baseline financial knowledge assessment.
3. Coach/educator reviews goals and immediate stability concerns.
4. Participant selects or confirms priority goals.
5. Staff identifies program pillars applicable now:
   - financial education;
   - stabilization;
   - credit recovery/building;
   - workforce/income;
   - business/wealth where appropriate.
6. System creates a service plan with required/recommended activities.
7. Participant sees plain-language tasks, not internal case jargon.
8. Staff records referrals for urgent needs beyond program scope.
9. Participant and staff acknowledge the plan.
10. Progress becomes visible through goals/milestones.

## Design rule
The plan is individualized without assuming every participant needs every pathway. Entrepreneurship remains optional.

## Success
Participant can answer:
- what am I working on first?
- why does it matter?
- what do I need to do?
- what will staff do?
- how will we know progress is happening?

---

# Journey 3 — Survivor-sensitive participant

## Intent
Provide financial recovery support without making technology itself a safety risk.

## Flow additions
1. Participant can designate safe contact method/time and whether voicemail/text content must be generic.
2. Survivor-sensitive information is captured only when required for service/safety.
3. Protected address/safety details use restricted fields rather than ordinary notes.
4. Staff role must explicitly permit survivor-sensitive access.
5. Routine staff dashboards show only what is necessary.
6. Referrals disclose minimum data.
7. Notifications avoid words that could expose violence, shelter, credit, debt, or program context on a shared device unless participant explicitly chooses otherwise.
8. Access to highly sensitive fields is audited.
9. Participant can update communication safety preference.

## Agent rule
General-purpose agents do not receive safety-plan/protected-location detail. If a future specialized workflow requires it, use narrow task-bound access and no persistent memory.

## Success
Participant can use the program without unnecessary disclosure or unsafe communications.

---

# Journey 4 — Financial education pathway

## Flow
1. Baseline assessment identifies knowledge priorities.
2. Program assigns required core modules and optional modules.
3. Participant completes content/activities.
4. Staff/participant records practical application tasks.
5. Post-module checks measure understanding.
6. Coach connects concepts to participant goals.
7. Completion and pre/post change are recorded.
8. Follow-up checks measure whether knowledge translated into action where appropriate.

## Examples of practical tasks
- create/update spending plan;
- open or optimize appropriate banking relationship;
- create emergency savings goal;
- review own credit report;
- create debt inventory;
- identify fraud/scam warning signs;
- choose one financial goal.

## Agent role
May tutor from approved curriculum, explain concepts, generate practice examples, and summarize progress. It may not turn approved educational content into guaranteed individualized legal/financial claims.

---

# Journey 5 — Credit recovery/building pathway

## Preconditions
- participant is enrolled in an eligible program/engagement;
- legal scope for entity/jurisdiction approved;
- staff role/training approved;
- required authorization active;
- secure credit-data workflow available.

## Flow
1. Participant completes credit education prerequisite.
2. Participant opts into credit-support pathway.
3. Required authorization is captured.
4. Participant provides report/data through approved method.
5. Credit specialist reviews.
6. Structured observations are created.
7. Staff and participant review action plan.
8. Rebuilding actions are assigned/tracked.
9. Possible report inaccuracies may become `DisputeCandidate` records.
10. Evidence is collected/reviewed.
11. If participant-specific dispute assistance is legally approved, draft is prepared.
12. Human approval gate binds to exact draft/version.
13. Approved external action is executed through controlled channel.
14. Response/follow-up is recorded.
15. New snapshot/progress data is captured at appropriate interval.
16. Outcome is measured with source/provenance.

## Agent role
Can assist with organization, completeness checks, comparison, and draft preparation after approval of the agent workflow. No autonomous disputes in early phases.

## Success
Participant understands what changed, what remains, and what behaviors/actions support long-term credit health. The organization can prove what it did without misrepresenting outcomes.

---

# Journey 6 — Financial stabilization pathway

## Flow
1. Coach identifies immediate stability priorities with participant.
2. System records goals in participant-selected order.
3. Budget/savings/debt/banking actions are created at the minimum detail necessary.
4. External housing, benefits, food, childcare, legal, DV, workforce, or other referrals are created where program scope ends.
5. Referral connection/status is followed up.
6. Milestones are recorded.
7. Stability assessment is repeated at program checkpoints.

## Important rule
Program does not imply that a participant failed because a budget did not solve structural income/housing/caregiving barriers.

---

# Journey 7 — Workforce/income pathway

## Flow
1. Participant chooses employment/income goal.
2. Staff records current baseline and desired outcome.
3. Participant receives workforce readiness activities or partner referral.
4. Training/interview/job milestones are tracked.
5. Job obtained/retention checkpoints are captured.
6. Income change is measured with source type.
7. Financial plan is updated as income changes.

## Agent role
May prepare resume/job-search materials if offered, find approved resources, track tasks, and summarize progress. Hiring/employment decisions belong to employers/partners.

---

# Journey 8 — Entrepreneurship/business pathway

## Preconditions
Participant expresses interest; pathway is not assigned merely because it exists.

## Flow
1. Entrepreneurship readiness/interest assessment.
2. Participant decides whether to proceed now, later, or not at all.
3. Business concept/current business profile captured.
4. Staff identifies stage:
   - idea;
   - pre-launch;
   - newly formed;
   - operating;
   - growth/readiness.
5. Education/tasks may cover planning, formation education, business banking, bookkeeping, business credit, capital readiness, grants, procurement, systems.
6. Funding opportunities are presented with source/date/eligibility caveats.
7. Milestones and business outcomes are recorded.
8. Participant may continue long-term wealth/asset pathway.

## Agent rule
No guaranteed grants/funding/revenue. Opportunity information must retain source and freshness.

---

# Journey 9 — Program completion / exit / follow-up

## Flow
1. Staff reviews completion requirements.
2. Participant completes post-assessments.
3. Open goals are marked achieved/continuing/referred/paused.
4. Exit reason and service summary recorded.
5. Participant receives ongoing resources/action plan.
6. Program enrollment moves to completed/exited.
7. Follow-up checkpoints scheduled based on program design and consent.
8. Outcomes at 30/90/180/etc. days may be collected if program methodology supports them.
9. Data retention rules apply after active service ends.

## Success
Completion is not merely attendance; the system captures defined outputs/outcomes and respects participants who exit early or choose different pathways.

---

# Journey 10 — Grant opportunity → award administration

## Flow
1. Human/agent discovers funding source.
2. Source is verified against official funder material.
3. Structured opportunity record is created.
4. Eligibility is checked:
   - entity;
   - geography;
   - population;
   - program;
   - award amount;
   - personnel/payroll eligibility;
   - indirect/admin;
   - match;
   - deadlines;
   - reporting;
   - restrictions.
5. Opportunity moves to pursue/decline review.
6. If pursued, task plan/LOI/proposal/budget records created.
7. Claims/metrics use approved source data.
8. Internal review occurs.
9. Authorized approver approves exact submission version.
10. Submission confirmation recorded.
11. If awarded, award/restrictions/reporting obligations created.
12. Personnel/program cost allocation follows award rules.
13. Reports use metric mappings and data-quality review.
14. Closeout/retention completed.

## Agent role
Strong fit for research, drafting, completeness checks, calendar/task creation, comparison to guidelines, and report preparation. No fabricated award history, deadlines, eligibility, or outcome data; no autonomous certification/submission by default.

---

# Journey 11 — Commercial client

## Flow
1. Lead sees commercial offer and terms.
2. Consultation/service scope is explained.
3. Required disclosures/contracts/fee timing follow approved legal model.
4. Client enters for-profit engagement.
5. Education/credit/business services are delivered according to commercial service catalog.
6. Client data remains for-profit scoped.
7. If person is also nonprofit participant, each relationship remains independently governed.
8. No nonprofit grant-funded activity is automatically applied to commercial engagement.

## Success
Commercial revenue supports a lawful sustainable business without using nonprofit participants, funds, or data improperly.

---

# Journey 12 — Agent-assisted operational task

## Flow
1. Human/system creates IACER-defined task.
2. System resolves entity, agent profile, tools, data classes, approval requirements.
3. Agent receives minimized context.
4. Agent performs allowed reads/analysis/drafts.
5. Agent requests approval if next step is consequential.
6. Exact action/version is presented to human approver.
7. If approved, approved executor performs action.
8. Result/confirmation recorded.
9. Audit event links trigger, agent run, approval, action, and result.
10. Runtime memory may retain only permitted procedural context; canonical result is saved to application domain.

## Failure path
If permission, legal status, destination, or data scope is ambiguous, agent stops the affected action and records/raises the blocker rather than guessing.

---

# Journey-level product requirements
Across all journeys:
- show users plain-language next steps;
- preserve active entity context;
- minimize data requests;
- support pause/resume where reasonable;
- record state transitions;
- distinguish staff-facing notes from participant-facing content;
- make errors recoverable;
- do not expose sensitive context in notification previews;
- provide accessible forms/content;
- show source/freshness for external opportunity information;
- create audit events for consequential actions;
- support human override with reason where policy permits, never silent bypass.

# Status
`DECIDED`: journeys above define planning baseline; individual screen flows remain future product design.

`RESEARCH NEEDED`: pilot program exact eligibility/service sequence, final credit workflow after counsel review, first communication channels, follow-up measurement schedule.
