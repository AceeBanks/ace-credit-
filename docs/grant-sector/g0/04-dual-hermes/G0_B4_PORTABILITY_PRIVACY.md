# G0 Book 4 — Skill Boundaries, Model Independence & Privacy Scope

**Document ID:** GS-G0-B4-C23-C25-PORT-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C23-C25
**Configs:** `skill_boundaries.yaml`, `model_independence.yaml`, `privacy_scope.yaml`
**Prototype:** `prototype/g0/agents/portability.py`
**Validator:** `tools/g0/validate_portability.py`

---

## 1. C23 — Role-specific prompt/skill boundary

Prevents role drift through shared mega-prompts:

- **Personal Hermes skill domains:** intake, clarification, brainstorming,
  client explanation, memory candidate classification, feedback capture.
- **CEO Hermes skill domains:** operational planning, task decomposition,
  result synthesis, failure/retry decisions, application workflow control,
  improvement proposal generation.
- **Shared:** low-level utilities and typed contract helpers only — role
  prompts, personality and memory policies are independent.
- **Progressive disclosure:** skill metadata loads broadly; full skill
  instructions load only when triggered.

## 2. C24 — Multi-model / provider independence

Dual Hermes is a **logical architecture**, not tied to one model/provider.

- `AgentIdentity` (PERSONAL/CEO/WORKER identities) is separate from
  `ModelExecution` (provider, version, runtime session).
- MODEL-001: provider swap never merges or changes memory namespaces.
- MODEL-002: a fallback must satisfy the required structured-output/tool
  capability, otherwise controlled degradation — never silent authority
  expansion.
- MODEL-003: model execution metadata lives in sidechain/audit, never in
  agent identity.

## 3. C25 — Privacy, memory scope & deletion

Every memory record resolves to scope: user, tenant, organization,
project/application, agent role, privacy class.

Deletion semantics: exclude from future retrieval · supersede/correct ·
remove user-specific memory subject to retention/audit · preserve required
canonical/audit evidence separately.

**Role duplication rule:** deleted Personal memory must not remain
retrievable merely because CEO cached a copy — duplication is minimized by
refs.

## 4. Verified behaviors

- `test_personal_session_does_not_load_ceo_skill_set`
- `test_provider_swap_preserves_identity_and_state`
- `test_fallback_lacking_capability_degrades_controlled`
- `test_deleted_personal_memory_not_retrievable_via_ceo_cache`
- `test_delete_scope_mismatch_rejected`
