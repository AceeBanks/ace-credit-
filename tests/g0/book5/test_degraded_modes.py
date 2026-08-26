"""G0-B5-C23 — Failure & degraded modes tests.

Required coverage (plan):
- every optional component has explicit degraded behavior;
- every integrity-critical component has fail-closed behavior.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.degradation import (  # noqa: E402
    DegradationError,
    DegradationManager,
)


def test_optional_components_degrades():
    dm = DegradationManager()
    dm.set_available("graph_projection", False)
    dm.set_available("vector_store", False)
    dm.set_available("semantica", False)

    assert dm.graph_projection_status()["status"] == "DEGRADED"
    assert dm.vector_store_status()["status"] == "DEGRADED"
    assert dm.semantica_status()["status"] == "DEGRADED"
    # core canonical operation continues (no exception raised)
    assert dm.available("graph_projection") is False
    # degraded modes recorded for audit (DEG-003)
    assert len(dm.audit_trail()) == 3
    assert dm.audit_trail()[0]["mode"] == "DEGRADED"


def test_optional_component_ok_when_available():
    dm = DegradationManager()
    assert dm.graph_projection_status()["status"] == "OK"
    assert dm.audit_trail() == []


def test_provenance_write_fails_closed_for_material():
    dm = DegradationManager()
    dm.set_available("provenance_write", False)
    dm.record_with_provenance(material=False)  # non-material ok
    with pytest.raises(DegradationError):
        dm.record_with_provenance(material=True)


def test_replay_never_fabricates():
    dm = DegradationManager()
    dm.set_available("historical_evidence", False)
    with pytest.raises(DegradationError):
        dm.replay(refs=["decision:1"], corrupt=["snap:missing"])
    ok = dm.replay(refs=["decision:1"], corrupt=[])
    assert ok["integrity"] == "OK"


def test_conflicted_fact_not_auto_promoted():
    dm = DegradationManager()
    dm.set_available("contradiction_service", False)
    dm.promote_conflicted(conflict_detected=False)  # no conflict: fine
    with pytest.raises(DegradationError):
        dm.promote_conflicted(conflict_detected=True)


def test_all_integrity_critical_have_fail_closed():
    import yaml
    policy = yaml.safe_load((_ROOT / "config/g0/evidence/degraded_modes.yaml")
                            .read_text(encoding="utf-8"))
    for comp in policy["components"]:
        if comp["role"] == "INTEGRITY_CRITICAL":
            assert comp.get("fail_closed_behavior"), comp["id"]
        else:
            assert comp.get("degraded_behavior"), comp["id"]
