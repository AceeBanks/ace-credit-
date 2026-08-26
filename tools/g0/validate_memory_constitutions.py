"""B4.C12-C13 — Personal + CEO memory constitution validator.

Fail-closed validation over config/g0/agents/{personal_memory_classes,
ceo_memory_classes,memory_ttl_policy}.yaml:

  * each role's class catalog matches the plan-required class set exactly,
    with distinct namespaces (anti-collapse);
  * the canonical-substitution rule and duplicate examples are declared for
    Personal memory;
  * CEO declares the non-durable-by-default classes and the lesson promotion
    flow (Book 7 eval gate);
  * the TTL policy covers every declared class, has a default, and declares
    the override + lesson-survival + outage-TTL rules.
"""
from __future__ import annotations

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

REQUIRED_PERSONAL_CLASSES = {
    "PM-IDENTITY", "PM-PREFERENCE", "PM-GOAL", "PM-DECISION",
    "PM-RELATIONSHIP", "PM-OPEN_LOOP", "PM-EPISODIC_SUMMARY",
}
REQUIRED_CEO_CLASSES = {
    "CM-SYSTEM-DOCTRINE", "CM-ACTIVE-PROJECT", "CM-BLOCKER",
    "CM-CAPABILITY", "CM-LESSON-CANDIDATE", "CM-PROMOTED-LESSON",
    "CM-HEALTH-DEGRADATION",
}
REQUIRED_CEO_NON_DURABLE = {
    "RAW_WORKER_LOGS", "ONE_OFF_RETRY_DETAILS", "ENTIRE_PROMPTS",
    "EVERY_GRANT_RESEARCHED", "CLOSED_TASK_CHATTER", "VERBOSE_TOOL_OUTPUT",
}


def validate_personal_classes(errors: list[str],
                             cfg: dict | None = None) -> None:
    try:
        data = cfg if cfg is not None else load_yaml(
            AGENTS_CONFIG_DIR / "personal_memory_classes.yaml")
    except ValidationFailure as exc:
        errors.append(str(exc))
        return
    if data.get("namespace") != "personal_hermes":
        errors.append("personal memory namespace must be personal_hermes")
    classes = {c.get("class_id") for c in data.get("classes", [])}
    if classes != REQUIRED_PERSONAL_CLASSES:
        errors.append(f"personal classes must be exactly "
                      f"{sorted(REQUIRED_PERSONAL_CLASSES)}; got {sorted(classes)}")
    if not data.get("canonical_substitution_rule"):
        errors.append("personal canonical_substitution_rule must be declared")
    if not data.get("canonical_duplicate_examples"):
        errors.append("personal canonical_duplicate_examples must be declared")


def validate_ceo_classes(errors: list[str],
                         cfg: dict | None = None) -> None:
    try:
        data = cfg if cfg is not None else load_yaml(
            AGENTS_CONFIG_DIR / "ceo_memory_classes.yaml")
    except ValidationFailure as exc:
        errors.append(str(exc))
        return
    if data.get("namespace") != "ceo_hermes":
        errors.append("ceo memory namespace must be ceo_hermes")
    classes = {c.get("class_id") for c in data.get("classes", [])}
    if classes != REQUIRED_CEO_CLASSES:
        errors.append(f"ceo classes must be exactly "
                      f"{sorted(REQUIRED_CEO_CLASSES)}; got {sorted(classes)}")
    non_durable = set(data.get("non_durable_by_default", []))
    missing = REQUIRED_CEO_NON_DURABLE - non_durable
    if missing:
        errors.append(f"ceo non_durable_by_default missing: {sorted(missing)}")
    flow = data.get("lesson_promotion_flow", "")
    if "Book 7" not in flow and "book 7" not in flow:
        errors.append("ceo lesson_promotion_flow must require Book 7 eval")


def validate_ttl_policy(errors: list[str],
                        cfg: dict | None = None) -> None:
    try:
        data = cfg if cfg is not None else load_yaml(
            AGENTS_CONFIG_DIR / "memory_ttl_policy.yaml")
    except ValidationFailure as exc:
        errors.append(str(exc))
        return
    if not data.get("default_ttl_days"):
        errors.append("memory_ttl_policy default_ttl_days required")
    class_ttls = data.get("class_ttls", {})
    all_classes = REQUIRED_PERSONAL_CLASSES | REQUIRED_CEO_CLASSES
    missing = all_classes - set(class_ttls)
    if missing:
        errors.append(f"class_ttls missing: {sorted(missing)}")
    unknown = set(class_ttls) - all_classes
    if unknown:
        errors.append(f"class_ttls unknown classes: {sorted(unknown)}")
    rules = " ".join(
        str(r.get("rule", r)) if isinstance(r, dict) else str(r)
        for r in data.get("ttl_rules", []))
    if "expires_at" not in rules:
        errors.append("ttl_rules must declare expires_at override")
    if "promoted lesson" not in rules:
        errors.append("ttl_rules must declare lesson survival after closure")
    if "CM-HEALTH-DEGRADATION" not in rules:
        errors.append("ttl_rules must declare outage TTL")


def main() -> int:
    errors: list[str] = []
    validate_personal_classes(errors)
    validate_ceo_classes(errors)
    validate_ttl_policy(errors)
    _, report = finish("memory_constitutions", not errors, {
        "errors": errors,
        "personal_classes": len(REQUIRED_PERSONAL_CLASSES),
        "ceo_classes": len(REQUIRED_CEO_CLASSES),
        "namespaces": ["personal_hermes", "ceo_hermes"],
    })
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
