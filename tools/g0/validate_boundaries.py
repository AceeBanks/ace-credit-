#!/usr/bin/env python3
"""G0-B6-C12-C15 — validate_boundaries.

Validates the integration/egress and data classification/PII policy
configs. Exit 0 when valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

INT_RULES = ("INT-001", "INT-002", "INT-003", "INT-004", "INT-005")
EGR_RULES = ("EGR-001", "EGR-002", "EGR-003", "EGR-004", "EGR-005")
DATA_RULES = ("DATA-001", "DATA-002", "DATA-003")
PII_RULES = ("PII-001", "PII-002", "PII-003", "PII-004")


def validate(errors: list[str] | None = None,
            integ: dict | None = None,
            data: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    integ = integ if integ is not None else load_yaml(
        _ROOT / "config/g0/security/integration_egress_policy.yaml")
    data = data if data is not None else load_yaml(
        _ROOT / "config/g0/security/data_classification_policy.yaml")

    int_ids = {r.get("id") for r in integ.get("integration_rules", [])}
    int_ids |= {r.get("id") for r in integ.get("egress_rules", [])}
    for rid in INT_RULES + EGR_RULES:
        if rid not in int_ids:
            errors.append(f"integration/egress policy missing rule {rid}")
            ok = False
    data_ids = {r.get("id") for r in data.get("data_rules", [])}
    data_ids |= {r.get("id") for r in data.get("pii_rules", [])}
    for rid in DATA_RULES + PII_RULES:
        if rid not in data_ids:
            errors.append(f"data classification policy missing rule {rid}")
            ok = False

    if len(integ.get("egress_classes", [])) != 6:
        errors.append("egress policy must define 6 egress classes")
        ok = False
    if integ["egress_phase1_defaults"].get("SUBMISSION_PORTAL") != "DISABLED":
        errors.append("SUBMISSION_PORTAL must stay disabled in phase 1")
        ok = False
    if len(data.get("data_classes", [])) != 8:
        errors.append("data classification must define 8 classes")
        ok = False
    if "169.254.169.254" not in integ.get("blocked_destinations", []):
        errors.append("cloud metadata endpoint must be blocked (EGR-002)")
        ok = False
    return ok, {"integration_rules": len(integ.get("integration_rules", []))
                + len(integ.get("egress_rules", [])),
                "egress_classes": len(integ.get("egress_classes", [])),
                "data_classes": len(data.get("data_classes", [])),
                "pii_fields": len(data.get("pii_fields", []))}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("BOUNDARY POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"boundary policy OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
