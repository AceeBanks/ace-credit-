# G0 Book 4 — Personal Memory Constitution

**Document ID:** GS-G0-B4-C12-MEMORY-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C12
**Config:** `config/g0/agents/personal_memory_classes.yaml`, `memory_ttl_policy.yaml`
**Prototype:** `prototype/g0/agents/memory_manager.py`
**Validator:** `tools/g0/validate_memory_constitutions.py`

---

## 1. Purpose

Define persistent **relationship continuity** without infinite
autobiographical storage. Personal memory answers:

> What should I remember to understand and help this client?

## 2. Durable memory classes

| Class | Meaning |
|---|---|
| PM-IDENTITY | Stable client/organization relationship context not better represented as canonical domain facts. |
| PM-PREFERENCE | Communication/work preferences. **Preferences are not business facts.** |
| PM-GOAL | Longer-lived user objectives. |
| PM-DECISION | Meaningful user choices/commitments not yet fully represented in domain state. |
| PM-RELATIONSHIP | Relevant partner/funder/contact context (subject to privacy/data policy). |
| PM-OPEN_LOOP | Unresolved ideas/questions the user expects to revisit. |
| PM-EPISODIC_SUMMARY | Compressed meaningful interaction episode. |

## 3. Do NOT store when canonical domain state is superior

EIN, grant deadline, award ceiling, verified revenue, application status,
source-backed statistics. Store a **canonical_ref** instead; freeform
duplication is a policy violation (`canonical_substitution_guard`).

## 4. Memory record fields

```yaml
memory_id:
memory_class:
tenant/user scope:
statement:
source_event_refs:
created_at:
last_confirmed_at:
importance:
confidence_state:
expires_at:
supersedes:
canonical_refs:
privacy_class:
```

## 5. Rules (frozen)

- stable preferences survive conversation compaction;
- official grant deadlines are never duplicated as freeform memory truth;
- old preferences can be superseded (append-only history);
- user corrections produce new records + supersession;
- forgetting is intentional — records past retention leave ACTIVE retrieval.

## 6. Verified behaviors

- `test_stable_preference_survives_compaction`
- `test_grant_deadline_not_duplicated_as_freeform_truth`
- `test_old_preference_can_be_superseded`
- `test_user_correction_produces_supersession`
