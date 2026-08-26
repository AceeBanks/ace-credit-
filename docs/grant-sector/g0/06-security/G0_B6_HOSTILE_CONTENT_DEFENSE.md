# G0-B6-C16/C17 — Hostile Content Defense (Prompt Injection & Malicious Files)

## Scope

Closes the untrusted-input loop of the Grant machine: external source
content and files are *data*, never policy, never authority, never tool
calls. Ratified law SEC-LAW-006/008 and Book 3's source-provenance rules
are enforced here as executable guards.

## C16 — Prompt injection defense (INJ-001..007)

| Rule | Meaning | Executable guard |
|---|---|---|
| INJ-001 | Source content is untrusted; injected instruction can never call a tool | `InjectionGuard.mark_untrusted` always sets `trusted: False`; `would_call_tool` flags coercion markers |
| INJ-002 | A "system message" inside source content remains data | `system_message_in_source_is_data` never elevates |
| INJ-003 | Source content can never change tenant/project scope | `assert_scope_immutable` rejects scope-switch instructions |
| INJ-004 | Malicious content cannot self-promote evidence | `would_promote_evidence` detects promotion coercion; promotion remains governed |
| INJ-005 | Retrieval poisoning cannot override official precedence | `RetrievalPrecedence.official_wins` |
| INJ-006 | Tool-use coercion in content cannot trigger tool calls | gateway authority is independent of model prompt (C9-C11) |
| INJ-007 | Credential solicitation never yields secrets | credentials are inaccessible to the model (C8) |

The decisive property is **tool authority independence**: a model may be
deceived, but the tool gateway (G0-B6-C9-C11) only executes a tool when an
AuthorizationDecision grants the capability — a prompt cannot mint one.

## C17 — Malicious document handling (FILE-001..007)

- Magic-byte validation, not extension trust (FILE-001).
- Size limits + archive-ratio checks block zip bombs (FILE-002).
- Quarantine before parsing (FILE-003).
- Macro/executable content is never executed (FILE-004).
- Path traversal sanitized; basename only (FILE-005).
- Parser output is never policy (FILE-006).
- Parser-generated links pass through the egress policy before any fetch
  (FILE-007).

## Verified

- Validator: `python tools/g0/validate_hostile_approval_audit.py`
- Tests: `tests/g0/book6/test_hostile_approval_audit.py` (C16/C17 section)
- Config: `config/g0/security/hostile_content_policy.yaml`
