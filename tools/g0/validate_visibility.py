#!/usr/bin/env python3
"""G0-B5-C22 — validate_visibility.

Validates the evidence visibility policy config. Exit 0 when valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_RULES = ("VIS-001", "VIS-002", "VIS-003", "VIS-004", "VIS-005",
                  "VIS-006")

EXPECTED_CLASSES = ("PUBLIC_SOURCE", "TENANT_PRIVATE", "TENANT_SHARED_APPROVED",
                    "PLATFORM_INTERNAL", "RESTRICTED_SENSITIVE")


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/evidence/visibility_policy.yaml")
    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"visibility policy missing rule {rid}")
            ok = False
    for cls in EXPECTED_CLASSES:
        if cls not in policy.get("visibility_classes", []):
            errors.append(f"visibility policy missing class {cls}")
            ok = False
    if not policy.get("retention", {}).get("tombstone_always_kept"):
        errors.append("retention must always keep tombstones (VIS-004)")
        ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "visibility_classes": len(policy.get("visibility_classes", [])),
                "rules": len(policy.get("rules", []))}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("VISIBILITY POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"visibility policy OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
