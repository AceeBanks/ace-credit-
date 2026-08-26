# G0 Book 2 — Chapter C8: Versioning, Revision & Temporal Semantics

## Decision

**Stable root + immutable revision.** Entities keep a stable root identity while
material terms evolve through immutable revisions. A revision never mutates a
prior revision; adding a revision yields a new revision chain. This makes
historical reconstruction possible without versioning everything
indiscriminately.

Machine-readable source of truth: `config/g0/domain/revision_policy.yaml`.
Executable form: `prototype/g0/domain/revisions.py`.

## Shapes

```
GrantOpportunity         ApplicationProject          Artifact (logical doc)
 └─ Revision 1           └─ Revision 1              └─ ArtifactVersion 1
 └─ Revision 2           └─ Revision 2              └─ ArtifactVersion 2
 └─ Revision 3           └─ Revision N              └─ ArtifactVersion N
```

- `Revision` is immutable: `revision_id`, `revision_number`, `changed_terms`,
  `created_at`, and a `material` flag classified once at creation from the
  policy catalog.
- `RevisionSet` binds a root id to an append-only chain; `add()` returns a new
  set, never mutating the old one.
- `DecisionAnchor` records the EXACT revision against which an eligibility
  decision, match score, requirement normalization or draft was produced.

## Temporal fields (semantic meaning — Book 3 defines freshness policy)

| Field | Meaning |
|---|---|
| `observed_at` | When the fact/observation was made in the world |
| `retrieved_at` | When data was captured from a source |
| `effective_from` / `effective_to` | Interval during which a value holds |
| `created_at` | When the record was created |
| `superseded_at` | When a revision was superseded by a material successor |

## Materiality

A change is MATERIAL (invalidates dependent decisions) if it touches any term in
the material catalog, at minimum: **deadline, eligibility, funding
amount/ceiling/floor, match requirement, geography, required attachment,
required narrative/question, submission method, cancellation, scoring /
evaluation criteria.** Non-material changes (formatting, wording) never
invalidate dependent decisions.

## Dependency invalidation

```
is_stale(anchor, revision_set) = any material revision after anchor.revision_id
```

An `ApplicationProject` records the exact `OpportunityRevision` against which
eligibility was evaluated, match score computed, requirements normalized and
drafts generated. When a material successor revision arrives, those dependent
decisions become STALE until re-evaluated; non-material successors do not.

## Tests (15 in `test_revision_semantics.py`)

- reconstruct application against revision N
- new revision does not mutate old decision
- material amendment marks dependent state stale
- non-material formatting change need not invalidate eligibility
- cancellation is material
- artifact version lineage remains intact (monotonic, contiguous, single root);
  gaps and cross-root chains fail closed
- revision-policy validator: unknown root rule, unknown temporal field,
  duplicate material category, empty affected terms all fail closed

Run: `python -m pytest tests/g0/book2/test_revision_semantics.py -q`
Result: **15 passed**.
