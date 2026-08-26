# G0 Book 4 — CEO Memory Constitution

**Document ID:** GS-G0-B4-C13-MEMORY-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C13
**Config:** `config/g0/agents/ceo_memory_classes.yaml`, `memory_ttl_policy.yaml`
**Prototype:** `prototype/g0/agents/memory_manager.py`
**Validator:** `tools/g0/validate_memory_constitutions.py`

---

## 1. Purpose

Define **lean operational continuity**. CEO memory answers:

> What should I retain to operate this product efficiently and correctly?

## 2. Durable memory classes

| Class | Meaning |
|---|---|
| CM-SYSTEM-DOCTRINE | References ratified laws/contracts, ideally by version rather than copied prose. |
| CM-ACTIVE-PROJECT | Operational summary of active project/application state; reconstructable from canonical state. |
| CM-BLOCKER | Known unresolved failure/blocker requiring continued attention. |
| CM-CAPABILITY | Operational knowledge about capability behavior/limitations, derived from registry/system state. |
| CM-LESSON-CANDIDATE | Observed recurring pattern awaiting validation/promotion. |
| CM-PROMOTED-LESSON | Validated operational lesson. |
| CM-HEALTH-DEGRADATION | Temporary awareness of source/tool/provider problems with TTL. |

## 3. Explicitly non-durable by default

raw worker logs · one-off retry details · entire prompts · every grant
researched · closed task chatter · verbose tool output.

## 4. Principle

Retain:

> "Georgia source X frequently requires browser fallback after API failure."

Do not retain:

> every historical HTML/error dump from source X.

## 5. Rules (frozen)

- closed task detail expires without losing the promoted lesson;
- project summary is reconstructable from canonical state (no memory
  required);
- transient provider outages expire after the CM-HEALTH-DEGRADATION TTL;
- `CM-LESSON-CANDIDATE` requires **Book 7 evaluation governance** before
  promotion to `CM-PROMOTED-LESSON` — no operational lesson self-promotes.

## 6. Verified behaviors

- `test_closed_task_detail_expires_but_lesson_survives`
- `test_project_summary_reconstructable_from_canonical_state`
- `test_transient_provider_outage_expires_after_ttl`
- `test_lesson_candidate_requires_book7_gate`
