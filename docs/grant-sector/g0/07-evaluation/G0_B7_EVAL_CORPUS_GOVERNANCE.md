# G0-B7-C4 — Eval Corpus Governance

**Document ID:** GS-G0-B7-C4-CORPUS
**Status:** RATIFIED (Book 7 chapter C4)
**Schema:** `schemas/g0/evaluation/eval_corpus_version.schema.json`
**Prototype:** `prototype/g0/evaluation/corpus.py::CorpusRegistry`

## Corpus classes

- GOLDEN_PUBLIC
- GOLDEN_SYNTHETIC
- GOLDEN_HUMAN_REVIEWED
- TENANT_PRIVATE_APPROVED
- ADVERSARIAL
- REGRESSION
- SHADOW_PRODUCTION
- HOLDOUT

## Rules (CORPUS-001..010)

1. **CORPUS-001 — versions immutable.** A corpus version cannot be modified
   after creation; `assert_unchanged` recomputes and compares the hash.
2. **CORPUS-002 — additions create a new version.** `next_version` chains a
   new version with a parent reference; the old version is untouched.
3. **CORPUS-003 — train/dev/eval/holdout separation.** Where learning occurs,
   splits are explicit; a HOLDOUT case cannot enter a development/eval corpus.
4. **CORPUS-004 — model-generated labels marked.** MODEL_GENERATED labels
   cannot be presented as human gold.
5. **CORPUS-005 — tenant-private never global by default.** TENANT_PRIVATE
   cases require governance approval and cannot enter GOLDEN_PUBLIC.
6. **CORPUS-006 — duplicates/near-duplicates tracked.** Duplicate reports
   name exact and near (overlap ≥ 0.9) duplicates per version.
7. **CORPUS-007 — contamination/leakage analysis.** Holdout overlap across
   versions is reported as contamination findings.
8. **CORPUS-008 — historical context retained.** Cases keep source and
   effective-date context.
9. **CORPUS-009 — benchmark composition report required.** Every version has
   a composition report: counts by case type, label origin, privacy class,
   duplicates and contamination.
10. **CORPUS-010 — export audit.** Exports record exactly which case ids are
    allowed into generalized eval/training; unauthorized tenant-private cases
    are excluded and listed.
