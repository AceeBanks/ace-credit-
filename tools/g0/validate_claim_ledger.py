#!/usr/bin/env python3
"""G0-B5-C16 — validate_claim_ledger.

Validates the claim ledger policy config (classes, statuses, rules) and
optionally a ledger entry JSON against the schema. Exit 0 when valid.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_RULES = ("CLAIM-001", "CLAIM-002", "CLAIM-003", "CLAIM-004",
                  "CLAIM-005", "CLAIM-006", "CLAIM-007")


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/evidence/claim_ledger_policy.yaml")

    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"claim ledger policy missing rule {rid}")
            ok = False
    if len(policy.get("support_statuses", [])) != 7:
        errors.append("claim ledger must define exactly 7 support statuses")
        ok = False
    for cls in policy.get("claim_classes", []):
        if not cls or not isinstance(cls, str):
            errors.append(f"invalid claim_class {cls!r}")
            ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "claim_classes": len(policy.get("claim_classes", [])),
                "rules": len(policy.get("rules", []))}


def validate_entry(entry: dict) -> list[str]:
    errs: list[str] = []
    try:
        import jsonschema
    except Exception:  # pragma: no cover
        errs.append("jsonschema unavailable")
        return errs
    schema = json.loads((_ROOT / "schemas/g0/evidence/"
                         "claim_ledger_entry.schema.json")
                        .read_text(encoding="utf-8"))
    errs.extend(f"schema: {e.message}" for e in
                sorted(jsonschema.Draft202012Validator(schema)
                       .iter_errors(entry), key=str))
    return errs


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("CLAIM LEDGER POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"claim ledger policy OK: {details}")
    if len(sys.argv) > 1:
        entry = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        perrs = validate_entry(entry)
        if perrs:
            print("ENTRY INVALID")
            for e in perrs:
                print(f"  - {e}")
            return 1
        print("entry OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
