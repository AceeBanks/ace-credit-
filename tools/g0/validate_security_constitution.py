#!/usr/bin/env python3
"""G0-B6-C1 — validate_security_constitution.

Validates the security constitutional laws: all 20 SEC-LAW-* ids present
with names, texts and fail-closed enforcement, no duplicates, no unknown
ids. Exit 0 when valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

VALID_ENFORCEMENT = ("FAIL_CLOSED", "APPEND_ONLY", "AUDITED")


def load_config(path: Path | None = None) -> dict:
    return load_yaml(path or (_ROOT / "config/g0/security/"
                              "security_constitution.yaml"))


def validate(errors: list[str] | None = None,
            cfg: dict | None = None) -> list[str]:
    errors = [] if errors is None else errors
    data = cfg if cfg is not None else load_config()
    laws = data.get("laws", [])
    ids = []
    for law in laws:
        lid = law.get("id")
        ids.append(lid)
        if not isinstance(lid, str) or not lid.startswith("SEC-LAW-"):
            errors.append(f"law id must start with SEC-LAW-: {lid!r}")
        if not law.get("name"):
            errors.append(f"law {lid}: missing name")
        if len(law.get("text", "")) < 20:
            errors.append(f"law {lid}: text too short")
        if law.get("enforcement") not in VALID_ENFORCEMENT:
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
    if len(required) != 20:
        errors.append("security constitution must define exactly 20 laws")
    return errors


def check(data: dict) -> tuple[bool, dict]:
    errors: list[str] = []
    validate(errors, cfg=data)
    return (not errors, {"errors": errors})


def main() -> int:
    errors: list[str] = []
    validate(errors)
    if errors:
        print("FAIL: security constitution invalid")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"security constitution OK: {len(load_config()['laws'])} laws")
    return 0


if __name__ == "__main__":
    sys.exit(main())
