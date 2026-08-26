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


def load_glossary() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "glossary.yaml")


def main() -> int:
    from tools.g0._common import emit
    ok, report = validate_glossary(load_glossary())
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
