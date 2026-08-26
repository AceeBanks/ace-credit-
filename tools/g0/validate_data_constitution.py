"""B3.C1 — Data Constitution validator.

Fail-closed validation over config/g0/source/data_constitution.yaml: every law
must carry id/title/rule/enforcement-category/affected-schemas/amendment-links
+ a FROZEN status, exactly the 20 required DATA-LAW ids are present with no
duplicates, and enforcement categories come from the plan set.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import SOURCE_CONFIG_DIR, finish, load_yaml  # noqa: E402

LAW_FIELDS = ("law_id", "title", "rule", "enforcement_category",
              "affected_schemas", "amendment_links", "status")
REQUIRED_LAW_IDS = {f"DATA-LAW-{n:03d}" for n in range(1, 21)}
VALID_ENFORCEMENT = {"MUST", "SHOULD"}

DATA_CONSTITUTION_PATH = SOURCE_CONFIG_DIR / "data_constitution.yaml"


def validate(data: dict) -> tuple[bool, dict]:
    errors: list[str] = []
    laws = data.get("laws") or []
    seen: set[str] = set()
    for law in laws:
        lid = law.get("law_id")
        if not lid:
            errors.append("law entry missing law_id")
            continue
        missing = [f for f in LAW_FIELDS if f not in law]
        if missing:
            errors.append(f"{lid}: missing fields {missing}")
        if law.get("enforcement_category") not in VALID_ENFORCEMENT:
            errors.append(f"{lid}: unknown enforcement category "
                          f"'{law.get('enforcement_category')}'")
        if law.get("status") != "FROZEN":
            errors.append(f"{lid}: must be FROZEN")
        if lid in seen:
            errors.append(f"{lid}: duplicate law id")
        seen.add(lid)
    present = {l.get("law_id") for l in laws}
    if present != REQUIRED_LAW_IDS:
        missing_ids = sorted(REQUIRED_LAW_IDS - present)
        errors.append(f"must contain exactly 20 laws; missing {missing_ids}")

    return finish("data_constitution", not errors, {
        "errors": errors,
        "law_count": len(seen),
        "frozen_count": sum(1 for l in laws if l.get("status") == "FROZEN"),
        "required_law_count": data.get("required_law_count"),
    })


def load() -> dict:
    return load_yaml(DATA_CONSTITUTION_PATH)


def main() -> int:
    from tools.g0._common import emit
    ok, report = validate(load())
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())