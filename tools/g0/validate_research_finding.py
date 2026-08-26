#!/usr/bin/env python3
"""G0-B5-C17 — validate_research_finding.

Validates the research finding policy config and optionally a finding JSON
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

EXPECTED_RULES = ("FIND-001", "FIND-002", "FIND-003", "FIND-004", "FIND-005")


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/evidence/research_finding_policy.yaml")
    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"research policy missing rule {rid}")
            ok = False
    if len(policy.get("research_types", [])) != 9:
        errors.append("research policy must define 9 research types")
        ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "research_types": len(policy.get("research_types", [])),
                "rules": len(policy.get("rules", []))}


def validate_finding_doc(finding: dict) -> list[str]:
    errs: list[str] = []
    try:
        import jsonschema
    except Exception:  # pragma: no cover
        errs.append("jsonschema unavailable")
        return errs
    schema = json.loads((_ROOT / "schemas/g0/evidence/"
                         "research_finding.schema.json")
                        .read_text(encoding="utf-8"))
    errs.extend(f"schema: {e.message}" for e in
                sorted(jsonschema.Draft202012Validator(schema)
                       .iter_errors(finding), key=str))
    return errs


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("RESEARCH POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"research finding policy OK: {details}")
    if len(sys.argv) > 1:
        finding = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        perrs = validate_finding_doc(finding)
        if perrs:
            print("FINDING INVALID")
            for e in perrs:
                print(f"  - {e}")
            return 1
        print("finding OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
