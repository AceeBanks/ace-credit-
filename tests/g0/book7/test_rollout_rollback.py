"""B7.C22 — Shadow/canary/rollback tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.rollout import (  # noqa: E402
    RollbackRegistry,
    RolloutError,
    monitor_rollout_trigger,
    shadow_has_no_client_effect,
    validate_rollout,
)


def test_offline_and_shadow_allowed():
    assert validate_rollout(rollout_class="SHADOW",
                            submission_capable=False)["allowed"]
    assert validate_rollout(rollout_class="OFFLINE_ONLY",
                            submission_capable=False)["allowed"]
    assert validate_rollout(rollout_class="FULL",
                            submission_capable=False)["allowed"]


def test_submission_disabled_regardless_of_class():
    for cls in ("SHADOW", "FULL", "INTERNAL_CANARY"):
        r = validate_rollout(rollout_class=cls, submission_capable=True)
        assert r["allowed"] is False


def test_client_canary_requires_authorization():
    r = validate_rollout(rollout_class="BOUNDED_CLIENT_CANARY",
                         submission_capable=False)
    assert r["allowed"] is False
    r = validate_rollout(rollout_class="BOUNDED_CLIENT_CANARY",
                         submission_capable=False,
                         client_canary_authorized=True)
    assert r["allowed"] is True


def test_unknown_rollout_class_rejected():
    assert not validate_rollout(rollout_class="MAGIC",
                                submission_capable=False)["allowed"]


def test_shadow_cannot_affect_client_outcome():
    assert shadow_has_no_client_effect(
        shadow_output_used=False, shadow_affected_outcome=False)["pass"]
    assert not shadow_has_no_client_effect(
        shadow_output_used=True, shadow_affected_outcome=False)["pass"]
    assert not shadow_has_no_client_effect(
        shadow_output_used=False, shadow_affected_outcome=True)["pass"]


def test_rollback_restores_baseline_identity():
    reg = RollbackRegistry()
    reg.register_baseline(version_ref="v1", config_identity="cfg-1")
    event = reg.rollback_to(rollout_event_id="ro-1", version_ref="v1",
                            trigger_code="SECURITY_ALERT",
                            trigger_reason="p0 alert")
    assert event["config_identity"] == "cfg-1"
    assert event["restored_version_ref"] == "v1"


def test_rollback_unknown_target_fails_closed():
    reg = RollbackRegistry()
    with pytest.raises(RolloutError):
        reg.rollback_to(rollout_event_id="ro-1", version_ref="nope",
                        trigger_code="EXPLICIT", trigger_reason="manual")


def test_rollback_unknown_trigger_rejected():
    reg = RollbackRegistry()
    reg.register_baseline(version_ref="v1", config_identity="cfg-1")
    with pytest.raises(RolloutError):
        reg.rollback_to(rollout_event_id="ro-1", version_ref="v1",
                        trigger_code="WHIM", trigger_reason="x")


def test_monitor_trigger_security_p0():
    t = monitor_rollout_trigger(factuality_ok=True, security_ok=False,
                                latency_ok=True, cost_ok=True,
                                structured_output_ok=True)
    assert t == {"trigger": "SECURITY_ALERT", "severity": "P0"}


def test_monitor_trigger_factuality():
    t = monitor_rollout_trigger(factuality_ok=False, security_ok=True,
                                latency_ok=True, cost_ok=True,
                                structured_output_ok=True)
    assert t["trigger"] == "FACTUALITY_DEGRADATION"


def test_monitor_no_trigger_when_healthy():
    t = monitor_rollout_trigger(factuality_ok=True, security_ok=True,
                                latency_ok=True, cost_ok=True,
                                structured_output_ok=True)
    assert t is None


def test_monitor_cost_runaway():
    t = monitor_rollout_trigger(factuality_ok=True, security_ok=True,
                                latency_ok=True, cost_ok=False,
                                structured_output_ok=True)
    assert t["trigger"] == "LATENCY_COST_RUNAWAY"
