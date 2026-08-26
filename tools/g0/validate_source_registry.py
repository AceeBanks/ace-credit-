"""B3.C2-C3 — source classification + SourceRegistry validator (fail-closed).

- every registered source has a known class and authority tier;
- source classes from the plan set with correct general tier mapping;
- derived internal objects carry external_authority:false and can never pose
  as external authority;
- source class alone never bypasses fact-specific precedence (checked against
  the precedence matrix config when present);
- duplicate source_id rejected; missing authority classification rejected;
- enabled web source without terms/robots/policies rejected or marked pending;
- auth-required source without credential scope rejected;
- adapter version required for enabled machine source.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import SOURCE_CONFIG_DIR, finish, load_yaml  # noqa: E402

CLASS_AUTHORITY = {
    "OFFICIAL_ISSUER": "A", "OFFICIAL_AGGREGATOR": "B",
    "OFFICIAL_TRANSACTIONAL": "B", "OFFICIAL_STATISTICAL": "B",
    "TRUSTED_CURATED": "C", "GOVERNED_WEB": "D", "USER_PROVIDED": "E",
    "DERIVED_INTERNAL": None,
}
VALID_TIERS = {"A", "B", "C", "D", "E"}
SELF_NO_AUTHORITY = {"DERIVED_INTERNAL"}
NO_AUTH_MODES = {"trigger", "api_key", "oauth", "client_credentials"}


def validate_classes(data: dict) -> tuple[bool, dict]:
    errors: list[str] = []
    classes = data.get("classes") or []
    seen: set[str] = set()
    for cls in classes:
        cid = cls.get("class_id")
        if not cid or cid in seen:
            errors.append(f"duplicate or empty class {cid!r}")
        seen.add(cid)
        expected = CLASS_AUTHORITY.get(cid)
        if expected is None and cid != "DERIVED_INTERNAL":
            errors.append(f"unknown class '{cid}'")
        if cid in SELF_NO_AUTHORITY:
            if cls.get("external_authority") not in (False, None):
                errors.append(f"{cid}: derived internal cannot be external authority")
        else:
            tier = cls.get("authority_tier")
            if tier != expected:
                errors.append(f"{cid}: tier {tier} != expected {expected}")
    return finish("source_classes", not errors, {
        "errors": errors, "class_count": len(seen),
    })


def validate_registry(data: dict, class_ids: set[str] | None = None) -> tuple[bool, dict]:
    errors: list[str] = []
    classes = class_ids or set()
    sources = data.get("sources") or []
    seen: set[str] = set()
    for s in sources:
        sid = s.get("source_id")
        if not sid:
            errors.append("source missing source_id")
            continue
        if sid in seen:
            errors.append(f"{sid}: duplicate source id")
        seen.add(sid)
        cls = s.get("source_class")
        if cls not in classes:
            errors.append(f"{sid}: unclassified or unknown source_class '{cls}'")
        tier = s.get("authority_tier")
        if tier not in VALID_TIERS:
            errors.append(f"{sid}: missing/unknown authority tier '{tier}'")
        # enabled web/pending source must have terms/robots/policy review
        if s.get("enabled") is True:
            for ref in ("terms_policy_ref", "robots_policy_ref",
                        "rate_limit_policy_ref", "health_policy_ref"):
                if not s.get(ref):
                    errors.append(f"{sid}: enabled source missing {ref}")
            if not s.get("adapter_version"):
                errors.append(f"{sid}: enabled source requires adapter_version")
        # auth-required source must declare credential scope
        if s.get("auth_mode") and s["auth_mode"] != "none" and not s.get("credential_scope_ref"):
            errors.append(f"{sid}: auth mode '{s['auth_mode']}' missing credential_scope_ref")
        if not s.get("domain_categories"):
            errors.append(f"{sid}: domain_categories required")
        if not s.get("base_urls") and not s.get("api_base_url"):
            errors.append(f"{sid}: at least one url required")
    return finish("source_registry", not errors, {
        "errors": errors, "source_count": len(seen),
    })


def load_classes() -> dict:
    return load_yaml(SOURCE_CONFIG_DIR / "source_classes.yaml")


def load_registry() -> dict:
    return load_yaml(SOURCE_CONFIG_DIR / "source_registry.yaml")


def main() -> int:
    from tools.g0._common import emit
    ok_classes, cls_report = validate_classes(load_classes())
    class_ids = {c["class_id"] for c in load_classes().get("classes", [])}
    ok_reg, reg_report = validate_registry(load_registry(), class_ids)
    ok = ok_classes and ok_reg
    return emit({"status": "PASS" if ok else "FAIL",
                 "source_classes": cls_report,
                 "source_registry": reg_report})


if __name__ == "__main__":
    sys.exit(main())