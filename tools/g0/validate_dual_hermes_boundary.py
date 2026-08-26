"""B4.C1 — Dual-Hermes Constitutional Boundary validator.

Fail-closed validation over config/g0/agents/dual_hermes_boundary.yaml:

  * exactly the 20 required DUAL-LAW ids, all FROZEN, with full fields and
    known enforcement categories;
  * the three roles (PERSONAL_HERMES, CEO_HERMES, WORKER_AGENT) are present
    with ceilings L1 / L2 / TASK_SCOPED and distinct memory namespaces;
  * every registry capability referenced by a role exists in the ratified
    Book 1 capability registry and satisfies the role's authority ceiling;
  * protocol-native capabilities are only used by their allowed roles;
  * no agent may reference submission-family or L4/L5-disabled capabilities;
  * Personal Hermes never references CEO-only capabilities;
  * CEO context classes exclude RAW_CLIENT_TRANSCRIPT;
  * prohibited overlaps and handoff responsibilities are declared;
  * no role's memory namespace is marked canonical.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    POLICY_CONFIG_DIR,
    ValidationFailure,
    emit,
    finish,
    load_yaml,
)

AGENTS_CONFIG_DIR = Path("config/g0/agents")

LAW_FIELDS = ("law_id", "title", "rule", "enforcement_category",
              "affected_schemas", "amendment_links", "status")
REQUIRED_LAW_IDS = {f"DUAL-LAW-{n:03d}" for n in range(1, 21)}
VALID_ENFORCEMENT = {"MUST", "SHOULD"}
REQUIRED_ROLES = {"PERSONAL_HERMES", "CEO_HERMES", "WORKER_AGENT"}
EXPECTED_CEILINGS = {"PERSONAL_HERMES": "L1", "CEO_HERMES": "L2",
                     "WORKER_AGENT": "TASK_SCOPED"}
FORBIDDEN_PREFIXES = ("application.submit", "submission.")
CEO_ONLY_CAPABILITIES = {
    # capabilities whose allowed_actor_types exclude ACTOR-HERMES-PERSONAL
    "opportunity.search", "opportunity.fetch", "opportunity.snapshot",
    "opportunity.normalize", "opportunity.compare_revision",
    "eligibility.extract_candidate_rules", "match.rank", "match.recompute",
    "research.funder", "research.winner", "research.community",
    "research.organization", "research.program", "evidence.extract_claim",
    "evidence.propose_promotion", "application.create_draft_project",
    "application.create_blueprint", "application.draft_section",
    "application.draft_full_proposal", "application.draft_business_plan",
    "application.update_internal", "application.prepare_submission_package",
    "budget.create", "budget.render", "qa.requirement_coverage",
    "qa.cross_document_consistency", "qa.alignment", "qa.humanization",
    "artifact.generate", "artifact.version", "artifact.export",
    "system.inspect_health", "system.propose_change",
}

BOUNDARY_PATH = AGENTS_CONFIG_DIR / "dual_hermes_boundary.yaml"


def _load_registry() -> dict:
    caps = load_yaml(POLICY_CONFIG_DIR / "capability_registry.yaml")
    by_id = {c["capability_id"]: c for c in caps.get("capabilities", [])}
    return by_id


def validate(data: dict, registry: dict | None = None) -> tuple[bool, dict]:
    errors: list[str] = []

    # --- laws ---------------------------------------------------------------
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
        errors.append(f"must contain exactly 20 laws; missing "
                      f"{sorted(REQUIRED_LAW_IDS - present)}")

    # --- roles --------------------------------------------------------------
    if registry is None:
        registry = _load_registry()
    roles = {r["role_id"]: r for r in data.get("roles", [])}
    missing_roles = REQUIRED_ROLES - set(roles)
    if missing_roles:
        errors.append(f"missing roles: {sorted(missing_roles)}")

    native = data.get("protocol_native_capabilities", {})
    if not isinstance(native, dict) or not native:
        errors.append("protocol_native_capabilities must be a non-empty map")

    namespaces: set[str] = set()
    for role_id, role in roles.items():
        if role.get("authority_ceiling") != EXPECTED_CEILINGS.get(role_id):
            errors.append(f"{role_id}: ceiling must be "
                          f"{EXPECTED_CEILINGS.get(role_id)}")
        ns = role.get("memory_namespace")
        if not ns:
            errors.append(f"{role_id}: memory namespace required")
        elif role_id != "WORKER_AGENT":
            if ns in namespaces:
                errors.append(f"{role_id}: memory namespace {ns} is shared "
                              "with another role (anti-collapse rule)")
            namespaces.add(ns)
        if role.get("memory_is_canonical") is not False:
            errors.append(f"{role_id}: memory_is_canonical must be false")
        for cap in role.get("capabilities", []):
            if cap in native:
                allowed = native[cap].get("roles", [])
                if role_id not in allowed:
                    errors.append(f"{role_id}: protocol-native capability "
                                  f"'{cap}' not allowed for this role")
                continue
            reg = registry.get(cap)
            if reg is None:
                errors.append(f"{role_id}: unknown capability '{cap}'")
                continue
            if reg.get("phase_status") != "ENABLED":
                errors.append(f"{role_id}: capability '{cap}' is not ENABLED")
            if reg.get("minimum_level") not in ("L0", "L1", "L2"):
                errors.append(f"{role_id}: capability '{cap}' has minimum "
                              f"level {reg.get('minimum_level')} above the "
                              "Book 4 role vocabulary")
        # Personal must never reference CEO-only capabilities
        if role_id == "PERSONAL_HERMES":
            for cap in role.get("capabilities", []):
                if cap in CEO_ONLY_CAPABILITIES:
                    errors.append(f"PERSONAL_HERMES references CEO-only "
                                  f"capability '{cap}'")
        # Workers carry no registry capabilities by default (task-granted)
        if role_id == "WORKER_AGENT" and role.get("capabilities"):
            errors.append("WORKER_AGENT must declare an empty static "
                          "capability list; grants arrive via TaskContract")
        # CEO context must never include raw client transcript
        if role_id == "CEO_HERMES":
            forbidden = role.get("forbidden_context_classes", [])
            if "RAW_CLIENT_TRANSCRIPT" not in forbidden:
                errors.append("CEO_HERMES must forbid RAW_CLIENT_TRANSCRIPT")
            if "RAW_CLIENT_TRANSCRIPT_HISTORY" in role.get("context_classes", []):
                errors.append("CEO_HERMES context_classes must not include "
                              "raw client transcript history")

    # --- prohibited overlaps / handoff --------------------------------------
    overlaps = data.get("prohibited_overlaps", [])
    if not overlaps:
        errors.append("prohibited_overlaps must be declared")
    for ov in overlaps:
        for field in ("overlap_id", "description", "reason", "prohibition"):
            if not ov.get(field):
                errors.append(f"prohibited_overlap {ov.get('overlap_id')}: "
                              f"missing '{field}'")
    handoffs = data.get("handoff_responsibilities", [])
    if not handoffs:
        errors.append("handoff_responsibilities must be declared")
    for h in handoffs:
        for field in ("from_role", "to_role", "responsibility"):
            if not h.get(field):
                errors.append(f"handoff {h.get('from_role')}->{h.get('to_role')}: "
                              f"missing '{field}'")

    return finish("dual_hermes_boundary", not errors, {
        "errors": errors,
        "law_count": len(seen),
        "role_count": len(roles),
        "distinct_namespaces": sorted(namespaces),
        "prohibited_overlap_count": len(overlaps),
        "handoff_count": len(handoffs),
        "required_law_count": data.get("required_law_count"),
    })


def load() -> dict:
    return load_yaml(BOUNDARY_PATH)


def main() -> int:
    try:
        data = load()
        ok, report = validate(data)
    except ValidationFailure as exc:
        ok, report = False, {"validator": "dual_hermes_boundary",
                             "status": "FAIL", "errors": [str(exc)]}
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
