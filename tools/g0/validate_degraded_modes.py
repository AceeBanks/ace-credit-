#!/usr/bin/env python3
"""G0-B5-C23 — validate_degraded_modes.

Validates the degraded modes registry: every component declares a role and
behavior; integrity-critical components declare fail-closed behavior.
Exit 0 when valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_RULES = ("DEG-001", "DEG-002", "DEG-003")
REQUIRED_COMPONENTS = ("graph_projection", "vector_store", "semantica",
                       "provenance_write", "historical_evidence",
                       "contradiction_service")
INTEGRITY_CRITICAL = ("provenance_write", "historical_evidence",
                      "contradiction_service")


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/evidence/degraded_modes.yaml")
    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"degraded modes policy missing rule {rid}")
            ok = False
    components = {c["id"]: c for c in policy.get("components", [])}
    for cid in REQUIRED_COMPONENTS:
        if cid not in components:
            errors.append(f"degraded modes missing component {cid}")
            continue
        comp = components[cid]
        if comp.get("role") not in ("OPTIONAL", "INTEGRITY_CRITICAL"):
            errors.append(f"component {cid}: invalid role")
        if comp["role"] == "OPTIONAL" and not comp.get("degraded_behavior"):
            errors.append(f"optional component {cid} lacks degraded_behavior")
        if comp["role"] == "INTEGRITY_CRITICAL" and not comp.get(
                "fail_closed_behavior"):
            errors.append(f"integrity-critical component {cid} lacks "
                          "fail_closed_behavior")
    return ok, {"policy_id": policy.get("policy_id"),
                "components": len(policy.get("components", [])),
                "rules": len(policy.get("rules", []))}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("DEGRADED MODES POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"degraded modes policy OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
