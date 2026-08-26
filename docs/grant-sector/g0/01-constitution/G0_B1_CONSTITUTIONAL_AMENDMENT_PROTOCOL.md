# G0 Book 1 — Constitutional Amendment Protocol (B1.C10)

**Status:** Ratified with the Book 1 constitution (v1.0)
**Source:** `G0_BOOK_01_MASTER_IMPLEMENTATION_PLAN_v1.0.md` §13 (B1.C10)
**Enforcement:** governance_protocol (amendment_status on every law in
`config/g0/policy/constitutional_laws.yaml`; AMENDABLE_BY_* vs FROZEN)

## Purpose

Book 1 is **stable but changeable through explicit governance**. The
constitution is the highest authority in the repository (see the authority
order recorded in `G0_B01_EXECUTION_MANIFEST.json`); any implementation or
config that conflicts with it is wrong until an amendment is ratified — never
silently superseded.

## Hard rule

> No code/config may silently supersede the constitution.
> If implementation conflicts with constitution, implementation is wrong until
> amendment is ratified.

## Amendment classes

| Class | Scope | Example | Pre-ratification evidence |
|---|---|---|---|
| **PATCH** | Wording/clarification; no semantic change | Fixing a typo in a normative statement | Review note; no behavioral tests change |
| **MINOR** | Adds a capability or law without weakening an existing invariant | Registering a new Phase 1 capability; adding a clarifying law | Capability registry + evaluator tests still pass; affected tests updated |
| **MAJOR** | Changes authority levels, human approval, tenant boundary, or canonical-truth semantics | Raising a capability minimum level; changing AP classes; altering memory-isolation law | Full Book 1 reality lock recomputed; adversarial suite re-run; all affected tests updated |

## Required amendment packet

Every amendment (PATCH/MINOR/MAJOR) must be proposed as a packet containing:

```text
Amendment ID          (e.g. AMD-B1-001)
Reason                (client/business/evidence-driven rationale)
Old law/contract      (exact prior text or registry entry)
New law/contract      (exact replacement)
Affected books/modules
Threat/risk analysis
Tests affected
Migration plan
Rollback plan
Reviewer approval     (human principal; LAW-B1-018 — agents cannot ratify
                       expansion of their own authority)
```

## Process

1. **Propose** — record the packet in the plan amendment register
   (`docs/grant-sector/G0_PLAN_AMENDMENT_REGISTER_v1.0.md` for planning
   amendments; constitutional amendments land in the Book 1 constitution
   source-of-authority map with a contradiction-ledger entry).
2. **Review** — human reviewer approval; agents may draft but never ratify
   changes to their own authority (LAW-B1-017/018).
3. **Ratify** — update `constitutional_laws.yaml` (or capability registry)
   with the new `amendment_status`/text; record the supersession in the
   contradiction ledger (Book 0 register) or a superseding amendment entry.
4. **Verify** — re-run `tests/g0/`; regenerate the Book 1 Reality Lock
   (`python tools/g0/build_book1_reality_lock.py`); the lock's freshness test
   fails if the committed lock no longer matches a regeneration.
5. **Record** — the amendment ID becomes part of the affected artifact's
   lineage (immutable revision event, LAW-B1-019).

## FROZEN laws

Laws whose `amendment_status` is `FROZEN` (LAW-B1-003/005/012/015/018/030 and
any security-critical law) may only change via a **MAJOR** amendment with the
full packet above — never via PATCH or silent drift. The validator
(`tools/g0/validate_constitution.py`) rejects unknown amendment statuses and
missing fields, so an under-specified amendment fails closed.
