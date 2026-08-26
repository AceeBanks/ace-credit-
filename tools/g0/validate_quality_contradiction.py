#!/usr/bin/env python3
"""G0-B5-C4-C6 — quality dimensions + contradiction types validator."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
QUALITY_PATH = _ROOT / "config/g0/evidence/evidence_quality_dimensions.yaml"
CONTRADICTION_PATH = _ROOT / "config/g0/evidence/contradiction_types.yaml"

REQUIRED_DIMENSIONS = {"authority", "directness", "freshness", "specificity",
                       "corroboration", "extraction_quality",
                       "identity_certainty", "temporal_fit"}
REQUIRED_QUALITY_CLASSES = {"VERIFIED_HIGH", "VERIFIED_MODERATE", "PROVISIONAL",
                            "CONFLICTED", "STALE", "UNSUPPORTED"}
REQUIRED_CONTRADICTION_TYPES = {
    "VALUE_CONFLICT", "IDENTITY_CONFLICT", "TEMPORAL_CONFLICT",
    "SOURCE_REVISION_CONFLICT", "SCOPE_CONFLICT", "UNIT_CONFLICT",
    "INTERPRETATION_CONFLICT"}


def load_configs() -> tuple[dict, dict]:
    quality = yaml.safe_load(QUALITY_PATH.read_text(encoding="utf-8"))
    contradiction = yaml.safe_load(CONTRADICTION_PATH.read_text(encoding="utf-8"))
    return quality, contradiction


def validate(errors: list[str] | None = None,
             quality: dict | None = None,
             contradiction: dict | None = None) -> list[str]:
    errors = [] if errors is None else errors
    if quality is None or contradiction is None:
        q, c = load_configs()
        quality = quality if quality is not None else q
        contradiction = contradiction if contradiction is not None else c

    dims = {d["id"] for d in quality.get("dimensions", [])}
    if dims != REQUIRED_DIMENSIONS:
        errors.append(f"dimensions mismatch: missing={sorted(REQUIRED_DIMENSIONS - dims)} "
                      f"unknown={sorted(dims - REQUIRED_DIMENSIONS)}")
    for d in quality.get("dimensions", []):
        if d.get("scale") != [0, 1]:
            errors.append(f"dimension {d.get('id')}: scale must be [0,1]")
        if not d.get("meaning"):
            errors.append(f"dimension {d.get('id')}: missing meaning")

    classes = {c["id"] for c in quality.get("quality_classes", [])}
    if classes != REQUIRED_QUALITY_CLASSES:
        errors.append(f"quality classes mismatch: {sorted(classes)}")
    for rule in ("QUAL-001", "QUAL-002", "QUAL-003", "QUAL-004"):
        if rule not in {h["id"] for h in quality.get("hard_rules", [])}:
            errors.append(f"missing quality hard rule {rule}")

    ctypes = {c["id"] for c in contradiction.get("contradiction_types", [])}
    if ctypes != REQUIRED_CONTRADICTION_TYPES:
        errors.append(f"contradiction types mismatch: missing="
                      f"{sorted(REQUIRED_CONTRADICTION_TYPES - ctypes)} "
                      f"unknown={sorted(ctypes - REQUIRED_CONTRADICTION_TYPES)}")
    for rule in ("CONTR-001", "CONTR-002", "CONTR-003", "CONTR-004",
                 "CONTR-005", "CONTR-006"):
        if rule not in {h["id"] for h in contradiction.get("hard_rules", [])}:
            errors.append(f"missing contradiction hard rule {rule}")
    return errors


def check(quality: dict, contradiction: dict) -> tuple[bool, dict]:
    errors: list[str] = []
    validate(errors, quality=quality, contradiction=contradiction)
    return (not errors, {"errors": errors})


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate quality/contradiction configs")
    ap.add_argument("--quality", type=Path, default=None)
    ap.add_argument("--contradiction", type=Path, default=None)
    args = ap.parse_args()
    errors: list[str] = []
    validate(errors,
             quality=yaml.safe_load(args.quality.read_text(encoding="utf-8"))
             if args.quality else None,
             contradiction=yaml.safe_load(args.contradiction.read_text(encoding="utf-8"))
             if args.contradiction else None)
    if errors:
        print("FAIL: quality/contradiction configs invalid")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: evidence quality dimensions and contradiction types valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
