"""G0-B3-C16-C17 — validate federal + Georgia source profiles.

Fail-closed checks:
  * every profile declares the required profile fields;
  * identifier namespaces come from the LIVE Book 2 namespace catalog
    (config/g0/domain/identifier_namespaces.yaml) — a profile may never
    introduce an ungoverned namespace;
  * capture methods and freshness policy refs come from known enums;
  * federal lanes include the five required federal profiles;
  * Georgia declares the crawled-state rule and namespaced-identifier policy,
    and every Georgia lane normalizes into the shared Book 2 core domain
    (no GeorgiaGrant-style root entity).
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    DOMAIN_CONFIG_DIR,
    SOURCE_CONFIG_DIR,
    ValidationFailure,
    emit,
    load_yaml,
)
from tools.g0.validate_domain import load_identifier_namespaces  # noqa: E402

REQUIRED_PROFILE_FIELDS = [
    "name", "role", "priority_facts", "identifier_namespaces",
    "capture_method", "expected_revision_semantics", "freshness_policy_ref",
    "rate_limit_auth_notes", "fixture_examples",
]

KNOWN_CAPTURE_METHODS = {
    "API_JSON", "API_XML", "BULK_FILE", "HTML", "PDF", "DOCX", "IMAGE",
    "MANUAL_UPLOAD", "USER_FORM", "OTHER",
}

KNOWN_FRESHNESS_REFS = {
    "active_opportunity", "durable_low_frequency", "historical_fixed",
    "irs_annual_filing", "annual_statistic", "acs_saipe",
}

# Roots that must NEVER appear: the design normalizes Georgia into the shared
# Book 2 core (GrantOpportunity / Award / Organization), not a state-specific
# root entity.
FORBIDDEN_ROOT_ENTITIES = {"GeorgiaGrant", "georgia_grant"}

EXPECTED_FEDERAL_LANES = {
    "grants_gov_simpler", "sam_assistance_listings", "usaspending",
    "irs_eo_bmf_990", "census_acs_saipe",
}
EXPECTED_GEORGIA_LANES = {
    "ga_opb_grants_portal", "ga_opb_active_grant_programs", "ga_dca",
}


def _known_namespaces() -> set[str]:
    """Live namespace IDs from the Book 2 catalog — never a hardcoded copy."""
    catalog = load_identifier_namespaces()
    return {ns["namespace_id"] for ns in catalog.get("namespaces", [])}


def validate_profiles(data: dict, errors: list, context: str,
                      namespaces: set[str]) -> None:
    profiles = data.get("source_profiles") or {}
    if not isinstance(profiles, dict) or not profiles:
        errors.append(f"{context}: source_profiles missing or empty")
        return
    for pid, p in profiles.items():
        for f in REQUIRED_PROFILE_FIELDS:
            if f not in p:
                errors.append(f"{context}/{pid}: missing profile field '{f}'")
        namespaces_used = p.get("identifier_namespaces") or []
        for ns in namespaces_used:
            if ns not in namespaces:
                errors.append(
                    f"{context}/{pid}: unknown identifier namespace {ns!r} "
                    f"(not in Book 2 catalog)")
        if p.get("capture_method") not in KNOWN_CAPTURE_METHODS:
            errors.append(f"{context}/{pid}: unknown capture_method "
                          f"{p.get('capture_method')!r}")
        if p.get("freshness_policy_ref") not in KNOWN_FRESHNESS_REFS:
            errors.append(f"{context}/{pid}: unknown freshness_policy_ref "
                          f"{p.get('freshness_policy_ref')!r}")


def validate_federal(data: dict, errors: list,
                     namespaces: set[str] | None = None) -> None:
    if namespaces is None:
        namespaces = _known_namespaces()
    validate_profiles(data, errors, "federal", namespaces)
    have = set((data.get("source_profiles") or {}).keys())
    missing = EXPECTED_FEDERAL_LANES - have
    if missing:
        errors.append(f"federal profiles missing expected lanes: {sorted(missing)}")


def validate_georgia(data: dict, errors: list,
                     namespaces: set[str] | None = None) -> None:
    if namespaces is None:
        namespaces = _known_namespaces()
    validate_profiles(data, errors, "georgia", namespaces)
    if not data.get("crawled_state_rule"):
        errors.append("georgia crawled-state rule must be declared "
                      "(capture then normalize then promote; no crawling "
                      "directly into CanonicalFact)")
    if not data.get("georgia_identifier_policy"):
        errors.append("georgia identifier policy must be declared "
                      "(portal IDs stored as namespaced external identifiers)")
    have = set((data.get("source_profiles") or {}).keys())
    missing = EXPECTED_GEORGIA_LANES - have
    if missing:
        errors.append(f"georgia profiles missing expected lanes: {sorted(missing)}")
    # No state-specific root entity: Georgia sources normalize into the shared
    # Book 2 core. Declared profile identifiers/keys must not smuggle in one.
    lower_keys = {str(k).lower() for k in profiles_keys(data)}
    for bad in FORBIDDEN_ROOT_ENTITIES:
        if bad.lower() in lower_keys:
            errors.append(f"georgia profile declares forbidden root entity "
                          f"'{bad}' — must normalize into Book 2 core entities")


def profiles_keys(data: dict) -> list:
    profiles = data.get("source_profiles") or {}
    return list(profiles.keys()) if isinstance(profiles, dict) else []


def main() -> int:
    errors: list[str] = []
    try:
        federal = load_yaml(SOURCE_CONFIG_DIR / "federal_profiles.yaml")
        georgia = load_yaml(SOURCE_CONFIG_DIR / "georgia_profiles.yaml")
        namespaces = _known_namespaces()
        validate_federal(federal, errors, namespaces)
        validate_georgia(georgia, errors, namespaces)
    except ValidationFailure as exc:
        errors.append(str(exc))
    ok = not errors
    report = {
        "validator": "validate_source_profiles",
        "status": "PASS" if ok else "FAIL",
        "errors": errors,
        "federal_profile_count": len(federal.get("source_profiles", {})),
        "georgia_profile_count": len(georgia.get("source_profiles", {})),
        "georgia_crawled_state_rule": bool(georgia.get("crawled_state_rule")),
        "namespace_catalog": "config/g0/domain/identifier_namespaces.yaml",
    }
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
