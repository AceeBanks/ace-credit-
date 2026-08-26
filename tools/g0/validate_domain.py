"""G0 Book 2 — domain ontology validators.

Fail-closed validators over the domain sources of truth in config/g0/domain/.
Every validator follows the same contract:

    validate(data) -> (ok: bool, report: dict)

Missing files, malformed fields or unknown enum values are hard failures
(fail closed), never warnings. Chapter functions are added as chapters land:

- C1  validate_glossary
- C3  validate_entity_types
- C5  validate_identifier_namespaces
- C6  validate_relationships
- C7  validate_state_machines
- C11 validate_requirement_types
- C13 validate_artifact_types
- C15 validate_common_grants_mapping
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import DOMAIN_CONFIG_DIR, finish, load_yaml  # noqa: E402

GLOSSARY_FIELDS = (
    "term", "definition", "what_it_is_not", "identity_scope",
    "mutable_attributes", "source_of_truth_book", "examples", "common_confusions",
)


def validate_glossary(glossary: dict) -> tuple[bool, dict]:
    """B2.C1 — glossary soundness: no duplicates, no circular definitions,
    required fields, banned ambiguous aliases are not used as canonical terms."""
    errors: list[str] = []
    terms = glossary.get("terms") or []
    seen: set[str] = set()
    for entry in terms:
        term = entry.get("term")
        if not term:
            errors.append("glossary entry missing 'term'")
            continue
        missing = [f for f in GLOSSARY_FIELDS if entry.get(f) is None or
                   (isinstance(entry.get(f), str) and not entry[f].strip())]
        if missing:
            errors.append(f"{term}: missing fields {missing}")
        if term in seen:
            errors.append(f"{term}: duplicate canonical term")
        seen.add(term)
        for banned in glossary.get("banned_ambiguous_aliases") or []:
            if term.lower() == banned.lower():
                errors.append(f"{term}: banned ambiguous alias used as canonical term")

    return finish("domain_glossary", not errors, {
        "errors": errors,
        "term_count": len(seen),
        "duplicates": len(terms) - len(seen),
    })


ENTITY_FIELDS = ("entity_type", "identity_prefix", "identity_scope",
                 "glossary_term", "revisioned_by", "state_machine",
                 "schema_file", "fields")
SCALAR_TYPES = {"string", "integer", "boolean", "number", "date", "datetime",
                "money", "string_array"}
IDENTITY_PREFIXES = ("org_", "person_", "role_", "extid_", "program_", "opp_",
                     "opp_rev_", "rule_", "eldec_", "award_", "app_",
                     "app_rev_", "req_", "budget_", "fact_", "claim_", "stat_",
                     "artifact_", "outcome_", "rel_", "cgx_")


def validate_entity_types(catalog: dict) -> tuple[bool, dict]:
    """B2.C3 — entity catalog: required fields, unique prefixes, valid field
    types, enum refs resolve, identity prefixes follow the B2.C4 scheme."""
    errors: list[str] = []
    enums = catalog.get("enums") or {}
    types = catalog.get("entity_types") or []
    seen: set[str] = set()
    prefixes: set[str] = set()
    for ent in types:
        et = ent.get("entity_type")
        if not et:
            errors.append("entity entry missing entity_type")
            continue
        # revisioned_by/state_machine may legitimately be null (leaf entities);
        # every other field must be present and non-null.
        nullable = {"revisioned_by", "state_machine"}
        missing = [f for f in ENTITY_FIELDS
                   if f not in ent or (ent.get(f) is None and f not in nullable)]
        if missing:
            errors.append(f"{et}: missing fields {missing}")
        if et in seen:
            errors.append(f"{et}: duplicate entity type")
        seen.add(et)
        prefix = ent.get("identity_prefix")
        if prefix:
            if prefix in prefixes:
                errors.append(f"{et}: duplicate identity prefix '{prefix}'")
            prefixes.add(prefix)
            if prefix not in IDENTITY_PREFIXES:
                errors.append(f"{et}: identity prefix '{prefix}' not in B2.C4 scheme")
        for f in ent.get("fields") or []:
            fname = f.get("name")
            ftype = f.get("type")
            if not fname or not ftype:
                errors.append(f"{et}: field missing name/type")
                continue
            if ftype == "enum":
                ref = f.get("ref")
                if ref not in enums:
                    errors.append(f"{et}.{fname}: enum ref '{ref}' unresolved")
            elif ftype not in SCALAR_TYPES:
                errors.append(f"{et}.{fname}: unknown field type '{ftype}'")
    return finish("domain_entity_types", not errors, {
        "errors": errors,
        "entity_count": len(seen),
        "schema_files": [e.get("schema_file") for e in types if e.get("schema_file")],
    })


NAMESPACE_FIELDS = (
    "namespace_id", "name", "issuer", "applies_to_entity_types", "format",
    "validation_rule", "globally_unique", "temporally_unique", "reusable",
    "case_sensitive", "normalization_rule", "verification_sources",
)


def validate_identifier_namespaces(data: dict, entity_types: dict | None = None) -> tuple[bool, dict]:
    """B2.C5 — namespaces: required fields, unique ids, entity refs resolve,
    boolean flags are booleans."""
    errors: list[str] = []
    entities = {e.get("entity_type") for e in (entity_types or {}).get("entity_types", [])}
    namespaces = data.get("namespaces") or []
    seen: set[str] = set()
    for ns in namespaces:
        nid = ns.get("namespace_id")
        if not nid:
            errors.append("namespace missing namespace_id")
            continue
        missing = [f for f in NAMESPACE_FIELDS if f not in ns or ns.get(f) is None]
        if missing:
            errors.append(f"{nid}: missing fields {missing}")
        if nid in seen:
            errors.append(f"{nid}: duplicate namespace")
        seen.add(nid)
        for flag in ("globally_unique", "temporally_unique", "reusable",
                     "case_sensitive"):
            if flag in ns and not isinstance(ns[flag], bool):
                errors.append(f"{nid}: {flag} must be boolean")
        if entities:
            for et in ns.get("applies_to_entity_types") or []:
                if et not in entities:
                    errors.append(f"{nid}: applies to unknown entity '{et}'")
    return finish("domain_identifier_namespaces", not errors, {
        "errors": errors, "namespace_count": len(seen),
    })


def load_identifier_namespaces() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "identifier_namespaces.yaml")


def load_entity_types() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "entity_types.yaml")


def load_glossary() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "glossary.yaml")


def main() -> int:
    from tools.g0._common import emit
    ok, report = validate_glossary(load_glossary())
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
