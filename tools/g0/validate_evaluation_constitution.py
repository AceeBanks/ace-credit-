"""B7.C1 — Evaluation Constitutional Law catalog validator.

Fail-closed linter: every EVAL-LAW must carry id, name, text and enforcement
category; ids must be exactly EVAL-LAW-001..EVAL-LAW-015 with no gaps or
duplicates; every law must be FAIL_CLOSED.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import emit, finish, load_yaml  # noqa: E402

CONSTITUTION_PATH = _ROOT / "config" / "g0" / "evaluation" / "evaluation_constitution.yaml"
EXPECTED_LAW_COUNT = 15


def validate(data: dict) -> tuple[bool, dict]:
    errors: list[str] = []
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
        for field in ("id", "name", "text", "enforcement"):
            value = law.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"{where}: missing required field '{field}'")
        if law.get("enforcement") != "FAIL_CLOSED":
            errors.append(f"{where}: enforcement must be FAIL_CLOSED")
        if lid:
            ids.append(lid)

    expected = [f"EVAL-LAW-{n:03d}" for n in range(1, EXPECTED_LAW_COUNT + 1)]
    dupes = sorted({x for x in ids if ids.count(x) > 1})
    if dupes:
        errors.append(f"duplicate law ids: {dupes}")
    if sorted(set(ids)) != sorted(expected):
        missing = sorted(set(expected) - set(ids))
        extra = sorted(set(ids) - set(expected))
        if missing:
            errors.append(f"missing expected law ids: {missing}")
        if extra:
            errors.append(f"unexpected law ids: {extra}")

    return finish("evaluation_constitution", not errors, {
        "law_count": len(ids),
        "unique_ids": len(set(ids)),
        "expected_law_ids": EXPECTED_LAW_COUNT,
        "frozen_count": len(ids),
        "errors": errors,
    })


def main() -> int:
    try:
        ok, report = validate(load_yaml(CONSTITUTION_PATH))
    except Exception as exc:  # pragma: no cover
        ok, report = False, {"validator": "evaluation_constitution",
                             "status": "FAIL", "errors": [str(exc)]}
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
