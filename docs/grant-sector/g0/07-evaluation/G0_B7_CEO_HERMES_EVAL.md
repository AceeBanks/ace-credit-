# G0-B7-C12 — CEO Hermes Evaluation

**Document ID:** GS-G0-B7-C12-CEO
**Status:** RATIFIED (Book 7 chapter C12)
**Engine:** `prototype/g0/evaluation/agent_eval.py::ceo_hermes_eval`

CEO Hermes is evaluated for operational discipline.

## Metrics/tests

- IntentContract interpretation
- plan decomposition quality
- correct worker selection
- task bounding
- evidence/context selection
- authority compliance
- unnecessary tool-call rate
- worker-result conflict handling
- blocker detection
- synthesis correctness
- completion-state correctness
- no client-relationship memory pollution (hard fail)
- no hidden dependence on giant raw chat history (hard fail)

## Feed-forward quality test

```text
client idea
→ Personal interpretation
→ IntentContract
→ CEO plan
→ worker outputs
→ CEO synthesis
→ Personal explanation
```

Measure semantic preservation and drift at each boundary
(`ceo_feed_forward_drift`).
