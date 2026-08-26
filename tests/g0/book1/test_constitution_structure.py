"""B1.C2 tests — constitutional law catalog validator.

Live catalog passes; injected defects (missing rationale, unknown enforcement
category, duplicate ID, missing law) fail closed.
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

from tools.g0.validate_constitution import validate

LIVE = Path("config/g0/policy/constitutional_laws.yaml")


def _load_live() -> dict:
    path = Path(__file__).resolve().parents[3] / LIVE
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_live_catalog_passes():
    ok, report = validate(_load_live())
    assert ok, report["errors"]
    assert report["law_count"] == 30
    assert report["unique_ids"] == 30


def test_all_30_law_ids_present_in_order():
    data = _load_live()
    ids = [law["id"] for law in data["laws"]]
    assert ids == [f"LAW-B1-{n:03d}" for n in range(1, 31)]


def test_every_law_has_required_fields():
    required = {"id", "title", "normative_statement", "rationale",
                "enforcement_category", "affected_capability_classes",
                "amendment_status"}
    for law in _load_live()["laws"]:
        assert required <= set(law), f"{law.get('id')} missing {required - set(law)}"


def test_missing_rationale_fails():
    data = copy.deepcopy(_load_live())
    del data["laws"][4]["rationale"]
    ok, report = validate(data)
    assert not ok
    assert any("rationale" in e for e in report["errors"])


def test_unknown_enforcement_category_fails():
    data = copy.deepcopy(_load_live())
    data["laws"][0]["enforcement_category"] = "vibes"
    ok, report = validate(data)
    assert not ok
    assert any("unknown enforcement_category" in e for e in report["errors"])


def test_duplicate_id_fails():
    data = copy.deepcopy(_load_live())
    data["laws"][5]["id"] = data["laws"][4]["id"]
    ok, report = validate(data)
    assert not ok
    assert any("duplicate" in e.lower() for e in report["errors"])


def test_removed_law_fails_with_gap():
    data = copy.deepcopy(_load_live())
    removed = data["laws"].pop(9)["id"]
    ok, report = validate(data)
    assert not ok
    assert removed in str(report["errors"])


def test_empty_capability_classes_fail():
    data = copy.deepcopy(_load_live())
    data["laws"][0]["affected_capability_classes"] = []
    ok, report = validate(data)
    assert not ok


def test_key_security_laws_are_frozen():
    by_id = {l["id"]: l for l in _load_live()["laws"]}
    for critical in ("LAW-B1-003", "LAW-B1-005", "LAW-B1-012", "LAW-B1-015",
                     "LAW-B1-018", "LAW-B1-030"):
        assert by_id[critical]["amendment_status"] == "FROZEN", critical
