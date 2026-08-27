# G0 Book 9 — Secret Management Production Plan

**Chapter:** B9.C21
**Date:** 2026-08-27
**Status:** FROZEN (interface); production secret store integration is
G1.10 — the Book 7 `DevRuntimeCredentialResolver` remains DEV_RUNTIME_ONLY
and is never confused with production secret management.

## Production interface

| Aspect | Decision |
|---|---|
| Secret store | managed secret store (e.g. AWS Secrets Manager / equivalent) — one provider-agnostic interface |
| Environment injection | secrets injected at deploy time into the service environment; never baked into images |
| Workload identity | services authenticate to the store via workload identity (IAM role / equivalent), never shared keys |
| Credential rotation | provider credentials rotatable; gateway re-resolves per policy |
| Provider/API credential ownership | platform/policy owns the ref; adapters receive the value only inside trusted execution |
| Local dev dummy credentials | `env.example` + `.env.local` with clearly-marked dev-only values; gitignored |
| Audit redaction | secrets never logged; redaction patterns verified (Book 7 tests G/H/I) |
| Incident revocation | rotate credential immediately; gateway denies on revoked ref; all affected audit refs listed |

## Hard rules

1. No secrets in the repo, fixtures, agent memory, or normal application
   logs.
2. `ModelRequest`/`ModelResponse` never carry credential values (schema
   enforced, leak-checked by tests).
3. The Book 7 dev resolver (`DEV_RUNTIME_ONLY`) may exist only for local
   development; production uses the store-backed resolver.
4. Destination binding: a credential ref is bound to provider + scope;
   a caller cannot redirect it to an arbitrary destination (SSRF law).
5. Any secret scan hit fails CI (`G0_B9_CI_CD_POLICY.md`).
