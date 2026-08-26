"""G0-B3-C13-C14 — validate dependency invalidation + identifier verification.

Fail-closed checks against the config of truth:
  * invalidation states / verification states / methods are from known enums
  * dependency edges are declared (downstream artifacts map to upstream facts)
  * chat-claimed identifiers are UNVERIFIED, never auto-verified
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

KNOWN_INVALIDATION_STATES = {
    "CURRENT", "STALE_RECOMPUTE_REQUIRED", "STALE_REVIEW_REQUIRED",
    "INVALID", "SUPERSEDED",
}
KNOWN_VERIFICATION_STATES = {
    "UNVERIFIED", "USER_ASSERTED", "SOURCE_ASSERTED", "VERIFIED_OFFICIAL",
    "CONFLICTED", "EXPIRED/SUPERSEDED",
}
KNOWN_METHODS = {
    "USER_PROVIDED", "SOURCE_MATCH", "OFFICIAL_RECORD_MATCH",
    "GEOGRAPHY_RESOLVER", "ISSUER_PORTAL",
}


def validate_dependency(cfg: dict, errors: list) -> None:
    for s in cfg.get("invalidation_states", []):
        if s not in KNOWN_INVALIDATION_STATES:
            errors.append(f"unknown invalidation state {s!r}")
    deps = cfg.get("dependencies") or {}
    if not isinstance(deps, dict) or not deps:
        errors.append("dependency edges missing")
        return
    for artifact, upstream in deps.items():
        if not isinstance(upstream, list) or not upstream:
            errors.append(f"{artifact}: dependency must list upstream fact classes")


def validate_identifier(cfg: dict, errors: list) -> None:
    for s in cfg.get("verification_states", []):
        if s not in KNOWN_VERIFICATION_STATES:
            errors.append(f"unknown verification state {s!r}")
    for m in cfg.get("verification_methods", []):
        if m not in KNOWN_METHODS:
            errors.append(f"unknown verification method {m!r}")
    if not cfg.get("chat_claim_rule"):
        errors.append("chat-claim rule must be declared (never auto-verify)")


def validate(config: Path) -> tuple[bool, dict]:
    cfg = load_yaml(config)
    errors: list[str] = []
    validate_dependency(cfg, errors)
    validate_identifier(cfg, errors)
    return finish("validate_dependency_identifier", not errors, {
        "errors": errors,
        "invalidation_state_count": len(cfg.get("invalidation_states", [])),
        "dependency_edge_count": len(cfg.get("dependencies", {})),
        "identifier_namespace_count": len(cfg.get("identifier_namespaces", [])),
    })


if __name__ == "__main__":
    default = SOURCE_CONFIG_DIR / "dependency_identifier.yaml"
    raise SystemExit(cli_main(validate, default))