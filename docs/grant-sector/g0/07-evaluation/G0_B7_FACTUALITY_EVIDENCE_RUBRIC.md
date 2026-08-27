# G0-B7-C8 — Factuality & Evidence Evaluation

**Document ID:** GS-G0-B7-C8-FACT
**Status:** RATIFIED (Book 7 chapter C8)
**Engine:** `prototype/g0/evaluation/metrics.py`

## Metrics

- material claim support rate
- citation precision
- citation recall for citation-required claims
- locator correctness
- unsupported claim count
- contradicted claim count
- stale-evidence usage
- source-authority compliance
- assumption labeling accuracy
- future-target/historical-fact classification accuracy

## Hard gate

A candidate that increases prose quality while increasing unsupported
material claims cannot promote. Same for any factuality regression:
`factuality_hard_gate()` compares baseline vs candidate unsupported counts
and claim support rates.

## Evidence authority

Book 3/5 evidence authority cannot be replaced by evaluator opinion
(EVAL-LAW-007, constitutional non-dilution). Generated output is not
evidence merely because another model scores it highly.
