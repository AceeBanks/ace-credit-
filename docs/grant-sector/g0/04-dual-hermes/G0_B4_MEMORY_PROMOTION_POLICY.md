# G0 Book 4 — Memory Promotion Policy

**Document ID:** GS-G0-B4-C15-PROMO-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C15
**Policy:** `config/g0/agents/memory_promotion_policy.yaml`
**Prototype:** `prototype/g0/agents/memory_lifecycle.py`
**Validator:** `tools/g0/validate_memory_lifecycle.py`

---

## 1. Purpose

**Separate remembering from learning.** Not every observation becomes durable
memory; not every lesson becomes doctrine.

## 2. Lifecycle

```text
EVENT / OBSERVATION
        ↓
MemoryCandidate
        ↓
classification → REJECT | TEMPORARY | PROMOTE_FOR_REVIEW
        ↓
validation / contradiction check
        ↓
PROMOTED MEMORY
        ↓
periodic revalidation → SUPERSEDED | EXPIRED | RETAINED
```

## 3. Promotion criteria

repeated use · explicit user statement/decision · high future utility ·
stability over time · not better represented as canonical · no contradiction
with higher-authority state · privacy/retention allowed.

## 4. Class routing (frozen)

- **Auto-promotable (low-risk, clear evidence):** PM-PREFERENCE, PM-GOAL,
  PM-OPEN_LOOP.
- **Review required:** PM-IDENTITY, PM-DECISION, PM-RELATIONSHIP, CM-BLOCKER,
  CM-CAPABILITY.
- **Book 7 eval required:** CM-LESSON-CANDIDATE — operational lessons that
  change agent behavior can never bypass evaluation before promotion to
  doctrine.

## 5. Rules (frozen)

| Rule | Content |
|---|---|
| PROMO-001 | Random conversational detail is classified REJECT. |
| PROMO-002 | Explicit durable preference with clear source evidence is auto-promotable. |
| PROMO-003 | A conflicting new preference triggers supersession flow, never coequal memories. |
| PROMO-004 | Operational lessons cannot bypass Book 7 evaluation. |
| PROMO-005 | Memory conflicting with canonical Book 2/3 state is flagged; canonical state wins for operational factual use. |

## 6. Verified behaviors

- `test_random_conversational_detail_rejected`
- `test_explicit_durable_preference_promoted`
- `test_conflicting_preference_requires_supersession`
- `test_operational_lesson_cannot_bypass_eval`
