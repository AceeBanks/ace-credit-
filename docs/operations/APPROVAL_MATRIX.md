# ACE Credit Human Approval Matrix

## Purpose
Define which actions agents, staff, supervisors, and authorized organizational leaders may perform without ambiguity. Approval is tied to the exact action/version and does not mean a person has blanket authority over the entire domain.

## Approval levels

### A0 — No special approval
Routine low-risk action within assigned role.

### A1 — Staff confirmation
A trained staff member reviews and confirms the proposed action before it changes an operational record.

### A2 — Supervisor/program owner approval
A designated program/functional leader approves a consequential internal action.

### A3 — Authorized organizational approval
Executive officer, board-authorized person, or other formally designated authority approves an external commitment, submission, financial action, or sensitive policy action.

### A4 — Professional/legal/compliance clearance + organizational approval
Requires documented qualified review before the organizational approver may authorize execution.

---

# Action matrix

| Action | Minimum level | Agent may prepare? | Agent may execute? | Audit required? |
|---|---:|---|---|---|
| Read public grant information | A0 | Yes | Yes, read-only | Research provenance |
| Create/update internal grant research record | A0/A1 depending sensitivity | Yes | Yes within scoped workflow | Yes |
| Recommend pursue/decline grant | A1 | Yes | No final decision unless explicitly delegated | Yes |
| Draft LOI/proposal | A1 | Yes | Draft only | Version history |
| Submit grant application | A3 | Yes | Only after exact submission approval; default human execution | Yes |
| Sign/certify grant terms | A3/A4 as appropriate | Prepare | No autonomous signature | Yes |
| Record participant attendance | A0/A1 | Yes | Yes if validated | Yes |
| Create routine participant task | A0/A1 | Yes | Yes if within service plan | Yes |
| Edit ordinary coaching note | A0/A1 | Assist | Human/staff workflow; agent writes only if explicitly authorized | Yes |
| View survivor-sensitive information | A2 role policy | Only task-minimized if approved | Read only unless specifically granted | Yes, heightened |
| Change participant eligibility decision | A2 | Prepare analysis | No autonomous final decision | Yes |
| Enroll/exit participant | A1/A2 | Prepare | May execute only after approved decision/workflow | Yes |
| Publish participant-facing curriculum | A2 | Draft | No without content approval | Yes/versioned |
| Change legal/compliance content | A4 | Draft/research | No | Yes |
| Review participant-provided credit information | A1 trained credit role | Assist after legal/security approval | Limited | Yes |
| Mark item as possible dispute candidate | A1 | Suggest | Staff confirms | Yes |
| Determine a dispute should be sent | A2/A4 depending legal workflow | Prepare | No | Yes |
| Send external credit dispute/communication | A4 until later policy | Prepare | No autonomous execution in early phases | Yes, exact version |
| Pull consumer report from provider | A4 until provider/compliance architecture approved | No by default | No | Yes |
| Send routine non-sensitive program reminder | A0/A1 | Yes | Yes after messaging/consent policy approved | Delivery log |
| Send marketing SMS/email | A2/A4 depending legal review | Draft | Only approved automation | Yes/consent |
| Refer participant to approved resource | A0/A1 | Yes | Yes with minimum data sharing | Yes |
| Share participant data with external partner | A2/A4 depending sensitivity/agreement | Prepare | Only approved data-sharing flow | Yes |
| Export participant-level data | A2 | Prepare | Staff only by default | Yes |
| Generate aggregated impact report draft | A1 | Yes | Yes, draft | Data provenance |
| Publish impact claim/report | A3 | Draft | No until review | Yes |
| Edit metric definition | A2 | Draft | No autonomous final change | Version/audit |
| Create staff user | A2/A3 | No default | Human/admin | Yes |
| Grant privileged role | A3 | No | Human/admin | Yes |
| Agent changes own permissions | Prohibited | No | No | Denied attempt logged |
| Rotate/revoke agent credential | A2/A3 | Assist | Admin workflow | Yes |
| Deploy ordinary tested code to development | A0/A1 | Yes | May be automated | CI record |
| Deploy to production | A2/A3 depending maturity | Yes | Only approved deployment policy | Yes |
| Change production auth/tenancy policy | A3/A4 | Draft/test | No autonomous change | Yes |
| Delete synthetic dev data | A0 | Yes | Yes | Optional |
| Delete protected production record | A3/A4 based on policy/legal hold | Prepare | No autonomous deletion | Yes |
| Restore production backup | A3 | No default | Authorized operator | Yes |
| Move money/initiate payment | A3/A4 | Prepare | No autonomous money movement | Yes |
| Set/approve nonprofit executive compensation | Board/governance process | Research/comparables | No | Governance record |
| Approve related-party contract | A3/A4 + conflict process | Prepare | No | Yes |
| Execute contract | A3 | Prepare | No autonomous signature | Yes |
| Change constitutional mission/population | Owner/governance only | Analyze | No | ADR/governance record |

---

# Approval object requirements
An approval record should eventually contain:
- `approval_id`;
- entity;
- action type;
- target record/object;
- exact version/hash where content is approved;
- requester;
- required approval level;
- approver identity/role;
- requested time;
- approved/rejected time;
- expiration if applicable;
- decision/rationale when required;
- policy/compliance basis;
- execution status and correlation ID.

## Version binding
For documents/communications, approval is invalid if material content changes after approval. The system should either hash/version the approved artifact or otherwise prove what was approved.

## Separation of duties
Where risk justifies, the system should support different people for:
- preparation vs. approval;
- payment setup vs. payment approval;
- grant preparation vs. certification;
- credit-action preparation vs. approval;
- privileged access request vs. grant;
- related-party proposer vs. conflict-free approval.

## Emergency controls
Production should eventually support:
- disable all agent writes;
- disable one agent/runtime;
- revoke credentials;
- disable one integration;
- pause scheduled jobs;
- temporarily freeze exports;
- invalidate sessions;
- place record/legal hold.

Emergency action itself is audited and reviewed after the incident.

## Approval UX principle
Do not bury high-risk approval in a generic “Confirm” dialog. Show:
- what will happen;
- target/destination;
- entity;
- affected person/record where appropriate;
- exact document/action version;
- data being shared;
- irreversible consequences;
- compliance warnings where applicable.

# Status
`DECIDED`: consequential actions use explicit approval records and agents cannot approve themselves.

`WORKING ASSUMPTION`: approval levels A0–A4 will map to role/policy rules in the future authorization service.

`RESEARCH NEEDED`: named organizational approvers, board delegation structure, legal/compliance approval requirements for exact service catalog.
