# G0 Book 6 — External Review Record 01

**Review id:** `G0_B6_EXTERNAL_REVIEW_01`
**Reviewed surface:** Book 6 authorization chain (`prototype/g0/security/`),
`config/g0/security/` policy, tool gateway, Book 6 test evidence, Reality Lock.
**Date:** 2026-08-26

## Review status

| Stage | Status |
|---|---|
| External review finding | **REPAIR_REQUIRED** |
| Repair commit | pending — `G0-B6-REPAIR-01: bind grants decisions tools approvals and project scope end-to-end` |
| Post-repair verification | **PASS** (see below) |
| External review resolution | **RESOLVED** — authorized to continue Book 7 execution |

## Finding P0 — grant authority enforcement (authorization gap)

**Severity: P0 (fail-open authorization).**

`Authorizer.authorize()` did not compare the grant's `authority_level`
against the capability's `required_level` or the principal's
`authority_level`. A low-authority grant could authorize a high-requirement
capability, and a grant could carry more authority than its principal
actually holds. Unknown/malformed levels were not rejected.

### Repair

- AUTH-R1 authority ladder enforced inside `authorize()`: `grant
  authority_level >= capability.required_level` AND `grant
  authority_level <= principal.authority_level`. Unknown or malformed
  levels rank as -1 and fail closed (`GRANT_AUTHORITY_INSUFFICIENT`).
- Mandated tests added in `tests/g0/book6/test_authorization.py`:
  - L4 principal + L2 grant + L4 capability => DENY
  - L4 principal + L4 grant + L4 capability => ALLOW
  - malformed grant level => DENY
  - grant above principal ceiling cannot authorize
- `grant_authority_enforced` predicate added to the Reality Lock.

## Finding P0 — authorization/tool capability substitution (authorization gap)

**Severity: P0 (bearer-token style ALLOW).**

ToolGateway treated an ALLOW decision as a bearer token for arbitrary tool
calls: the decision's `capability_id` was optional, and when present was not
verified against the tool's declared `capability_ids`. A research ALLOW could
be reused for application mutation. Callers could also construct
`AuthorizationDecision` mappings by hand.

### Repair

- `AuthorizationDecision` contract is now canonical and self-verifying
  (AUTH-R2): `request_id`, `principal_id`, `tenant_id`, `project_id`,
  `capability_id`, `resource_id`, `decision`, `reason_code`, `grant_id`,
  `decision_timestamp` plus a canonical `request_hash` and a self-integrity
  `decision_id` (SHA-256 over the fixed field set). `DECISION_REQUIRED_FIELDS`
  includes `decision_id`.
- ToolGateway MUST receive `authorization_decision.capability_id` and verify
  it is one of `tool.capability_ids`. Missing capability_id => DENY
  (`MISSING_CAPABILITY`); capability not declared by the tool => DENY
  (`CAPABILITY_NOT_DECLARED`). No `if granted: check` pattern remains.
- Decisions are issued only through the trusted `DecisionRegistry` owned by
  the Authorizer (item 8): the gateway verifies shape, integrity, issuance
  (`decision_unissued`), and tamper-resistance (`decision_tampered`) against
  the registry when configured. Caller-forged dicts fail `decision_shape_ok`
  unless emitted by the trusted constructor, and can never collide with a
  recorded `decision_id`.
- `authorization_capability_binding_pass` and `authorizer_gateway_e2e_pass`
  predicates added to the Reality Lock.

## Finding P0 — same-tenant cross-project scope (authorization gap)

**Severity: P0 (tenant-level privilege escape).**

ScopeEvaluator evaluated tenant membership but not project scope. A worker
holding a project-scoped grant for Project A could reach Project B in the
same tenant. Resources carried no structural project metadata.

### Repair

- Resource metadata is now structural: `resource_id` + `tenant_id` +
  `project_id` (AUTH-R3). ScopeEvaluator evaluates tenant membership AND
  project scope when the resource or grant is project-scoped.
- `grant.project_id` non-null => request project MUST match; same-tenant
  cross-project access is DENIED (`PROJECT_DENIED`).
- Worker delegation grants are project-bound by default (AUTH-R5, GRANT-007).
- `project_scope_pass` and `authorization_resource_binding_pass` predicates
  added to the Reality Lock.

## Finding P1 — approval-registry integration

**Severity: P1 (approval truth bypass).**

Approval-requiring operations relied on raw approval-string membership
instead of validating through ApprovalRegistry against tenant, capability,
resource, resource_version, action, expiry, revocation and approval class.

### Repair

- Approval-requiring operations are validated exclusively through
  `ApprovalRegistry` (AUTH-R4); raw string membership is no longer approval
  truth. Validated approval refs (decision/evidence) are bound into the ALLOW
  decision and enforced by the gateway.
- `approval_registry_integration_pass` predicate added to the Reality Lock.

## End-to-end seam verification (item 7)

New harness `tests/g0/book6/_seam.py` runs the real chain —
PrincipalRegistry → GrantRegistry → Authorizer → ApprovalRegistry → ToolGateway —
with no manually mocked AuthorizationDecisions. Attack suite
`tests/g0/book6/test_authorizer_gateway_e2e.py` covers A–N:

- A research ALLOW reused for application mutation => DENY
- B ALLOW reused for a different tool => DENY
- C ALLOW reused for a different tenant => DENY
- D ALLOW reused for a different project => DENY
- E ALLOW reused for a different resource => DENY
- F expired grant => DENY
- G lower-authority grant => DENY
- H revoked approval => DENY
- I approval for a previous resource version => DENY
- J worker Project A reaching Project B in same tenant => DENY
- K missing capability in decision => DENY
- L forged granted capability in caller-created dict => DENY
- M replay of an ALLOW decision => DENY
- N submission remains impossible (capability absent / disabled)

Result: **16 passed** (including explicit deny-assertions on every attack).

## Post-repair verification

| Suite | Command | Result |
|---|---|---|
| Book 0 | `python -m pytest tests/g0/book0 -q` | **51 passed** |
| Book 1 | `python -m pytest tests/g0/book1 -q` | **133 passed** |
| Book 2 | `python -m pytest tests/g0/book2 -q` | **255 passed** |
| Book 3 | `python -m pytest tests/g0/book3 -q` | **243 passed** |
| Book 4 | `python -m pytest tests/g0/book4 -q` | **276 passed** |
| Book 5 | `python -m pytest tests/g0/book5 -q` | **228 passed, 3 skipped** (semantica not installed) |
| Book 6 | `python -m pytest tests/g0/book6 -q` | **227 passed** |
| Full G0 | `python -m pytest tests/g0 -q` | **1413 passed, 3 skipped** |
| Reality Lock | `python tools/g0/build_book6_reality_lock.py` | **PASS**, `ready_for_book7=True`, `p0_open=0` |
| Seam bindings | `python tools/g0/validate_seam_bindings.py` | **PASS** |

- `G0_B6_REALITY_LOCK.json` regenerated with 6 new predicates:
  `grant_authority_enforced`, `authorization_capability_binding_pass`,
  `authorization_resource_binding_pass`, `project_scope_pass`,
  `approval_registry_integration_pass`, `authorizer_gateway_e2e_pass`.
- Committed lock equals honest regeneration (freshness self-tests green, 18/18).

## Resolution

All four findings are repaired and verified. External review is recorded as
**RESOLVED**; Book 7 execution is authorized to continue.
