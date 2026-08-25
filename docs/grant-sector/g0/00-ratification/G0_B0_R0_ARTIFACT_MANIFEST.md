# G0 Book 0 — B0.C1 R0/G0 Artifact Manifest

**Chapter:** B0.C1 — R0 Artifact Manifest
**Status:** IMPLEMENTED
**Machine-readable source of truth:** `config/g0/ratification/artifact_manifest.yaml`
**Validator:** `tools/g0/validate_artifact_manifest.py`

## WHAT

Canonical inventory of all 23 pre-ratification R0/G0 planning artifacts on
branch `grant-sector-r0-salvage`. Each entry records artifact ID, path,
content-pinning git blob SHA, declared version, artifact type, authority
class, status, observation date, and supersession relationships.

## WHY

Book 1+ must be able to cite R0 evidence without re-interpreting which
documents are authoritative, current, or superseded. Content-hash pinning
converts "the docs say" into a checkable claim: any later edit to a pinned
artifact is detected as authority drift.

## AUTHORITY

Per the campaign authority order and the Book 0 master prompt (§4 B0.C1).
Authority classes distinguish binding candidates from evidence classes:

- `binding_candidate` — governs execution now; subject to ratification.
- `architecture_evidence` — architecture-bearing findings.
- `research_evidence` — research/external-review inputs.
- `reject_ledger` — anti-pattern prohibitions.
- `amendment` — active planning amendments.
- `provisional_downstream_draft` — future-book material not yet ratified.

## INPUTS

Every `*.md` planning artifact under `docs/grant-sector/` at starting SHA
`0cdd8b0e70b68eec4599e2cef7c20ba0f9e89454`. No grant-sector artifact was
edited to produce this manifest (lineage preservation rule).

## OUTPUTS

- `config/g0/ratification/artifact_manifest.yaml` (23 artifacts)
- this document

## INVARIANTS

1. All artifact IDs unique; all paths unique.
2. Every artifact has version, status, authority class, observation date.
3. Every referenced path exists in the repository.
4. Recorded blob SHA equals current file content hash (no drift).
5. Supersession chains are acyclic and reference known IDs only.
6. Unknown authority class or status → validation failure.

## FAILURE MODE

Validator exits non-zero on any violation. A later edit to any pinned
artifact fails the manifest validator until a supersession record updates
the manifest.

## TEST

`tests/g0/book0/test_artifact_manifest.py` — structural pass on the live
manifest plus negative fixtures (duplicate ID, missing file, content drift,
supersession cycle, unknown authority class).

## HANDOFF

The decision register (B0.C2) cites these artifact IDs as its source
lineage; every decision must resolve to entries in this manifest.
