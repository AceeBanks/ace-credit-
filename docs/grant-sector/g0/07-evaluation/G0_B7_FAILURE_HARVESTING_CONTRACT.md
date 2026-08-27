# G0-B7-C26 — Production Feedback & Failure Harvesting

**Document ID:** GS-G0-B7-C26-FC
**Status:** RATIFIED (Book 7 chapter C26)
**Engine:** `prototype/g0/evaluation/ops_eval.py`

Book 7 creates the safe input side of future improvement.

## FailureCase

Capture: capability/task, input/evidence refs, observed output, expected
behavior if known, failure taxonomy, severity, reviewer/user feedback,
reproducibility, candidate lesson refs.

## Feedback is not direct training truth (EVAL-LAW-012)

- client dislikes tone → preference signal
- grant loses → not proof draft was bad
- reviewer corrects deadline → factual error candidate
- worker repeatedly misses requirement → strong regression candidate

Book 7 harvests evidence for improvement without letting anecdotes rewrite
production behavior.
