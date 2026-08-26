# G0 Book 2 — Chapter C15: CommonGrants Interoperability Contract

## Decision

Provide standards compatibility while retaining richer internal semantics.
Map internal domain to CommonGrants Opportunity / Application / Award concepts.
Every mapped field receives exactly one classification:
**EXACT / EXTENSION / INTERNAL_ONLY / EXTERNAL_ONLY / LOSSY**.

Machine-readable source of truth: `config/g0/domain/common_grants_mapping.yaml`.
Executable form: `prototype/g0/domain/common_grants.py`.

## Schema-pin status (honest)

The plan requires the ACTUAL pinned CommonGrants schemas/SDK version selected
by the project — not memory of the standard. **No CommonGrants SDK is vendored
in this workspace yet**, so:

- `common_grants_schema_version: "unpinned"`, `vendor_status:
  pending_common_grants_schema_vendor`
- every mapping row carries `validation: pending_schema_vendor`
- `check_schema_version()` fails closed on any mismatch (unpinned can never
  match), so no compatibility claim can be made prematurely.

The mapping MECHANISM (round trip, classification, extension preservation,
lossy reporting, unknown-field handling) is fully executable and tested; the
field rows themselves must be re-verified against the vendored schemas before
production use (recorded as the C16+/G0.3 vendor step).

## Mapping matrix

10 columns per row: `internal_entity`, `internal_field`, `common_grants_entity`,
`common_grants_field`, `mapping_class`, `transform`, `reverse_transform`,
`loss_notes`, `validation`, `example`. Entities covered: GrantOpportunity (5
rows), ApplicationProject (5 rows), Award (5 rows) — EXACT identity mappings,
Decimal↔string transforms, declared-LOSSY status/deadline mappings, and a
`cgx_` extension row.

## Rules enforced

- **Round-trip**: EXACT mappings must survive internal → CG → internal with
  semantic equality; LOSSY loss is explicit and test-visible.
- **Extension namespace**: project-owned `cgx_` fields (evidence lineage,
  eligibility decision trace, match explanation, application workflow state,
  artifact lineage, client review, QA status, outcome-learning metadata) are
  preserved; unknown `cgx_` fields coming back in are kept; unknown non-`cgx_`
  fields are rejected (fail closed).
- **No shadow semantics**: no second internal field mirrors an external name;
  one internal field maps to at most one CG field per entity (duplicate targets
  fail the validator).
- **External IDs never replace internal identity**: external ids map into
  `CommonGrantsExtension` records; internal stable ids stay authoritative.

## Tests (12 in `test_common_grants.py`)

- Opportunity / Application / Award round trips (incl. Decimal↔string)
- extension preservation both directions
- unknown non-extension field rejected
- lossy fields explicit and visible
- schema-version mismatch fails closed (unpinned + wrong pin)
- external ID mapping without replacing internal identity
- validator: missing matrix column, duplicate CG target fail closed

Run: `python -m pytest tests/g0/book2/test_common_grants.py -q` — **12 passed**.
