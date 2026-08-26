"""B4.C2-C3 — Personal and CEO Operating Contract validator.

Fail-closed validation over config/g0/agents/role_contracts.yaml:

  * Personal: fact handling must be PROPOSAL_ONLY, canonical mutation must be
    false, the submission family and CEO-only families must be prohibited,
    raw transcript history must be a forbidden context class, and the
    FACT_UPDATE_PROPOSAL output class must exist.
  * CEO: raw transcript must not be required, the contract must operate from
    INTENT_CONTRACT, unresolved critical input behavior must be
    CLARIFICATION_REQUEST, closed project chatter must be excluded by default,
    and RAW_CLIENT_TRANSCRIPT must be forbidden.
  * Both contracts declare non-empty responsibilities / non-responsibilities
    and forbidden context classes.
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
ROLE_CONTRACTS_PATH = AGENTS_CONFIG_DIR / "role_contracts.yaml"

REQUIRED_PERSONAL_PROHIBITED_PREFIXES = ["application.submit", "submission.",
                                         "research.", "opportunity."]
REQUIRED_CEO_FORBIDDEN = {"RAW_CLIENT_TRANSCRIPT", "CLOSED_PROJECT_CHATTER"}
REQUIRED_PERSONAL_FORBIDDEN = {"RAW_CLIENT_TRANSCRIPT_HISTORY",
                               "CLOSED_PROJECT_CHATTER"}


def validate(data: dict) -> tuple[bool, dict]:
    errors: list[str] = []

    personal = data.get("personal_contract")
    ceo = data.get("ceo_contract")
    if not personal:
        errors.append("personal_contract missing")
    if not ceo:
        errors.append("ceo_contract missing")

    if personal:
        if personal.get("role_ref") != "PERSONAL_HERMES":
            errors.append("personal_contract role_ref must be PERSONAL_HERMES")
        if personal.get("fact_handling") != "PROPOSAL_ONLY":
            errors.append("personal fact_handling must be PROPOSAL_ONLY")
        if personal.get("canonical_mutation_allowed") is not False:
            errors.append("personal canonical_mutation_allowed must be false")
        if not personal.get("responsibilities"):
            errors.append("personal responsibilities must be non-empty")
        if not personal.get("non_responsibilities"):
            errors.append("personal non_responsibilities must be non-empty")
        prefixes = personal.get("prohibited_capability_prefixes", [])
        for required in REQUIRED_PERSONAL_PROHIBITED_PREFIXES:
            if not any(p == required or p.startswith(required)
                       for p in prefixes):
                errors.append(f"personal must prohibit capability prefix "
                              f"'{required}'")
        forbidden = set(personal.get("forbidden_context_classes", []))
        missing = REQUIRED_PERSONAL_FORBIDDEN - forbidden
        if missing:
            errors.append(f"personal forbidden context classes missing: "
                          f"{sorted(missing)}")
        outputs = set(personal.get("output_classes", []))
        if "FACT_UPDATE_PROPOSAL" not in outputs:
            errors.append("personal output_classes must include "
                          "FACT_UPDATE_PROPOSAL")
        if not personal.get("inference_policy"):
            errors.append("personal inference_policy must be declared")

    if ceo:
        if ceo.get("role_ref") != "CEO_HERMES":
            errors.append("ceo_contract role_ref must be CEO_HERMES")
        if ceo.get("raw_transcript_required") is not False:
            errors.append("ceo raw_transcript_required must be false")
        if ceo.get("operates_from") != "INTENT_CONTRACT":
            errors.append("ceo operates_from must be INTENT_CONTRACT")
        if ceo.get("unresolved_critical_input_behavior") != "CLARIFICATION_REQUEST":
            errors.append("ceo unresolved_critical_input_behavior must be "
                          "CLARIFICATION_REQUEST")
        if ceo.get("closed_project_chatter") != "EXCLUDED_BY_DEFAULT":
            errors.append("ceo closed_project_chatter must be "
                          "EXCLUDED_BY_DEFAULT")
        if not ceo.get("responsibilities"):
            errors.append("ceo responsibilities must be non-empty")
        if not ceo.get("non_responsibilities"):
            errors.append("ceo non_responsibilities must be non-empty")
        forbidden = set(ceo.get("forbidden_context_classes", []))
        missing = REQUIRED_CEO_FORBIDDEN - forbidden
        if missing:
            errors.append(f"ceo forbidden context classes missing: "
                          f"{sorted(missing)}")
        if not ceo.get("promoted_lesson_flow"):
            errors.append("ceo promoted_lesson_flow must be declared")

    return finish("role_contracts", not errors, {
        "errors": errors,
        "personal_responsibilities": len(personal.get("responsibilities", []))
        if personal else 0,
        "ceo_responsibilities": len(ceo.get("responsibilities", [])) if ceo else 0,
        "personal_output_classes": len(personal.get("output_classes", []))
        if personal else 0,
        "ceo_output_classes": len(ceo.get("output_classes", [])) if ceo else 0,
    })


def load() -> dict:
    return load_yaml(ROLE_CONTRACTS_PATH)


def main() -> int:
    try:
        data = load()
        ok, report = validate(data)
    except ValidationFailure as exc:
        ok, report = False, {"validator": "role_contracts",
                             "status": "FAIL", "errors": [str(exc)]}
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
