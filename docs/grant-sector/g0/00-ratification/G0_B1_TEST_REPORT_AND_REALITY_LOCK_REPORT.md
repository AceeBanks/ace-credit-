# G0 Book 1 — Test Report & Reality Lock Report

**Test command:** `python -m pytest tests/g0/book1 -q`
**Result:** **103 passed, 0 failed, 0 blocked** (full suite; the Reality Lock's
inner derivation run records 102 passed + 1 self-excluded freshness test — see
`evidence.test_results.scope` in `G0_B1_REALITY_LOCK.json`)

## Coverage by chapter

| Suite | Tests | Proves |
|---|---|---|
| `test_constitution_structure.py` | 10 | B1.C2 law catalog: 30 laws, unique IDs in order, required fields, injected defects (missing rationale, unknown enforcement category, duplicate ID, removed law, empty capability classes) fail closed; key security laws FROZEN |
| `test_authority_matrix.py` | 15 | B1.C3-C8: actor ceilings, capability registry, worker non-inheritance, no agent canonical-mutation without approval, no conversational credentials, submission disabled / drafting enabled, self-improvement no self-ratification, failure classes fail closed |
| `test_policy_evaluator.py` | 23 | B1.C11 executable PDP: twelve-step decision order, deny-by-default, unknown actor/capability/tenant deny, approval enforcement (AP2/AP3, expired/agent-principal approvals fail closed), evaluator crash fails closed |
| `test_client_vision_coverage.py` | 7 | B1.C12: all 13 Phase 1 client deliverables have a legal capability path (CR-01..CR-12); CR-13 auto-submit has NO legal path |
| `test_georgia_first.py` | 5 | B1.C13: no constitutional clause hard-codes California; Georgia amendment authoritative; Georgia proof lane (fetch/snapshot/winners/draft) legal at L2 |
| `test_adversarial_authority.py` | 19 | B1.C14: A1-A15 adversarial scenarios — tool escalation, worker inheritance, cross-tenant, secret-in-memory, prompt injection, self-policy expansion, QA fact rewriting, model fallback, invented capability, disguised external communication — all fail closed |
| `test_book_integration.py` | 18 | B1.C15: the 15 mandatory constitution assertions + coverage targets (100% policy metadata, zero submission paths, zero open P0) |
| `test_book1_reality_lock.py` | 6 | B1.C16: lock is DERIVED — open P0, enabled submission, missing audit metadata, self-ratification, failing/missing tests each flip readiness to FAIL; committed lock must equal honest regeneration (stale-lock defense) |

**Total: 103 tests across 8 suites.**

## Adversarial design notes

- Every chapter was proven against injected defects (negative fixtures), not just
  the happy path — a policy that cannot fail cannot prove anything.
- The policy decision point is deterministic and memory-independent: the same
  inputs always produce the same decision, and rebuilding the registry from files
  after an agent reset changes nothing (A12).
- The Reality Lock treats a not-run test suite as blocking
  (`adversarial_p0_pass: null` ⇒ FAIL), so absence of evidence never reads as
  success.
- Readiness is a conjunction of predicates computed from the live policy
  registers, the executable evaluator, and a live pytest run; no predicate is
  hand-written. `submission_disabled` is derived from registry/policy evidence
  (CD-003), not tool availability.

## Reality Lock reproduction

```bash
python tools/g0/build_book1_reality_lock.py \
  --out docs/grant-sector/g0/00-ratification/G0_B1_REALITY_LOCK.json
```

Exit code 0 ⇔ PASS. Regeneration is deterministic given repository state.

## Lock snapshot (2026-08-26)

| Predicate | Value |
|---|---|
| status | PASS |
| constitution_complete | true (30 laws) |
| client_phase1_coverage | 1.0 |
| actors_with_authority_ceiling | 1.0 |
| capabilities_with_policy_metadata | 1.0 |
| unknown_defaults_deny | true |
| tenant_scope_tests_pass | true |
| submission_disabled | true |
| drafting_enabled_l2 | true |
| self_improvement_tests_pass | true |
| secret_boundary_tests_pass | true |
| adversarial_p0_pass | true |
| p0_open | 0 |
| **ready_for_book2** | **true** |
