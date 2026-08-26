#!/usr/bin/env python3
"""G0-B5-C20 — validate_draft_readiness.

Validates the draft evidence readiness policy config. Exit 0 when valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_RULES = ("DRAFT-001", "DRAFT-002", "DRAFT-003", "DRAFT-004",
                  "DRAFT-005", "DRAFT-006")


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/evidence/draft_readiness_policy.yaml")
    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"draft readiness policy missing rule {rid}")
            ok = False
    if not (0 < policy.get("coverage_threshold", 0) < 1):
        errors.append("coverage_threshold must be in (0, 1)")
        ok = False
    if len(policy.get("required_d0_outputs", [])) != 6:
        errors.append("required_d0_outputs must list 6 outputs")
        ok = False
    if "unresolved_evidence_gaps" not in policy.get(
            "d1_worker_result_fields", []):
        errors.append("worker result must carry unresolved_evidence_gaps "
                      "(DRAFT-005)")
        ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "rules": len(policy.get("rules", [])),
                "threshold": policy.get("coverage_threshold")}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("DRAFT READINESS POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"draft readiness policy OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
