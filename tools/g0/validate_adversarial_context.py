#!/usr/bin/env python3
"""G0-B4-C26 — adversarial context & memory scenario catalog validator.

Validates config/g0/agents/adversarial_context.yaml: all 25 scenarios
present, unique, with non-empty fail-closed expectations; the five
context invariants present; and no unknown ids. Fail-closed: any
missing/unknown entry fails the validator.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]

_REQUIRED_IDS = [f"A{i}" for i in range(1, 26)]
_REQUIRED_INVARIANT_IDS = [f"I{i}" for i in range(1, 6)]


def load_config(path: Path | None = None) -> dict:
    cfg_path = path or (_ROOT / "config/g0/agents/adversarial_context.yaml")
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8"))


def validate(errors: list[str] | None = None, cfg: dict | None = None) -> list[str]:
    errors = [] if errors is None else errors
    data = cfg if cfg is not None else load_config()
    if not isinstance(data, dict):
        errors.append("adversarial_context.yaml must be a mapping")
        return errors

    scenarios = data.get("adversarial_scenarios")
    if not isinstance(scenarios, list):
        errors.append("adversarial_scenarios must be a list")
        return errors

    ids = []
    names = set()
    for s in scenarios:
        sid = s.get("id")
        ids.append(sid)
        name = s.get("name", "")
        expectation = s.get("expectation", "")
        if not isinstance(sid, str) or not sid:
            errors.append("every scenario needs a non-empty string id")
        if not isinstance(name, str) or not name:
            errors.append(f"scenario {sid}: missing name")
        if not isinstance(expectation, str) or len(expectation) < 10:
            errors.append(f"scenario {sid}: expectation must be a concrete fail-closed statement")
        if name in names:
            errors.append(f"duplicate scenario name {name!r}")
        names.add(name)

    missing = [i for i in _REQUIRED_IDS if i not in ids]
    if missing:
        errors.append(f"missing required scenarios: {missing}")
    unknown = [i for i in ids if i not in _REQUIRED_IDS]
    if unknown:
        errors.append(f"unknown scenario ids: {unknown}")

    invariants = data.get("context_invariants")
    if not isinstance(invariants, list):
        errors.append("context_invariants must be a list")
    else:
        iids = [iv.get("id") for iv in invariants]
        for iv in invariants:
            if not isinstance(iv.get("expectation", ""), str) or len(iv.get("expectation", "")) < 10:
                errors.append(f"invariant {iv.get('id')}: expectation must be concrete")
        imissing = [i for i in _REQUIRED_INVARIANT_IDS if i not in iids]
        if imissing:
            errors.append(f"missing required invariants: {imissing}")
        iunknown = [i for i in iids if i not in _REQUIRED_INVARIANT_IDS]
        if iunknown:
            errors.append(f"unknown invariant ids: {iunknown}")
    return errors


def check(data: dict) -> tuple[bool, dict]:
    """Convention-compatible entrypoint for lock builders: (ok, report)."""
    errors: list[str] = []
    validate(errors, cfg=data)
    return (not errors, {"errors": errors})


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate adversarial context catalog")
    ap.add_argument("--config", type=Path, default=None, help="config path override (tests)")
    args = ap.parse_args()
    errors: list[str] = []
    validate(errors, cfg=load_config(args.config) if args.config else None)
    if errors:
        print("FAIL: adversarial context catalog invalid")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: adversarial context catalog valid (A1-A25 + I1-I5)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
