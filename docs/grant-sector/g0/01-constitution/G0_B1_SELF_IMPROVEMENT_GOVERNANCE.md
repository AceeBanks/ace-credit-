# G0 Book 1 — Self-Improvement Governance

**Chapter:** B1.C7 · **Machine-readable source:** `config/g0/policy/self_improvement.yaml`

Agents may improve the system. They may never unilaterally promote changes —
above all, never their own authority (LAW-B1-017/018).

## Change classes

prompt · skill · source-adapter · extraction-rule · model/provider ·
capability/policy · schema/domain · UI workflow · infrastructure.

## Promotion lifecycle (no step may be skipped)

```text
OBSERVATION → CANDIDATE LESSON → CHANGE PROPOSAL → CHANGE IMPACT MAP → SANDBOX
→ BASELINE VS CANDIDATE EVAL → SECURITY / REGRESSION CHECK → APPROVAL
→ VERSIONED PROMOTION → MONITOR → ROLLBACK IF NEEDED
```

## Authority restriction

CEO Hermes **may**: create observation; propose lesson; draft change; request eval.
CEO Hermes **may NOT**: promote its own authority increase; disable audit or
security controls; silently change constitutional laws; deploy untested
production code.

Workers may only create observations; lessons flow up through CEO synthesis —
a worker can never seed a change path that bypasses the control plane.

## Hard rules (machine-checked)

- A proposal increasing the proposing agent's own authority requires human
  ratification by a principal OTHER than any agent.
- Eval evidence must exist before APPROVAL; a prompt change without eval cannot promote.
- Failed candidates cannot become active.
- Rollback metadata is required at promotion time for production promotion.
- Every promotion is an A4 audit event linking proposal → eval run → approver(s) → version.

Plan-mandated checks: self-authored policy expansion blocked ✔ · prompt change
without eval cannot promote ✔ · failed candidate cannot become active ✔ ·
rollback metadata required ✔
