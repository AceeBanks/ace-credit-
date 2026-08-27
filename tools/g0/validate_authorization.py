#!/usr/bin/env python3
"""G0-B6-C4-C5 — validate_authorization.

Validates the capability grant policy (rules GRANT-001..006, delegable vs
non-delegable separation, phase-disabled list) and the authorization reason
code catalog. Exit 0 when valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.security.authorization import REASON_CODES  # noqa: E402
from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_RULES = ("GRANT-001", "GRANT-002", "GRANT-003", "GRANT-004",
                  "GRANT-005", "GRANT-006", "GRANT-007")

EXPECTED_REASON_CODES = (
    "PRINCIPAL_UNKNOWN", "PRINCIPAL_DISABLED", "SESSION_INVALID",
    "TENANT_DENIED", "CAPABILITY_UNKNOWN", "CAPABILITY_DISABLED",
    "AUTHORITY_INSUFFICIENT", "GRANT_MISSING", "GRANT_EXPIRED",
    "GRANT_AUTHORITY_INSUFFICIENT", "PROJECT_DENIED",
    "RESOURCE_DENIED", "TASK_SCOPE_DENIED", "DATA_CLASS_DENIED",
    "EGRESS_DENIED", "APPROVAL_REQUIRED", "EXPLICIT_DENY", "ALLOW",
)


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/security/capability_grant_policy.yaml")
    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"grant policy missing rule {rid}")
            ok = False
    delegable = set(policy.get("delegable_capabilities", []))
    non_delegable = set(policy.get("non_delegable_capabilities", []))
    overlap = delegable & non_delegable
    if overlap:
        errors.append(f"capabilities both delegable and non-delegable: "
                      f"{sorted(overlap)}")
        ok = False
    if "submission.execute" not in policy.get("phase_disabled_capabilities", []):
        errors.append("submission.execute must remain phase-disabled (GRANT-005)")
        ok = False
    if "submission.execute" not in non_delegable:
        errors.append("submission.execute must be non-delegable")
        ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "delegable": len(delegable),
                "non_delegable": len(non_delegable),
                "rules": len(policy.get("rules", []))}


def validate_reason_codes() -> list[str]:
    errs = []
    for code in EXPECTED_REASON_CODES:
        if code not in REASON_CODES:
            errs.append(f"missing reason code {code}")
    if len(REASON_CODES) != len(set(REASON_CODES)):
        errs.append("duplicate reason codes")
    return errs


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    rc_errs = validate_reason_codes()
    errs.extend(rc_errs)
    if not ok or rc_errs:
        print("AUTHORIZATION POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"authorization policy OK: {details}; {len(REASON_CODES)} reason codes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
