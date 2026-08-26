"""B5.C11-C12 — Disposable vector index + graph projection prototype.

Vectors and graph projections are rebuildable from canonical state/evidence
(VEC-008, PROJ-002); node ids derive from internal canonical ids
(PROJ-001); graph-only mutation cannot create canonical facts (PROJ-003);
the exit test (EXIT-001) deletes and rebuilds the projection without
semantic loss.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Deterministic content-based pseudo-embedding (prototype; real embeddings
# are pluggable behind the same contract — VEC-003 records model/version).


def _tokens(text: str) -> set[str]:
    return {w for w in text.lower().split() if len(w) >= 3}


def pseudo_embedding(text: str) -> tuple[int, ...]:
    """Deterministic bag-of-tokens signature (prototype embedding)."""
    return tuple(sorted(hash(t) % 2**20 for t in _tokens(text)))


class VectorIndex:
    """Disposable derived index: vectors -> canonical refs only."""

    def __init__(self, embedding_model: str = "pseudo-v1"):
        self.embedding_model = embedding_model
        self._vectors: dict[str, tuple[int, ...]] = {}
        self._refs: dict[str, dict] = {}

    def index(self, *, ref: str, text: str, tenant_scope: str,
              visibility: str, evidence_class: str) -> None:
        self._vectors[ref] = pseudo_embedding(text)
        self._refs[ref] = {
            "ref": ref, "tenant_scope": tenant_scope,
            "visibility": visibility, "evidence_class": evidence_class,
            "embedding_model": self.embedding_model,
        }

    def search(self, query: str, *, tenant_scope: str, limit: int = 5,
               allow_cross_tenant: bool = False) -> list[dict]:
        """VEC-006: no cross-tenant similarity search by default."""
        if not allow_cross_tenant:
            candidates = [ref for ref, meta in self._refs.items()
                          if meta["tenant_scope"] == tenant_scope]
        else:
            candidates = list(self._refs)
        q_vec = pseudo_embedding(query)
        scored = []
        for ref in candidates:
            vec = self._vectors.get(ref)
            if vec is None:
                continue  # deleted/never-indexed vectors are not retrievable
            overlap = len(set(q_vec) & set(vec))
            scored.append((overlap, ref))
        scored.sort(key=lambda x: -x[0])
        return [{"ref": ref, "score": score}
                for score, ref in scored[:limit]]

    def resolve(self, ref: str) -> dict:
        """Every vector points back to a stable canonical ref (VEC-002)."""
        meta = self._refs.get(ref)
        if meta is None:
            return {"ref": ref, "deleted": True}
        if meta["visibility"] == "DELETED":
            return {"ref": ref, "deleted": True}
        return dict(meta)

    def delete(self, ref: str) -> None:
        """VEC-005: deletion hides the artifact from future retrieval."""
        if ref in self._refs:
            self._refs[ref]["visibility"] = "DELETED"
            self._vectors.pop(ref, None)

    def rebuild(self, canonical_sources: dict[str, str]) -> int:
        """VEC-008: index rebuilds from canonical artifacts/snapshots."""
        count = 0
        for ref, text in canonical_sources.items():
            meta = self._refs.get(ref)
            tenant = meta["tenant_scope"] if meta else "tenant-a"
            visibility = meta["visibility"] if meta else "PUBLIC_SOURCE"
            eclass = meta["evidence_class"] if meta else "EVIDENCE_CLAIM"
            if visibility == "DELETED":
                continue
            self.index(ref=ref, text=text, tenant_scope=tenant,
                       visibility=visibility, evidence_class=eclass)
            count += 1
        return count


class GraphProjection:
    """Projection of canonical evidence into a graph. Rebuildable (EXIT-001)."""

    def __init__(self, schema_version: str = "proj-v1"):
        self.schema_version = schema_version
        self._nodes: dict[str, dict] = {}
        self._edges: list[dict] = []
        self._events: list[dict] = []

    def project(self, *, source_refs: list[str],
                canonical_nodes: dict[str, dict],
                edges: list[dict]) -> dict:
        """PROJ-001: node ids derive from internal canonical ids."""
        for node_id, attrs in canonical_nodes.items():
            self._nodes[node_id] = {"canonical_id": node_id, **attrs}
        for edge in edges:
            self._edges.append(dict(edge))
        event = {
            "projection_event_id": f"pe-{len(self._events) + 1}",
            "source_refs": list(source_refs),
            "projection_target": "graph",
            "projection_schema_version": self.schema_version,
            "created_at": "2026-08-26T00:00:00+00:00",
            "status": "COMPLETE",
        }
        self._events.append(event)
        return event

    def mutate_graph_only(self, node_id: str, attrs: dict) -> None:
        """PROJ-003: graph-only mutation is recorded but never canonical."""
        self._nodes.setdefault(node_id, {"canonical_id": node_id}).update(attrs)
        self._nodes[node_id]["graph_only_mutation"] = True

    def canonical_node_ids(self) -> list[str]:
        return sorted(self._nodes)

    def rebuild_from_canonical(self, canonical_nodes: dict[str, dict],
                               edges: list[dict]) -> tuple[int, int]:
        """EXIT-001: delete + rebuild without semantic loss."""
        node_count = len(canonical_nodes)
        self._nodes = {}
        self._edges = []
        for node_id, attrs in canonical_nodes.items():
            self._nodes[node_id] = {"canonical_id": node_id, **attrs}
        self._edges = [dict(e) for e in edges]
        return node_count, len(self._edges)
