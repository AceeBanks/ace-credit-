"""B3.C1 tests — Data Constitution.

The 20 binding data laws are present and frozen; injected defects (missing
law, duplicate id, unknown enforcement category, unfrozen law) fail closed.
"""
from __future__ import annotations

import copy

from tools.g0.validate_data_constitution import load, validate


def test_live_constitution_passes():
    ok, report = validate(load())
    assert ok, report["errors"]
    assert report["law_count"] == 20
    assert report["frozen_count"] == 20


def test_all_20_laws_present_and_numbered():
    laws = {l["law_id"] for l in load()["laws"]}
    assert laws == {f"DATA-LAW-{n:03d}" for n in range(1, 21)}


def test_laws_carry_linkage_and_affected_schemas():
    for law in load()["laws"]:
        assert law["affected_schemas"]
        assert law["status"] == "FROZEN"
        assert law["enforcement_category"] in ("MUST", "SHOULD")


def test_required_first_laws_present():
    laws = {l["law_id"]: l for l in load()["laws"]}
    assert "registered-source promotion" == laws["DATA-LAW-001"]["title"].lower()
    assert "immutable source history" == laws["DATA-LAW-003"]["title"].lower()
    assert "raw hash identity" == laws["DATA-LAW-004"]["title"].lower()
    assert "ad" in laws["DATA-LAW-020"]["title"].lower()


def test_missing_law_fails():
    data = copy.deepcopy(load())
    data["laws"] = [l for l in data["laws"] if l["law_id"] != "DATA-LAW-010"]
    ok, report = validate(data)
    assert not ok
    assert any("missing ['DATA-LAW-010']" in e for e in report["errors"])


def test_duplicate_law_id_fails():
    data = copy.deepcopy(load())
    data["laws"].append(dict(data["laws"][0]))
    ok, report = validate(data)
    assert not ok
    assert any("duplicate law id" in e for e in report["errors"])


def test_unknown_enforcement_fails():
    data = copy.deepcopy(load())
    data["laws"][0]["enforcement_category"] = "MAYBE"
    ok, report = validate(data)
    assert not ok
    assert any("unknown enforcement" in e for e in report["errors"])


def test_unfrozen_law_fails():
    data = copy.deepcopy(load())
    data["laws"][0]["status"] = "DRAFT"
    ok, report = validate(data)
    assert not ok
    assert any("FROZEN" in e for e in report["errors"])