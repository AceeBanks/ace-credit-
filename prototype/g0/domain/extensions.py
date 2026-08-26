"""G0 Book 2 — B2.C16 extension namespace & sector portability.

Grant-specific concepts stay in the grant namespace; cross-sector primitives
move to a platform namespace only through explicit ADR; provider-specific
fields live in namespaced extensions, never root-schema pollution. Registering
a new provider (state/private/future sector) must not change core identity
semantics.
"""
from __future__ import annotations

VALID_PREFIX_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789_")


def provider_prefix(provider: str, namespace_catalog: dict) -> str:
    """The namespaced prefix for a provider, from the extension config."""
    for entry in namespace_catalog.get("provider_namespaces", []):
        if entry["provider"] == provider:
            return entry["prefix"]
    raise ValueError(f"unknown provider '{provider}' (not in extension namespace config)")


def is_namespaced(field: str, prefix: str) -> bool:
    """A provider field must carry the provider's prefix."""
    return field.startswith(prefix) and len(field) > len(prefix)


def register_provider(core_identity_before: dict, core_identity_after: dict) -> bool:
    """Registering/adding a provider must leave core identity semantics
    unchanged (same identity-prefix scheme, same root entities). Returns False
    (fail closed) when the provider addition mutated core identity."""
    return core_identity_before == core_identity_after


def core_identity_scheme(entity_types: list[dict]) -> dict[str, str]:
    """The identity-prefix scheme of the core entity catalog."""
    return {e["entity_type"]: e["identity_prefix"] for e in entity_types
            if e.get("identity_prefix")}
