#!/usr/bin/env python3
"""G0-B5-C24 — validate_adversarial_evidence.

Validates the adversarial evidence scenario catalog: all 40 scenarios
present with severity and guard; every P0 scenario has a guard. Exit 0 when
valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_COUNT = 40


def validate(errors: list[str] | None = None,
            catalog: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    catalog = catalog if catalog is not None else load_yaml(
        _ROOT / "config/g0/evidence/adversarial_evidence.yaml")
    scenarios = catalog.get("scenarios", [])
    if len(scenarios) != EXPECTED_COUNT:
        errors.append(f"adversarial catalog must have {EXPECTED_COUNT} "
                      f"scenarios, got {len(scenarios)}")
        ok = False
    ids = set()
    for s in scenarios:
        sid = s.get("id")
        if not str(sid).startswith("ADV-"):
            errors.append(f"scenario id must start with ADV-: {sid!r}")
        if sid in ids:
            errors.append(f"duplicate scenario {sid}")
        ids.add(sid)
        if s.get("severity") not in ("P0", "P1"):
            errors.append(f"{sid}: severity must be P0 or P1")
        if not s.get("guard"):
            errors.append(f"{sid}: guard required")
    return ok, {"policy_id": catalog.get("policy_id"),
                "scenarios": len(scenarios),
                "p0": sum(1 for s in scenarios if s.get("severity") == "P0")}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("ADVERSARIAL CATALOG INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"adversarial catalog OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
