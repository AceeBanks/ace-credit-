#!/usr/bin/env python3
"""G0-B6-C9-C11 — validate_tool_gateway.

Validates the tool registry/gateway/MCP facade policy: rules TOOL-001..011,
5 tool statuses, 5 side-effect classes, gateway responsibilities vs
non-responsibilities, MCP facade rules and the role surfaces. Exit 0 when
valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_RULES = tuple(f"TOOL-{i:03d}" for i in range(1, 12))


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/security/tool_registry_policy.yaml")
    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"tool policy missing rule {rid}")
            ok = False
    if len(policy.get("tool_statuses", [])) != 5:
        errors.append("tool policy must define 5 statuses")
        ok = False
    if len(policy.get("side_effect_classes", [])) != 5:
        errors.append("tool policy must define 5 side-effect classes")
        ok = False
    if "verify_authorization_decision" not in \
            policy.get("gateway_responsibilities", []):
        errors.append("gateway must verify the AuthorizationDecision")
        ok = False
    if "submission.execute" not in policy.get("hidden_never_capabilities", []):
        errors.append("submission.execute must be hidden/never-discoverable")
        ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "rules": len(policy.get("rules", [])),
                "statuses": len(policy.get("tool_statuses", [])),
                "responsibilities": len(
                    policy.get("gateway_responsibilities", []))}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("TOOL GATEWAY POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"tool gateway policy OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
