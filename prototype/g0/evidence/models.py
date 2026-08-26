"""B5.C2-C3 — Core evidence models (prototype).

ProvenanceRef: one common reference vocabulary for tracing data and outputs.
EvidenceGraph: typed edges between refs with endpoint compatibility enforced
by config; edges can never create facts that do not exist in the governed
layer, cross-tenant edges are denied, and tombstones do not orphan history.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class EvidenceGraphError(ValueError):
    """Raised when a graph operation violates the evidence laws."""


@dataclass
class ProvenanceRef:
    ref_id: str
    ref_type: str
    entity_type: str
    entity_id: str
    tenant_id: str
    content_hash: str
    version_or_revision_id: str | None = None
    observed_at: str | None = None
    effective_at: str | None = None
    locator: dict | None = None
    tombstoned: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref_id": self.ref_id, "ref_type": self.ref_type,
            "entity_type": self.entity_type, "entity_id": self.entity_id,
            "tenant_id": self.tenant_id, "content_hash": self.content_hash,
            "version_or_revision_id": self.version_or_revision_id,
            "observed_at": self.observed_at, "effective_at": self.effective_at,
            "locator": self.locator, "tombstoned": self.tombstoned,
        }


@dataclass
class EvidenceEdge:
    edge_id: str
    edge_type: str
    from_ref: ProvenanceRef
    to_ref: ProvenanceRef
    tenant_scope: str
    created_at: str
    created_by: str
    method: str | None = None
    confidence_dimensions: dict[str, float] = field(default_factory=dict)
    status: str = "ACTIVE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id, "edge_type": self.edge_type,
            "from_ref": self.from_ref.to_dict(), "to_ref": self.to_ref.to_dict(),
            "tenant_scope": self.tenant_scope, "created_at": self.created_at,
            "created_by": self.created_by, "method": self.method,
            "confidence_dimensions": dict(self.confidence_dimensions),
            "status": self.status,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_ref(*, ref_id: str, ref_type: str, entity_type: str, entity_id: str,
             tenant_id: str, content_hash: str, **kw) -> ProvenanceRef:
    return ProvenanceRef(ref_id=ref_id, ref_type=ref_type,
                         entity_type=entity_type, entity_id=entity_id,
                         tenant_id=tenant_id, content_hash=content_hash, **kw)


class EvidenceGraph:
    """In-memory prototype graph. Physical storage is replaceable (EVID-LAW-015)."""

    def __init__(self, endpoint_rules: dict | None = None,
                 edge_types_config: dict | None = None):
        self._refs: dict[str, ProvenanceRef] = {}
        self._edges: list[EvidenceEdge] = []
        self._edge_types: set[str] = set()
        self._endpoint_rules: dict[str, dict] = {}
        if edge_types_config:
            for fam in edge_types_config.get("edge_families", []):
                self._edge_types.update(fam.get("edge_types", []))
        if endpoint_rules:
            for rule in endpoint_rules:
                self._endpoint_rules[rule["edge_type"]] = rule

    # ---- refs ----

    def put_ref(self, ref: ProvenanceRef) -> ProvenanceRef:
        existing = self._refs.get(ref.ref_id)
        if existing and existing.content_hash != ref.content_hash:
            raise EvidenceGraphError(
                f"ref {ref.ref_id} hash mismatch: immutable identity violated")
        self._refs[ref.ref_id] = ref
        return ref

    def get_ref(self, ref_id: str) -> ProvenanceRef:
        ref = self._refs.get(ref_id)
        if ref is None:
            raise EvidenceGraphError(f"ref {ref_id} does not resolve")
        return ref

    def resolve_or_tombstone(self, ref_id: str) -> dict:
        """Every supported ref resolves to a typed object or explicit tombstone."""
        ref = self._refs.get(ref_id)
        if ref is None or ref.tombstoned:
            return {"ref_id": ref_id, "tombstoned": True}
        return ref.to_dict()

    def tombstone(self, ref_id: str) -> None:
        if ref_id not in self._refs:
            raise EvidenceGraphError(f"cannot tombstone unknown ref {ref_id}")
        self._refs[ref_id].tombstoned = True

    # ---- edges ----

    def add_edge(self, *, edge_type: str, from_ref: ProvenanceRef,
                 to_ref: ProvenanceRef, tenant_scope: str,
                 created_by: str, method: str | None = None,
                 confidence_dimensions: dict | None = None,
                 edge_id: str | None = None) -> EvidenceEdge:
        if edge_type not in self._edge_types:
            raise EvidenceGraphError(f"unknown edge type {edge_type!r}")
        # ADV-031: malicious source content must not create a self-SUPPORTS
        # edge; no ref may point to itself.
        if from_ref.ref_id == to_ref.ref_id:
            raise EvidenceGraphError(
                f"self-loop edge denied: {from_ref.ref_id} cannot {edge_type} "
                "itself (GRAPH-004)")
        # ADV-032: corroboration must come from distinct sources; a duplicate
        # of the same upstream content is not corroboration.
        if edge_type == "CORROBORATES" and \
                from_ref.content_hash == to_ref.content_hash:
            raise EvidenceGraphError(
                "CORROBORATES requires distinct source content; duplicate "
                "of the same upstream is not corroboration (GRAPH-005)")
        if tenant_scope not in (from_ref.tenant_id, to_ref.tenant_id):
            raise EvidenceGraphError(
                "edge tenant_scope must belong to one of its endpoints")
        if from_ref.tenant_id != to_ref.tenant_id:
            raise EvidenceGraphError(
                "cross-tenant edges are denied (GRAPH-002)")
        # endpoint compatibility (GRAPH-001): the config decides legal pairs
        rule = self._endpoint_rules.get(edge_type)
        if rule:
            if from_ref.ref_type not in rule["from_types"]:
                raise EvidenceGraphError(
                    f"edge {edge_type}: from type {from_ref.ref_type} not "
                    f"allowed {rule['from_types']}")
            if to_ref.ref_type not in rule["to_types"]:
                raise EvidenceGraphError(
                    f"edge {edge_type}: to type {to_ref.ref_type} not "
                    f"allowed {rule['to_types']}")
        for ep in (from_ref, to_ref):
            if ep.tombstoned:
                raise EvidenceGraphError(
                    f"cannot add edge from/to tombstoned ref {ep.ref_id}")
        edge = EvidenceEdge(
            edge_id=edge_id or f"edge-{len(self._edges) + 1}",
            edge_type=edge_type, from_ref=from_ref, to_ref=to_ref,
            tenant_scope=tenant_scope, created_at=_now(), created_by=created_by,
            method=method, confidence_dimensions=dict(confidence_dimensions or {}))
        self._edges.append(edge)
        return edge

    def edges(self, *, edge_type: str | None = None,
              ref_id: str | None = None) -> list[EvidenceEdge]:
        out = self._edges
        if edge_type:
            out = [e for e in out if e.edge_type == edge_type]
        if ref_id:
            out = [e for e in out
                   if e.from_ref.ref_id == ref_id or e.to_ref.ref_id == ref_id]
        return list(out)

    def neighbors(self, ref_id: str) -> list[tuple[str, str]]:
        """(neighbor_ref_id, edge_type) pairs for graph traversal."""
        return [(e.to_ref.ref_id, e.edge_type) if e.from_ref.ref_id == ref_id
                else (e.from_ref.ref_id, e.edge_type)
                for e in self._edges if ref_id in (e.from_ref.ref_id,
                                                   e.to_ref.ref_id)]

    def claim_support_chain(self, claim_ref_id: str) -> list[dict]:
        """Walk SUPPORTS/DERIVED_FROM back to SourceSnapshot (workload W1)."""
        chain: list[dict] = []
        frontier = [claim_ref_id]
        seen: set[str] = set()
        while frontier:
            current = frontier.pop(0)
            if current in seen:
                continue
            seen.add(current)
            ref = self.resolve_or_tombstone(current)
            if ref.get("tombstoned"):
                chain.append({"ref_id": current, "tombstoned": True})
                continue
            chain.append(ref)
            for neighbor, edge_type in self.neighbors(current):
                if edge_type in ("SUPPORTS", "DERIVED_FROM",
                                 "NORMALIZED_FROM", "EXTRACTED_FROM",
                                 "OBSERVED_IN"):
                    frontier.append(neighbor)
        return chain
