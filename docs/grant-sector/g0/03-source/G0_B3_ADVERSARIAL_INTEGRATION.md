# G0-B3 — Adversarial Data Suite & Integration/Replay/Property Tests (C25-C26)

## Scope

Attacks the source-data constitution with the plan's 25 adversarial scenarios (B3.C25) and proves the 22 mandatory integration invariants plus six deterministic property tests (B3.C26).

## C25 — Adversarial Data Test Suite (A1-A25)

Config of truth: `config/g0/source/adversarial_data.yaml` · Prototype guards: `prototype/g0/source/adversarial_guards.py` · Tests: `tests/g0/book3/test_adversarial_data.py`

All 25 scenarios from the plan are encoded as executable, fail-closed tests:

- **Authority & precedence** — A1 stale cached deadline loses to the current official amendment (old value stays lineage as SUPERSEDED); A2 equal-authority conflict → CONFLICTED and critical use blocked; A22 old/archived private page never outranks the current issuer page.
- **Evidence integrity** — A3 search snippets cannot promote a claim; A4 model-cited fake sources are rejected; A6 parser table corruption (250,000 → 25,000) prevents verified promotion; A17 a normalized fact with no raw snapshot is NON_REPLAYABLE.
- **Hostile content** — A5 web prompt injection is inert and policy-unaffected; A12 redirects to ungoverned domains blocked; A19 malicious uploaded docs/executables quarantined; A16 an adapter can never self-promote (the promotion service governs state).
- **Semantics** — A8 USER_ASSERTED EIN never outranks a VERIFIED_OFFICIAL one (identity review); A9 county/city statistic mismatch blocked; A10 old census vintage stale; A20 amount units mismatch caught; A21 timezone-ambiguous dates are UNRESOLVED, never silently midnight.
- **Change & lifecycle** — A14 a material amendment after a D0 draft stales the packet/draft; A15 nonmaterial formatting changes invalidate nothing; A13 duplicate same-content retrieval dedupes bytes while preserving retrieval timing; A25 retention deletion demotes downstream evidence; A11 deleted webpages stay replayable under retention; A18 cross-tenant source uploads rejected; A23 award→opportunity linkage requires proof (never fabricated); A24 descriptive cohort analysis allowed, unsupported causal inference blocked.

## C26 — Integration, Replay & Property Tests

Tests: `tests/g0/book3/test_integration_property.py`

The 22 mandatory invariants are each proven executable, including: every enabled source exists in the registry; every material fact traces to a snapshot; snapshots are immutable; parsing is versioned separately from capture; promotion policy is independent of the extraction engine; precedence is fact-class-specific; freshness is semantic not generic age; equal-authority critical conflicts block; P0 changes invalidate dependents; statistics preserve geography/population/time/vintage; web content has no policy authority; health failure can never fake freshness; retention/deletion propagates; Georgia/federal sources normalize into Book 2; D0 packets reconstruct without agent memory.

Six property tests confirm determinism/idempotency: raw-content hashing, the precedence resolver, the freshness resolver, dependency invalidation, the provenance graph (no orphan material facts), and replay preserving source identities.

## Validation

- `python tools/g0/validate_adversarial.py` → **PASS** (catalog of 25 scenarios, 22 invariants, 6 property tests)

## Commits

- `G0-B3-C25-C26` chapter band.

## Status

PASS — the source-data constitution survives its adversarial suite and every integration invariant holds against live repository evidence.
