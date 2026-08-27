# G1 Wave 2 — Real Source Connectivity + Evidence

**Line:** `grant-sector-g1-production` (seeded from G0 final head)
**Status:** DEV / MOCK adapters implemented, LIVE pending network-enabled configuration
**Commit series:** `G1-W2-C1` … `G1-W2-BOOK`

## Governing Law

From Book 5 (immutable SourceSnapshots), Book 8 C29 (revision invalidation),
and the Source Adapter Law:

1. Every source **registers** — no caller-supplied arbitrary endpoints.
2. Every fetch produces an **immutable, content-hashed snapshot** — a change
   yields a NEW snapshot, never a mutation.
3. External source content is **untrusted data, never authority** — parsers
   and crawlers never outrank official solicitation truth.
4. Material term changes create a **new OpportunityRevision** (append-only)
   and **selectively invalidate** downstream stages.
5. Parser output retains **page / section / locator / snapshot lineage** —
   no OCR perfection assumptions.

## What Was Implemented

### Source adapters (`grant_platform/sources/adapters.py`)

| Adapter | Source id | Authority class | Status |
|---|---|---|---|
| Grants.gov / Simpler | `grants_gov` | OFFICIAL_SOLICITATION | DEV (fixture-backed fetch) |
| Georgia state | `georgia_state` | OFFICIAL_SOLICITATION | DEV |
| USAspending | `usaspending` | FUNDER_RECORD | DEV |
| Census / community | `census_community` | GOVERNMENT_STATISTIC | DEV |

- `SourceRegistry` denies unknown sources (`SourceError`).
- `BaseSourceAdapter.capture()` fetches → sha256-hashes → normalizes → emits
  an immutable `Snapshot` with `snapshot_id = snap-<source>-<hash[:12]>`,
  `canonical_url`, `retrieved_at`, `payload_ref` (object storage ref).
- The fetch callable is **bound at construction**: network in LIVE lanes,
  fixture callable in DEV/CI. No network in CI.

### Revision watcher (`grant_platform/sources/watcher.py`)

- `classify_change()` diffs normalized payloads against a **term catalog**:
  `MATERIAL_TERMS = (deadline, funding_ceiling, eligibility, required, attachment)`
  vs `NON_MATERIAL_TERMS = (formatting, cover_sheet_style)`.
- `build_revision_change()`: material change → new `rev-<snapshot>` id and
  selective invalidation of `eligibility / match / project / drafting /
  assurance / package`. Non-material → no revision, no invalidation.
- Old snapshot/revision is never mutated (append-only, Book 5).

### Parser lane (`grant_platform/sources/watcher.py`)

- `parse_document()` default splitter handles markdown/text with
  `{page, section, locator, text}` output; PDF/DOCX splitters are
  adapter-bound and must return the same shape (G1.3 hardening).
- `extraction_lineage` records `parser:default:<doc>` or `parser:adapter:<doc>`.

### Snapshot persistence (`grant_platform/store/db.py`)

- `create_snapshot()`, `latest_snapshot()`, `snapshots_for()` — canonical
  metadata in the Store (Postgres in prod, SQLite in dev/CI); payloads live
  in object storage.

## Tests

`tests/test_source_adapters.py` — 9 tests:

- adapters register with correct authority classes
- unknown source denied
- capture emits immutable hash-identified snapshot
- snapshot persists in store (tenant-scoped)
- material change → new revision + selective invalidation (old snapshot untouched)
- non-material change → nothing invalidated
- unknown term change → not material
- parser lane emits locator lineage
- hostile payload cannot inject material terms / authority (untrusted content)

**Seed suite at Wave 2:** 45 passed, 0 failed.

## Honest Status

- All four adapters are **DEV** (fixture-backed). LIVE wiring requires a
  network-enabled configuration with governed egress and is a G1.3/G1.5
  hardening item — the mission's "at least one real public opportunity"
  test (§32) is **BLOCKED on live network authorization** and recorded as
  such; the adapter contract, snapshots, revision watcher, and persistence
  are fully exercised against fixtures.
- `REAL_SOURCE_LIVE_FETCH` is deliberately not faked: no network calls in CI.
