"""G0-B5-C22 — Privacy, retention & evidence visibility prototype.

Enforces VIS-001..006: tenant-private evidence is not globally retrievable,
edges never raise endpoint visibility, derived indexes respect deletion,
tombstones/hashes survive retention, explanation packets filter by viewer
authority, and tenant exports stay within the tenant.
"""
from __future__ import annotations

from typing import Any

from prototype.g0.evidence.models import EvidenceGraph


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/evidence/"
                           "visibility_policy.yaml").read_text(encoding="utf-8"))


_POLICY = _load_policy()


class VisibilityManager:
    """Tracks per-ref visibility (default TENANT_PRIVATE)."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY
        self._visibility: dict[str, str] = {}
        self._deleted: set[str] = set()

    def declare(self, ref_id: str, visibility: str) -> None:
        if visibility not in self.policy["visibility_classes"]:
            raise ValueError(f"unknown visibility {visibility!r}")
        self._visibility[ref_id] = visibility

    def visibility_of(self, ref_id: str) -> str:
        return self._visibility.get(ref_id, self.policy["default_visibility"])

    def delete(self, ref_id: str) -> None:
        """VIS-004: restrict current access; tombstone/hash are preserved by
        the underlying graph (the manager only removes live visibility)."""
        self._deleted.add(ref_id)

    def _rank(self, vis: str) -> int:
        return self.policy["viewer_authority_ranking"].get(vis, 0)

    def viewer_max_rank(self, viewer_class: str) -> int:
        for v in self.policy["authorized_viewer_classes"]:
            if v["name"] == viewer_class:
                return self._rank(v["max_visibility"])
        return 0

    def visible(self, *, ref_id: str, tenant_id: str | None,
                viewer_class: str, owner_tenant: str | None = None) -> bool:
        """VIS-001/005: a ref is visible when (a) not deleted, (b) its
        visibility rank is within the viewer's max rank, and (c) tenant-bound
        viewers only see their own tenant's private data."""
        if ref_id in self._deleted:
            return False
        vis = self.visibility_of(ref_id)
        if self._rank(vis) > self.viewer_max_rank(viewer_class):
            return False
        for v in self.policy["authorized_viewer_classes"]:
            if v["name"] == viewer_class and v.get("tenant_bound"):
                # tenant-bound viewers see PUBLIC_SOURCE or own-tenant refs
                if vis == "TENANT_PRIVATE":
                    if tenant_id is None or owner_tenant != tenant_id:
                        return False
        return True

    def scoped_refs(self, *, refs: list[str], tenant_id: str | None,
                    viewer_class: str,
                    owner_tenants: dict[str, str] | None = None) -> list[str]:
        """VIS-001: filter a ref list to what the viewer may see."""
        owner_tenants = owner_tenants or {}
        return [r for r in refs
                if self.visible(ref_id=r, tenant_id=tenant_id,
                                viewer_class=viewer_class,
                                owner_tenant=owner_tenants.get(r))]

    def scoped_graph_query(self, *, graph: EvidenceGraph,
                           tenant_id: str | None,
                           viewer_class: str,
                           node_ids: list[str]) -> list[str]:
        """Mixed public/private query: no private node metadata leaks
        (VIS-001). Returns only visible node ids; nothing else escapes."""
        owners = {rid: graph._refs[rid].tenant_id for rid in node_ids
                  if rid in graph._refs}
        return self.scoped_refs(refs=node_ids, tenant_id=tenant_id,
                                viewer_class=viewer_class,
                                owner_tenants=owners)

    def vector_results(self, *, candidates: list[str]) -> list[str]:
        """VIS-003: vector index honors deletion — deleted refs never appear
        in results, regardless of ranking."""
        return [r for r in candidates if r not in self._deleted]

    def rebuild_visibility(self, *, nodes: dict[str, dict]) -> dict[str, str]:
        """VIS-003: visibility survives projection/rebuild — each projected
        node carries its visibility class."""
        return {nid: n.get("visibility", self.visibility_of(nid))
                for nid, n in nodes.items()}

    def tenant_export(self, *, graph: EvidenceGraph,
                      tenant_id: str) -> list[dict]:
        """VIS-006: a tenant exports its own evidence lineage only."""
        out = []
        for ref_id, ref in graph._refs.items():
            if ref.tenant_id != tenant_id:
                continue
            if ref_id in self._deleted:
                continue  # current access restricted; tombstone/hash retained
            out.append({"ref_id": ref_id, "ref_type": ref.ref_type,
                        "content_hash": ref.content_hash,
                        "visibility": self.visibility_of(ref_id)})
        return out
