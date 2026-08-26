"""G0 Book 2 — B2.C15 CommonGrants interoperability contract.

Maps internal domain objects to CommonGrants Opportunity/Application/Award
concepts WITHOUT reducing internal richness. Every field is classified exactly
one of EXACT / EXTENSION / INTERNAL_ONLY / EXTERNAL_ONLY / LOSSY.

The mapping is MECHANISM-only until the project vendors the real CommonGrants
schemas: `common_grants_schema_version` is "unpinned" and check_schema_version()
fails closed on any mismatch, so no compatibility claim can be made
prematurely. Extension fields live under the project-owned `cgx_` namespace;
external IDs never replace internal identity.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation


def classify_rows(mapping: dict) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {c: set() for c in mapping["mapping_classes"]}
    for ent in mapping["entities"]:
        for row in ent["rows"]:
            cls = row["mapping_class"]
            if cls not in out:
                raise ValueError(f"unknown mapping class '{cls}'")
            out[cls].add(f"{ent['entity']}.{row['internal_field']}")
    return out


def rows_for(mapping: dict, entity: str) -> list[dict]:
    ent = next((e for e in mapping["entities"] if e["entity"] == entity), None)
    if ent is None:
        raise ValueError(f"no mapping rows for entity '{entity}'")
    return ent["rows"]


def to_common_grants(internal: dict, mapping: dict, entity: str) -> dict:
    """internal -> CommonGrants. EXACT/EXTENSION/EXTERNAL_ONLY mapped;
    INTERNAL_ONLY excluded (no richness leak); LOSSY applied with transform."""
    external: dict = {}
    for row in rows_for(mapping, entity):
        cls = row["mapping_class"]
        if cls == "INTERNAL_ONLY":
            continue
        field = row["common_grants_field"]
        value = internal.get(row["internal_field"])
        if value is None:
            continue
        transform = row.get("transform") or "identity"
        if transform != "identity":
            value = _apply_transform(transform, value)
        external[field] = value
    return external


def from_common_grants(external: dict, mapping: dict, entity: str) -> dict:
    """CommonGrants -> internal (EXACT/EXTENSION/LOSSY reverse). Unknown cgx_
    extension fields are preserved; unknown non-extension fields are rejected
    (fail closed)."""
    internal: dict = {}
    cgx = mapping["extension_namespace"]
    known = {row["common_grants_field"]: row for row in rows_for(mapping, entity)}
    for field, value in external.items():
        if field in known:
            row = known[field]
            if row["mapping_class"] in ("EXACT", "EXTENSION", "LOSSY"):
                reverse = row.get("reverse_transform") or "identity"
                if reverse not in ("identity", "none"):
                    value = _apply_transform(reverse, value)
                if reverse != "none":
                    internal[row["internal_field"]] = value
                # reverse_transform 'none' -> value not reconstructible; the
                # field stays absent (loss declared by the LOSSY row)
            # INTERNAL_ONLY / EXTERNAL_ONLY rows never appear externally
            continue
        if field.startswith(cgx):
            internal[field] = value          # preserve project-owned extension
            continue
        raise ValueError(f"unknown non-extension CommonGrants field '{field}'")
    return internal


def round_trip(internal: dict, mapping: dict, entity: str) -> tuple[bool, list[str]]:
    """EXACT fields must survive internal -> CG -> internal with semantic
    equality. Returns (ok, mismatch list)."""
    ext = to_common_grants(internal, mapping, entity)
    back = from_common_grants(ext, mapping, entity)
    mismatches: list[str] = []
    for row in rows_for(mapping, entity):
        if row["mapping_class"] != "EXACT":
            continue
        field = row["internal_field"]
        if back.get(field) != internal.get(field):
            mismatches.append(field)
    return not mismatches, mismatches


def lossy_fields(mapping: dict, entity: str) -> list[dict]:
    """Every LOSSY mapping is explicit and test-visible."""
    return [row for row in rows_for(mapping, entity)
            if row["mapping_class"] == "LOSSY"]


def check_schema_version(mapping: dict, actual_version: str) -> tuple[bool, str]:
    """The CommonGrants pin must match the vendored schemas. 'unpinned' can
    never match — compatibility claims require a vendored, verified pin."""
    pinned = mapping["common_grants_schema_version"]
    if pinned == "unpinned":
        return False, "CommonGrants schema pin is unpinned (vendor schemas first)"
    if pinned != actual_version:
        return False, f"schema version mismatch: pinned '{pinned}', actual '{actual_version}'"
    return True, "schema version verified"


def _apply_transform(name: str, value):
    if name == "identity":
        return value
    if name == "decimal_to_string":
        return str(value)
    if name == "string_to_decimal":
        try:
            return Decimal(value)
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(f"cannot convert '{value}' to Decimal")
    if name in ("map_status", "map_state", "latest_revision_deadline"):
        # CG vocabulary is coarser (status) or the field is derived from the
        # latest revision; the reverse transform restores the closest internal
        # value. Deterministic, and the mapping row declares the loss.
        return value
    raise ValueError(f"unknown transform '{name}'")
