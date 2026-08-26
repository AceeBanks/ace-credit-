# G0 Book 2 — Chapter C16: Extension Namespace & Sector Portability

## Decision

Keep the grant ontology precise while preventing it from becoming a dead end
for later Financial Literacy Framework sectors.

Machine-readable source of truth: `config/g0/domain/extension_namespace.yaml`.
Executable form: `prototype/g0/domain/extensions.py`.

## Rules (all enforced)

1. **Grant-specific concepts stay in the grant namespace** — GrantOpportunity,
   OpportunityRevision, EligibilityRule/Set/Decision, ApplicationProject,
   Requirement, Award, etc.
2. **Cross-sector primitives move to platform namespace only through an
   explicit ADR** (`platform_move_rule: explicit_adr_required`) — candidates:
   Organization, Person, Artifact, EvidenceClaim, CanonicalFact,
   StatisticObservation.
3. **No premature generalization** — GrantOpportunity is never renamed into a
   meaningless `OpportunityObject` (`premature_generalization_prohibited`).
4. **Provider-specific fields live in namespaced extensions**, never
   root-schema pollution. Provider prefixes: `ga_` (Georgia), `fed_` (federal),
   `cgx_` (CommonGrants).

## Portability

Registering a future state/private grant provider must not change core identity
semantics: `register_provider` compares the core identity-prefix scheme before
and after; any mutation fails closed. Unknown providers are rejected.

## Tests (8 in `test_extension_portability.py`)

- grant concepts stay in grant namespace
- no premature generalization
- cross-sector primitives move only via explicit ADR
- provider prefixes are namespaced (root pollution rejected)
- adding a provider does not change core identity semantics (mutated scheme fails)
- identity prefix scheme has stable roots
- unknown provider fails closed
- validator: missing grant concept, unprefixed provider, premature
  generalization all fail closed

Run: `python -m pytest tests/g0/book2/test_extension_portability.py -q` — **8 passed**.
