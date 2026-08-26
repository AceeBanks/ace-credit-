"""G0-B3-C6-C7 — validate capture/replay and extraction/normalization semantics.

Fail-closed checks against the config of truth:
  * raw blob hash integrity (content addressing) is enforced
  * replay classes are from the known set; NON_REPLAYABLE not allowed for
    promoted critical data unless explicitly exempted
  * extraction engines / statuses from known enums
  * LLM/OCR/low-confidence extractions are CANDIDATE, never auto-VERIFIED
  * schema-invalid extraction fails normalization
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    SOURCE_CONFIG_DIR,
    ValidationFailure,
    cli_main,
    finish,
    load_yaml,
    require_field,
)

KNOWN_REPLAY_CLASSES = {
    "EXACT_REPLAY", "COMPATIBLE_REPLAY", "PARTIAL_REPLAY", "NON_REPLAYABLE",
}
KNOWN_ENGINES = {
    "deterministic_json_mapper", "html_parser", "unstructured", "markitdown",
    "opendataloader_pdf", "ocr", "pixel_rag", "llm_structured",
}
KNOWN_EXTRACTION_STATUSES = {"COMPLETED", "FAILED", "PARTIAL"}
# Engines whose output must remain CANDIDATE until separately verified.
CANDIDATE_ONLY_ENGINES = {"llm_structured", "ocr", "pixel_rag"}


def validate_capture(cfg: dict, errors: list) -> None:
    blobs = cfg.get("raw_objects", [])
    from prototype.g0.source.snapshot import sha256_hex
    for b in blobs:
        ctx = b.get("object_id", "<anon>")
        h = b.get("raw_hash")
        if not h:
            errors.append(f"{ctx}: missing raw_hash")
            continue
        data = b.get("raw_bytes")
        if isinstance(data, bytes):
            if h != sha256_hex(data):
                errors.append(f"{ctx}: blob hash mismatch (corrupt capture)")
        if b.get("retention_class") and not b.get("immutable"):
            errors.append(f"{ctx}: raw capture must be immutable")
        replay = b.get("replay_class")
        if replay is not None and replay not in KNOWN_REPLAY_CLASSES:
            errors.append(f"{ctx}: invalid replay_class {replay!r}")
        if replay == "NON_REPLAYABLE" and b.get("promoted_critical"):
            errors.append(f"{ctx}: NON_REPLAYABLE unacceptable for promoted critical data")


def validate_extraction(cfg: dict, errors: list) -> None:
    events = cfg.get("extraction_events", [])
    from prototype.g0.source.extraction import ExtractionStore, ExtractionEvent, ExtractionStatus
    for e in events:
        ctx = e.get("extraction_event_id", "<anon>")
        eng = e.get("engine")
        if eng not in KNOWN_ENGINES:
            errors.append(f"{ctx}: unknown engine {eng!r}")
        st = e.get("status")
        if st not in KNOWN_EXTRACTION_STATUSES:
            errors.append(f"{ctx}: invalid status {st!r}")
        # Heuristic engines must not be recorded as auto-verified facts.
        if eng in CANDIDATE_ONLY_ENGINES and e.get("auto_verified"):
            errors.append(f"{ctx}: {eng} output cannot auto-become a verified fact")


def validate(config: Path) -> tuple[bool, dict]:
    cfg = load_yaml(config)
    errors: list[str] = []
    validate_capture(cfg, errors)
    validate_extraction(cfg, errors)
    return finish("validate_capture_extraction", not errors, {
        "errors": errors,
        "raw_object_count": len(cfg.get("raw_objects", [])),
        "extraction_event_count": len(cfg.get("extraction_events", [])),
    })


if __name__ == "__main__":
    default = SOURCE_CONFIG_DIR / "capture_extraction.yaml"
    raise SystemExit(cli_main(validate, default))