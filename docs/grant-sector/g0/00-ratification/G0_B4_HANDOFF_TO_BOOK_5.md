# G0 Book 4 — Handoff to Book 5

**From:** Book 4 — Dual-Hermes Protocol & Memory Constitution
**To:** Book 5 — Evidence, Decision Records & Replay
**Precondition met:** `ready_for_book5: true` (computed, see `G0_B4_REALITY_LOCK.json`)

## What Book 5 receives (all executable in `tests/g0/book4/`)

1. **Dual-Hermes boundary** — Personal (client-facing cognitive/relationship
   layer) and CEO (decomposition/orchestration) are distinct actors with a
   machine-readable capability partition; workers are bounded executors with
   L2-only authority; deny-by-default throughout (C1).
2. **The cognitive chain as contracts** — Client idea → Personal
   interpretation → `IntentContract` → CEO decomposition → `TaskPlan` /
   `TaskContract` → bounded workers → `WorkerResult` → CEO synthesis →
   `ExplanationPacket` → Personal → client. Every hop is a typed artifact with
   a schema and fail-closed tests (C2-C11).
3. **Sidechain isolation** — worker traces live behind `SidechainManifest`s
   with fail-closed secret scanning; parent context receives only bounded
   `WorkerResult`s; trace content never enters Personal context (C8-C9).
4. **Role memory constitutions** — Personal classes (preferences, goals,
   relationship continuity) and CEO classes (lean operational continuity) are
   disjoint; memory is curated, scoped, TTL-governed, supersession-driven, and
   **never canonical truth** (C12-C16).
5. **Context engineering** — mandatory-anchor compaction, factual preservation,
   authority-over-recency retrieval, cold-restart reconstruction from durable
   state (raw chat never required) (C17-C19).
6. **Co-adaptation + feedback** — factual corrections route to canonical
   mutation proposals, never silent memory rewrites; preferences supersede
   cleanly (C20-C21).
7. **D1 mock-draft contract** — the full chain applied to a Georgia-first
   mock draft: MOCK / NON-SUBMISSION label mandatory, no raw transcript, no
   submission capability, every claim traces to Book 3 evidence refs (C22).
8. **Portability & privacy** — skill boundaries per role, model/provider
   independence (identity survives swaps), scoped deletion with no duplicate
   resurrection (C23-C25).
9. **Proven P0 adversarial posture** — A1-A25 context/memory pollution
   scenarios green; 22 integration invariants + 5 property tests green (C26-C27).

## Therefore

Book 4 proves intent is preserved through the chain **without** accumulating
uncontrolled context. CEO and workers consume typed contracts and refs into
governed canonical/evidence state — which is exactly the input Book 5's
evidence lineage, decision records and replay need: every `WorkerResult`,
`OutcomeArtifact` and explanation already pins exact project +
OpportunityRevision + source/evidence refs.

## Out of Book 4 scope (deferred)

- evidence storage backend selection / relational-vs-graph bake-off (Book 5);
- production auth/secrets/credential brokerage (Book 6);
- bounded Humanizer style-transform candidate (Book 7/8 — reserved, not
  integrated; see external-component ledger).
