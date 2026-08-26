"""G0-B3-C22-C24 — validate source-health + D0 packet/harness policy.

Fail-closed checks:
  * health states and metrics come from known enums; schema-drift flow,
    historical-availability rule and hard-stale rule are declared;
  * D0 packet declares all nine sections, the output labels, the explicit
    fact states, and the five success criteria;
  * the Shadow Draft Harness flow is declared in order, model permissions are
    L2-only with no submission tooling, and the hard stop is declared.
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

KNOWN_HEALTH_STATES = {
    "HEALTHY", "DEGRADED", "FAILING", "AUTH_ERROR", "RATE_LIMITED",
    "SCHEMA_CHANGED", "DISABLED", "UNKNOWN",
}
KNOWN_METRICS = {
    "last_successful_fetch", "failure_rate", "latency", "schema_validation_rate",
    "extraction_quality_trend", "http_status_distribution", "rate_limit_events",
    "content_change_frequency", "duplicate_rate", "stale_source_count",
    "downstream_invalidations",
}

REQUIRED_PACKET_SECTIONS = [
    "client_profile_fixture", "georgia_opportunity", "opportunity_requirements",
    "eligibility", "funder_program_research", "historical_winner_award_research",
    "community_impact_statistics", "budget_assumptions", "proposal_profile",
]
REQUIRED_OUTPUT_LABELS = {"MOCK", "NON_SUBMISSION", "NOT_CLIENT_APPROVED_FINAL"}
REQUIRED_FACT_STATES = {"NEEDS_CLIENT_INPUT", "NEEDS_SOURCE", "PROVISIONAL",
                        "UNSUPPORTED_DO_NOT_USE"}
REQUIRED_SUCCESS_CRITERIA = {
    "exact_source_revision_visible", "material_claims_traceable",
    "requirement_coverage_measurable",
    "no_agent_memory_required_for_reconstruction", "regenerable_from_packet",
}
REQUIRED_HARNESS_FLOW = [
    "d0_data_packet", "application_blueprint_generator",
    "requirement_to_section_map", "evidence_retrieval_from_packet",
    "draft_section_generator", "factuality_citation_check",
    "requirement_coverage_check", "cross_section_consistency",
    "mock_proposal_artifact", "d0_qa_report",
]


def validate_health(cfg: dict, errors: list) -> None:
    states = set(cfg.get("health_states", []))
    unknown = states - KNOWN_HEALTH_STATES
    if unknown:
        errors.append(f"unknown health states: {sorted(unknown)}")
    missing = KNOWN_HEALTH_STATES - states
    if missing:
        errors.append(f"health states missing: {sorted(missing)}")
    metrics = set(cfg.get("metrics", []))
    unknown_m = metrics - KNOWN_METRICS
    if unknown_m:
        errors.append(f"unknown metrics: {sorted(unknown_m)}")
    for rule in ("schema_drift_flow", "historical_availability_rule",
                 "hard_stale_rule"):
        if not cfg.get(rule):
            errors.append(f"health policy must declare '{rule}'")


def validate_d0(cfg: dict, errors: list) -> None:
    sections = cfg.get("packet_sections", [])
    if sections != REQUIRED_PACKET_SECTIONS:
        errors.append("packet_sections must be exactly the nine required sections")
    labels = set(cfg.get("output_labels", []))
    if labels != REQUIRED_OUTPUT_LABELS:
        errors.append("output labels must be MOCK, NON_SUBMISSION, NOT_CLIENT_APPROVED_FINAL")
    states = set(cfg.get("fact_states", []))
    if states != REQUIRED_FACT_STATES:
        errors.append("fact states must be exactly the four explicit states")
    criteria = set(cfg.get("success_criteria", []))
    missing_c = REQUIRED_SUCCESS_CRITERIA - criteria
    if missing_c:
        errors.append(f"success criteria missing: {sorted(missing_c)}")
    flow = cfg.get("harness_flow", [])
    if flow != REQUIRED_HARNESS_FLOW:
        errors.append("harness_flow must be exactly the ten specified stages in order")
    perms = cfg.get("model_permissions", [])
    if "L2_INTERNAL_ONLY" not in perms or "NO_EMAIL_SEND_SUBMISSION" not in perms:
        errors.append("model permissions must be L2 internal only with no "
                      "email/send/submission tools")
    if not cfg.get("hard_stop"):
        errors.append("hard stop must be declared (D0 is never submission-ready)")


def main() -> int:
    errors: list[str] = []
    try:
        health = load_yaml(SOURCE_CONFIG_DIR / "source_health_policy.yaml")
        d0 = load_yaml(SOURCE_CONFIG_DIR / "d0_data_packet.yaml")
        validate_health(health, errors)
        validate_d0(d0, errors)
    except ValidationFailure as exc:
        errors.append(str(exc))
    ok = not errors
    return emit({
        "validator": "validate_health_d0",
        "status": "PASS" if ok else "FAIL",
        "errors": errors,
        "health_state_count": len(health.get("health_states", [])),
        "packet_section_count": len(d0.get("packet_sections", [])),
        "harness_stage_count": len(d0.get("harness_flow", [])),
    })


if __name__ == "__main__":
    sys.exit(main())
