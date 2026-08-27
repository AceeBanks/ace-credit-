# G0-B7-C25 — Privacy, Leakage & Benchmark Integrity

**Document ID:** GS-G0-B7-C25-PRIV
**Status:** RATIFIED (Book 7 chapter C25)
**Config:** `config/g0/evaluation/privacy_policies.yaml`
**Engine:** `prototype/g0/evaluation/ops_eval.py`

## Threats

- tenant-private examples leaking into global eval (P0)
- evaluation corpus copied into prompts visible to unrelated tenants
- holdout contamination (P0)
- model memorization mistaken for capability
- duplicate examples inflating scores
- production logs containing secrets
- evaluator receiving unnecessary PII
- candidate skill generated from another tenant's private workflow

## Required controls (PRIV-001..008)

- privacy class on every case
- tenant scope
- redaction/minimization
- explicit approval for generalized reuse
- holdout separation
- duplicate/near-duplicate analysis
- audit of corpus exports
- deletion/retention linkage

**Cross-tenant leakage = P0** (EVAL-LAW-011, non-compensatory).
