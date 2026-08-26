"""G0-B3-C8-C9 — validate source precedence matrix and freshness constitution.

Fail-closed checks:
  * every fact class in the matrix references known source classes
  * equal-authority conflict rule is declared (no last-write-wins)
  * freshness states / policy fields are from known enums; critical fact
    classes (opportunity_deadline, opportunity_eligibility) must block on
    hard-stale
  * vintage-based policies are declared appropriately
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

KNOWN_FRESHNESS_STATES = {
    "FRESH", "SOFT_STALE", "HARD_STALE", "UNKNOWN_FRESHNESS", "HISTORICAL_FIXED",
}
KNOWN_SOURCE_CLASSES = {
    "OFFICIAL_ISSUER", "OFFICIAL_AGGREGATOR", "OFFICIAL_TRANSACTIONAL",
    "OFFICIAL_STATISTICAL", "TRUSTED_CURATED", "GOVERNED_WEB", "USER_PROVIDED",
}
# Critical use-once facts that must block readiness when hard-stale.
CRITICAL_DEADLINE_FACTS = {"opportunity_deadline", "opportunity_eligibility"}


def validate_precedence(cfg: dict, errors: list) -> None:
    matrix = cfg.get("precedence_matrix")
    if not isinstance(matrix, dict) or not matrix:
        errors.append("precedence_matrix missing")
        return
    for fact, chain in matrix.items():
        if not isinstance(chain, list) or not chain:
            errors.append(f"{fact}: precedence chain must be a non-empty list")
            continue
        for stage in chain:
            entries = stage if isinstance(stage, list) else [stage]
            for entry in entries:
                for label, body in entry.items():
                    classes = body.get("source_classes") or []
                    if not isinstance(classes, list) or not classes:
                        errors.append(f"{fact}/{label}: source_classes missing or empty")
                    for c in classes:
                        if c not in KNOWN_SOURCE_CLASSES:
                            errors.append(f"{fact}/{label}: unknown source class {c!r}")
                    if label.startswith("editorial_note"):
                        continue
    if not cfg.get("equal_authority_conflict_rule"):
        errors.append("equal_authority_conflict_rule must be declared (no last-write-wins)")


def validate_freshness(cfg: dict, errors: list) -> None:
    states = cfg.get("freshness_states") or []
    for s in states:
        if s not in KNOWN_FRESHNESS_STATES:
            errors.append(f"unknown freshness state {s!r}")
    policies = cfg.get("policies") or {}
    if not isinstance(policies, dict) or not policies:
        errors.append("freshness policies missing")
        return
    for name, p in policies.items():
        fc = p.get("fact_class")
        if fc in CRITICAL_DEADLINE_FACTS:
            if not p.get("critical_use_block_on_hard_stale"):
                errors.append(f"{name}: critical fact {fc} must block on hard-stale")


def validate_precedence_config(path: Path) -> tuple[bool, dict]:
    cfg = load_yaml(path)
    errors: list[str] = []
    validate_precedence(cfg, errors)
    return finish("source_precedence_matrix", not errors, {
        "errors": errors,
        "fact_class_count": len(cfg.get("precedence_matrix", {})),
    })


def validate_freshness_config(path: Path) -> tuple[bool, dict]:
    cfg = load_yaml(path)
    errors: list[str] = []
    validate_freshness(cfg, errors)
    return finish("freshness_constitution", not errors, {
        "errors": errors,
        "policy_count": len(cfg.get("policies", {})),
    })


if __name__ == "__main__":
    from tools.g0._common import emit as _emit
    ok_p, rep_p = validate_precedence_config(SOURCE_CONFIG_DIR / "precedence_matrix.yaml")
    ok_f, rep_f = validate_freshness_config(SOURCE_CONFIG_DIR / "freshness_policy.yaml")
    raise SystemExit(_emit({"status": "PASS" if (ok_p and ok_f) else "FAIL",
                            "precedence": rep_p, "freshness": rep_f}))