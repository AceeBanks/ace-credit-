"""B2.C3 — derive schemas/g0/domain/*.json from config/g0/domain/entity_types.yaml.

Schemas are DERIVED artifacts — never hand-written — so the catalog stays the
single source of truth. Regeneration is deterministic:

    python tools/g0/generate_domain_schemas.py [--check]

`--check` exits non-zero if any committed schema is stale (used by tests).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import DOMAIN_CONFIG_DIR, load_yaml  # noqa: E402

SCHEMA_DIR = _ROOT / "schemas" / "g0" / "domain"

_SCALAR_JSON = {
    "string": {"type": "string"},
    "integer": {"type": "integer"},
    "boolean": {"type": "boolean"},
    "number": {"type": "number"},
    "date": {"type": "string", "format": "date"},
    "datetime": {"type": "string", "format": "date-time"},
    "money": {"type": "string",
              "pattern": r"^\d+(\.\d{1,2})?$",
              "description": "fixed-point decimal as string; float money is prohibited (B2.C12)"},
    "string_array": {"type": "array", "items": {"type": "string"}},
}


def field_schema(field: dict, enums: dict) -> dict:
    ftype = field["type"]
    if ftype == "enum":
        return {"type": "string", "enum": sorted(enums[field["ref"]])}
    return dict(_SCALAR_JSON[ftype])


def generate_schemas(catalog: dict) -> dict[str, dict]:
    enums = catalog.get("enums") or {}
    out: dict[str, dict] = {}
    for ent in catalog.get("entity_types", []):
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": ent["entity_type"],
            "description": f"B2.C3 core entity — {ent['entity_type']} "
                           f"(identity prefix {ent.get('identity_prefix')})",
            "type": "object",
            "properties": {},
            "required": [],
        }
        for f in ent.get("fields", []):
            schema["properties"][f["name"]] = field_schema(f, enums)
            if f.get("required"):
                schema["required"].append(f["name"])
        schema["additionalProperties"] = False
        out[ent["schema_file"]] = schema
    return out


def main() -> int:
    check = "--check" in sys.argv
    catalog = load_yaml(DOMAIN_CONFIG_DIR / "entity_types.yaml")
    schemas = generate_schemas(catalog)
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    stale: list[str] = []
    for name, schema in sorted(schemas.items()):
        path = SCHEMA_DIR / name
        payload = json.dumps(schema, indent=2) + "\n"
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != payload:
                stale.append(name)
        else:
            path.write_text(payload, encoding="utf-8")
            print(f"wrote {name}")
    if check:
        if stale:
            print(f"STALE SCHEMAS: {stale} (re-run generator)")
            return 1
        print(f"all {len(schemas)} schemas up to date")
        return 0
    print(f"generated {len(schemas)} schemas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
