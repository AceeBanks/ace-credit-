# G0-B6-C25 — Attack Surface Register

## Objective

Enumerate every externally or agent-accessible boundary so no surface is
implicit.

## Register fields

For each of the 17 registered surfaces, the register records:
`entry point`, `principal types`, `input trust level`, `tenant scope`,
`capabilities`, `secrets involved`, `egress involved`, `controls`,
`rate limits`, `logging`, and `P0 failure mode`.

## Surfaces

| ID | Name | Trust | P0 failure mode |
|---|---|---|---|
| SRF-001 | web_ui_api | UNTRUSTED | cross-tenant read via guessed artifact id |
| SRF-002 | personal_hermes_mcp | UNTRUSTED | Personal escalates to CEO capability |
| SRF-003 | ceo_hermes_mcp | SEMI_TRUSTED | CEO invokes hidden submission tool |
| SRF-004 | worker_tool_surface | SEMI_TRUSTED | worker exceeds parent capability |
| SRF-005 | source_browser_crawler | UNTRUSTED | crawler crosses registered-source boundary |
| SRF-006 | file_upload | UNTRUSTED | macro executes / zip bomb exhausts storage |
| SRF-007 | document_parser | UNTRUSTED | parser output treated as policy |
| SRF-008 | vector_graph_retrieval | SEMI_TRUSTED | vector leaks tenant B to tenant A |
| SRF-009 | credential_gateway | TRUSTED | credential returned to agent context |
| SRF-010 | oauth_callbacks | UNTRUSTED | wrong-tenant state confusion |
| SRF-011 | webhooks | UNTRUSTED | forged webhook mutates canonical state |
| SRF-012 | integration_executor | UNTRUSTED | Activepieces flow mutates canonical state |
| SRF-013 | database_admin | TRUSTED | agent gains direct DB access |
| SRF-014 | observability | TRUSTED | telemetry cross-tenant leak |
| SRF-015 | artifact_export | SEMI_TRUSTED | export bypasses classification / public link leak |
| SRF-016 | external_email_outreach | SEMI_TRUSTED | injected content triggers email send |
| SRF-017 | grant_portal_submission | TRUSTED | L5 endpoint accidentally enabled |

SRF-017 is **structurally disabled** (ASR-003): the submission capability
is phase-disabled, no grant exists in any Phase-1 surface, and a feature
flag cannot enable it.

## Verified

- Validator: `python tools/g0/validate_attack_surface.py` (17 surfaces,
  11 fields each).
- Config: `config/g0/security/attack_surface.yaml`