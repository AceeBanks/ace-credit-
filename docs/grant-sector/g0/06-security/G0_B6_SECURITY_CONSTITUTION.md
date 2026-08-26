# G0-B6-C1 — Security Constitution

## Purpose

Freeze the security laws before choosing implementation providers. Book 6
turns the Book 1 constitutional authority model into an enterprise-grade
security and execution boundary.

## Laws (SEC-LAW-001..020)

1. **Stable authenticated principal** — every active actor has one;
   anonymous consequential actions are prohibited.
2. **Authentication ≠ authorization** — identity alone grants no capability.
3. **Tenant scope mandatory** — tenant-owned access resolves the tenant
   explicitly.
4. **Capability scope mandatory** — only registered capabilities within
   granted bounds.
5. **Workers do not inherit parent authority** — each worker gets an
   explicit task capability grant.
6. **Credentials never enter agent context** — raw secrets are server-side
   only.
7. **Tool gateways enforce policy independently of agents** — prompt
   compliance is not a security boundary.
8. **External source content has zero policy authority** — prompt injection
   is hostile data.
9. **External side effects require their own capability** — read/draft
   cannot become send/submit.
10. **Unknown/expired/revoked grants deny** — no stale authority.
11. **Cross-tenant leakage is P0** — a release blocker.
12. **No direct database access as agent capability** — governed interfaces
    only.
13. **Approval is durable evidence** — bound to actor/action/resource/version.
14. **Admin override explicit and audited** — no hidden superuser.
15. **Observability redacts sensitive data** — logging is not exfiltration.
16. **Security-critical failures fail closed** — ambiguity cannot bypass.
17. **Tool definitions are versioned** — schema drift cannot expand side
    effects.
18. **Third-party workflow systems are subordinate executors** — never
    canonical authority/state.
19. **Future L4/L5 reuse this exact model** — no submission bypass.
20. **Data access is least necessary** — minimized context and tool output.

Machine-readable config: `config/g0/security/security_constitution.yaml`
Validator: `tools/g0/validate_security_constitution.py`
Tests: `tests/g0/book6/test_security_constitution.py`
