#!/usr/bin/env python3
"""G0-B6-C25 — validate_attack_surface.

Validates the attack surface register: every row must carry the full
field set from the plan, and submission surfaces must be structurally
disabled.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

REQUIRED_FIELDS = ("entry_point", "principal_types", "input_trust",
                   "tenant_scope", "capabilities", "secrets", "egress",
                   "controls", "rate_limits", "logging", "p0_failure")
MIN_SURFACES = 17
ASR_RULES = tuple(f"ASR-{i:03d}" for i in range(1, 4))


def validate(errors: list[str] | None = None,
             register: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    register = register if register is not None else load_yaml(
        _ROOT / "config/g0/security/attack_surface.yaml")

    surfaces = register.get("surfaces", [])
    if len(surfaces) < MIN_SURFACES:
        errors.append(f"attack surface register must list at least "
                      f"{MIN_SURFACES} surfaces; found {len(surfaces)}")
        ok = False
    seen: set[str] = set()
    for s in surfaces:
        sid = s.get("id", "?")
        if sid in seen:
            errors.append(f"duplicate surface id {sid}")
            ok = False
        seen.add(sid)
        for f in REQUIRED_FIELDS:
            if f not in s or s[f] is None:
                errors.append(f"surface {sid} missing required field {f}")
                ok = False
            elif isinstance(s[f], str) and not s[f].strip():
                errors.append(f"surface {sid} has empty field {f}")
                ok = False

    # submission must remain disabled
    for s in surfaces:
        if "submission" in s.get("name", "") or \
                "submission" in s.get("entry_point", ""):
            if "submission.execute" in s.get("capabilities", []) and \
                    "submission_disabled" not in s.get("controls", []):
                errors.append(
                    f"{s['id']}: submission surface missing the "
                    "submission_disabled control")
                ok = False

    rule_ids = {r.get("id") for r in register.get("register_rules", [])}
    for rid in ASR_RULES:
        if rid not in rule_ids:
            errors.append(f"register missing rule {rid}")
            ok = False

    return ok, {"surfaces": len(surfaces), "fields_checked": len(REQUIRED_FIELDS)}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("REGISTER INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"attack surface register OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
