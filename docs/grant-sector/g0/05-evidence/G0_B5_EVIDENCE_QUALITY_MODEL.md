# G0 Book 5 — Evidence Quality Model

**Chapter:** B5.C4 · **Config:** `config/g0/evidence/evidence_quality_dimensions.yaml`

## Dimensions (all inspectable)

authority · directness · freshness · specificity · corroboration ·
extraction_quality · identity_certainty · temporal_fit

A composite score may rank results but never erases component values
(EVID-LAW-014). Class derivation is deterministic:

- **VERIFIED_HIGH** — high authority + direct + fresh + specific + corroborated;
- **VERIFIED_MODERATE** — verified but with a moderate dimension;
- **PROVISIONAL** — plausible, not yet verified;
- **CONFLICTED** — contradicted by equal-or-higher authority;
- **STALE** — fails freshness for its claim class;
- **UNSUPPORTED** — no support set.

## Hard rules

- QUAL-001 — high authority + stale is never silently high confidence;
- QUAL-002 — low extraction quality stays visible;
- QUAL-003 — conflicting authoritative evidence cannot be averaged away;
- QUAL-004 — composite score is reproducible.

## Tests

`tests/g0/book5/test_evidence_quality.py` — 7 tests incl. QUAL-001/003 and
validator fail-closed behavior.
