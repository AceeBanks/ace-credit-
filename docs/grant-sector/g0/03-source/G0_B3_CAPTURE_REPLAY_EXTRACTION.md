# G0-B3 — Capture, Replay & Extraction/Normalization Lineage (C6-C7)

## Scope

Defines the **capture, replay and content-addressed storage protocol** (B3.C6) and the **extraction & normalization event model** (B3.C7). Together they make external data reproducible and economically storable, and rigorously separate *what the source contained* from *what our software inferred or normalized*.

## C6 — Capture, Replay & Content-Addressed Storage

Config of truth: `config/g0/source/capture_extraction.yaml` · Prototype: `prototype/g0/source/capture.py`

### Capture pipeline

```
SourceRequest → HTTP/API/Browser Fetch → CaptureEvent → Raw Blob Hash →
Object Store → SourceSnapshot Metadata
```

`ContentAddressedStore` keys raw objects by a deterministic content hash (`sha256`), so identical bytes share one address while every retrieval keeps its own event. It enforces integrity on read (corrupt blobs are detected and fail) and carries `encryption_at_rest`, tenant/security metadata, `retention_class`, and immutable references. Technology choice (object store vendor) is deferred to G1/Book 9; the contract is frozen now.

### Replay classes

| class | meaning |
|---|---|
| `EXACT_REPLAY` | same code/version available |
| `COMPATIBLE_REPLAY` | newer compatible parser against raw capture |
| `PARTIAL_REPLAY` | raw exists but exact transformation unavailable |
| `NON_REPLAYABLE` | unacceptable for promoted critical data unless exempted |

Given a `SourceSnapshot`, the raw object, and the adapter/parser version identity, `reproduce()` reproduces normalized extraction or explicitly reports why the historical implementation is unavailable — fail-closed on any mismatch.

## C7 — Extraction & Normalization Event Model

Config of truth: `config/g0/source/capture_extraction.yaml` · Prototype: `prototype/g0/source/extraction.py`

### ExtractionEvent

Carries `extraction_event_id`, `snapshot_id`, `engine`, `engine_version`, `strategy`, timing, `quality_metrics`, `output_artifact_ref`, `status`, `errors`. Engines include deterministic JSON mapper, HTML parser, Unstructured, MarkItDown, OpenDataLoader PDF, OCR, PixelRAG, and LLM structured extraction.

### NormalizationEvent

Links a normalization to its extraction (`normalization_event_id`, `extraction_event_id`, `normalizer_name`/`version`, `target_schema`, `source_fields`, `output_entity_or_claim_refs`, `confidence_components`, `validation_status`).

### Hard rule

**LLM extraction output is a candidate structured representation, not an automatic CanonicalFact.** Outputs of candidate-only engines (`llm_structured`, `ocr`, `pixel_rag`) are CANDIDATE until separately verified; a low-confidence extraction (`overall_confidence < 0.7`) can never become a VERIFIED fact; schema-invalid extraction fails normalization.

## Tests

`tests/g0/book3/test_capture_extraction.py` — 15 tests covering:
- content-addressed store dedups bytes; corrupt blob fails hash verification;
- capture→replay fixture equality; parser upgrade replays old raw without refetching;
- missing/corrupt raw blocked (NON_REPLAYABLE);
- historical snapshot stays replayable under retention even if source disappears;
- NON_REPLAYABLE rejected for promoted critical data;
- same raw snapshot supports multiple extraction strategies without overwriting prior outputs;
- parser version lineage preserved; low-confidence output cannot become VERIFIED;
- candidate-only engines cannot auto-verify.

## Validation

- Validator CLI: `python tools/g0/validate_capture_extraction.py` → **PASS**
- Book 3 suite: 50 passed (35 prior + 15 new)

## Commits

- `G0-B3-C6-C7` chapter band.

## Status

PASS — capture/replay reproducibility and extraction/normalization lineage are fail-closed and under test.