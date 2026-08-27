# G0-B7-C22 — Shadow, Canary & Rollback

**Document ID:** GS-G0-B7-C22-ROLLOUT
**Status:** RATIFIED (Book 7 chapter C22)
**Engine:** `prototype/g0/evaluation/rollout.py`
**Schemas:** `rollout_event.schema.json`, `rollback_event.schema.json`

## Rollout classes

- OFFLINE_ONLY — no live influence
- SHADOW — observes same inputs or replays traces; cannot affect client outcome
- INTERNAL_CANARY — limited internal/test users
- BOUNDED_CLIENT_CANARY — only after future authorization; low-risk
  reversible behavior only
- FULL — promoted default

During current G0 grant work, **consequential external submission remains
disabled regardless of rollout class.**

## Rollback

Rollback must restore the known baseline configuration/version **without
depending on agent memory** (EVAL-LAW-009). Every promoted change registers
its baseline config identity; rollback restores it exactly.

Triggers:

- hard-gate failure
- factuality degradation
- security alert (P0)
- latency/cost runaway
- structured-output failure
- human quality regression
