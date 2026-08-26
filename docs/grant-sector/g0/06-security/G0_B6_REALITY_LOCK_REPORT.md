# G0-B6 — Reality Lock Report

## Lock

`docs/grant-sector/g0/00-ratification/G0_B6_REALITY_LOCK.json`

`python tools/g0/build_book6_reality_lock.py`
→ **status=PASS, ready_for_book7=true, p0_open=0**.

## Derived predicates (not asserted)

| Predicate | Value |
|---|---|
| security_constitution_complete | true |
| principal_model_pass | true |
| tenant_isolation_pass | true |
| capability_grant_pass | true |
| authorization_default_deny | true |
| credential_boundary_pass | true |
| tool_gateway_pass | true |
| mcp_boundary_pass | true |
| egress_policy_pass | true |
| data_classification_pass | true |
| prompt_injection_pass | true |
| malicious_document_pass | true |
| approval_enforcement_pass | true |
| audit_security_pass | true |
| revocation_pass | true |
| break_glass_pass | true |
| submission_disabled | true |
| attack_surface_register_pass | true |
| cross_tenant_p0_pass | true |
| secret_exposure_p0_pass | true |
| adversarial_p0_pass | true |
| p0_open | 0 |
| ready_for_book7 | true |

## Freshness & defect-injection

`tests/g0/book6/test_book6_reality_lock.py` (13 tests) proves:
- FRESH-001 the committed lock derives PASS from current evidence;
- FRESH-002 a hand-edited `ready_for_book7=true` cannot be trusted blindly;
- FRESH-003 the recorded book6 test total is real;
- each injected defect flips the lock to FAIL:
  - empty security constitution → FAIL
  - empty principal policy → FAIL
  - empty capability-grant policy → FAIL
  - `submission_phase: ENABLED` → FAIL
  - <6 p0 threat rows → FAIL (open P0)
  - failing test results → FAIL
  - missing test results → adversarial_p0_pass null (never a false claim)

The recursion guard (`G0_SKIP_LOCK_FRESHNESS=1`) mirrors Book 5: the
builder's inner pytest run skips the committed-lock tests so the build
does not self-pollute.

## Defect-injection proof (per injected defect → FAIL)

| Injected defect | Predicate flipped | Lock status |
|---|---|---|
| Empty security constitution | security_constitution_complete | FAIL |
| Empty principal policy | principal_model_pass | FAIL |
| Empty capability-grant policy | authorization_default_deny | FAIL |
| submission_phase=ENABLED | submission_disabled | FAIL |
| p0_threats=[] | p0_open ≥ 1 | FAIL |
| failing tests | (all behavioral) | FAIL |
| no test results | adversarial_p0_pass=null | not PASS |