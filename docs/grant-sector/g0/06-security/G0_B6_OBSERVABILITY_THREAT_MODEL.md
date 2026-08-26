# G0-B6-C23/C24 — Security Observability & Threat Model

## C23 — Observability (OBS-001..006)

Signals needed to detect abuse without drowning in logs:

`auth_failure`, `denied_authorization`, `cross_tenant_attempt`,
`secret_redaction_hit`, `tool_call`, `unusual_destination_attempt`,
`prompt_injection_detection`, `revoked_token_use`, `approval_failure`,
`parser_quarantine_failure`, `ssrf_block`, `break_glass_use`.

- **OBS-001** Telemetry prefers IDs/hashes/reason codes over raw sensitive
  payloads; values that look like secrets are redacted at the boundary.
- **OBS-002/003** Auth-failure bursts and cross-tenant attempts alert at
  HIGH.
- **OBS-004** Break-glass use alerts at HIGH and is visible in reports.
- **OBS-005** Secret-redaction hits alert at CRITICAL_P0.
- **OBS-006** Telemetry is tenant-filtered.

Alert classes: INFO / WARNING / HIGH / CRITICAL_P0.

## C24 — Threat Model

STRIDE-like product-specific inventory covering 11 actors, 9 assets and
10 threat classes. Every P0 threat carries attack path, control, detection
and residual risk:

| ID | Class | Attack | Control | Residual |
|---|---|---|---|---|
| THR-001 | cross-tenant leakage | Tenant A guesses Tenant B artifact ID | tenant-scoped store + per-read authz | LOW |
| THR-002 | disclosure | secret in agent context/trace | credentials inaccessible to model + redaction | LOW |
| THR-003 | elevation | actor exceeds grant | capability grants + default-deny | LOW |
| THR-004 | prompt/tool injection | source coerces tool call | tool authority independent of prompt | LOW |
| THR-005 | tampering | forged integration receipt | integration non-authoritative | MEDIUM |
| THR-006 | disclosure | SSRF to internal/metadata | egress allowlist independent of model | LOW |

P1 rows cover quota bypass and audit-write failure (fail-closed).

## Verified

- Validator: `python tools/g0/validate_lifecycle_security.py`
- Tests: `tests/g0/book6/test_lifecycle_security.py` (C23/C24 sections)
- Config: `config/g0/security/observability_policy.yaml`,
  `config/g0/security/threat_model.yaml`
