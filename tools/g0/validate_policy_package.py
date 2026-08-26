"""B1.C3-C8 — Policy package validator (actors, ladder, capabilities, approvals, failures).

Cross-checks the five machine-readable registers against each other, enforcing
Book 1 invariants:

- every capability has complete policy metadata;
- every actor referenced exists and its ceiling can reach the capability;
- submission/L5/LEGALLY_MATERIAL paths are disabled in Phase 1;
- workers never gain families their contract didn't grant (checked at eval time);
- approval/failure enums resolve.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

POLICY_DIR = _ROOT / "config" / "g0" / "policy"
CAP_FIELDS = (
    "capability_id", "family", "description", "minimum_level", "allowed_actor_types",
    "resource_types", "requires_tenant_scope", "requires_project_scope",
    "approval_policy", "side_effect_class", "reversibility", "audit_class",
    "rate_limit_class", "input_schema_ref", "output_schema_ref", "failure_mode",
    "phase_status",
)
ACTOR_FIELDS = (
    "actor_type", "purpose", "default_authority_ceiling",
    "allowed_capability_families", "forbidden_capability_families",
    "requires_tenant_scope", "may_hold_credentials", "may_create_workers",
    "audit_class", "status",
)


def validate(data: dict) -> tuple[bool, dict]:
    """Validate a pre-loaded mapping {actors, ladder, capabilities, approvals,
    failures} (parsed YAML dicts)."""
    errors: list[str] = []
    actors = {a.get("actor_type"): a for a in data["actors"].get("actors", [])}
    levels = data["ladder"].get("level_order") or []
    caps = data["capabilities"].get("capabilities", [])
    approvals = {c.get("id") for c in data["approvals"].get("classes", [])}
    failures = {f.get("class_id") for f in data["failures"].get("failure_classes", [])}
    valid_audit = set(data["capabilities"].get("valid_audit_classes") or [])

    def level_rank(level: object) -> int:
        try:
            return levels.index(level)
        except ValueError:
            return -1  # unknown level ranks below everything -> fails closed

    seen_caps: set[str] = set()
    enabled_count = 0
    for cap in caps:
        cid = cap.get("capability_id")
        where = f"cap({cid})"
        if not isinstance(cap, dict):
            errors.append(f"capability[{cid}]: not a mapping")
            continue
        NULLABLE = {"input_schema_ref", "output_schema_ref"}  # schema wiring lands later
        missing = [f for f in CAP_FIELDS if f not in cap or
                   (f not in NULLABLE and cap.get(f) is None)]
        if missing:
            errors.append(f"{where}: missing fields {missing}")
        if cid in seen_caps:
            errors.append(f"{where}: duplicate capability id")
        seen_caps.add(cid)

        if cap.get("minimum_level") not in levels:
            errors.append(f"{where}: unknown minimum_level '{cap.get('minimum_level')}'")
        if cap.get("approval_policy") not in approvals:
            errors.append(f"{where}: unknown approval class '{cap.get('approval_policy')}'")
        if cap.get("failure_mode") not in failures:
            errors.append(f"{where}: unknown failure mode '{cap.get('failure_mode')}'")
        if valid_audit and cap.get("audit_class") not in valid_audit:
            errors.append(f"{where}: unknown audit class '{cap.get('audit_class')}'")

        min_level = cap.get("minimum_level")
        status = cap.get("phase_status")
        # Constitutional hard rule: nothing reaches L5 / legally-material /
        # APX while Phase 1 stands.
        if min_level == "L5" and status != "DISABLED":
            errors.append(f"{where}: L5 capability must be DISABLED in Phase 1")
        if cap.get("approval_policy") == "APX" and status != "DISABLED":
            errors.append(f"{where}: APX capability must be DISABLED in Phase 1")
        if cap.get("side_effect_class") == "LEGALLY_MATERIAL" and status != "DISABLED":
            errors.append(f"{where}: LEGALLY_MATERIAL capability must be DISABLED in Phase 1")
        if status == "ENABLED":
            enabled_count += 1
        for at in cap.get("allowed_actor_types") or []:
            if at not in actors:
                errors.append(f"{where}: references unregistered actor '{at}'")
                continue
            actor = actors[at]
            ceiling = actor.get("default_authority_ceiling")
            if ceiling != "HUMAN_SOVEREIGN" and level_rank(ceiling) < level_rank(min_level):
                errors.append(
                    f"{where}: actor '{at}' ceiling {ceiling} below required {min_level}")
            fam = cap.get("family")
            if fam in (actor.get("forbidden_capability_families") or []):
                errors.append(
                    f"{where}: family '{fam}' is forbidden for actor '{at}'")

    for aid, actor in actors.items():
        where = f"actor({aid})"
        if not isinstance(actor, dict):
            errors.append(f"{where}: not a mapping")
            continue
        missing = [f for f in ACTOR_FIELDS if actor.get(f) is None]
        if missing:
            errors.append(f"{where}: missing fields {missing}")
        if actor.get("default_authority_ceiling") not in (
                levels + ["HUMAN_SOVEREIGN"]):
            errors.append(f"{where}: unknown ceiling '{actor.get('default_authority_ceiling')}'")
        if actor.get("status") == "ACTIVE" and actor.get("may_hold_credentials") \
                and actor.get("actor_type", "").startswith("ACTOR-HERMES"):
            errors.append(f"{where}: conversational actor holding credentials (LAW-B1-014)")
        if actor.get("may_create_workers") and aid not in ("ACTOR-HERMES-CEO",):
            errors.append(f"{where}: worker creation restricted to CEO Hermes (LAW-B1-009/010)")

    # Draft-vs-submit special rule from B1.C6: drafting must be ENABLED at <=L2.
    draft_caps = [c for c in caps if str(c.get("capability_id", "")).startswith("application.draft")]
    if not draft_caps or not any(c.get("phase_status") == "ENABLED" for c in draft_caps):
        errors.append("drafting capabilities must be ENABLED (LAW-B1-013)")

    report = {
        "ok": not errors,
        "actor_count": len(actors),
        "capability_count": len(seen_caps),
        "enabled_capability_count": enabled_count,
        "disabled_capability_count": len(seen_caps) - enabled_count,
        "errors": errors,
    }
    return report["ok"], report


def load_package() -> dict:
    return {
        "actors": load_yaml(POLICY_DIR / "actor_catalog.yaml"),
        "ladder": load_yaml(POLICY_DIR / "authority_matrix.yaml"),
        "capabilities": load_yaml(POLICY_DIR / "capability_registry.yaml"),
        "approvals": load_yaml(POLICY_DIR / "approval_matrix.yaml"),
        "failures": load_yaml(POLICY_DIR / "failure_matrix.yaml"),
    }


def main() -> int:
    ok, report = validate(load_package())
    print(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
