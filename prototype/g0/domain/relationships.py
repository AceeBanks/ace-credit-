"""G0 Book 2 — B2.C6 relationship semantics.

Typed edges: endpoint type checking, cardinality enforcement, self-loop
prohibition for org-to-org edges, tenant containment. Graph-storage agnostic
by design (the catalog defines semantics whether the implementation later
uses relational tables, graph projections or hybrid storage).
"""
from __future__ import annotations

from prototype.g0.domain.models import Relationship


def endpoint_types_ok(rel: Relationship, spec: dict, resolve) -> bool:
    """Both endpoints must be legal for the relationship type.

    `resolve(ref) -> entity_type` maps a ref string to its entity type.
    """
    try:
        src_type = resolve(rel.source_ref)
        tgt_type = resolve(rel.target_ref)
    except KeyError:
        return False
    return (src_type in spec.get("source_entity_types", [])
            and tgt_type in spec.get("target_entity_types", []))


def cardinality_ok(spec: dict, existing_source_count: int, *,
                   existing_target_count: int = 0) -> bool:
    """Enforce the catalog cardinality for the source side of a new edge.

    1:1 -> source must not already have an edge; 1:N -> source may have many
    (enforced by caller passing the count); N:M -> always allowed at the
    type level.
    """
    card = spec.get("cardinality")
    if card == "1:1":
        return existing_source_count == 0
    if card in ("1:N", "N:M", "N:1"):
        return True
    return False


def self_loop_allowed(rel: Relationship, spec: dict) -> bool:
    """no_self_loop edges (org partner / fiscal sponsor) reject source==target."""
    if spec.get("no_self_loop") and rel.source_ref == rel.target_ref:
        return False
    return True


def tenants_ok(rel: Relationship, tenant_of, tenant_id: str) -> bool:
    """Cross-tenant relationships are rejected: every endpoint must belong to
    the relationship's tenant (platform tenant for tenant-neutral edges)."""
    try:
        return tenant_of(rel.source_ref) == tenant_id and tenant_of(rel.target_ref) == tenant_id
    except KeyError:
        return False
