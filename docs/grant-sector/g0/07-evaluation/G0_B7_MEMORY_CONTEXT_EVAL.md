# G0-B7-C14 — Memory & Context Evaluation

**Document ID:** GS-G0-B7-C14-MEM
**Status:** RATIFIED (Book 7 chapter C14)
**Engine:** `prototype/g0/evaluation/agent_eval.py::memory_context_eval`

Test the Book 4 memory doctrine empirically.

## Scenarios

- cold restart
- long-running client relationship
- multiple simultaneous grants
- conflicting updated preference
- inactive project reactivation
- huge worker trace
- irrelevant old conversation
- context compaction
- source amendment
- model/provider swap

## Metrics

- mandatory anchor retention (deadline, project, tenant survive restart)
- relevant-memory recall
- irrelevant-context rate
- cross-project bleed (hard fail)
- cross-tenant bleed (P0 hard fail)
- token footprint
- reconstruction correctness
- stale-memory usage (hard fail)
- question repetition

Compare bounded assembled context against raw-history baselines where
useful. Cold reconstruction must succeed without hidden chat history.
