"""G0-B7-C22 — Shadow, canary, rollout & rollback.

G0 does not need unsafe autonomous production experimentation. Rollout
classes: OFFLINE_ONLY, SHADOW, INTERNAL_CANARY, BOUNDED_CLIENT_CANARY,
FULL. Consequential external submission stays disabled regardless of
class. Rollback restores the known baseline configuration/version without
depending on agent memory (EVAL-LAW-009).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

ROLLOUT_CLASSES = ("OFFLINE_ONLY", "SHADOW", "INTERNAL_CANARY",
                   "BOUNDED_CLIENT_CANARY", "FULL")

ROLLBACK_TRIGGERS = ("HARD_GATE_FAILURE", "FACTUALITY_DEGRADATION",
                     "SECURITY_ALERT", "LATENCY_COST_RUNAWAY",
                     "STRUCTURED_OUTPUT_FAILURE", "HUMAN_QUALITY_REGRESSION",
                     "EXPLICIT")


class RolloutError(ValueError):
    """Raised when a rollout/rollback contract is violated."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_rollout(*, rollout_class: str, submission_capable: bool,
                     client_canary_authorized: bool = False) -> dict:
    """Rollout class validation; external submission disabled regardless of
    class; BOUNDED_CLIENT_CANARY requires explicit future authorization."""
    if rollout_class not in ROLLOUT_CLASSES:
        return {"allowed": False, "reason": f"unknown rollout class "
                                            f"{rollout_class!r}"}
    if submission_capable:
        return {"allowed": False,
                "reason": "consequential external submission remains disabled "
                          "regardless of rollout class"}
    if rollout_class == "BOUNDED_CLIENT_CANARY" and not client_canary_authorized:
        return {"allowed": False,
                "reason": "BOUNDED_CLIENT_CANARY requires explicit "
                          "authorization and is limited to low-risk "
                          "reversible behavior"}
    return {"allowed": True, "rollout_class": rollout_class}


def shadow_has_no_client_effect(*, shadow_output_used: bool,
                                shadow_affected_outcome: bool) -> dict:
    """SHADOW: candidate observes same inputs or replays traces but cannot
    affect client outcome."""
    if shadow_affected_outcome:
        return {"pass": False,
                "reason": "shadow candidate affected a client outcome"}
    if shadow_output_used:
        return {"pass": False,
                "reason": "shadow output was consumed as production truth"}
    return {"pass": True, "shadow_safe": True}


class RollbackRegistry:
    """Versioned rollback store: every promoted change has a rollback path
    that restores the exact previous configuration identity."""

    def __init__(self) -> None:
        self._baselines: dict[str, dict] = {}
        self._events: dict[str, dict] = {}

    def register_baseline(self, *, version_ref: str,
                          config_identity: str) -> None:
        self._baselines[version_ref] = {
            "version_ref": version_ref,
            "config_identity": config_identity,
            "registered_at": _now(),
        }

    def rollback_to(self, *, rollout_event_id: str, version_ref: str,
                    trigger_code: str, trigger_reason: str) -> dict:
        """Rollback restores the known baseline — never agent memory."""
        if trigger_code not in ROLLBACK_TRIGGERS:
            raise RolloutError(f"unknown rollback trigger {trigger_code!r}")
        baseline = self._baselines.get(version_ref)
        if baseline is None:
            raise RolloutError(
                f"rollback target {version_ref} not registered; rollback "
                "must not depend on agent memory (EVAL-LAW-009)")
        event = {
            "rollback_event_id": f"rb-{len(self._events) + 1}",
            "rollout_event_id": rollout_event_id,
            "restored_version_ref": version_ref,
            "trigger_code": trigger_code,
            "trigger_reason": trigger_reason,
            "config_identity": baseline["config_identity"],
            "rolled_back_at": _now(),
        }
        self._events[event["rollback_event_id"]] = event
        return event

    def last_rollback(self) -> dict | None:
        if not self._events:
            return None
        return self._events[max(self._events)]


def monitor_rollout_trigger(*, factuality_ok: bool, security_ok: bool,
                            latency_ok: bool, cost_ok: bool,
                            structured_output_ok: bool) -> dict | None:
    """C22: triggers may include hard-gate failure, factuality degradation,
    security alert, latency/cost runaway, structured-output failure."""
    if not security_ok:
        return {"trigger": "SECURITY_ALERT", "severity": "P0"}
    if not factuality_ok:
        return {"trigger": "FACTUALITY_DEGRADATION", "severity": "P1"}
    if not structured_output_ok:
        return {"trigger": "STRUCTURED_OUTPUT_FAILURE", "severity": "P1"}
    if not latency_ok or not cost_ok:
        return {"trigger": "LATENCY_COST_RUNAWAY", "severity": "P2"}
    return None
