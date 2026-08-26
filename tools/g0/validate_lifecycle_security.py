#!/usr/bin/env python3
"""G0-B6-C20-C24 — validate_lifecycle_security.

Validates the lifecycle, break-glass, revocation, observability and
threat-model policies. Exit 0 when valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

LIF_RULES = tuple(f"LIF-{i:03d}" for i in range(1, 8))
BG_RULES = tuple(f"BG-{i:03d}" for i in range(1, 7))
REV_RULES = tuple(f"REV-{i:03d}" for i in range(1, 6))
OBS_RULES = tuple(f"OBS-{i:03d}" for i in range(1, 7))

TOKEN_STATES = {"ISSUED", "ACTIVE", "EXPIRING", "EXPIRED", "REVOKED",
                "ROTATED", "COMPROMISED"}
BG_PURPOSES = {"tenant_lockout_recovery", "security_incident_containment",
               "service_restoration", "corrupted_authorization_state_repair"}
REVOCABLES = {"principal", "membership", "capability_grant",
              "service_identity", "credential", "tool_version",
              "integration", "approval_token", "model_provider_route"}
ALERT_CLASSES = {"INFO", "WARNING", "HIGH", "CRITICAL_P0"}
OBS_SIGNALS = {"auth_failure", "denied_authorization", "cross_tenant_attempt",
               "secret_redaction_hit", "tool_call",
               "unusual_destination_attempt", "prompt_injection_detection",
               "revoked_token_use", "approval_failure",
               "parser_quarantine_failure", "ssrf_block", "break_glass_use"}


def validate(errors: list[str] | None = None,
             lifecycle: dict | None = None,
             obs: dict | None = None,
             threat: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    lifecycle = lifecycle if lifecycle is not None else load_yaml(
        _ROOT / "config/g0/security/lifecycle_policy.yaml")
    obs = obs if obs is not None else load_yaml(
        _ROOT / "config/g0/security/observability_policy.yaml")
    threat = threat if threat is not None else load_yaml(
        _ROOT / "config/g0/security/threat_model.yaml")

    # lifecycle rules (lifecycle + break-glass + revocation sections)
    lif_ids = {r.get("id") for r in lifecycle.get("rules", [])}
    lif_ids |= {r.get("id") for r in lifecycle.get("break_glass_rules", [])}
    lif_ids |= {r.get("id") for r in lifecycle.get("revocation_rules", [])}
    for rid in LIF_RULES + BG_RULES + REV_RULES:
        if rid not in lif_ids:
            errors.append(f"lifecycle policy missing rule {rid}")
            ok = False
    states = set(lifecycle.get("token_lifecycle_states", []))
    if not TOKEN_STATES.issubset(states):
        errors.append("lifecycle policy missing token states "
                      f"{TOKEN_STATES - states}")
        ok = False
    purposes = set(lifecycle.get("break_glass_purposes", []))
    if not BG_PURPOSES.issubset(purposes):
        errors.append("break-glass purposes incomplete "
                      f"{BG_PURPOSES - purposes}")
        ok = False
    revocables = set(lifecycle.get("revocable_objects", []))
    if not REVOCABLES.issubset(revocables):
        errors.append("revocable objects incomplete "
                      f"{REVOCABLES - revocables}")
        ok = False
    if not lifecycle.get("cache_policy", {}).get(
            "revocation_invalidation_bound_seconds"):
        errors.append("lifecycle policy must define a revocation "
                      "invalidation bound (REV-005)")
        ok = False

    # observability
    obs_ids = {r.get("id") for r in obs.get("rules", [])}
    for rid in OBS_RULES:
        if rid not in obs_ids:
            errors.append(f"observability policy missing rule {rid}")
            ok = False
    signals = set(obs.get("signal_classes", []))
    if not OBS_SIGNALS.issubset(signals):
        errors.append("observability signals incomplete "
                      f"{OBS_SIGNALS - signals}")
        ok = False
    if not ALERT_CLASSES.issubset(set(obs.get("alert_classes", []))):
        errors.append("alert classes must include INFO/WARNING/HIGH/"
                      "CRITICAL_P0")
        ok = False
    if "secret_redaction_hit" not in obs.get("class_thresholds", {}):
        errors.append("secret_redaction_hit must map to an alert class")
        ok = False

    # threat model
    if len(threat.get("p0_threats", [])) < 6:
        errors.append("threat model must register at least 6 P0 threats")
        ok = False
    if len(threat.get("threat_classes", [])) != 10:
        errors.append("threat model must define 10 threat classes")
        ok = False
    for t in threat.get("p0_threats", []):
        for f in ("attack", "control", "detection", "residual_risk"):
            if f not in t:
                errors.append(f"P0 threat {t.get('id')} missing {f}")
                ok = False
    return ok, {
        "lifecycle_rules": len(lif_ids),
        "token_states": len(states),
        "bg_purposes": len(purposes),
        "revocables": len(revocables),
        "obs_signals": len(signals),
        "p0_threats": len(threat.get("p0_threats", [])),
    }


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"lifecycle/break-glass/revocation/observability/threat OK: "
          f"{details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
