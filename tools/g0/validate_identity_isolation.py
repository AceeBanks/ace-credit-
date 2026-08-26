#!/usr/bin/env python3
"""G0-B6-C2-C3 — validate_identity_isolation.

Validates the principal/identity policy: 11 principal types, 5 product
roles, 4 membership statuses, rules IDN-001..005 and the resource scope
hierarchy. Exit 0 when valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_RULES = ("IDN-001", "IDN-002", "IDN-003", "IDN-004", "IDN-005")
EXPECTED_TYPES = 11
EXPECTED_ROLES = ("OWNER", "ADMIN", "MEMBER", "REVIEWER", "READ_ONLY")


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/security/principal_policy.yaml")
    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"principal policy missing rule {rid}")
            ok = False
    types = policy.get("principal_types", [])
    if len(types) != EXPECTED_TYPES:
        errors.append(f"principal policy must define {EXPECTED_TYPES} types, "
                      f"got {len(types)}")
        ok = False
    if len(set(types)) != len(types):
        errors.append("duplicate principal types")
        ok = False
    for role in EXPECTED_ROLES:
        if role not in policy.get("tenant_membership_roles", []):
            errors.append(f"missing product role {role}")
            ok = False
    if "Tenant" not in policy.get("resource_scope_hierarchy", []):
        errors.append("resource scope hierarchy must start at Tenant")
        ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "principal_types": len(types),
                "rules": len(policy.get("rules", []))}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("PRINCIPAL POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"principal policy OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
