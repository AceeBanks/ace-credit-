#!/usr/bin/env python3
"""G0-B5-C18 — validate_linkage.

Validates the audit/evidence/decision linkage policy config. Exit 0 when
valid; 1 with errors otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_RULES = ("LINK-001", "LINK-002", "LINK-003", "LINK-004")


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/evidence/linkage_policy.yaml")
    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"linkage policy missing rule {rid}")
            ok = False
    if len(policy.get("forward_path", [])) != 7:
        errors.append("linkage policy forward_path must have 7 steps")
        ok = False
    if len(policy.get("backward_path", [])) != 6:
        errors.append("linkage policy backward_path must have 6 steps")
        ok = False
    if "decision_record_ref" not in policy.get("redaction_never_removes", []):
        errors.append("redaction must preserve decision_record_ref (LINK-004)")
        ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "rules": len(policy.get("rules", [])),
                "forward_path": len(policy.get("forward_path", [])),
                "backward_path": len(policy.get("backward_path", []))}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("LINKAGE POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"linkage policy OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
