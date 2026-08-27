# G0-B7-C17 — Parser & Retrieval Evaluation

**Document ID:** GS-G0-B7-C17-PARSER
**Status:** RATIFIED (Book 7 chapter C17)
**Engine:** `prototype/g0/evaluation/routing_eval.py`

Book 3 parser candidates (Marker per Amendment 002, plus existing
candidates) and Book 5 retrieval strategies get empirical comparison.

## Parser lanes

Metrics: text fidelity, headings, tables/forms, OCR, page/locator lineage,
extraction errors, latency/cost, hardware needs, failure detection.

**Hard gate:** no parser wins if it cannot preserve or reconstruct enough
location metadata to support Book 5 evidence lineage for material claims
(locator lineage ≥ 0.9).

## Retrieval

Compare exact/relational/full-text/vector/graph strategies for appropriate
tasks. Do not reward semantic retrieval for tasks where exact lookup is the
correct mechanism (exact IDs, deadlines, revisions). Semantic retrieval that
improves recall while returning stale authority is a hard failure (C29-6).
