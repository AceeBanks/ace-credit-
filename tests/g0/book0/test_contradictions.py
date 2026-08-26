"""B0.C3 tests — contradiction ledger validator.

Live-ledger pass plus adversarial fixtures: an OPEN P0 must fail the gate,
phantom lineage must fail, unknown enums must fail.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from tools.g0.validate_contradictions import validate

LIVE = Path("config/g0/contradiction_ledger.yaml")


def _load_live() -> dict:
    path = (Path(__file__).resolve().parents[3]
            / "config/g0/ratification/contradiction_ledger.yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_live_ledger_passes_with_zero_open_p0():
    ok, report = validate(_load_live())
    assert ok, report["errors"]
    assert report["open_p0"] == []
    assert report["unique_ids"] == report["contradiction_count"]


def test_all_ten_mandated_probes_present():
    data = _load_live()
    ids = {c["contradiction_id"] for c in data["contradictions"]}
    for cid in [f"CD-{i:03d}" for i in range(1, 11)]:
        assert cid in ids, f"mandated probe {cid} missing"


def test_every_entry_resolved():
    for c in _load_live()["contradictions"]:
        assert c["status"] == "RESOLVED", f"{c['contradiction_id']} still open"


# ---------- negative / adversarial fixtures ----------

def _mutate(fn) -> dict:
    data = _load_live()
    fn(data)
    return data


def test_open_p0_fails_gate():
    def inject(data):
        p1 = next(c for c in data["contradictions"] if c["severity"] == "P1")
        p1["severity"] = "P0"
        p1["status"] = "OPEN"
        p1.pop("resolution", None)
    ok, report = validate(_mutate(inject))
    assert not ok
    assert any("GATE VIOLATION" in e for e in report["errors"])
    assert report["open_p0"]


def test_open_p1_does_not_fail_gate_but_is_visible():
    def inject(data):
        p1 = next(c for c in data["contradictions"] if c["severity"] == "P1")
        p1["status"] = "OPEN"
        p1["resolution"] = ""
    ok, report = validate(_mutate(inject))
    assert not ok  # empty resolution is itself a hard failure
    assert any("missing or empty required field 'resolution'" in e
               for e in report["errors"])


def test_phantom_source_fails():
    def inject(data):
        data["contradictions"][0]["source_a"].append("GS-PHANTOM-404")
    ok, report = validate(_mutate(inject))
    assert not ok
    assert any("does not resolve" in e for e in report["errors"])


def test_phantom_affected_decision_fails():
    def inject(data):
        data["contradictions"][0]["affected_decisions"] = ["DEC-NOT-REAL"]
    ok, report = validate(_mutate(inject))
    assert not ok
    assert any("DEC-NOT-REAL" in e and "decision register" in e for e in report["errors"])


def test_unknown_severity_fails():
    def inject(data):
        data["contradictions"][0]["severity"] = "P9"
    ok, _ = validate(_mutate(inject))
    assert not ok


def test_unknown_status_fails():
    def inject(data):
        data["contradictions"][0]["status"] = "MAYBE"
    ok, _ = validate(_mutate(inject))
    assert not ok


def test_duplicate_contradiction_id_fails():
    def inject(data):
        data["contradictions"].append(dict(data["contradictions"][0]))
    ok, report = validate(_mutate(inject))
    assert not ok
    assert any("duplicate contradiction_id" in e for e in report["errors"])
