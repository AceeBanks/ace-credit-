# G0 Book 4 — Context Assembly Policy

**Document ID:** GS-G0-B4-C11-CONTEXT-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C11
**Schema:** `schemas/g0/agents/context_bundle.schema.json`
**Policy:** `config/g0/agents/context_budget_policy.yaml`
**Prototype:** `prototype/g0/agents/context_builder.py`
**Validator:** `tools/g0/validate_context_explanation.py`

---

## 1. Purpose

Replace "send the whole conversation" with **explicit contextual assembly**.
Each operation receives a `ContextBundle` assembled from canonical state and
selected memory — never an inherited, ever-growing transcript.

## 2. ContextBundle

```yaml
context_bundle_id:
consumer_actor:
operation_type:
tenant_id:
project_id:
canonical_state_refs:
evidence_refs:
memory_refs:
recent_interaction_refs:
policy_refs:
task_refs:
anchors:
excluded_context_classes:
context_budget:
assembled_at:
```

## 3. Assembly order (frozen)

```text
1. required canonical state
2. required current evidence
3. active task/project state
4. mandatory policy/constraints
5. promoted role-specific memory
6. selected recent interaction context
7. optional supporting history within budget
```

## 4. Never default-inject

- entire user history;
- entire worker traces;
- closed project transcripts;
- secrets;
- irrelevant application documents;
- stale memory marked superseded.

## 5. Anchor policy (frozen)

**Mandatory anchors always survive budget pressure.** If the budget cannot
hold the mandatory refs, assembly is an error — the anchor is never dropped.
Anchor priority is P0_MANDATORY.

## 6. Budget & priority

Budget measured in tokens/characters, item count, relevance class and
mandatory-vs-optional priority. Retrieval order:

1. exact required refs;
2. active state;
3. role-specific memory class;
4. semantic relevance;
5. recency as tie-breaker only.

## 7. Verified behaviors

- `test_anchors_survive_budget_pressure`
- `test_budget_below_mandatory_fails`
- `test_irrelevant_old_conversations_excluded`
- `test_deterministic_mandatory_refs_same_state`
