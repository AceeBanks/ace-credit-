# G0 Book 9 — Security Baseline Verification

**Chapter:** B9.C22
**Date:** 2026-08-27
**Status:** PASS (prototype topology); re-run required when the production
topology lands (G1.10) — the ADR is invalid if integration weakens Book 6.

## Hard boundaries re-verified

| Boundary | Prototype evidence | Production requirement |
|---|---|---|
| Tenant isolation | structural tenant scope; cross-tenant decision reuse DENIED (MEASURED) | same, in real topology |
| Project isolation | cross-project decision reuse DENIED (MEASURED) | same |
| Worker task scope | TaskContract-scoped workers; no client contact unless permitted (MEASURED) | same |
| Personal/CEO separation | distinct principals/profiles; Personal cannot use CEO-only model profile (MEASURED) | same |
| Secret brokerage | server-side resolver; secret never in prompts/logs/response (MEASURED, tests G/H/I) | production store-backed resolver |
| Egress control | arbitrary base URL / metadata endpoint DENIED (MEASURED) | same in deployment network |
| Prompt injection containment | untrusted source text never enters agent authority; deterministic gates win (MEASURED) | same |
| Tool-gateway enforcement | forged/raw AuthorizationDecision JSON DENIED (MEASURED) | same |
| Approvals | ApprovalRegistry-validated approvals bound into decisions (MEASURED) | same |
| Audit | every consequential state has a DecisionRecord/audit ref (MEASURED) | same |
| Submission disablement | no submission capability/table/route exists (MEASURED, migration test asserts) | same — structurally impossible |

## Attack suite (Book 8 resilience, re-run at G0 seal)

All 6/6 denied: cross-tenant decision reuse, cross-project decision reuse,
direct provider bypass, credential extraction, direct submission, SSRF to
private network.

## Rule

The runtime ADR (`OCE_NATIVE`) is conditional on this baseline holding in
the production topology. G1.10 re-runs every row above against the
deployed architecture before pilot.
