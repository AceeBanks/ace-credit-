# G0 Model Runtime — Governed Model Gateway

G0-B7-PHASE-B · smallest Book-6-compliant model runtime boundary.

## Why this exists

The governed G0 pipeline previously had **no authorized model runtime**: the
only credential in the environment (`OPENROUTER_API_KEY`) was consumed by
workspace tooling, not by any G0 adapter, so live D2 honestly reported
`BLOCKED_MODEL_RUNTIME`. This component adds the governed boundary so an
actual model can write grounded Grant drafts without violating Book 6
credential/egress/authorization rules.

## Architecture

```
Hermes / Worker / Evaluation Harness
        ↓
   ModelRequest (typed, no secrets)
        ↓
  Governed Model Gateway
        ↓
 Provider Profile Registry (frozen, project-owned)
        ↓
 Credential Resolution (vault ref or DEV_RUNTIME_ONLY env resolver)
        ↓
      Provider Adapter (bounded; OpenRouter adapter)
        ↓
   ModelResponse (typed, attributable, redacted)
        ↓
 usage / cost / latency / audit (credential REF id only)
```

Project-owned contracts stay sovereign: ModelRequest, ModelResponse,
ProviderProfile, audit records. Providers are subordinate adapters; no
provider code exists in the D2 harness or evaluation modules.

## Contracts

- `schemas/g0/model/model_request.schema.json` — typed request. No secret
  fields, ever.
- `schemas/g0/model/model_response.schema.json` — typed response with
  provider/model/version/tokens/latency/cost and audit ref.
- `prototype/g0/model/gateway.py` — `ModelGateway`, `ProviderProfileRegistry`,
  `DevRuntimeCredentialResolver`.
- `prototype/g0/model/adapters.py` — `OpenRouterAdapter` (bounded) and
  `FakeAdapter` (tests).
- `config/g0/model/model_gateway_policy.yaml` — provider profiles + rules
  MR-001..MR-008.

## Security properties (MR-001..MR-008)

| Rule | Enforced by |
|---|---|
| MR-001 | Gateway verifies the PDP AuthorizationDecision (DecisionRegistry), capability binding, freshness; no execution without ALLOW |
| MR-002 | Unknown provider profile / unknown model => DENY; frozen base_url |
| MR-003 | Egress + SSRF: blocked destinations, exact frozen origin, redirect revalidation |
| MR-004 | Credentials server-side only; caller keys rejected; response/audit redacted |
| MR-005 | One-shot replay guard on model_request_id/request_id |
| MR-006 | Structured audit with credential REF id, never value |
| MR-007 | Purpose + principal-type gates (Personal Hermes cannot use CEO-only profiles) |
| MR-008 | Submission stays phase-disabled; model execution is `model.invoke`, never a submission path |

## Capability

`model.invoke` is a registered, **delegable** capability (added to
`config/g0/security/capability_grant_policy.yaml`) so workers can receive
project-bound drafting grants; the grant authority ladder (AUTH-R1) and
project scope (AUTH-R3) apply unchanged.

## DEV_RUNTIME_ONLY

`DevRuntimeCredentialResolver` reads the provider key from the process
environment **inside the trusted adapter call**, returns it only to the
adapter, and the gateway redacts all serialized artifacts. It is explicitly
not production secret management — the Book 6 `CredentialVault` remains the
production path. Raw values never enter ModelRequest/ModelResponse, logs, or
audit.

## Tests

`tests/g0/book7/test_model_runtime.py` — attacks A..O (mission §13):

A authorized worker + approved model → allowed
B unknown provider → denied
C unknown model → denied
D Personal uses CEO-only profile → denied
E worker outside project → denied
F cross-tenant request → denied
G caller includes API key → rejected
H provider secret absent → fail closed
I secret never appears in logs/response
J arbitrary base URL → denied (PDP + gateway layers)
K metadata/localhost redirect → denied
L model disabled → denied
M request replay → denied
N structured-output + unsupported model → denied
O submission capability remains disabled

Red-green tests prove the defenses are real (flip the defense → test
fails).
