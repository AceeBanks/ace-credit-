#!/usr/bin/env python3
"""G0-B5-C1 — evidence constitution validator.

All 15 EVID-LAW entries present, unique, with concrete fail-closed or
append-only enforcement. Any missing/unknown law fails the validator.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
CONSTITUTION_PATH = _ROOT / "config/g0/evidence/evidence_constitution.yaml"

VALID_ENFORCEMENT = {"FAIL_CLOSED", "APPEND_ONLY"}


def load_config(path: Path | None = None) -> dict:
    return yaml.safe_load((path or CONSTITUTION_PATH).read_text(encoding="utf-8"))


def validate(errors: list[str] | None = None, cfg: dict | None = None) -> list[str]:
    errors = [] if errors is None else errors
    data = cfg if cfg is not None else load_config()
    laws = data.get("laws", [])
    ids = []
    for law in laws:
        lid = law.get("id")
        ids.append(lid)
        if not isinstance(lid, str) or not lid.startswith("EVID-LAW-"):
            errors.append(f"law id must start with EVID-LAW-: {lid!r}")
        if not law.get("name"):
            errors.append(f"law {lid}: missing name")
        if len(law.get("text", "")) < 20:
            errors.append(f"law {lid}: text too short")
        enforcement = law.get("enforcement")
        if enforcement not in VALID_ENFORCEMENT:
            errors.append(f"law {lid}: enforcement must be one of "
                          f"{sorted(VALID_ENFORCEMENT)}")
    required = data.get("required_law_ids", [])
    missing = [r for r in required if r not in ids]
    if missing:
        errors.append(f"missing required laws: {missing}")
    unknown = [i for i in ids if i not in required]
    if unknown:
        errors.append(f"unknown law ids: {unknown}")
    if len(ids) != len(set(ids)):
        errors.append("duplicate law ids present")
    return errors


def check(data: dict) -> tuple[bool, dict]:
    errors: list[str] = []
    validate(errors, cfg=data)
    return (not errors, {"errors": errors})


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate evidence constitution")
    ap.add_argument("--config", type=Path, default=None)
    args = ap.parse_args()
    errors: list[str] = []
    validate(errors, cfg=load_config(args.config) if args.config else None)
    if errors:
        print("FAIL: evidence constitution invalid")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: evidence constitution valid (EVID-LAW-001..015)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
