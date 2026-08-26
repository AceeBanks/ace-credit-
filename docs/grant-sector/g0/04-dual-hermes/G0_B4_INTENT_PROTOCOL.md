# G0 Book 4 — Intent Protocol

**Document ID:** GS-G0-B4-C4-PROTOCOL-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C4
**Schema:** `schemas/g0/agents/intent_contract.schema.json`
**Prototype:** `prototype/g0/agents/intent_builder.py`
**Validator:** `tools/g0/validate_intent_clarification.py`

---

## 1. Purpose

The `IntentContract` is the central boundary translating human conversation
into operational work. CEO Hermes operates **from the IntentContract**, not
from raw chat.

## 2. Schema

```yaml
intent_id:
tenant_id:
client_actor_id:
organization_id:
intent_type:
objective:
desired_outcome:
constraints:
known_facts_refs:
user_assertions:
open_questions:
non_goals:
priority:
deadline_or_time_horizon:
authority_scope:
requested_capabilities:
confidence_state:
source_conversation_refs:
created_at:
```

## 3. Intent classes

- `EXPLORE_IDEA`
- `FIND_GRANTS`
- `ASSESS_OPPORTUNITY`
- `BUILD_APPLICATION`
- `UPDATE_PROFILE`
- `REVIEW_DRAFT`
- `RESEARCH_FUNDER`
- `RESEARCH_WINNERS`
- `EXPLAIN_RESULT`
- `OTHER_CONTROLLED_EXTENSION`

## 4. Hard rules

1. **Raw conversation is linked, not embedded wholesale.** `source_conversation_refs`
   are opaque refs retrievable for audit; they never enter CEO active context.
2. **Known canonical facts use refs.** `known_facts_refs` point at Book 2/3
   canonical objects; no embedded copies that can silently drift.
3. **User assertions are labeled `ASSERTION` until promoted.** The schema
   constrains assertion status to `ASSERTION`; promotion is a separate
   governed event.
4. **Authority scope is explicit.** One of `EXPLORE_ONLY`, `RESEARCH_ONLY`,
   `RESEARCH_AND_DRAFT_ONLY`, `PREPARE_ONLY`.
5. **Unresolved critical questions remain visible.** `open_questions` persist
   across versions until answered.
6. **Submission while phase-disabled is normalized.** Requests for
   `application.submit` / `submission.*` are normalized to
   `application.prepare_submission_package` with a recorded note, or rejected.

## 5. Amendment semantics

A clarification answer or client feedback produces a **new intent version**
(`supersedes_intent_id`) — the prior intent history is never silently
mutated.

## 6. Verified behaviors

- `test_intent_missing_tenant_fails`
- `test_submission_request_normalized_to_prepare_only`
- `test_user_assertion_does_not_become_canonical_fact`
- `test_conversation_refs_retrievable_without_ceo_context`
- `test_amend_intent_versions_not_mutates`
