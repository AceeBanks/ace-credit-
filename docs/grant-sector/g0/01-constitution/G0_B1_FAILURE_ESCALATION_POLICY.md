# G0 Book 1 — Failure, Degradation & Escalation Law

**Chapter:** B1.C8 · **Machine-readable source:** `config/g0/policy/failure_matrix.yaml`

| Class | Trigger | Action | May degrade to |
|---|---|---|---|
| F-AUTH | missing/invalid permission | FAIL_CLOSED | nothing |
| F-TENANT | missing/ambiguous tenant scope | FAIL_CLOSED | nothing |
| F-SOURCE | source unavailable/stale/contradictory | bounded retry → alternate registered source → uncertainty/escalation | RETRY_BOUNDED, PARTIAL_WITH_UNCERTAINTY, HUMAN_ESCALATION |
| F-SCHEMA | invalid typed output | repair/retry within bound, then fail task | RETRY_BOUNDED, HUMAN_ESCALATION |
| F-WORKER | timeout/crash | bounded retry/reassign preserving task lineage | RETRY_BOUNDED, HUMAN_ESCALATION |
| F-MODEL | provider/model failure | permitted fallback IF capability requirements remain satisfied | PARTIAL_WITH_UNCERTAINTY, READ_ONLY |
| F-EVIDENCE | claim unsupported | omit or label unsupported; NEVER fabricate | PARTIAL_WITH_UNCERTAINTY |
| F-BUDGET | numerical mismatch | block finalization until deterministic reconciliation passes | none |
| F-DEADLINE | deadline unknown/conflicted | block readiness/submission status; refresh/escalate | HUMAN_ESCALATION |
| F-QA | quality failure | repair iteration or human review; never silent final | HUMAN_ESCALATION |

## Invariants

1. **Security/authority uncertainty always fails closed** — F-AUTH/F-TENANT have
   no degraded bypass. This is the machine-readable form of LAW-B1-005.
2. No failure mode may produce silent canonical mutation.
3. Every capability in the registry declares a `failure_mode` drawn from this
   matrix (validator-enforced).

The policy evaluator maps its DENY reason codes onto F-AUTH/F-TENANT so the
evaluator's fail-closed behavior and this law cannot drift apart.
