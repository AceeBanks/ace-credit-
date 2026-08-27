# G0-B7-C24 — Cost, Latency & Reliability

**Document ID:** GS-G0-B7-C24-COST
**Status:** RATIFIED (Book 7 chapter C24)
**Engine:** `prototype/g0/evaluation/ops_eval.py`

Quality must be operationally viable. Track per capability:

- token/input/output use
- model cost
- external API cost
- p50/p95 latency
- timeout rate
- retry rate
- schema failure rate
- tool failure rate
- recovery success
- context size

## Cost guard

Cost optimization cannot bypass correctness/evidence/security floors.
42-evey cost/delegation plugins may be evaluated as telemetry/helpers, not
adopted as authority (Amendment 002).

## Reliability

A candidate that is cheaper but unreliable fails; structured-output
failures and timeouts are measured, not hidden.
