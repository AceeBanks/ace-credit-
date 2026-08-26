"""B1.C2 — Constitutional law catalog validator.

Fail-closed linter per Book 1 plan: every law must carry ID, title, normative
statement, rationale, enforcement category, affected capability classes and
amendment status; IDs must be exactly LAW-B1-001..LAW-B1-030 with no gaps or
duplicates.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

LAWS_PATH = _ROOT / "config" / "g0" / "policy" / "constitutional_laws.yaml"
REQUIRED_FIELDS = (
    "id", "title", "normative_statement", "rationale",
    "enforcement_category", "affected_capability_classes", "amendment_status",
)


def validate(data) -> tuple[bool, dict]:
    """Validate a parsed law catalog (mapping or path). Returns (ok, report)."""
    errors: list[str] = []
    if isinstance(data, (str, Path)):
        data = load_yaml(Path(data))
    if not isinstance(data, dict):
        return False, {"ok": False, "errors": ["catalog root is not a mapping"]}

    laws = data.get("laws")
    if not isinstance(laws, list) or not laws:
        return False, {"ok": False, "errors": ["laws list missing or empty"]}

    ids = []
    for i, law in enumerate(laws):
        lid = law.get("id") if isinstance(law, dict) else None
        where = f"law[{i}]({lid})"
        if not isinstance(law, dict):
            errors.append(f"{where}: not a mapping")
            continue
        for field in REQUIRED_FIELDS:
            value = law.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"{where}: missing required field '{field}'")
            if field == "affected_capability_classes":
                if not isinstance(value, list) or not value:
                    errors.append(f"{where}: affected_capability_classes must be a non-empty list")
            if field in ("enforcement_category", "amendment_status"):
                key = ("valid_enforcement_categories"
                       if field == "enforcement_category"
                       else "valid_amendment_statuses")
                allowed = data.get(key)
                if isinstance(allowed, list) and value not in allowed:
                    errors.append(f"{where}: unknown {field} '{value}'")

    # exact contiguous ID set LAW-B1-001..LAW-B1-030
    expected = [f"LAW-B1-{n:03d}" for n in range(1, len(laws) + 1)]
    seen = [l.get("id") for l in laws if isinstance(l, dict)]
    dupes = sorted({x for x in seen if seen.count(x) > 1})
    if dupes:
        errors.append(f"duplicate law ids: {dupes}")
    if sorted(x for x in seen if x) != sorted(expected):
        missing = sorted(set(expected) - set(seen))
        extra = sorted(set(seen) - set(expected))
        if missing:
            errors.append(f"missing expected law ids: {missing}")
        if extra:
            errors.append(f"unexpected law ids: {extra}")

    report = {
        "ok": not errors,
        "law_count": len([x for x in seen if x]),
        "unique_ids": len(set(x for x in seen if x)),
        "expected_law_ids": len(laws),
        "frozen_count": sum(1 for l in laws if isinstance(l, dict)
                            and l.get("amendment_status") == "FROZEN"),
        "errors": errors,
    }
    return report["ok"], report


def main() -> int:
    ok, report = validate(LAWS_PATH)
    print(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
