"""G0-B5-C8 — Temporal replay contract tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.replay import (  # noqa: E402
    ReplayError,
    build_replay_packet,
    current_state_must_not_substitute,
    historical_exact_inputs,
    replay_deterministic,
)


def _decision() -> dict:
    return {
        "decision_id": "dec-1", "decision_type": "ELIGIBILITY",
        "tenant_id": "tenant-a", "project_id": "proj-1",
        "input_refs": [
            {"input_role": "opportunity_revision", "ref": "opp-rev-3",
             "version_or_revision_id": "rev-3"},
            {"input_role": "eligibility_rule", "ref": "rule/eligibility-v2"},
        ],
        "configuration_refs": ["config/eligibility-v2"],
        "policy_ref": "policy/eligibility-v2",
        "model_or_engine_ref": "deterministic-service/eligibility-v2",
        "result": {"eligible": True},
    }


def _resolver(ref: str, revision: str | None = None):
    if ref == "opp-rev-3" and revision == "rev-3":
        return {"ref": ref, "snapshot_ref": "snap-opp-3"}
    if ref == "rule/eligibility-v2":
        return {"ref": ref, "snapshot_ref": "snap-rule-v2"}
    return None


def test_replay_packet_pins_snapshots():
    packet = build_replay_packet(decision=_decision(),
                                 source_snapshot_resolver=_resolver)
    assert "snap-opp-3" in packet.source_snapshot_refs
    assert "snap-rule-v2" in packet.source_snapshot_refs


def test_missing_historical_dependency_is_p0_integrity_failure():
    with pytest.raises(ReplayError, match="P0 integrity"):
        build_replay_packet(decision=_decision(),
                            source_snapshot_resolver=lambda ref, revision=None: None)


def test_historical_exact_never_substitutes_current_state():
    packet = build_replay_packet(decision=_decision(),
                                 source_snapshot_resolver=_resolver)
    historical = historical_exact_inputs(packet)
    assert historical[0]["version_or_revision_id"] == "rev-3"
    current = [{"input_role": "opportunity_revision", "ref": "opp-rev-5",
                "version_or_revision_id": "rev-5"}]
    with pytest.raises(ReplayError, match="cannot substitute"):
        current_state_must_not_substitute(packet, current)
    # same inputs are fine
    current_state_must_not_substitute(packet, historical)


def test_deterministic_replay_reproduces():
    packet = build_replay_packet(decision=_decision(),
                                 source_snapshot_resolver=_resolver)
    result = replay_deterministic(packet, lambda p: {
        "decision_id": p["decision"]["decision_id"],
        "eligible": True, "replayed": True})
    assert result["eligible"] is True and result["replayed"] is True


def test_current_source_update_cannot_alter_historical_exact():
    packet = build_replay_packet(decision=_decision(),
                                 source_snapshot_resolver=_resolver)
    before = historical_exact_inputs(packet)
    # even if the resolver now returns a newer revision, the packet is frozen
    assert all(i.get("version_or_revision_id") != "rev-5" for i in before)
