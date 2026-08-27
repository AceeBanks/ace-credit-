# G0-B7-C18 — Evaluator Governance

**Document ID:** GS-G0-B7-C18-GOV
**Status:** RATIFIED (Book 7 chapter C18)
**Engine:** `prototype/g0/evaluation/evaluators.py`

Evaluation itself can fail; governance makes it auditable.

## Evaluator types

- deterministic assertion
- schema validator
- domain rule evaluator
- statistical metric
- independent LLM judge
- pairwise preference judge
- human reviewer
- production outcome metric

## Requirements

Each evaluator declares:

- what it measures
- what it cannot measure
- version
- known bias/failure modes
- required independence
- calibration evidence where relevant

## LLM judge calibration

Use reviewed cases to measure agreement, positional bias, verbosity bias and
self-preference where practical. Deterministic truth always wins when it
conflicts with an LLM judge (EVAL-LAW-004). A candidate cannot be the sole
evaluator of itself (EVAL-LAW-006). Never let one opaque "quality judge"
decide production promotion (EVAL-LAW-013).
