#!/usr/bin/env python3
"""G0-B5-C10-C12 — retrieval + projection policies validator."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_PATH = _ROOT / "config/g0/evidence/retrieval_policies.yaml"
PROJECTION_PATH = _ROOT / "config/g0/evidence/projection_policies.yaml"

REQUIRED_LANES = {"EXACT_STRUCTURED_LOOKUP", "FILTERED_RELATIONAL",
                  "GRAPH_TRAVERSAL", "FULL_TEXT", "VECTOR_SEMANTIC"}


def load_configs() -> tuple[dict, dict]:
    return (yaml.safe_load(RETRIEVAL_PATH.read_text(encoding="utf-8")),
            yaml.safe_load(PROJECTION_PATH.read_text(encoding="utf-8")))


def validate(errors: list[str] | None = None,
             retrieval: dict | None = None,
             projection: dict | None = None) -> list[str]:
    errors = [] if errors is None else errors
    if retrieval is None or projection is None:
        r, p = load_configs()
        retrieval = retrieval if retrieval is not None else r
        projection = projection if projection is not None else p

    lanes = {l["id"] for l in retrieval.get("lanes", [])}
    if lanes != REQUIRED_LANES:
        errors.append(f"lanes mismatch: {sorted(lanes)}")
    for rule in ("RETR-001", "RETR-002", "RETR-003", "RETR-004", "RETR-005"):
        if rule not in {a["id"] for a in retrieval.get("authority_rules", [])}:
            errors.append(f"missing retrieval rule {rule}")

    for rule in ("VEC-001", "VEC-002", "VEC-003", "VEC-004", "VEC-005",
                 "VEC-006", "VEC-007", "VEC-008"):
        if rule not in {v["id"] for v in projection.get("vector_index_rules", [])}:
            errors.append(f"missing vector rule {rule}")
    for rule in ("PROJ-001", "PROJ-002", "PROJ-003", "PROJ-004", "PROJ-005",
                 "PROJ-006", "PROJ-007"):
        if rule not in {p["id"] for p in projection.get("graph_projection_rules", [])}:
            errors.append(f"missing projection rule {rule}")
    if projection.get("exit_test", {}).get("id") != "EXIT-001":
        errors.append("missing EXIT-001 exit test")
    return errors


def check(retrieval: dict, projection: dict) -> tuple[bool, dict]:
    errors: list[str] = []
    validate(errors, retrieval=retrieval, projection=projection)
    return (not errors, {"errors": errors})


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate retrieval/projection configs")
    ap.add_argument("--retrieval", type=Path, default=None)
    ap.add_argument("--projection", type=Path, default=None)
    args = ap.parse_args()
    errors: list[str] = []
    validate(errors,
             retrieval=yaml.safe_load(args.retrieval.read_text(encoding="utf-8"))
             if args.retrieval else None,
             projection=yaml.safe_load(args.projection.read_text(encoding="utf-8"))
             if args.projection else None)
    if errors:
        print("FAIL: retrieval/projection configs invalid")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: retrieval lanes and projection policies valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
