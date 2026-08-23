# IACER Specification Standard

IACER is the required planning structure for material work in ACE Credit. It exists to remove ambiguity before agents act.

## I — Intent

State the goal, mission connection, user/business value, and reason the work exists.

Questions to answer:
- What problem are we solving?
- For whom?
- Why now?
- What mission or operating objective does this advance?
- What is explicitly out of scope?

## A — Abstraction

Turn vague concepts into explicit definitions, assumptions, boundaries, and decision points.

Clarify:
- undefined terms;
- subjective words such as “secure,” “simple,” “fast,” or “complete”;
- actor roles and permissions;
- what the agent may decide vs. what requires human approval;
- legal/compliance uncertainty;
- data classifications;
- state transitions;
- business rules;
- dependencies and failure modes.

Nothing material should be left for an agent to infer when it can be specified.

## C — Context

Provide the facts necessary to make the work coherent with the rest of the system.

Include as relevant:
- mission and population;
- nonprofit vs. for-profit entity;
- target users and staff roles;
- current architecture/code;
- prior decisions/ADRs;
- operational workflow;
- compliance considerations;
- grant or partner requirements;
- data sources;
- integrations;
- constraints, dependencies, and known risks.

Do not overload Context with unrelated history.

## E — Expectations

Define the required behavior and quality bar.

Include as relevant:
- functional requirements;
- non-functional requirements;
- privacy/security requirements;
- human approval gates;
- accessibility;
- testing expectations;
- observability/auditability;
- performance expectations;
- user experience expectations;
- prohibited behavior;
- acceptance criteria.

Expectations should be testable whenever possible.

## R — Results

List the concrete outputs that prove completion.

Examples:
- files created/updated;
- migrations/schema changes;
- APIs or workflows implemented;
- tests passing;
- documentation/ADR updated;
- screenshots or evidence;
- measurable acceptance checks;
- unresolved risks recorded;
- rollout/rollback instructions.

A Result is an artifact or verifiable condition, not “work on X.”

---

# IACER Task Template

## Intent
**Goal:**

**Mission/Business reason:**

**Users/beneficiaries:**

**Non-goals:**

## Abstraction
**Definitions:**

**Assumptions:**

**Business rules:**

**Decisions requiring human approval:**

**Unknowns/research needed:**

## Context
**Entity:** Nonprofit / For-profit / Shared infrastructure

**Relevant system context:**

**Data involved:**

**Integrations:**

**Compliance/security context:**

**Dependencies:**

## Expectations
**Functional requirements:**

**Security/privacy:**

**Audit/observability:**

**Testing:**

**Acceptance criteria:**

## Results
- [ ] Deliverable 1
- [ ] Deliverable 2
- [ ] Tests/validation complete
- [ ] Documentation updated
- [ ] Risks/unknowns recorded

## Status
Use one or more: `DECIDED`, `WORKING ASSUMPTION`, `RESEARCH NEEDED`, `OPEN QUESTION`, `FUTURE IDEA`.
