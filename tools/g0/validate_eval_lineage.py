#!/usr/bin/env python3
"""G0-B5-C19 — validate_eval_lineage.

Validates the eval lineage policy config and optionally an eval case JSON
document against the schema. Exit 0 when valid.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_RULES = ("EVAL-001", "EVAL-002", "EVAL-003", "EVAL-004", "EVAL-005")


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/evidence/eval_lineage_policy.yaml")
    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"eval lineage policy missing rule {rid}")
            ok = False
    if len(policy.get("label_origins", [])) != 5:
        errors.append("eval lineage must define 5 label origins")
        ok = False
    if "TENANT_PRIVATE" not in policy.get("governance_required_classes", []):
        errors.append("TENANT_PRIVATE must require governance (EVAL-005)")
        ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "label_origins": len(policy.get("label_origins", [])),
                "rules": len(policy.get("rules", []))}


def validate_case_doc(case: dict) -> list[str]:
    errs: list[str] = []
    try:
        import jsonschema
    except Exception:  # pragma: no cover
        errs.append("jsonschema unavailable")
        return errs
    schema = json.loads((_ROOT / "schemas/g0/evidence/"
                         "eval_case_lineage.schema.json")
                        .read_text(encoding="utf-8"))
    errs.extend(f"schema: {e.message}" for e in
                sorted(jsonschema.Draft202012Validator(schema)
                       .iter_errors(case), key=str))
    return errs


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("EVAL LINEAGE POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"eval lineage policy OK: {details}")
    if len(sys.argv) > 1:
        case = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        perrs = validate_case_doc(case)
        if perrs:
            print("CASE INVALID")
            for e in perrs:
                print(f"  - {e}")
            return 1
        print("case OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
