# G0 Book 4 — Memory Supersession & Forgetting Policy

**Document ID:** GS-G0-B4-C16-SUPERSEDE-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C16
**Schema:** `schemas/g0/agents/memory_supersession.schema.json`
**Prototype:** `prototype/g0/agents/memory_manager.py`, `memory_lifecycle.py`

---

## 1. Purpose

Prevent long-term memory from becoming a pile of contradictory current
truths.

## 2. Memory states

`ACTIVE` · `PROVISIONAL` · `SUPERSEDED` · `EXPIRED` · `CONFLICTED` · `ARCHIVED`

## 3. Supersession example

```text
Old preference:  "Show me only top 3 grants"
New preference:  "I want to review up to 10 now"
→ old memory SUPERSEDED, new memory ACTIVE
```

The old record remains retrievable for historical reconstruction
(append-only), but is excluded from active context.

## 4. Canonical conflict rule (frozen)

If freeform memory conflicts with canonical Book 2/3 state:

- canonical state wins for operational factual use;
- memory may remain as historical/user-assertion context but can never
  override truth;
- the conflict is flagged (`canonical_conflict_flag`).

## 5. Forgetting rule (frozen)

Memory with no durable value and past its retention window expires from
active retrieval. Archived raw interaction remains only under the separate
retention policy.

## 6. Verified behaviors

- `test_superseded_record_excluded_from_active_context`
- `test_historical_reconstruction_still_shows_old_record`
- `test_canonical_conflict_flagged`
- `test_canonical_state_wins_over_memory`
- `test_forgetting_rule_expires_from_active_retrieval`
