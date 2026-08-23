# ACE Credit Repository Structure

## Intent
Keep governance, application code, imported runtimes, infrastructure, tests, and operational knowledge understandable to both humans and coding agents. The repository must evolve without making the existing Hermes WebUI subtree the architectural center of ACE Credit.

## Current state
The root repository currently contains ACE Credit bootstrap files plus an imported `hermes-webui/` codebase. That subtree has its own architecture, tests, workflows, contribution instructions, and runtime concerns. It should be treated as a runtime/operator component rather than the location where ACE Credit business logic is built.

## Target top-level structure

```text
/
├─ README.md
├─ AGENTS.md
├─ HERMES_SETUP.md
├─ docs/
│  ├─ CONSTITUTION.md
│  ├─ IACER.md
│  ├─ ROADMAP.md
│  ├─ END_STATE.md
│  ├─ DELIVERABLES.md
│  ├─ PHASE1_IACER.md
│  ├─ architecture/
│  ├─ compliance/
│  ├─ security/
│  ├─ product/
│  ├─ impact/
│  └─ operations/
├─ .github/
│  ├─ ISSUE_TEMPLATE/
│  ├─ pull_request_template.md
│  └─ workflows/                 # ACE Credit CI only
├─ apps/                         # future first-party user-facing apps
│  ├─ staff-console/
│  ├─ participant-portal/
│  └─ public-site/               # only if maintained in this repo
├─ services/                     # future first-party backend/application services
│  ├─ api/
│  ├─ worker/
│  └─ integrations/
├─ packages/                     # future shared first-party modules
│  ├─ domain/
│  ├─ authz/
│  ├─ policy/
│  ├─ audit/
│  ├─ schemas/
│  └─ agent-adapters/
├─ infra/                        # deployment/IaC when selected
│  ├─ environments/
│  ├─ modules/
│  └─ policies/
├─ tests/                        # ACE Credit cross-system/contract tests
│  ├─ fixtures/
│  ├─ security/
│  ├─ tenancy/
│  └─ integration/
├─ scripts/                      # safe ACE Credit developer/admin scripts
├─ agent-runtimes/               # runtime-specific ACE config, not authoritative data
│  ├─ hermes/
│  └─ openclaw/
└─ hermes-webui/                 # imported Hermes WebUI runtime/operator component
```

This is a target organization, not permission to create empty directories or choose frameworks prematurely.

## Ownership boundaries

### Root governance
Root `AGENTS.md` and `docs/` govern ACE Credit mission, product, security, compliance, domain, and architecture.

### `hermes-webui/`
Treat as an imported/vendor-like runtime subtree. Changes inside it must follow its nested `AGENTS.md`, tests, and upstream architecture in addition to ACE Credit security/mission rules. Avoid placing ACE-specific domain logic directly inside Hermes WebUI files.

### `apps/`
First-party presentation layers. Apps should call application APIs/capabilities rather than duplicate policy/business rules.

### `services/`
Deployable first-party services. Start with the fewest services needed. A modular monolith is acceptable and likely preferable before scale proves service separation is necessary.

### `packages/domain/`
Pure or mostly pure domain concepts, validation, state transitions, and types where the selected implementation language allows. Must not depend on Hermes/OpenClaw.

### `packages/authz/` and `packages/policy/`
Entity/role/context authorization, approval gates, data-class restrictions, and policy evaluation.

### `packages/audit/`
Audit-event contracts and helpers. Audit storage implementation may live in a service.

### `packages/agent-adapters/`
Runtime-neutral agent capability contract and runtime adapters. No participant business rules may exist only in a runtime adapter.

### `infra/`
Infrastructure as code, deployment definitions, environment policies, backup configuration. No secrets.

### `agent-runtimes/`
Tracked runtime configuration/templates needed to operate ACE agents safely. Actual secrets, runtime databases, personal memory, caches, sessions, and production data stay outside GitHub.

## Branching
Default branch: `main`.

Recommended branch naming:
- `foundation/...`
- `phaseN/...`
- `feature/...`
- `fix/...`
- `security/...`
- `docs/...`
- `runtime/hermes-...`
- `runtime/openclaw-...`

Material changes should flow through PRs.

## PR scope
Prefer one coherent IACER outcome per PR. Large phase packages may contain multiple documents when they jointly establish one architecture gate.

## Architecture Decision Records
Location: `docs/architecture/ADR-NNNN-short-name.md`.

Every ADR should contain:
- status;
- date;
- context;
- decision;
- alternatives;
- consequences;
- security/compliance effects;
- revisit triggers.

Statuses:
- Proposed
- Accepted
- Superseded
- Deprecated
- Rejected

## Generated vs. canonical files
If runtime-specific instruction files are generated from canonical governance, mark them as generated and document source/refresh process. Do not hand-edit generated copies in ways that create policy drift.

## Data fixtures
Development fixtures must be synthetic. Use obvious fake identities and generated account/credit examples. No anonymized production export should be assumed safe without a formal de-identification review.

Suggested structure:
```text
tests/fixtures/
├─ people.synthetic.json
├─ programs.synthetic.json
├─ credit.synthetic.json
├─ grants.synthetic.json
└─ README.md
```

## Configuration
- `.env.example` may document variable names only.
- environment-specific secrets live outside Git.
- production configuration is managed through a secrets/config service chosen later.
- runtime configs should reference secret names, never embed tokens.

## Dependency policy
Before adding a dependency, record:
- purpose;
- maintained status;
- license compatibility;
- security implications;
- data it receives;
- whether a standard-library/existing dependency can satisfy the need;
- exit/replace strategy for critical vendors.

## Imported/open-source components
For `hermes-webui/` and any future imported code:
- preserve upstream license notices;
- document upstream repository/version/commit where practical;
- avoid mixing ACE secrets/data into upstream test fixtures;
- isolate ACE customizations;
- periodically evaluate how upstream changes are incorporated;
- do not assume upstream security defaults are sufficient for ACE production data.

## CI separation
Root ACE workflows should not unintentionally duplicate or break nested Hermes workflows. CI should eventually have explicit scopes:
- governance/docs validation;
- first-party app/service tests;
- security/secret scanning;
- tenancy/authz tests;
- runtime component tests when touched.

## Definition of a first-party application foundation
Before creating `apps/` or `services/` implementation code, accept ADRs for:
1. primary implementation language/framework;
2. database/storage;
3. authentication/identity;
4. authorization/tenancy implementation;
5. hosting/deployment;
6. API contract approach;
7. background workflow strategy;
8. observability/audit storage.

Those decisions should follow MVP/domain requirements, not precede them.

## Status
`DECIDED`: first-party ACE logic will live outside `hermes-webui/`; runtime configs remain separate from authoritative business state.

`WORKING ASSUMPTION`: monorepo with a modular first-party application is preferred until complexity justifies multiple repos/services.
