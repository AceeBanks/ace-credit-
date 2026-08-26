"""G0 Book 2 — C20/C21 domain guards (fail-closed).

- known_domain_type: invented root entities are rejected (A20);
- relationship tenant check: cross-tenant relationships are rejected (A15);
- identifier normalization is idempotent (C21 property).
"""
from __future__ import annotations

import inspect
import re

from prototype.g0.domain import models
from prototype.g0.domain.models import Relationship


def known_domain_types() -> set[str]:
    """All real domain types: catalog entity types + prototype model classes."""
    from tools.g0.validate_domain import load_entity_types
    types = {e["entity_type"] for e in load_entity_types()["entity_types"]}
    types |= {name for name, obj in inspect.getmembers(models, inspect.isclass)
              if obj.__module__ == models.__name__}
    return types


def require_known_type(name: str) -> bool:
    """A20 — an agent-invented root entity type is rejected."""
    return name in known_domain_types()


def relationship_tenant_matches(rel: Relationship, source_tenant: str | None,
                               target_tenant: str | None) -> bool:
    """A15 — a relationship's tenant must agree with both endpoints' tenants
    when those are known; a cross-tenant link is rejected."""
    if rel.tenant_id is None:
        return True
    if source_tenant is not None and source_tenant != rel.tenant_id:
        return False
    if target_tenant is not None and target_tenant != rel.tenant_id:
        return False
    return True


def normalize_identifier(normalization_rule: str, value: str) -> str:
    """Apply a namespace normalization rule deterministically (B2.C5)."""
    if normalization_rule == "trim":
        return value.strip()
    if normalization_rule == "trim_upper":
        return value.strip().upper()
    if normalization_rule == "trim_lower":
        return value.strip().lower()
    if normalization_rule == "strip_non_alnum_upper":
        return re.sub(r"[^A-Za-z0-9]", "", value).upper()
    if normalization_rule == "identity":
        return value
    raise ValueError(f"unknown normalization rule '{normalization_rule}'")
