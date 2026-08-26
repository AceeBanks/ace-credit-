"""B4.C4-C5 — Intent + Clarification protocol validator.

Fail-closed validation over:

  * schemas/g0/agents/intent_contract.schema.json and
    clarification_request.schema.json: valid JSON Schema, strict
    (additionalProperties false), with the plan-required fields;
  * config/g0/agents/clarification_policy.yaml: known question types, all six
    CLARIFY-001..006 rules declared with full fields, blocking effects and
    escalation bounds declared.
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

KNOWN_QUESTION_TYPES = {
    "MISSING_REQUIRED_INPUT", "AMBIGUOUS_INPUT", "CONFLICTING_INPUT",
    "ELIGIBILITY_CRITICAL", "SCOPE_CONFIRMATION", "PREFERENCE_CONFIRMATION",
}
KNOWN_ANSWER_TYPES = {"FREE_TEXT", "SINGLE_CHOICE", "DATE", "MONEY",
                      "BOOLEAN", "LOCATION"}
REQUIRED_RULE_IDS = {f"CLARIFY-{n:03d}" for n in range(1, 7)}
RULE_FIELDS = ("rule_id", "title", "rule", "enforcement")
INTENT_REQUIRED = ["intent_id", "tenant_id", "client_actor_id",
                   "organization_id", "intent_type", "objective",
                   "authority_scope", "confidence_state", "created_at"]
CLARIFICATION_REQUIRED = ["clarification_id", "intent_id", "requesting_actor",
                          "question_type", "question", "why_needed",
                          "blocking", "expected_answer_type", "created_at"]


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


def _check_required(schema: dict, required: list[str], name: str,
                    errors: list[str]) -> None:
    props = set(schema.get("properties", {}))
    missing_props = [r for r in required if r not in props]
    if missing_props:
        errors.append(f"{name}: missing properties {missing_props}")
    required_declared = set(schema.get("required", []))
    missing_required = [r for r in required if r not in required_declared]
    if missing_required:
        errors.append(f"{name}: missing required fields {missing_required}")


def validate_intent_schema(errors: list[str]) -> None:
    ok, schema = _load_schema("intent_contract.schema.json")
    if not ok:
        errors.append(schema.get("error", "intent schema invalid"))
        return
    _check_required(schema, INTENT_REQUIRED, "intent_contract.schema.json",
                    errors)
    props = schema["properties"]
    # user assertions must be labeled ASSERTION
    assertions = props.get("user_assertions", {}).get("items", {})
    if assertions.get("properties", {}).get("status", {}).get("const") != "ASSERTION":
        errors.append("intent schema: user_assertions.status must be const ASSERTION")
    # raw conversation must be refs, never embedded transcript
    if props.get("source_conversation_refs", {}).get("type") != "array":
        errors.append("intent schema: source_conversation_refs must be an array of refs")
    # known facts must be refs
    if props.get("known_facts_refs", {}).get("type") != "array":
        errors.append("intent schema: known_facts_refs must be an array of refs")
    # authority scope must be explicit
    if "authority_scope" not in props:
        errors.append("intent schema: authority_scope must be explicit")
    # open questions must remain visible
    if props.get("open_questions", {}).get("type") != "array":
        errors.append("intent schema: open_questions must be an array")


def validate_clarification_schema(errors: list[str]) -> None:
    ok, schema = _load_schema("clarification_request.schema.json")
    if not ok:
        errors.append(schema.get("error", "clarification schema invalid"))
        return
    _check_required(schema, CLARIFICATION_REQUIRED,
                    "clarification_request.schema.json", errors)
    props = schema["properties"]
    if props.get("blocking", {}).get("type") != "boolean":
        errors.append("clarification schema: blocking must be boolean")


def validate_clarification_policy(errors: list[str]) -> None:
    try:
        data = load_yaml(AGENTS_CONFIG_DIR / "clarification_policy.yaml")
    except ValidationFailure as exc:
        errors.append(str(exc))
        return
    types = set(data.get("question_types", []))
    unknown = types - KNOWN_QUESTION_TYPES
    if unknown:
        errors.append(f"unknown question types: {sorted(unknown)}")
    missing_types = KNOWN_QUESTION_TYPES - types
    if missing_types:
        errors.append(f"missing question types: {sorted(missing_types)}")
    answer_types = set(data.get("expected_answer_types", []))
    unknown_answers = answer_types - KNOWN_ANSWER_TYPES
    if unknown_answers:
        errors.append(f"unknown expected answer types: {sorted(unknown_answers)}")
    rules = data.get("rules", [])
    seen: set[str] = set()
    for rule in rules:
        rid = rule.get("rule_id")
        if not rid:
            errors.append("clarification rule missing rule_id")
            continue
        missing = [f for f in RULE_FIELDS if f not in rule]
        if missing:
            errors.append(f"{rid}: missing fields {missing}")
        if rid in seen:
            errors.append(f"{rid}: duplicate rule id")
        seen.add(rid)
    if seen != REQUIRED_RULE_IDS:
        errors.append(f"clarification rules must be exactly "
                      f"{sorted(REQUIRED_RULE_IDS)}; got {sorted(seen)}")
    effects = data.get("blocking_effects", {})
    if effects.get("eligibility_critical_unanswered") != \
            "BLOCK_ELIGIBILITY_AND_DRAFT_READINESS":
        errors.append("blocking_effects.eligibility_critical_unanswered must "
                      "BLOCK_ELIGIBILITY_AND_DRAFT_READINESS")
    esc = data.get("escalation", {})
    if not esc.get("max_repeat_blocking_questions"):
        errors.append("escalation.max_repeat_blocking_questions required")
    if not esc.get("escalation_flow"):
        errors.append("escalation.escalation_flow required")


def main() -> int:
    errors: list[str] = []
    validate_intent_schema(errors)
    validate_clarification_schema(errors)
    validate_clarification_policy(errors)
    _, report = finish("intent_clarification", not errors, {
        "errors": errors,
        "schemas": ["intent_contract", "clarification_request"],
        "policy": "clarification_policy.yaml",
    })
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
