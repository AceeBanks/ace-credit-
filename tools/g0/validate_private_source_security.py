"""G0-B3-C18-C19 — validate private-source + hostile-source security policy.

Fail-closed checks:
  * private-source registration requirements / source classes come from known
    enums and the uncertainty / identity-continuity / precedence rules are
    declared;
  * source-security threat classes and rules come from known enums; the
    source-envelope and redirect policy are declared; exfiltration and
    injection pattern lists are non-empty.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    SOURCE_CONFIG_DIR,
    ValidationFailure,
    emit,
    load_yaml,
)

KNOWN_REGISTRATION_REQUIREMENTS = {
    "issuer_ownership_verified", "relevant_pages_identified",
    "update_frequency_estimated", "terms_robots_reviewed",
    "crawler_strategy_tested", "authority_limited_to_issuer_controlled_facts",
    "historical_winners_only_where_supported",
}
KNOWN_SOURCE_CLASSES = {"OFFICIAL_ISSUER", "OFFICIAL_AGGREGATOR",
                        "OFFICIAL_TRANSACTIONAL", "OFFICIAL_STATISTICAL",
                        "TRUSTED_CURATED", "GOVERNED_WEB", "USER_PROVIDED",
                        "DERIVED_INTERNAL"}

KNOWN_THREAT_CLASSES = {
    "prompt_injection", "malicious_links", "data_exfiltration_instructions",
    "embedded_scripts", "poisoned_metadata", "malicious_documents",
    "oversized_decompression_bomb", "credential_phishing",
    "source_domain_impersonation", "ssrf_via_crawler_urls", "redirect_abuse",
}
KNOWN_SECURITY_RULES = {
    "source_content_cannot_grant_capabilities",
    "workers_receive_untrusted_data_envelope",
    "crawler_egress_restricted_by_policy",
    "raw_html_never_executes_in_trusted_context",
    "downloads_scanned_by_file_type",
    "redirects_and_domain_changes_logged",
    "credentials_never_exposed_to_source_content",
    "extraction_prompts_distinguish_instructions_from_data",
    "suspicious_content_quarantinable",
    "decisions_policy_gated_outside_source_context",
}

DECLARED_RULES = {
    "uncertainty_rule", "identity_continuity_rule", "precedence_rule",
    "source_envelope", "redirect_policy",
}


def validate_private(cfg: dict, errors: list) -> None:
    reqs = cfg.get("registration_requirements", [])
    unknown = set(reqs) - KNOWN_REGISTRATION_REQUIREMENTS
    if unknown:
        errors.append(f"unknown registration requirements: {sorted(unknown)}")
    for rule in ("uncertainty_rule", "identity_continuity_rule", "precedence_rule"):
        if not cfg.get(rule):
            errors.append(f"private policy must declare '{rule}'")
    classes = cfg.get("allowed_source_classes", [])
    unknown_c = set(classes) - KNOWN_SOURCE_CLASSES
    if unknown_c:
        errors.append(f"unknown allowed source classes: {sorted(unknown_c)}")
    if not cfg.get("optional_curated_providers"):
        errors.append("optional curated providers list must be declared")


def validate_security(cfg: dict, errors: list) -> None:
    threats = cfg.get("threat_classes", [])
    unknown = set(threats) - KNOWN_THREAT_CLASSES
    if unknown:
        errors.append(f"unknown threat classes: {sorted(unknown)}")
    rules = cfg.get("security_rules", [])
    unknown_r = set(rules) - KNOWN_SECURITY_RULES
    if unknown_r:
        errors.append(f"unknown security rules: {sorted(unknown_r)}")
    for rule in ("source_envelope", "redirect_policy"):
        if not cfg.get(rule):
            errors.append(f"security policy must declare '{rule}'")
    if not cfg.get("exfiltration_patterns"):
        errors.append("exfiltration patterns must be non-empty")
    if not cfg.get("injection_patterns"):
        errors.append("injection patterns must be non-empty")


def main() -> int:
    errors: list[str] = []
    try:
        private = load_yaml(SOURCE_CONFIG_DIR / "private_source_policy.yaml")
        security = load_yaml(SOURCE_CONFIG_DIR / "source_security_policy.yaml")
        validate_private(private, errors)
        validate_security(security, errors)
    except ValidationFailure as exc:
        errors.append(str(exc))
    ok = not errors
    return emit({
        "validator": "validate_private_source_security",
        "status": "PASS" if ok else "FAIL",
        "errors": errors,
        "registration_requirement_count": len(private.get("registration_requirements", [])),
        "threat_class_count": len(security.get("threat_classes", [])),
        "security_rule_count": len(security.get("security_rules", [])),
    })


if __name__ == "__main__":
    sys.exit(main())
