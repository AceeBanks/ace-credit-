"""B4.C22 — D1 Hermes mock-draft contract validator.

Fail-closed validation over config/g0/agents/d1_mock_draft_contract.yaml:
the MOCK_NON_SUBMISSION label, L2 ceiling, disabled submission, the seven
fixture requirements, the seven outputs, the six restrictions and the six
success metrics.
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

REQUIRED_FIXTURES = {
    "APPROVED_CLIENT_ORGANIZATION_FIXTURE",
    "BOOK3_GOVERNED_GEORGIA_OPPORTUNITY_SNAPSHOT",
    "EXACT_OPPORTUNITY_REVISION", "D0_DRAFT_CONTEXT_BUNDLE",
    "INTENT_VIA_PERSONAL_HERMES", "CEO_TASKPLAN_TASKCONTRACTS",
    "MOCK_PROPOSAL_ARTIFACT",
}
REQUIRED_OUTPUTS = {
    "VISIBLE_OPPORTUNITY_MATCH_RATIONALE",
    "VISIBLE_GRANT_FUNDER_WINNER_COMMUNITY_RESEARCH",
    "APPLICATION_BLUEPRINT", "FULL_MOCK_PROPOSAL_OR_DEFINED_SECTION_SET",
    "BUSINESS_PLAN_STRATEGY_STUB_IF_RELEVANT", "QA_REPORT",
    "CLIENT_EXPLANATION",
}
REQUIRED_RESTRICTIONS = {
    "MOCK_NON_SUBMISSION_LABEL_REQUIRED", "NO_L4_L5_ACTION",
    "UNSUPPORTED_FACTS_STAY_PLACEHOLDERS_OR_QUESTIONS",
    "NO_FABRICATED_TESTIMONIAL_OR_PARTNERSHIP",
    "EXACT_SOURCE_EVIDENCE_REFS_RETAINED",
    "SIDECHAINS_AVAILABLE_WITHOUT_ENTERING_PERSONAL_CONTEXT",
}
REQUIRED_METRICS = {
    "INTENT_SURVIVES_PERSONAL_TO_CEO_TRANSLATION",
    "CEO_EXECUTES_WITHOUT_RAW_CLIENT_TRANSCRIPT",
    "WORKER_OUTPUTS_REMAIN_BOUNDED",
    "FACTUAL_CLAIMS_TRACE_TO_BOOK3_EVIDENCE",
    "RESET_RECONSTRUCT_AFTER_GENERATION_SUCCEEDS",
    "MOCK_PROPOSAL_CONSISTENT_WITH_EXACT_OPPORTUNITY_REVISION",
}

D1_CONTRACT_PATH = AGENTS_CONFIG_DIR / "d1_mock_draft_contract.yaml"


def validate(data: dict) -> tuple[bool, dict]:
    errors: list[str] = []
    if data.get("label") != "MOCK_NON_SUBMISSION":
        errors.append("label must be MOCK_NON_SUBMISSION")
    if data.get("authority_ceiling") != "L2":
        errors.append("authority_ceiling must be L2")
    if data.get("submission") != "DISABLED":
        errors.append("submission must be DISABLED")

    fixtures = set(data.get("fixture_requirements", []))
    missing = REQUIRED_FIXTURES - fixtures
    if missing:
        errors.append(f"fixture_requirements missing: {sorted(missing)}")
    outputs = set(data.get("outputs", []))
    missing_outputs = REQUIRED_OUTPUTS - outputs
    if missing_outputs:
        errors.append(f"outputs missing: {sorted(missing_outputs)}")
    restrictions = set(data.get("restrictions", []))
    missing_restr = REQUIRED_RESTRICTIONS - restrictions
    if missing_restr:
        errors.append(f"restrictions missing: {sorted(missing_restr)}")
    metrics = set(data.get("success_metrics", []))
    missing_metrics = REQUIRED_METRICS - metrics
    if missing_metrics:
        errors.append(f"success_metrics missing: {sorted(missing_metrics)}")

    return finish("d1_contract", not errors, {
        "errors": errors,
        "fixture_requirements": len(fixtures),
        "outputs": len(outputs),
        "restrictions": len(restrictions),
        "success_metrics": len(metrics),
    })


def load() -> dict:
    return load_yaml(D1_CONTRACT_PATH)


def main() -> int:
    try:
        ok, report = validate(load())
    except ValidationFailure as exc:
        ok, report = False, {"validator": "d1_contract",
                             "status": "FAIL", "errors": [str(exc)]}
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
