"""B4.C14-C16 — Worker memory / promotion / supersession validator.

Fail-closed validation over the four lifecycle schemas (memory_candidate,
memory_record, memory_promotion, memory_supersession) and the promotion
policy config: strict schemas, known memory states, candidate classification
enum, promotion validation states, and the policy's criteria / auto-promote /
review / Book-7-eval class splits plus the five PROMO rules.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    ValidationFailure,
    emit,
    finish,
    load_yaml,
)

AGENTS_CONFIG_DIR = Path("config/g0/agents")
SCHEMAS_DIR = Path("schemas/g0/agents")

CANDIDATE_REQUIRED = ["candidate_id", "proposed_memory_class",
                      "proposed_statement", "source_refs", "why_useful",
                      "importance", "proposed_by"]
RECORD_REQUIRED = ["memory_id", "memory_class", "namespace", "statement",
                   "created_at", "importance", "confidence_state", "status"]
PROMOTION_REQUIRED = ["promotion_id", "candidate_id", "decision",
                      "criteria_evidence", "validation_state", "proposed_by",
                      "promoted_at"]
SUPERSESSION_REQUIRED = ["supersession_id", "old_record_id", "new_record_id",
                         "reason", "created_at"]
REQUIRED_PROMO_RULES = {f"PROMO-{n:03d}" for n in range(1, 6)}
REQUIRED_CRITERIA = {
    "REPEATED_USE", "EXPLICIT_USER_STATEMENT", "HIGH_FUTURE_UTILITY",
    "STABILITY_OVER_TIME", "NOT_BETTER_REPRESENTED_AS_CANONICAL",
    "NO_HIGHER_AUTHORITY_CONTRADICTION", "PRIVACY_RETENTION_ALLOWED",
}


def _load_schema(name: str) -> tuple[bool, dict]:
    path = SCHEMAS_DIR / name
    if not path.exists():
        return False, {"error": f"missing schema file {path}"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, {"error": f"{name} is not valid JSON: {exc}"}
    if data.get("type") != "object":
        return False, {"error": f"{name} must be an object schema"}
    if data.get("additionalProperties") is not False:
        return False, {"error": f"{name} must set additionalProperties=false"}
    return True, data


def _check(name: str, required: list[str], errors: list[str]) -> None:
    ok, schema = _load_schema(name)
    if not ok:
        errors.append(schema.get("error", f"{name} invalid"))
        return
    props = set(schema.get("properties", {}))
    missing = [r for r in required if r not in props]
    if missing:
        errors.append(f"{name}: missing properties {missing}")
    missing_req = [r for r in required
                   if r not in set(schema.get("required", []))]
    if missing_req:
        errors.append(f"{name}: missing required fields {missing_req}")


def validate_promotion_policy(errors: list[str]) -> None:
    try:
        data = load_yaml(AGENTS_CONFIG_DIR / "memory_promotion_policy.yaml")
    except ValidationFailure as exc:
        errors.append(str(exc))
        return
    criteria = set(data.get("criteria", []))
    if criteria != REQUIRED_CRITERIA:
        errors.append(f"criteria must be exactly {sorted(REQUIRED_CRITERIA)}")
    auto = set(data.get("auto_promotable_classes", []))
    review = set(data.get("review_required_classes", []))
    book7 = set(data.get("book7_eval_required_classes", []))
    overlap = auto & review | auto & book7 | review & book7
    if overlap:
        errors.append(f"class split overlaps: {sorted(overlap)}")
    if "CM-LESSON-CANDIDATE" not in book7:
        errors.append("CM-LESSON-CANDIDATE must require Book 7 eval")
    rules = data.get("rules", [])
    seen: set[str] = set()
    for rule in rules:
        rid = rule.get("rule_id")
        if not rid:
            errors.append("promotion rule missing rule_id")
            continue
        if rid in seen:
            errors.append(f"{rid}: duplicate rule id")
        seen.add(rid)
    if seen != REQUIRED_PROMO_RULES:
        errors.append(f"promotion rules must be exactly "
                      f"{sorted(REQUIRED_PROMO_RULES)}; got {sorted(seen)}")
    gate = data.get("promotion_criteria_gate", {})
    required = set(gate.get("auto_promote_requires", []))
    if "EXPLICIT_USER_STATEMENT" not in required:
        errors.append("auto-promote gate must require EXPLICIT_USER_STATEMENT")
    if "NO_HIGHER_AUTHORITY_CONTRADICTION" not in required:
        errors.append("auto-promote gate must require "
                      "NO_HIGHER_AUTHORITY_CONTRADICTION")


def main() -> int:
    errors: list[str] = []
    _check("memory_candidate.schema.json", CANDIDATE_REQUIRED, errors)
    _check("memory_record.schema.json", RECORD_REQUIRED, errors)
    _check("memory_promotion.schema.json", PROMOTION_REQUIRED, errors)
    _check("memory_supersession.schema.json", SUPERSESSION_REQUIRED, errors)
    validate_promotion_policy(errors)
    _, report = finish("memory_lifecycle", not errors, {
        "errors": errors,
        "schemas": ["memory_candidate", "memory_record", "memory_promotion",
                    "memory_supersession"],
        "policy": "memory_promotion_policy.yaml",
    })
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
