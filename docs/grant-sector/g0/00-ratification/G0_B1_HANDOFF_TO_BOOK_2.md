# G0 Book 1 — Handoff to Book 2

**From:** Book 1 constitutional control plane (`G0_BOOK_01_MASTER_IMPLEMENTATION_PLAN_v1.0.md`)
**To:** Book 2 — domain entities & relationships (`G0_BOOK_02_MASTER_IMPLEMENTATION_PLAN_v1.0.md`)
**Precondition met:** `ready_for_book2: true` (computed, see `G0_B1_REALITY_LOCK.json`)

## Binding constraints Book 2 must implement

1. **Canonical truth is outside agent memory** (LAW-B1-001): entity identities
   and facts must be provider-independent and replayable; agent memory is never
   authoritative system state.
2. **Typed capability/policy engine** (DEC-GOV-001, B1.C11): authorization
   evaluates actor + tenant + project + capability + resource + authority +
   risk; missing information ⇒ DENY. Book 2's operations are routed through
   the executable policy prototype and its policy-as-data registers.
3. **Entity identities are provider-independent** (LAW-B1-022): external
   provider IDs (funders, portals, CMC/RSS source IDs) are references, never
   internal primary sovereignty.
4. **All external facts need lineage** (LAW-B1-007/019/020): every fact carries
   source lineage; material source changes invalidate dependents; revisions are
   immutable lineage events.
5. **Submission prohibition is structural** (CD-003, B1.C5): the capability
   layer dominates tool availability; `application.submit` and the
   `submission.*` family remain DISABLED/APX in Phase 1. Book 2 must not add
   any path that makes submission reachable.
6. **Drafting is allowed at L2** (LAW-B1-013): application drafts
   (proposal/business plan/pitch deck/goal sheets/sections) are legal at L2 for
   CEO Hermes; submission-ready packaging requires human approval (AP2).
7. **Tenant scope is mandatory** (LAW-B1-015): every tenant-scoped entity and
   audit event carries a tenant; cross-tenant access is blocked by the scope
   model (`can_view_audit`).
8. **Deterministic rules remain deterministic** (LAW-B1-006): eligibility,
   budget reconciliation and numeric QA are deterministic services outside the
   LLM; the LLM never computes them.
9. **Georgia is the first state-source proof priority** (B1.C13, Amendment
   001): fixtures/adapters prefer Georgia; the product model stays
   jurisdiction-agnostic.
10. **Proposal and business plan are distinct artifacts** (LAW-B1-025).
11. **Dynamic grant alignment is mandatory** (LAW-B1-026): deliverables must
    map to the specific solicitation's requirements.
12. **Client-visible research is required** (LAW-B1-024): research and match
    explanations are a product obligation, not an internal detail.

## What Book 2 answers

Book 1 settled **who is authorized to act** (actors, authority ladder,
capability registry, approval classes, failure semantics, audit contract).
Book 2 defines **what the entities and relationships are** — the canonical
domain model (organization, opportunity, eligibility rule set, evidence/claim,
application project, blueprint, artifact, audit event), their identifiers,
lifecycle states and provenance chains — without re-opening any authority
decision above.

## Provisional downstream artifacts

Book 1 treats the following as assumed by Book 2 (per the execution manifest's
authority order; any conflict must be recorded in the contradiction ledger or
an amendment proposal):

- Canonical storage (Postgres) is authoritative; Redis is transport/cache only.
- Workers are bounded/disposable and return short result packets; full traces
  live in sidechains/audit storage.
- CommonGrants compatibility is a design principle (LAW-B1-021), never a
  surrender of internal semantics.
