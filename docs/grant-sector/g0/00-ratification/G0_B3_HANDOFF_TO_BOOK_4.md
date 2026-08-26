# G0 Book 3 — Handoff to Book 4

**From:** Book 3 — source governance / provenance (`G0_BOOK_03_MASTER_IMPLEMENTATION_PLAN_v1.0.md`)
**To:** Book 4 — Dual-Hermes Protocol & Memory Constitution
**Precondition met:** `ready_for_book4: true` (computed, see `G0_B3_REALITY_LOCK.json`)

## What Book 4 receives (all executable in `tests/g0/book3/`)

1. **Registered source identities** — `SourceRegistry` with classes/authority
   tiers; every ENABLED source is governed (adapter version + policy refs);
   unregistered discovery is never promotion (C2-C3).
2. **Snapshot/provenance semantics** — immutable `SourceSnapshot`s with
   content-addressed raw storage, capture events, replay classes, and
   versioned extraction/normalization lineage (C4-C7).
3. **Fact/claim/statistic states** — promotion states (CANDIDATE → VERIFIED /
   REJECTED / CONFLICTED / STALE / SUPERSEDED), conflict states with
   resolution methods, and `StatisticObservation` geography/population/
   time/vintage semantics (C10-C11, C15).
4. **Conflict/freshness states** — equal-authority conflicts block critical
   use; freshness is fact-class × source-class semantic (deadline vs annual
   vintage vs historical-fixed), hard-stale blocks readiness (C8-C9).
5. **Exact domain object identities/revisions** — dependency invalidation
   stales exactly the affected decisions/artifacts on P0 changes; external
   identifiers carry namespaced verification state (C13-C14).
6. **D0 DraftContextBundle / Data Packet** — the D0 source-governed packet
   reconstructs deterministically without agent memory; requirement coverage
   is measurable; every output is MOCK / NON-SUBMISSION /
   NOT_CLIENT_APPROVED_FINAL (C23-C24).
7. **Source security envelope** — hostile source content is inert data,
   quarantinable, and never grants capabilities (C19).
8. **Audit/provenance expectations** — end-to-end provenance chains trace any
   material claim to source capture or fail loudly; retention/deletion
   semantics propagate to replay/evidence status (C20-C21).

## Therefore

Hermes does **not** need to "remember" where facts came from. Book 4's memory
protocol receives references into governed canonical/evidence state, plus the
D0 packet as the first grounded, non-submission draft harness input.

## D0 is unlocked

Per plan §36, the first **Shadow Draft** may execute immediately after Book 3
ratification: choose one real Georgia opportunity, capture/register the exact
source revision, build the approved client-profile fixture, normalize
eligibility + requirements, gather 2-5 strong funder/winner/community evidence
sources, build the typed D0 Data Packet, generate the blueprint and draft
sections, run factuality/citation/coverage QA, and produce the Mock Proposal +
Research Pack + QA Report. D0 remains an evaluation artifact, never
submission-ready.

## Out of Book 3 scope (deferred)

- Hermes memory protocol / dual-Hermes intent routing (Book 4);
- final evidence storage backend selection (Book 5);
- production auth/secrets system (Book 6);
- productionized crawler/parser engines (Book 9) — adapters stay replaceable
  behind the frozen contracts.
