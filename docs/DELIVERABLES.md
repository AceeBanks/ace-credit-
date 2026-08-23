# Foundation Deliverables

This document defines what must exist before ACE Credit moves from planning into sustained application development.

## Governance deliverables

1. `README.md` — project orientation and current phase.
2. `AGENTS.md` — runtime-neutral operating contract for coding and operations agents.
3. `docs/CONSTITUTION.md` — non-negotiable mission, entity, data, human-authority, and compliance rules.
4. `docs/IACER.md` — canonical task specification format.
5. `docs/ROADMAP.md` — phased dependency roadmap.
6. `docs/END_STATE.md` — definition of the intended mature system.
7. `docs/DELIVERABLES.md` — foundation completion criteria.

## Next foundation deliverables

The following should be created immediately after this initial governance package is approved:

- `docs/architecture/DOMAIN_MAP.md`
- `docs/architecture/SYSTEM_CONTEXT.md`
- `docs/architecture/ADR-0001-agent-runtime-boundary.md`
- `docs/architecture/ADR-0002-entity-tenancy-boundary.md`
- `docs/security/DATA_CLASSIFICATION.md`
- `docs/security/THREAT_MODEL.md`
- `docs/compliance/COMPLIANCE_REGISTER.md`
- `docs/compliance/CREDIT_SERVICES_MATRIX.md`
- `docs/product/ACTORS_AND_ROLES.md`
- `docs/product/USER_JOURNEYS.md`
- `docs/product/MVP_SCOPE.md`
- `docs/impact/OUTCOME_MODEL.md`
- `.github/ISSUE_TEMPLATE/iacer-task.md`
- `.github/pull_request_template.md`

## Technical foundation deliverables

No framework is constitutionally required yet. Technical choices should follow domain, security, deployment, maintenance, and agent-operability requirements.

Before feature development, the repository should have:

- application/workspace structure;
- local development instructions;
- environment-variable schema with no committed secrets;
- formatting/linting;
- automated tests;
- CI checks;
- dependency and security scanning where practical;
- database migration strategy;
- seeded synthetic development data;
- structured logging;
- audit-event model;
- authentication/authorization architecture;
- backup/recovery plan before production data;
- deployment environments separated at least into development and production.

## Agent operations deliverables

The system should support an agent runtime without making that runtime the source of truth.

Required concepts:

- runtime adapter boundary;
- explicit tool allowlists;
- environment-specific permissions;
- read-only vs. write-capable agent roles;
- approval-gated consequential actions;
- task logs/auditability;
- secret isolation;
- failure/retry behavior;
- kill switch or rapid credential revocation procedure.

Hermes/OpenClaw-specific files may be added after the runtime experiment ADR is accepted.

## Product foundation deliverables

Before MVP coding is considered scoped, define:

- primary users and staff users;
- nonprofit vs. for-profit workflows;
- pilot population and program boundaries;
- participant onboarding lifecycle;
- program enrollment lifecycle;
- case/coaching lifecycle;
- financial education lifecycle;
- outcome measurement lifecycle;
- referral lifecycle;
- credit module boundaries;
- data collection minimums;
- human approval points.

## Foundation completion standard

Phase 0/1 foundation is considered complete when:

- mission and entity rules are explicit;
- ambiguous product concepts have IACER definitions;
- major actors and workflows are mapped;
- sensitive data is classified;
- consequential actions have approval gates;
- initial compliance unknowns have owners/status;
- MVP scope has clear non-goals;
- architecture choices are recorded as decisions rather than assumptions;
- coding agents can select a task and know exactly what “done” means.
