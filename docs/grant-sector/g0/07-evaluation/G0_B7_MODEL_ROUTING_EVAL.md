# G0-B7-C16 — Model & Routing Evaluation

**Document ID:** GS-G0-B7-C16-MODEL
**Status:** RATIFIED (Book 7 chapter C16)
**Engine:** `prototype/g0/evaluation/routing_eval.py`

Models are interchangeable implementation resources, not personalities
embedded in architecture (Book 4 MODEL-001..003).

## Per capability/task class

- correctness
- factuality
- instruction adherence
- structured-output validity
- latency
- cost
- context-window behavior
- tool-use reliability
- variance/retry rate
- safety regression (hard veto)
- provider availability/fallback behavior

## Routing

A routing candidate must prove value against a simpler baseline:

```text
cheap deterministic/small model  → routine classification/extraction
stronger model                   → complex research synthesis/drafting
fallback                         → provider failure or schema failure
```

Do not route merely because a plugin claims intelligent routing. A routing
candidate must be ≥10% cheaper AND at least as correct as the simple
baseline; routing must never select a model lacking structured-output
reliability for a task that requires it (C29-9).
