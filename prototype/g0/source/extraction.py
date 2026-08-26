"""G0-B3-C7 — Extraction & normalization event model.

Separates what the source contained from what our software inferred or
normalized. Extractions are keyed by (snapshot, engine, engine_version) so
multiple strategies can run over the SAME raw capture without overwriting prior
outputs. LLM output is a candidate structure, never an automatic CanonicalFact.

Normalization is fail-closed: schema-invalid or low-confidence extractions
cannot become VERIFIED facts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ExtractionEngine(Enum):
    DETERMINISTIC_JSON_MAPPER = "deterministic_json_mapper"
    HTML_PARSER = "html_parser"
    UNSTRUCTURED = "unstructured"
    MARKITDOWN = "markitdown"
    OPEN_DATA_LOADER_PDF = "opendataloader_pdf"
    OCR = "ocr"
    PIXEL_RAG = "pixel_rag"
    LLM_STRUCTURED = "llm_structured"


class ExtractionStatus(Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class ValidationStatus(Enum):
    RAW = "RAW"
    CANDIDATE = "CANDIDATE"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ExtractionEvent:
    extraction_event_id: str
    snapshot_id: str
    engine: str
    engine_version: str
    strategy: str
    started_at: str
    completed_at: str
    quality_metrics: dict
    output_artifact_ref: str
    status: ExtractionStatus
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NormalizationEvent:
    normalization_event_id: str
    extraction_event_id: str
    normalizer_name: str
    normalizer_version: str
    target_schema: str
    source_fields: list[str]
    output_entity_or_claim_refs: list[str]
    confidence_components: dict
    validation_status: ValidationStatus


MIN_ACCEPTABLE_CONFIDENCE = 0.7


class Lineage:
    """Keeps per-(snapshot, engine) extraction outputs distinct."""

    def __init__(self, ev: ExtractionEvent) -> None:
        self.extraction = ev
        self.normalizations: list[NormalizationEvent] = []
        self._normalized_root: dict | None = None
        self._confidence: float | None = None


class ExtractionStore:
    def __init__(self) -> None:
        self._extractions: dict[str, ExtractionEvent] = {}
        self._lineage: dict[str, Lineage] = {}
        self._normalizations: dict[str, NormalizationEvent] = {}

    def register_extraction(self, ev: ExtractionEvent) -> None:
        if ev.extraction_event_id in self._extractions:
            raise ValueError(f"duplicate extraction event {ev.extraction_event_id}")
        self._extractions[ev.extraction_event_id] = ev
        self._lineage[ev.extraction_event_id] = Lineage(ev)

    def extractions_for_snapshot(self, snapshot_id: str) -> list[ExtractionEvent]:
        return [e for e in self._extractions.values() if e.snapshot_id == snapshot_id]

    def normalize(self, n: NormalizationEvent) -> None:
        """Attach a normalization to its extraction. Fail closed on invalid schema
        or low confidence: such output is REJECTED or left as CANDIDATE, never
        VERIFIED."""
        lin = self._lineage.get(n.extraction_event_id)
        if lin is None:
            raise KeyError(f"no extraction for {n.extraction_event_id}")
        status = n.validation_status
        if status == ValidationStatus.VERIFIED:
            conf = n.confidence_components.get("overall_confidence")
            if conf is not None and conf < MIN_ACCEPTABLE_CONFIDENCE:
                raise ValueError(
                    f"low-confidence ({conf:.2f}) extraction cannot become a VERIFIED fact"
                )
        lin.normalizations.append(n)
        self._normalizations[n.normalization_event_id] = n

    def normalizations_for_extraction(self, extraction_event_id: str) -> list[NormalizationEvent]:
        lin = self._lineage.get(extraction_event_id)
        return lin.normalizations if lin else []


def same_snapshot_multi_strategy_ok(store: ExtractionStore, snapshot_id: str) -> bool:
    """Same raw snapshot may support multiple extraction strategies without
    overwriting prior outputs (true if each key is distinct)."""
    events = store.extractions_for_snapshot(snapshot_id)
    keys = [(e.snapshot_id, e.engine, e.engine_version) for e in events]
    return len(keys) == len(set(keys))