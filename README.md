# ACE Credit

ACE Credit is the working repository for a governed financial empowerment ecosystem centered on the financial stability, economic mobility, stronger credit, income growth, asset building, entrepreneurship where appropriate, wealth creation, and long-term economic independence of Black women.

The repository is intended to become the durable source of truth for nonprofit program strategy, separate for-profit operations, grant intelligence, financial education, credit recovery/building, workforce and business pathways, impact measurement, agent operations, application architecture, compliance research, and implementation code.

## Current phase

**Phase 1 — Domain, Compliance, Security & MVP Foundation**

The current goal is to remove the decisions a coding/operations agent should never be forced to invent: legal-entity boundaries, user roles, sensitive-data handling, regulated-service gates, human approvals, domain definitions, outcome definitions, and MVP/non-goals.

Start here:

1. [`AGENTS.md`](AGENTS.md) — operating contract for all ACE Credit coding/operations agents.
2. [`docs/CONSTITUTION.md`](docs/CONSTITUTION.md) — non-negotiable mission, entity, human-authority, compliance, and data principles.
3. [`docs/IACER.md`](docs/IACER.md) — required specification method: Intent, Abstraction, Context, Expectations, Results.
4. [`docs/PHASE1_IACER.md`](docs/PHASE1_IACER.md) — current detailed phase specification and exit gate.
5. [`docs/architecture/DOMAIN_MAP.md`](docs/architecture/DOMAIN_MAP.md) — bounded business domains/core objects.
6. [`docs/architecture/SYSTEM_CONTEXT.md`](docs/architecture/SYSTEM_CONTEXT.md) — actors, trust boundaries, systems, and data flows.
7. [`docs/product/MVP_SCOPE.md`](docs/product/MVP_SCOPE.md) — staff-first safe MVP and explicit non-goals.
8. [`docs/compliance/COMPLIANCE_REGISTER.md`](docs/compliance/COMPLIANCE_REGISTER.md) — legal/compliance research and production blockers.
9. [`docs/security/DATA_CLASSIFICATION.md`](docs/security/DATA_CLASSIFICATION.md) and [`docs/security/THREAT_MODEL.md`](docs/security/THREAT_MODEL.md) — privacy/security foundation.
10. [`docs/ROADMAP.md`](docs/ROADMAP.md) and [`docs/END_STATE.md`](docs/END_STATE.md) — dependency roadmap and mature-system definition.

## Agent/runtime architecture

Hermes Agent + Hermes WebUI are already present in this repository and may be used as an operations/runtime layer. OpenClaw remains a candidate runtime. Neither runtime is the permanent constitutional or business-data source of truth.

See:
- [`HERMES_SETUP.md`](HERMES_SETUP.md)
- [`docs/architecture/ADR-0001-agent-runtime-boundary.md`](docs/architecture/ADR-0001-agent-runtime-boundary.md)
- [`docs/architecture/RUNTIME_EVALUATION.md`](docs/architecture/RUNTIME_EVALUATION.md)

ACE-specific business logic should be built outside the imported `hermes-webui/` subtree. That subtree retains its own nested engineering instructions for changes to Hermes WebUI itself.

## Architecture principles

- nonprofit and for-profit are separate legal/operational entities;
- legal entity is a first-class data/security boundary;
- shared technology does not imply shared funds, contracts, staff time, participant/client data, or permissions;
- production business rules live in the application/policy layer, not agent memory;
- agents receive bounded capabilities and cannot approve themselves;
- consequential external actions remain human-gated;
- development uses synthetic data only;
- credit/debt workflows do not launch on unstated legal assumptions;
- outcomes require definitions and provenance;
- credit score alone is not the definition of financial stability.

## Phase 1 exit gate

Before sustained feature implementation, the repository must make it possible for a coding agent to determine, for any MVP workflow:

- who owns the data/workflow;
- which legal entity it belongs to;
- which actor can read/write/approve it;
- what data classification applies;
- what state transitions are valid;
- which audit event is required;
- whether legal/compliance review blocks the feature;
- whether the feature is MVP, later-stage, or prohibited for now;
- exactly what constitutes completion.

Do not begin high-risk credit/debt automation merely because the runtime makes it technically possible.
