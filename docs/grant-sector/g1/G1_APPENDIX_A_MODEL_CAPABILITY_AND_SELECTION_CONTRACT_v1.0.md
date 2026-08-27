# G1 Appendix A — Model Capability & Selection Contract

**Version:** 1.0
**Status:** FROZEN (G1 implementation contract)
**Supersedes:** nothing — extends Book 7 model runtime + Book 9 ADR
(`OCE_NATIVE`). It does NOT reopen Book 9 architecture.

## 1. Model provider principle

The Grant platform owns `ModelRequest`, `ModelResponse`, `ModelProfile`,
`ModelCapability`, `ModelSelectionPolicy`, and `ModelRun` provenance.
Providers are replaceable adapters behind the governed Model Gateway
(`prototype/g0/model/gateway.py`).

Primary aggregation path: **OpenRouter**. Direct providers (Anthropic,
OpenAI, Google, MiniMax, others) may be configured as additional adapters.
No provider becomes architectural truth.

## 2. Model profile contract

Every selectable model exposes machine-readable metadata (schema:
`schemas/g1/model/model_profile.schema.json`):

| Field | Type | Notes |
|---|---|---|
| `provider_id` / `provider_type` | string | adapter identity |
| `model_id` | string | exact provider model id |
| `display_name` | string | user-facing |
| `context_window_tokens` | int | total window |
| `max_output_tokens` | int | per-response cap |
| `supports_structured_output` | bool | JSON-mode/structured |
| `supports_tools` | bool | tool-calling |
| `supports_vision` | bool | image input |
| `input_cost` / `output_cost` | decimal (per 1M tokens) | USD, configurable |
| `availability` | enum | `ENABLED \| BETA \| DISABLED` |
| `quality_tier` / `latency_tier` / `cost_tier` | enum | evidence-derived labels, not marketing |
| `evaluation_status` | string | Book 7 eval ref or `NOT_EVALUATED` |
| `allowed_tasks` | list[str] | task capability ids |
| `full_proposal_eligible` | bool | long-form factory eligibility |
| `research_eligible` / `qa_eligible` | bool | |
| `humanizer_eligible` / `extraction_eligible` | bool | bounded lanes only |
| `minimum_context_headroom` | int | reserved safety tokens |
| `fallback_compatible` | list[str] | fallback model ids |
| `enabled` | bool | runtime switch |

## 3. Context eligibility (pre-invocation gate)

Before invocation compute:

```
required_context =
    estimated_input_tokens
  + expected_output_tokens
  + system/policy overhead
  + safety headroom (minimum_context_headroom)
```

A model is eligible only if:

```
context_window_tokens >= required_context
AND
max_output_tokens >= expected_output_tokens
```

For long-form proposal drafting, the safety target is:

```
available context >= 2 × estimated working input requirement
```

The exact multiplier is `PROVISIONAL_G1_DEFAULT` until measured production
evidence calibrates it (recorded in the model selection policy config).

A structurally incapable model is never offered to the user — eligibility
is enforced backend-side, not merely hinted in the UI.

## 4. Large context ≠ unbounded architecture

A 1M-token context window is headroom, not permission to collapse the
bounded architecture. The system retains:

- `ApplicationBlueprint` (sectioned);
- bounded section workers with `ContextBundle`;
- per-section QA;
- CEO synthesis;
- cross-section consistency pass;
- global factuality/claim-ledger QA.

Never dump all client history, all source documents, all worker traces, or
all memory into one prompt.

## 5. Model selection UX

- Default: **AUTO — RECOMMENDED**.
- Advanced users may optionally choose `provider` + `model`.
- Backend retains final eligibility authority.
- Incompatible selection → (A) reject with a clear message, or (B) use a
  governed fallback if the user enabled fallback.
- The ACTUAL provider/model used is recorded on `ModelRun`,
  `ArtifactVersion`, `DecisionRecord`, and the audit trail — never assumed.

## 6. Auto-routing rules

Auto may consider: task type, quality evidence, context requirement,
structured-output requirement, cost, latency, provider availability,
tenant policy.

Auto MUST NOT: choose unapproved models; bypass Book 6 capability policy;
use provider keys outside the server-side credential flow; route on
marketing labels.

## 7. Model UI requirements

Basic view: `Model [ Auto — Recommended ]`.

Advanced view: provider, model, task eligibility, context window, cost
tier, quality/eval status, fallback toggle.

Normal clients do not need to understand model infrastructure.

## 8. Contract enforcement

- Profiles live in config (`config/g1/model/`) and are validated against
  the schema in CI.
- Selection logic (`platform/model/selection.py`) is unit-tested: context
  gate, task-eligibility gate, fallback, Auto routing.
- Gateway integration re-uses Book 7 PDP/egress/credential rules unchanged.

## Commit: `G1-APPENDIX-A`
