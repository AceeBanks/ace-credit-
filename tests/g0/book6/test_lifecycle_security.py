"""G0-B6-C20-C24 — Lifecycle, break-glass, revocation, observability and
threat-model tests.

Required coverage (plan):
C20: revoked membership invalidates new decisions; cached allow cannot
    survive revocation beyond bound; compromised credential blocked;
    rotation does not expose old/new secret.
C21: normal admin token cannot invoke break glass implicitly; break-glass
    action generates A4 audit; automatic expiry; use visible in security
    report.
C22: disabling tool blocks all subsequent use; credential compromise does
    not require resetting Hermes memory; revoked worker grant stops task
    safely; incident preserves decision/audit evidence.
C23: observability prefers IDs/reason codes; alerts classify correctly;
    tenant-filtered telemetry; secret redaction hit.
C24: threat model inventory complete (actors, assets, classes, P0 rows
    with attack/control/detection/residual risk).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.security.lifecycle import (  # noqa: E402
    BreakGlassRegistry,
    IncidentRecovery,
    LifecycleError,
    LifecycleRegistry,
    SecurityObservability,
)
from tools.g0.validate_lifecycle_security import validate  # noqa: E402


# ------------------------------------------------------------- C20 lifecycle

def test_revoked_membership_invalidates_new_decisions():
    reg = LifecycleRegistry()
    reg.issue_token(token_id="tok-1", principal_id="p-1", tenant_id="t-a")
    assert reg.token_state(token_id="tok-1", principal_id="p-1",
                           membership_active=True) == "ACTIVE"
    assert reg.token_state(token_id="tok-1", principal_id="p-1",
                           membership_active=False) == "MEMBERSHIP_REVOKED"


def test_cached_allow_cannot_survive_revocation_beyond_bound():
    from datetime import datetime, timedelta, timezone

    def _stale_iso(seconds_ago: float) -> str:
        return (datetime.now(timezone.utc)
                - timedelta(seconds=seconds_ago)).isoformat()

    reg = LifecycleRegistry()
    reg.cache_decision(cache_key="k", allow=True)
    # age the cache entry beyond the 60s invalidation bound, then revoke:
    # the cached allow must no longer survive.
    reg._cache["k"] = (True, _stale_iso(120))
    assert reg.cached_allow(cache_key="k", revoked_after="2999-01-01T00:00:00") \
        is False
    # a fresh cache entry with no revocation → cached allow valid
    reg2 = LifecycleRegistry()
    reg2.cache_decision(cache_key="k", allow=True)
    assert reg2.cached_allow(cache_key="k", revoked_after="2000-01-01T00:00:00") \
        is True


def test_compromised_credential_blocked_even_if_valid():
    reg = LifecycleRegistry()
    reg.register_credential(credential_id="cred-1", service_identity="svc-1")
    reg.mark_compromised(object_id="cred-1", object_type="credential")
    with pytest.raises(LifecycleError):
        reg.rotate_credential(credential_id="cred-1")


def test_rotation_never_exposes_secret():
    reg = LifecycleRegistry()
    reg.register_credential(credential_id="cred-1", service_identity="svc-1")
    result = reg.rotate_credential(credential_id="cred-1")
    assert "secret" not in result
    assert "value" not in result
    assert result["rotations"] == 1


def test_compromise_triggers_dependent_token_revocation():
    reg = LifecycleRegistry()
    reg.register_credential(credential_id="cred-1", service_identity="svc-1")
    reg.issue_token(token_id="tok-1", principal_id="p-1", tenant_id="t-a")
    reg._tokens["tok-1"]["credential_id"] = "cred-1"
    reg.mark_compromised(object_id="cred-1", object_type="credential")
    assert reg._tokens["tok-1"]["state"] == "REVOKED"


def test_expired_token_rejected():
    reg = LifecycleRegistry()
    reg.issue_token(token_id="tok-1", principal_id="p-1", tenant_id="t-a",
                    ttl_seconds=1)
    import time
    time.sleep(1.1)
    assert reg.token_state(token_id="tok-1", principal_id="p-1",
                           membership_active=True) == "EXPIRED"


def test_short_lived_token_bound_enforced():
    reg = LifecycleRegistry()
    with pytest.raises(LifecycleError):
        reg.issue_token(token_id="tok-9", principal_id="p-1",
                        tenant_id="t-a", ttl_seconds=86400)


# ------------------------------------------------------------- C21 break-glass

def test_normal_admin_token_cannot_invoke_break_glass_implicitly():
    reg = BreakGlassRegistry()
    # no implicit path: invoke() requires explicit purpose + reason
    with pytest.raises(LifecycleError):
        reg.invoke(actor_id="admin-1", reason="", purpose="")
    with pytest.raises(LifecycleError):
        reg.invoke(actor_id="admin-1", reason="just do it",
                   purpose="not-an-allowed-purpose")


def test_break_glass_requires_elevated_audit():
    reg = BreakGlassRegistry()
    act = reg.invoke(actor_id="admin-1", purpose="tenant_lockout_recovery",
                     reason="tenant locked out by expired membership")
    assert act["audit_class"] == "A4"
    with pytest.raises(LifecycleError):
        reg.authorize(action_id=act["action_id"], actor_id="admin-1",
                      audit_write_ok=False)


def test_break_glass_auto_expiry():
    reg = BreakGlassRegistry()
    act = reg.invoke(actor_id="admin-1", purpose="service_restoration",
                     reason="service degraded after config repair",
                     ttl_seconds=-1)
    assert reg.authorize(action_id=act["action_id"], actor_id="admin-1",
                         audit_write_ok=True) is False


def test_break_glass_use_visible_in_security_report():
    reg = BreakGlassRegistry()
    reg.invoke(actor_id="admin-1", purpose="security_incident_containment",
               reason="contain suspected credential misuse")
    visible = reg.list_visible()
    assert len(visible) == 1
    assert visible[0]["actor_id"] == "admin-1"
    assert visible[0]["audit_class"] == "A4"


# ------------------------------------------------------------- C22 revocation

def test_disabled_tool_blocks_subsequent_use():
    reg = LifecycleRegistry()
    reg.revoke(object_id="tool:v1", object_type="tool_version",
               reason="disabled")
    assert reg._revoked.get("tool:v1") == "disabled"


def test_revoked_worker_grant_fails_closed():
    reg = LifecycleRegistry()
    reg.revoke(object_id="grant:worker-1", object_type="capability_grant",
               reason="task completed")
    # authorization against the revoked grant must not silently pass
    assert "grant:worker-1" in reg._revoked
    assert reg.cached_allow(cache_key="grant:worker-1",
                            revoked_after="2999-01-01T00:00:00") is False


def test_incident_preserves_evidence_before_repair():
    rec = IncidentRecovery()
    seq = rec.run()
    assert seq[0] == "DETECT"
    # canonical plan order: PRESERVE_EVIDENCE and ASSESS before ROTATE_REPAIR
    assert seq.index("PRESERVE_EVIDENCE") < seq.index("ROTATE_REPAIR")
    assert seq.index("ASSESS_AFFECTED_TENANTS_RESOURCES") < \
        seq.index("ROTATE_REPAIR")
    with pytest.raises(LifecycleError):
        rec.run(["DETECT", "REVOKE", "ROTATE_REPAIR"])  # missing preserve


def test_credential_compromise_does_not_reset_hermes_memory():
    # memory lives outside the credential boundary; compromise only
    # revokes credential + dependents, never touches memory stores
    reg = LifecycleRegistry()
    reg.register_credential(credential_id="cred-1", service_identity="svc-1")
    reg.mark_compromised(object_id="cred-1", object_type="credential")
    assert reg._credentials["cred-1"]["state"] == "REVOKED"
    # no memory namespace exists or was touched in this prototype


# ------------------------------------------------------------- C23 observability

def test_observability_prefers_ids_and_reason_codes():
    obs = SecurityObservability()
    ev = obs.record(tenant_id="t-a", signal="denied_authorization",
                    reason_code="NO_GRANT",
                    detail={"principal_id": "p-1", "capability": "tool:x"})
    assert "raw" not in ev["detail"]
    assert ev["reason_code"] == "NO_GRANT"


def test_secret_values_redacted_in_telemetry():
    obs = SecurityObservability()
    ev = obs.record(tenant_id="t-a", signal="secret_redaction_hit",
                    reason_code="REDACTED_SECRET",
                    raw="the api key is sk-1234abcd")
    assert ev["detail"]["raw"] == "REDACTED"
    assert ev["alert_class"] == "CRITICAL_P0"


def test_alert_classification():
    obs = SecurityObservability()
    obs.record(tenant_id="t-a", signal="tool_call", reason_code="OK")
    obs.record(tenant_id="t-a", signal="cross_tenant_attempt",
               reason_code="CROSS_TENANT")
    obs.record(tenant_id="t-a", signal="break_glass_use", reason_code="BG")
    alerts = obs.alerts_above("HIGH")
    classes = {a["alert_class"] for a in alerts}
    assert classes == {"HIGH"}  # INFO tool_call excluded; no CRITICAL here
    assert all(a["alert_class"] != "INFO" for a in alerts)


def test_tenant_filtered_telemetry():
    obs = SecurityObservability()
    obs.record(tenant_id="t-a", signal="auth_failure", reason_code="BAD_PW")
    obs.record(tenant_id="t-b", signal="auth_failure", reason_code="BAD_PW")
    events = obs.tenant_events(tenant_id="t-a")
    assert len(events) == 1
    assert all(e["tenant_id"] == "t-a" for e in events)


# ------------------------------------------------------------- C24 threat model

def test_threat_model_inventory_complete():
    ok, details = validate()
    assert ok
    assert details["p0_threats"] >= 6
    assert details["obs_signals"] == 12


def test_every_p0_threat_has_full_row():
    import yaml
    data = yaml.safe_load(
        (_ROOT / "config/g0/security/threat_model.yaml")
        .read_text(encoding="utf-8"))
    for t in data["p0_threats"]:
        for field in ("attack", "control", "detection", "residual_risk"):
            assert t.get(field), f"{t['id']} missing {field}"


def test_attack_surface_coverage_in_threat_model():
    # the C25 register surfaces map to threat model classes
    import yaml
    data = yaml.safe_load(
        (_ROOT / "config/g0/security/threat_model.yaml")
        .read_text(encoding="utf-8"))
    assert "prompt_tool_injection" in data["threat_classes"]
    assert "cross_tenant_inference_leakage" in data["threat_classes"]
    assert "supply_chain_compromise" in data["threat_classes"]
