"""B4.C20-C21 — Feedback / co-adaptation validator.

Fail-closed validation over config/g0/agents/feedback_policy.yaml: the seven
feedback types, the six-stage flow, the type->routing map (all seven types
covered, no unknown targets), the four FEEDBACK rules, and the co-adaptation
metrics.
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

REQUIRED_FEEDBACK_TYPES = {
    "INTENT_MISUNDERSTOOD", "FACTUAL_CORRECTION", "PREFERENCE_CORRECTION",
    "ARTIFACT_REVISION_REQUEST", "PRIORITY_CHANGE",
    "PROJECT_CANCELLATION_PAUSE", "RESULT_DISAGREEMENT",
}
REQUIRED_FLOW = [
    "CLIENT_CORRECTION", "PERSONAL_HERMES", "CLASSIFY_FEEDBACK",
    "ROUTE_TO_AMENDMENT_OR_PROPOSAL_OR_SUPERSESSION",
    "CEO_NOTIFY_IF_OPERATIONAL_IMPACT", "SELECTIVE_REPLAN_RECOMPUTE",
]
VALID_ROUTING_TARGETS = {
    "INTENT_AMENDMENT", "FACT_PROPOSAL", "MEMORY_SUPERSESSION",
    "ARTIFACT_REVISION_REQUEST", "PROJECT_STATE_CHANGE",
    "EXPLANATION_REVIEW",
}
REQUIRED_RULES = {f"FEEDBACK-{n:03d}" for n in range(1, 5)}
REQUIRED_METRICS = {
    "CLARIFICATION_RATE", "REPEATED_MISSING_INTENT_FIELDS",
    "CEO_REPLANNING_RATE", "CLIENT_REJECTION_OF_INTENT_INTERPRETATION",
    "AVOIDABLE_CEO_QUESTIONS", "WORKER_FAILURES_FROM_INCOMPLETE_TASK_CONTRACTS",
    "CLIENT_CONFUSION_AFTER_EXPLANATION",
}


def main() -> int:
    errors: list[str] = []
    try:
        data = load_yaml(AGENTS_CONFIG_DIR / "feedback_policy.yaml")
    except ValidationFailure as exc:
        errors.append(str(exc))
        return emit(finish("feedback_loop", False, {"errors": errors})[1])

    types = set(data.get("feedback_types", []))
    if types != REQUIRED_FEEDBACK_TYPES:
        errors.append(f"feedback_types must be exactly "
                      f"{sorted(REQUIRED_FEEDBACK_TYPES)}")
    if data.get("flow") != REQUIRED_FLOW:
        errors.append("flow must be exactly the six-stage feedback flow")

    routing = data.get("routing", {})
    if set(routing) != REQUIRED_FEEDBACK_TYPES:
        errors.append("routing must cover exactly the seven feedback types")
    unknown_targets = set(routing.values()) - VALID_ROUTING_TARGETS
    if unknown_targets:
        errors.append(f"routing has unknown targets: {sorted(unknown_targets)}")
    if routing.get("FACTUAL_CORRECTION") != "FACT_PROPOSAL":
        errors.append("FACTUAL_CORRECTION must route to FACT_PROPOSAL")

    rules = data.get("rules", [])
    seen: set[str] = set()
    for rule in rules:
        rid = rule.get("rule_id")
        if not rid:
            errors.append("feedback rule missing rule_id")
            continue
        if rid in seen:
            errors.append(f"{rid}: duplicate rule id")
        seen.add(rid)
    if seen != REQUIRED_RULES:
        errors.append(f"feedback rules must be exactly "
                      f"{sorted(REQUIRED_RULES)}; got {sorted(seen)}")

    metrics = set(data.get("coadaptation_metrics", []))
    missing = REQUIRED_METRICS - metrics
    if missing:
        errors.append(f"coadaptation_metrics missing: {sorted(missing)}")

    _, report = finish("feedback_loop", not errors, {
        "errors": errors,
        "feedback_types": len(types),
        "routing_entries": len(routing),
        "coadaptation_metrics": len(metrics),
    })
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
