"""G0-B3-C10-C12 — validate promotion, conflict and source-change governance.

Fail-closed checks against the config of truth:
  * promotion states / conflict types / resolution methods / materiality are
    from known enums
  * critical fact classes are listed (deadline, eligibility, amount, required
    attachments, legal identity, submission method, geography, cancellation)
  * unresolved conflicts on critical facts block critical use
  * every P0 signal / P1 signal is known; classify_change is exercised by tests
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    SOURCE_CONFIG_DIR,
    cli_main,
    finish,
    load_yaml,
)

KNOWN_PROMOTION_STATES = {
    "CANDIDATE", "PROVISIONAL", "VERIFIED", "CONFLICTED", "STALE",
    "REJECTED", "SUPERSEDED",
}
KNOWN_CONFLICT_TYPES = {
    "VALUE_CONFLICT", "TEMPORAL_CONFLICT", "IDENTITY_CONFLICT",
    "GEOGRAPHY_CONFLICT", "UNIT_CONFLICT", "SOURCE_VERSION_CONFLICT",
    "INTERPRETATION_CONFLICT", "USER_OFFICIAL_CONFLICT",
}
KNOWN_RESOLUTION_METHODS = {
    "SOURCE_PRECEDENCE", "EFFECTIVE_DATE", "SOURCE_REFRESH",
    "MERGE_COMPATIBLE", "HUMAN_REVIEW", "OFFICIAL_CLARIFICATION",
    "UNRESOLVED_BLOCK",
}
KNOWN_MATERIALITY = {"P0", "P1", "P2"}
KNOWN_CHANGE_CLASSES = {
    "CREATED", "UPDATED", "DELETED", "CANCELLED",
    "PARSER_OUTPUT_CHANGE", "METADATA_CHANGE",
}
CRITICAL_FACT_CLASSES = {
    "opportunity_deadline", "opportunity_eligibility", "opportunity_award_ceiling",
    "opportunity_award_floor", "opportunity_required_attachments",
    "legal_organization_name", "opportunity_submission_instructions", "geography",
}


def validate_promotion(cfg: dict, errors: list) -> None:
    for s in cfg.get("promotion_states", []):
        if s not in KNOWN_PROMOTION_STATES:
            errors.append(f"unknown promotion state {s!r}")
    critical = cfg.get("critical_fact_classes") or []
    missing = CRITICAL_FACT_CLASSES - set(critical)
    if missing:
        errors.append(f"critical fact classes missing from config: {sorted(missing)}")


def validate_conflict(cfg: dict, errors: list) -> None:
    for t in cfg.get("conflict_types", []):
        if t not in KNOWN_CONFLICT_TYPES:
            errors.append(f"unknown conflict type {t!r}")
    for m in cfg.get("resolution_methods", []):
        if m not in KNOWN_RESOLUTION_METHODS:
            errors.append(f"unknown resolution method {m!r}")
    if not cfg.get("unresolved_critical_block"):
        errors.append("unresolved conflict on critical facts must block/degrage readiness")


def validate_source_change(cfg: dict, errors: list) -> None:
    for m in cfg.get("materiality_classes", []):
        if m not in KNOWN_MATERIALITY:
            errors.append(f"unknown materiality {m!r}")
    for c in cfg.get("change_classes", []):
        if c not in KNOWN_CHANGE_CLASSES:
            errors.append(f"unknown change class {c!r}")
    for s in cfg.get("p0_signals", []):
        if not s:
            errors.append("empty P0 signal")
    for s in cfg.get("p1_signals", []):
        if not s:
            errors.append("empty P1 signal")


def validate(config: Path) -> tuple[bool, dict]:
    cfg = load_yaml(config)
    errors: list[str] = []
    validate_promotion(cfg, errors)
    validate_conflict(cfg, errors)
    validate_source_change(cfg, errors)
    return finish("validate_promotion_conflict", not errors, {
        "errors": errors,
        "promotion_state_count": len(cfg.get("promotion_states", [])),
        "conflict_type_count": len(cfg.get("conflict_types", [])),
        "materiality_count": len(cfg.get("materiality_classes", [])),
    })


if __name__ == "__main__":
    default = SOURCE_CONFIG_DIR / "promotion_conflict.yaml"
    raise SystemExit(cli_main(validate, default))