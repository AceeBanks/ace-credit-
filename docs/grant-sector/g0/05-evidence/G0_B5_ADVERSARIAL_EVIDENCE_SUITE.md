# G0-B5-C24 — Adversarial Evidence Suite

## Purpose

Attack evidence integrity before Books 6/7/8 rely on it. All P0
integrity/security scenarios must pass.

## Coverage (ADV-01..ADV-40)

Machine-readable catalog: `config/g0/evidence/adversarial_evidence.yaml`
(40 scenarios; 38 P0, 2 P1), validated by
`tools/g0/validate_adversarial_evidence.py`.

The suite (`tests/g0/book5/test_adversarial_evidence.py`) attacks every
scenario against the real prototypes:

- **fabrication**: claims pointing at non-existent sources (ADV-01),
  recursive research self-citation (ADV-04), synthetic testimonials (ADV-21),
  budget numbers without lineage (ADV-22);
- **substitution**: current state into historical replay (ADV-07),
  secondary source instead of the official one (ADV-03), stale sources
  (ADV-06), humanization after QA (ADV-23);
- **leakage**: cross-tenant edges (ADV-12), cross-tenant nearest neighbors
  (ADV-11), deleted evidence via embeddings (ADV-13), restricted metadata
  (ADV-38), private eval cases (ADV-30);
- **escalation**: graph mutation creating canonical facts (ADV-09),
  self-SUPPORTS edge from malicious source (ADV-31), duplicate
  corroboration (ADV-32);
- **stale-state shortcuts**: projection lag serving stale dependencies
  (ADV-26), old eligibility after revision (ADV-16), resolved contradiction
  after amendment (ADV-36), quality composite hiding staleness (ADV-33);
- **integrity failures**: hash mismatch (ADV-27), missing engine metadata
  (ADV-34), dependency cycles (ADV-37), degraded optional components
  (ADV-24/25), explanation omitting uncertainty (ADV-40).

## Guards added for this suite

- GRAPH-004 (self-loop edges denied), GRAPH-005 (corroboration needs
  distinct content) — `models.py`;
- FIND-006 (evidence bottoms out at sources) — `research.py`;
- CLAIM-008 (statistic geography/unit must match) — `claim_ledger.py`;
- INV-008 (stale dependency results blocked until recompute) —
  `dependencies.py`;
- CONTR-004 (resolutions reopen on amendment) — `contradictions.py`;
- VIS-007 (license-restricted reuse requires approval) — `visibility.py`;
- DEC-002 enforcement (deterministic replay requires engine metadata) —
  `replay.py`.
