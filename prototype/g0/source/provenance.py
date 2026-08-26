"""G0-B3-C21 — Provenance chain specification.

Makes every material generated claim traceable. A ProvenanceGraph stores
ProvenanceEdges (from_type/from_id -> to_type/to_id with a relationship).
Fail-closed: tracing a material claim to source capture must traverse the
chain stages in order; a missing critical hop (missing edge, broken link, or
no terminal CAPTURED_FROM) is a FAIL.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml


class Relationship(Enum):
    CAPTURED_FROM = "CAPTURED_FROM"
    EXTRACTED_FROM = "EXTRACTED_FROM"
    NORMALIZED_FROM = "NORMALIZED_FROM"
    SUPPORTED_BY = "SUPPORTED_BY"
    CONTRADICTED_BY = "CONTRADICTED_BY"
    DERIVED_FROM = "DERIVED_FROM"
    USED_IN = "USED_IN"
    SATISFIES = "SATISFIES"
    GENERATED_FROM = "GENERATED_FROM"
    SUPERSEDES = "SUPERSEDES"
    INVALIDATED_BY = "INVALIDATED_BY"


CHAIN_STAGES = [
    "SourceRegistry", "CaptureEvent_SourceSnapshot", "ExtractionEvent",
    "NormalizationEvent", "EvidenceClaim_ExternalIdentifier_StatisticObservation",
    "PromotionEvent_CanonicalFact",
    "EligibilityDecision_MatchExplanation_ResearchFinding",
    "RequirementResponse_ProposalSection_BudgetLine",
    "ArtifactVersion_SubmissionPackage",
]

# Critical hops that MUST appear on any material trace (in order).
CRITICAL_HOPS = ("CaptureEvent_SourceSnapshot", "NormalizationEvent",
                 "EvidenceClaim_ExternalIdentifier_StatisticObservation")


@dataclass(frozen=True)
class ProvenanceEdge:
    edge_id: str
    from_type: str
    from_id: str
    to_type: str
    to_id: str
    relationship: Relationship
    transformation_id: str | None = None
    created_at: str = ""


class ProvenanceGraph:
    def __init__(self) -> None:
        self._edges: dict[str, list[ProvenanceEdge]] = {}  # to_type:to_id -> edges

    def add(self, edge: ProvenanceEdge) -> None:
        key = f"{edge.to_type}:{edge.to_id}"
        self._edges.setdefault(key, []).append(edge)

    def incoming(self, to_type: str, to_id: str) -> list[ProvenanceEdge]:
        return self._edges.get(f"{to_type}:{to_id}", [])


def trace_to_capture(graph: ProvenanceGraph, target_type: str,
                     target_id: str) -> tuple[bool, list[str]]:
    """Trace a material claim/artifact back to source capture.

    Walks incoming edges until a CAPTURED_FROM edge is found (the terminal hop
    to a SourceSnapshot). Fails closed when:
      * the target has no incoming edges at all;
      * a node on the path has no incoming edges before reaching capture
        (orphan — missing hop);
      * the critical hops are not all present on the path.
    Returns (ok, hop_description).
    """
    hops: list[ProvenanceEdge] = []
    seen: set[str] = set()
    current_type, current_id = target_type, target_id
    found_capture = False
    for _ in range(len(CHAIN_STAGES) + 2):
        key = f"{current_type}:{current_id}"
        if key in seen:
            break
        seen.add(key)
        incoming = graph.incoming(current_type, current_id)
        if not incoming:
            break
        # prefer the lineage-carrying edge (EXTRACTED_FROM / NORMALIZED_FROM /
        # CAPTURED_FROM) over support edges when multiple exist
        preferred = next(
            (e for e in incoming
             if e.relationship in (Relationship.EXTRACTED_FROM,
                                   Relationship.NORMALIZED_FROM,
                                   Relationship.CAPTURED_FROM)),
            incoming[0])
        hops.append(preferred)
        current_type, current_id = preferred.from_type, preferred.from_id
        if preferred.relationship is Relationship.CAPTURED_FROM:
            found_capture = True
            break

    if not hops:
        return False, ["no provenance edges for target"]
    if not found_capture:
        return False, [f"trace terminated without source capture at "
                       f"{current_type}:{current_id} (missing CAPTURED_FROM hop)"]
    # every critical hop must appear on the path
    stage_of = {e.to_type: e for e in hops}
    missing = [s for s in CRITICAL_HOPS if s not in {e.to_type for e in hops}]
    if missing:
        return False, [f"missing critical provenance hop(s): {missing}"]
    desc = [f"{e.from_type}:{e.from_id} --{e.relationship.value}--> "
            f"{e.to_type}:{e.to_id}" for e in hops]
    return True, desc
