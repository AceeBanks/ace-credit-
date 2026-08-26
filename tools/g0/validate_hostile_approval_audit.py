#!/usr/bin/env python3
"""G0-B6-C16-C19 — validate_hostile_approval_audit.

Validates the hostile content policy and the approval/audit policy. Exit 0
when valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

INJ_RULES = tuple(f"INJ-{i:03d}" for i in range(1, 8))
FILE_RULES = tuple(f"FILE-{i:03d}" for i in range(1, 8))
APPR_RULES = tuple(f"APPR-{i:03d}" for i in range(1, 7))
AUD_RULES = tuple(f"AUD-{i:03d}" for i in range(1, 6))


def validate(errors: list[str] | None = None,
            hostile: dict | None = None,
            appr: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    hostile = hostile if hostile is not None else load_yaml(
        _ROOT / "config/g0/security/hostile_content_policy.yaml")
    appr = appr if appr is not None else load_yaml(
        _ROOT / "config/g0/security/approval_audit_policy.yaml")

    inj_ids = {r.get("id") for r in hostile.get("rules", [])}
    for rid in INJ_RULES:
        if rid not in inj_ids:
            errors.append(f"hostile content policy missing rule {rid}")
            ok = False
    file_ids = {r.get("id") for r in hostile.get("file_rules", [])}
    for rid in FILE_RULES:
        if rid not in file_ids:
            errors.append(f"file policy missing rule {rid}")
            ok = False

    appr_ids = {r.get("id") for r in appr.get("rules", [])}
    for rid in APPR_RULES + AUD_RULES:
        if rid not in appr_ids:
            errors.append(f"approval/audit policy missing rule {rid}")
            ok = False

    if len(hostile.get("threat_classes", [])) != 6:
        errors.append("hostile content policy must define 6 threat classes")
        ok = False
    if len(appr.get("audit_classes", [])) != 11:
        errors.append("approval/audit policy must define 11 audit classes")
        ok = False
    if not appr.get("tamper_resistance", {}).get("integrity_hash_chain"):
        errors.append("audit tamper resistance must include integrity hash "
                      "chain (AUD-005)")
        ok = False
    return ok, {"inj_rules": len(inj_ids), "file_rules": len(file_ids),
                "threat_classes": len(hostile.get("threat_classes", [])),
                "audit_classes": len(appr.get("audit_classes", []))}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"hostile/approval/audit policy OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
