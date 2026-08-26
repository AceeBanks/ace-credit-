# G0 Book 5 — Retrieval Constitution

**Chapter:** B5.C10 · **Config:** `config/g0/evidence/retrieval_policies.yaml`

## Lanes (most deterministic first)

1. EXACT_STRUCTURED_LOOKUP — IDs, canonical facts, current revision, requirements, decisions;
2. FILTERED_RELATIONAL — scoped entity/project/evidence queries;
3. GRAPH_TRAVERSAL — lineage, dependencies, contradiction neighborhoods;
4. FULL_TEXT — source/artifact text;
5. VECTOR_SEMANTIC — discovery/similarity, never authority.

**RETR-001** — use the most deterministic lane that can answer the question;
never vector-search an EIN, deadline or canonical amount when exact lookup
exists.

## Authority rules

- RETR-002 — retrieval rank is not authority; a top-ranked semantic result
  may be excluded from operational use if evidence policy rejects it;
- RETR-003 — a vector result can never override a canonical fact;
- RETR-004 — stale/conflicted evidence is flagged in results;
- RETR-005 — tenant filters apply before exposure.

## Tests

`tests/g0/book5/test_retrieval_authority.py` — 6 tests.
