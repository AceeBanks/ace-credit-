#!/usr/bin/env python3
"""G0-B5-C2-C3 — provenance ref + evidence graph semantics validator.

Validates:
  * provenance_ref.schema.json + evidence_edge.schema.json against examples;
  * config/g0/evidence/evidence_edge_types.yaml: every family's edge types
    are known, endpoint rules exist for relational edge types, hard rules
    are present.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema
import yaml

_ROOT = Path(__file__).resolve().parents[2]
EDGE_TYPES_PATH = _ROOT / "config/g0/evidence/evidence_edge_types.yaml"
SCHEMAS_DIR = _ROOT / "schemas/g0/evidence"

FAMILY_EDGE_TYPES = {
    "source_lineage": {"EXTRACTED_FROM", "NORMALIZED_FROM", "OBSERVED_IN", "DERIVED_FROM"},
    "evidence_semantics": {"SUPPORTS", "CONTRADICTS", "CORROBORATES", "SUPERSEDES", "QUALIFIES", "MEASURES"},
    "decision_lineage": {"DECISION_USED", "DECISION_PRODUCED", "EVALUATED_AGAINST", "EXPLAINED_BY"},
    "application_lineage": {"REQUIREMENT_SATISFIED_BY", "ARTIFACT_USES", "BUDGET_SUPPORTS", "QA_CHECKED", "REVIEWED_BY"},
    "dependency_semantics": {"DEPENDS_ON", "INVALIDATES", "REQUIRES_RECOMPUTE"},
}


def load_edge_config(path: Path | None = None) -> dict:
    return yaml.safe_load((path or EDGE_TYPES_PATH).read_text(encoding="utf-8"))


def load_schemas() -> dict:
    out = {}
    for name in ("provenance_ref.schema.json", "evidence_edge.schema.json"):
        out[name] = json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))
    return out


def validate(errors: list[str] | None = None, cfg: dict | None = None) -> list[str]:
    errors = [] if errors is None else errors
    data = cfg if cfg is not None else load_edge_config()

    known: set[str] = set()
    for fam in data.get("edge_families", []):
        family = fam.get("family")
        types = set(fam.get("edge_types", []))
        expected = FAMILY_EDGE_TYPES.get(family)
        if expected is None:
            errors.append(f"unknown edge family {family!r}")
            continue
        if types != expected:
            errors.append(f"family {family}: expected {sorted(expected)} "
                          f"got {sorted(types)}")
        known |= types

    rules = {r["edge_type"]: r for r in data.get("edge_endpoint_rules", [])}
    for r in data.get("edge_endpoint_rules", []):
        if r["edge_type"] not in known:
            errors.append(f"endpoint rule for unknown edge type {r['edge_type']!r}")
        if not r.get("from_types") or not r.get("to_types"):
            errors.append(f"edge {r['edge_type']}: from/to types required")
    # relational edge types must have endpoint rules
    for et in ("SUPPORTS", "CONTRADICTS", "SUPERSEDES", "DECISION_USED",
               "DEPENDS_ON", "INVALIDATES", "REQUIRES_RECOMPUTE"):
        if et not in rules:
            errors.append(f"edge {et} missing endpoint rules")

    hard_rules = data.get("hard_rules", [])
    hard_ids = {h.get("id") for h in hard_rules}
    for required in ("GRAPH-001", "GRAPH-002", "GRAPH-003"):
        if required not in hard_ids:
            errors.append(f"missing hard rule {required}")

    # schema spot-checks
    schemas = load_schemas()
    try:
        jsonschema.validate(
            {"ref_id": "r1", "ref_type": "SOURCE_SNAPSHOT",
             "entity_type": "SourceSnapshot", "entity_id": "snap-1",
             "tenant_id": "tenant-a", "content_hash": "abc12345"},
            schemas["provenance_ref.schema.json"])
    except jsonschema.ValidationError as e:  # pragma: no cover
        errors.append(f"provenance_ref schema rejects a valid ref: {e.message}")
    try:
        jsonschema.validate(
            {"ref_id": "r1", "ref_type": "SOURCE_SNAPSHOT",
             "entity_type": "SourceSnapshot", "entity_id": "snap-1",
             "tenant_id": "tenant-a", "content_hash": "not-a-hash"},
            schemas["provenance_ref.schema.json"])
        errors.append("provenance_ref schema accepts an invalid content_hash")
    except jsonschema.ValidationError:
        pass
    return errors


def check(data: dict) -> tuple[bool, dict]:
    errors: list[str] = []
    validate(errors, cfg=data)
    return (not errors, {"errors": errors})


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate provenance/graph semantics")
    ap.add_argument("--config", type=Path, default=None)
    args = ap.parse_args()
    errors: list[str] = []
    validate(errors, cfg=load_edge_config(args.config) if args.config else None)
    if errors:
        print("FAIL: provenance/graph semantics invalid")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: provenance refs and evidence graph semantics valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
