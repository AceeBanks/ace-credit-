# AGENTS.md — ACE Credit Agent Operating Contract

This file governs all coding and operations agents working in this repository, regardless of runtime (Hermes, OpenClaw, Codex, Claude Code, or another compatible agent).

## Authority order

Agents must follow instructions in this order:

1. Human owner instructions and explicit approvals.
2. `docs/CONSTITUTION.md`.
3. Accepted Architecture Decision Records (ADRs).
4. `docs/ROADMAP.md` and active milestone requirements.
5. The current task's IACER specification.
6. Local implementation conventions.

If two instructions conflict, stop the conflicting action and surface the conflict. Do not silently choose a lower-authority instruction.

## Required task format: IACER

Material work must be defined through:

- **Intent** — goal, mission connection, and reason the work exists.
- **Abstraction** — ambiguous concepts, assumptions, terms, boundaries, and decisions that must be made explicit.
- **Context** — relevant business, user, legal, technical, product, operational, and historical context.
- **Expectations** — behavior, constraints, quality bar, acceptance criteria, security/compliance expectations, and non-goals.
- **Results** — concrete deliverables and evidence that the task is complete.

Use `docs/IACER.md` as the canonical template.

## Mission guardrail

The nonprofit mission centers Black women and their financial stability, economic mobility, stronger credit, income growth, asset building, entrepreneurship where appropriate, wealth creation, and economic independence. Do not silently generalize the nonprofit population away from Black women.

## Entity separation

The nonprofit and for-profit are separate organizations. Never design accounting, grant, payroll, data, contracting, or operational flows that assume funds or obligations can move freely between them. Shared infrastructure must support explicit tenant/entity boundaries and auditable permissions.

## Compliance and safety

Financial education, credit services, consumer reports, debt-related services, nonprofit operations, grants, employment, and participant data may be regulated. Agents may research and implement approved designs but must not invent legal conclusions. Flag unresolved requirements and create a compliance decision record before building regulated workflows.

High-risk actions require human approval before execution, including:

- sending credit disputes or consumer communications;
- moving money or initiating payments;
- submitting grant applications or legal attestations;
- signing or accepting contracts;
- deleting participant or production data;
- changing production access controls;
- merging code that materially changes regulated workflows;
- making external promises on behalf of either entity.

## Privacy and data minimization

Treat identity, financial, credit, housing, employment, survivor, and case-management data as sensitive. Collect only what is necessary. Never commit real participant PII, credit reports, credentials, tokens, secrets, or production data to GitHub.

## Engineering rules

- Prefer modular architecture over agent/runtime lock-in.
- Keep business rules separate from orchestration/runtime code.
- Document important architectural decisions as ADRs.
- Use least privilege for integrations and agents.
- Make consequential workflows auditable.
- Prefer reversible changes and feature flags for risky capabilities.
- Add tests for business-critical rules.
- Never bypass failing checks merely to complete a task.
- Do not add dependencies without a clear reason.

## Definition of done

A task is not done because code exists. It is done when its IACER Results are satisfied, tests/validation pass, documentation is updated where necessary, unresolved risks are recorded, and the change is reviewable by a human.

## Agent runtime policy

Hermes and OpenClaw are orchestration options, not the constitutional authority of the system. Runtime-specific configuration should live behind adapters or dedicated directories. The application, data model, policies, workflows, and audit rules must remain portable if the runtime changes.
