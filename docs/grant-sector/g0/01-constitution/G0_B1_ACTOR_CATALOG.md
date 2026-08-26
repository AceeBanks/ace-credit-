# G0 Book 1 — Actor Catalog

**Chapter:** B1.C3 · **Machine-readable source:** `config/g0/policy/actor_catalog.yaml` · **Validator:** `tools/g0/validate_policy_package.py`

14 actor types. People, agents, services and stores are never conflated.

| Actor | Purpose | Ceiling | May create workers | Credentials | Audit | Status |
|---|---|---|---|---|---|---|
| ACTOR-HUMAN-CLIENT | Business concept/profile; reviews; authorizes consequential actions | HUMAN_SOVEREIGN (tenant) | no | no | A4 | ACTIVE |
| ACTOR-HUMAN-ADMIN | Platform/policy/security ops via audited paths | HUMAN_SOVEREIGN (platform) | no | no | A4 | ACTIVE |
| ACTOR-HERMES-PERSONAL | Relationship intelligence; intent formation; explanation | L1 | no | no | A1 | ACTIVE |
| ACTOR-HERMES-CEO | Planning; decomposition; delegation; synthesis | L2 | yes | no | A2 | ACTIVE |
| ACTOR-WORKER | Bounded specialist work inside one TaskContract | L2 task-scoped | no | no | A2 | ACTIVE |
| ACTOR-DETERMINISTIC-SERVICE | Eligibility/budget/schema/policy/deadline determinism | L3 narrow | no | no | A2 | ACTIVE |
| ACTOR-SOURCE-ADAPTER | Fetch/normalize registered sources | L2 source-ops only | no | runtime-only | A1 | ACTIVE |
| ACTOR-POLICY-ENGINE | Evaluates permissions/approvals/scope | L3 | no | no | A2 | ACTIVE |
| ACTOR-CANONICAL-DATABASE | System-of-record substrate | L3 | no | own DB only | A2 | ACTIVE |
| ACTOR-ARTIFACT-STORE | Immutable versioned artifacts | L2 | no | own storage only | A2 | ACTIVE |
| ACTOR-EXTERNAL-INTEGRATION | Email/CRM/portals effectors | DISABLED in Phase 1 | no | runtime-only | A3 | DISABLED |
| ACTOR-OUTREACH-AGENT | Future outbound work | future L4 | no | no | A3 | FUTURE |
| ACTOR-SUBMISSION-AGENT | Future legal submission execution | future L5 | no | decided at ratification | A4 | DISABLED |
| ACTOR-TRACKER-AGENT | Future award/rejection tracking | future L2 | no | no | A1 | FUTURE |

## Key boundaries

- **Workers inherit nothing by default** — `allowed_capability_families: []`; every grant arrives through a TaskContract capability list, re-checked by the policy evaluator (LAW-B1-010).
- **No conversational actor holds credentials** — enforced by validator (LAW-B1-014).
- **Worker creation is CEO-only** (LAW-B1-009).
- **ACTOR-EXTERNAL-INTEGRATION is DISABLED**: it may technically reach external endpoints, but tool access ≠ authority (LAW-B1-003). This is the structural answer to "could a generic HTTP client become submission?"
