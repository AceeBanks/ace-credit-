# G0 Book 1 — Product Constitution v1.0

**Book:** G0-B1 (Product Constitution & Authority)
**Status:** RATIFIED_CANDIDATE — implementation agent does NOT self-ratify; external review pending.
**Machine-readable law catalog:** `config/g0/policy/constitutional_laws.yaml`
**Authority order:** ratified constitution > Book master plans > global G0 plan > R0 findings.

## Preamble

This constitution governs the **Grant Intelligence + Application Production
System**: a governed platform that researches grant opportunities, produces
evidence-grounded application documents, and prepares submission-ready output
for human decision — within a broader future Financial Literacy Framework.

The product is NOT:

- a grant-writing chatbot;
- a search engine;
- a generic autonomous agent;
- a workflow automation shell;
- a document generator.

Hermes (Personal and CEO) is the **operator** of this constitution, never its
author, and never the product's source of truth. Canonical truth lives outside
agent memory (LAW-B1-001).

## Mission Clause (Phase 1)

Preserve the client-defined Phase 1 chain:

```text
INTAKE → RESEARCH & MATCHING → DOCUMENT GENERATION → QUALITY / HUMANIZATION → SUBMISSION-READY OUTPUT
```

Target throughput: enough relevant opportunities to support **1–10 qualified
applications per day**, across federal/state/foundation/corporate and
restricted/unrestricted categories.

Research, matching, and document generation are **explicitly permitted**
Phase 1 capabilities (LAW-B1-013). The architecture must not delay core client
value — writing grants — until the submission system exists.

## Scope Clause: Phase boundary table

| Area | Phase | Status |
|---|---|---|
| Intake, research & matching | Phase 1 | IN SCOPE |
| Document generation (proposal, business plan, pitch deck, budget, goal sheets) | Phase 1 | IN SCOPE |
| Quality / humanization passes | Phase 1 | IN SCOPE |
| Submission-READY package preparation | Phase 1 | IN SCOPE |
| Automated SUBMISSION / certify / sign | Out of Phase 1 | PROHIBITED until explicitly ratified (APX/L5 disabled) |
| Outreach / prework | Phase 2+ | Extension point only |
| Grant tracking, award/rejection feedback | Phase 2+ | Extension point only |
| Other financial-literacy sectors | Phase 2+ | Extension point only |

The critical distinction frozen here:

```text
PREPARE A SUBMISSION PACKAGE = allowed bounded work (L2)
SUBMIT / CERTIFY / SIGN       = high-consequence future authority (L5, disabled)
```

## Platform planes (frozen)

1. **Relationship Plane** — client-facing continuity (Personal Hermes).
2. **Control Plane** — authority, policy, approval, audit.
3. **Work Plane** — bounded task execution (CEO Hermes + workers).
4. **Data/Evidence Plane** — canonical state, evidence lineage, artifacts.

## Extension principle

Nothing in Phase 1 may prevent later outreach/prework, tracking,
award/rejection feedback, or future financial-literacy sectors. All extensions
enter through the same capability/audit/identity/approval model
(LAW-B1-030); extension can never weaken existing authority controls.

## Amendment rule

No code/config may silently supersede this constitution. If implementation
conflicts with it, the implementation is wrong until an amendment is ratified
(`G0_B1_CONSTITUTIONAL_AMENDMENT_PROTOCOL.md`).

## What this document is not

It does not define entities/relationships (Book 2), source contracts (Book 3),
or memory protocols (Book 4). It defines WHO MAY DO WHAT under which authority,
and proves it with executable policy (`prototype/g0/policy/`).
