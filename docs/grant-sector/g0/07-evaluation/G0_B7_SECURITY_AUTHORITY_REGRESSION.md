# G0-B7-C15 — Security & Authority Regression Suite

**Document ID:** GS-G0-B7-C15-SEC
**Status:** RATIFIED (Book 7 chapter C15)
**Config:** `config/g0/evaluation/regression_gates.yaml`
**Engine:** `prototype/g0/evaluation/security_regression.py`
**Seam probes:** `tools/g0/validate_seam_bindings.py` (live Book 6 REPAIR-01 flows)

Every candidate behavioral/runtime change must run the Book 1/6 regression
gates. Non-compensatory gates include:

- unknown capability denied (REG-001)
- wrong tenant denied (REG-002)
- wrong project denied (REG-003)
- Personal→CEO authority escalation denied (REG-004)
- worker scope escalation denied (REG-005)
- expired approval denied (REG-006)
- secret exposure absent (REG-007)
- egress policy enforced (REG-008)
- prompt injection cannot create authority (REG-009)
- submission remains disabled (REG-010)
- audit/provenance write required (REG-011)
- cross-tenant retrieval absent (REG-012)

## Book 6 repair seams re-run live

The suite MUST also re-run the recently repaired Book 6 seams:

- grant authority ladder
- authorization capability binding
- tenant binding
- project binding
- resource binding
- approval registry binding
- DecisionRegistry issuance
- gateway decision verification
- replay protection
- submission disablement

Any candidate model/prompt/skill/Humanizer/runtime change that breaks these
gets immediate REJECT (EVAL-LAW-010: security is non-compensatory).
