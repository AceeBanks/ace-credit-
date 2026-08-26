# G0-B6-C9/C10/C11 — Tool Registry, Gateway & Hermes MCP Facade

## Tool registry (C9)

Versioned `ToolDefinition` (tool_id, version, provider, capability_ids,
side_effect_class, network_destinations, credential_requirements,
read_write_class, status). Statuses: EXPERIMENTAL, APPROVED_INTERNAL,
APPROVED_PRODUCTION, DEPRECATED, DISABLED.

Rules TOOL-001..005: unknown tools denied; version changes altering side
effects/schema require review; tools cannot declare capabilities outside
the registry; disabled tools deny even with capability; discovered
MCP/community tools are never auto-authorized to production.

## Gateway (C10)

`verify decision → resolve tool → resolve credential ref → inject
server-side → enforce egress → execute → sanitize result → audit`.

TOOL-006..010: tool availability ≠ permission (gateway enforces the
AuthorizationDecision independently); credentials invisible to callers (auth
header override rejected); destinations allowlisted (redirects cannot leak
credentials); external side effects require the side-effect capability;
returned payloads never contain credentials.

## Hermes MCP facade (C11)

Personal → CEO → gateway → canonical services, with filtered surfaces:
Personal (client read, intent, explanation, review), CEO (research, matching,
internal drafting, QA, bounded operational state), workers (reduced
manifests). No direct DB access, no raw-secret endpoints, no wildcard HTTP
tool, request IDs propagated end-to-end, hidden tools (submission,
arbitrary DB query) never discoverable.

## Implementation

- `config/g0/security/tool_registry_policy.yaml`
- `schemas/g0/security/tool_definition.schema.json`
- `prototype/g0/security/tool_gateway.py` (`ToolRegistry`, `ToolGateway`,
  `MCPFacade`)
- `tools/g0/validate_tool_gateway.py`
- `tests/g0/book6/test_tool_gateway.py` (16 tests)
