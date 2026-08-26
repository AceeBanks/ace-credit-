# G0-B6 — Handoff to Book 7

| Field | Value |
|---|---|
| Status | INTERNAL REALITY LOCK PASS (external ratification separate) |
| Branch | `grant-sector-r0-salvage` |
| Lock | `G0_B6_REALITY_LOCK.json` — status PASS, `ready_for_book7: true`, `p0_open: 0` |
| Full suite | `python -m pytest tests/g0 -q` → **1388 passed, 3 skipped** |
| Book 6 suite | 202 exclusive (199 passed + 3 skipped under freshness guard) |
| Adversarial P0 suite | 50 scenarios + 31 integration/perf = **81 passed** |

## What Book 7 receives (plan C30 list)

- Stable principals / actor identities
- Capability-grant semantics
- Authorization reason codes (deny-by-default)
- Tenant / resource scope model
- Data classifications + PII controls
- Tool registry / version metadata
- Security audit events (integrity hash chain)
- Prompt-injection / security fixtures
- Approval / token model (durable, hash-bound)
- Model/provider security constraints
- Eval privacy restrictions

## Book 7 must then answer

> How are candidate prompts, skills, models, workflows, source adapters and
> security changes **measured** and **promoted** without violating any of
> these boundaries?

Book 7 must respect that every security control closed in Book 6 is a
constraint, not an obstacle: promotion happens within the capability-grant
lattice, through the tool gateway, with bounded evidence and never over
canonical state.

## Hard invariants preserved

- Authentication never implies authorization.
- Unknown/missing tenant defaults deny.
- Workers never inherit broad parent authority.
- Credentials stay server-side and scoped; never in agent context.
- Tool availability does not imply permission (gateway enforces decision).
- External side effects require a separate capability; submission stays
  structurally disabled.
- Egress destination validated independently of model output.
- Prompt injection cannot create authority.
- Tenant isolation applies to DB, graph, vector, artifacts and audit.
- Approval tokens are resource/version bound.
- Security-control outage fails closed.
- L5 submission remains disabled regardless of approval or feature flag.

## External components cleared for Book 7

- **Semantica** (from Book 5 bake-off): **ADOPT_OPTIONAL_ACCELERATOR,
  deferred** — graph/vector remain projections, never canonical truth.
- **blader/humanizer**: reserved as a **BOUNDED STYLE_TRANSFORM
  CANDIDATE** for the Book 7/8 quality pipeline; a ratified amendment is
  required before integration, and it must never change canonical
  facts/evidence.

## Key contracts now executable

| Area | Artifact |
|---|---|
| Security constitution (20 laws) | `config/g0/security/security_constitution.yaml` |
| Principals / tenant isolation | `prototype/g0/security/identity.py` |
| Capability grants / authorization | `prototype/g0/security/authorization.py` |
| Authn / sessions / credentials | `prototype/g0/security/authn.py` |
| Tool gateway / MCP facade | `prototype/g0/security/tool_gateway.py` |
| Egress / classification / PII | `prototype/g0/security/boundaries.py` |
| Injection / file / approval / audit | `prototype/g0/security/hostile_content.py`, `approvals_audit.py` |
| Lifecycle / break-glass / revocation / obs | `prototype/g0/security/lifecycle.py` |
| Threat model / attack register | `config/g0/security/threat_model.yaml`, `attack_surface.yaml` |