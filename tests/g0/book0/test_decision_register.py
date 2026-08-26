"""B0.C2 tests — decision register validator.

Proves the live register is sound AND that the validator actually fails on
injected defects: phantom lineage, unknown status, unresolved supersession
cycles, missing conditions, and category coverage gaps.
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

from tools.g0.validate_decision_register import validate

LIVE = Path("config/g0/ratification/decision_register.yaml")


def _load_live() -> dict:
    path = Path(__file__).resolve().parents[3] / LIVE
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _validate(data: dict) -> tuple[bool, dict]:
    return validate(data)


def test_live_register_passes():
    ok, report = _validate(_load_live())
    assert ok, report["errors"]
    assert report["unique_ids"] == report["decision_count"]
    assert not report["missing_categories"]


def test_every_required_category_covered():
    data = _load_live()
    covered = {d["category"] for d in data["decisions"]}
    missing = set(data["required_categories"]) - covered
    assert not missing, f"uncovered categories: {missing}"


def test_no_phantom_source_lineage():
    import yaml as _yaml
    manifest = _yaml.safe_load(
        (Path(__file__).resolve().parents[3]
         / "config/g0/ratification/artifact_manifest.yaml").read_text(encoding="utf-8"))
    known = {a["artifact_id"] for a in manifest["artifacts"]}
    for dec in _load_live()["decisions"]:
        assert dec["source_artifact_ids"], f"{dec['decision_id']} cites no artifacts"
        phantom = set(dec["source_artifact_ids"]) - known
        assert not phantom, f"{dec['decision_id']}: phantom sources {phantom}"


# ---------- negative / adversarial fixtures ----------

def _mutate(fn) -> dict:
    data = _load_live()
    fn(data)
    return data


def _drop_last_category(data):
    data["decisions"] = [d for d in data["decisions"]
                         if d["category"] != "Georgia-first"]


def test_missing_category_coverage_fails():
    ok, report = _validate(_mutate(_drop_last_category))
    assert not ok
    assert any("Georgia-first" in e for e in report["errors"])


def test_phantom_source_fails():
    def inject(data):
        data["decisions"][0]["source_artifact_ids"].append("GS-FAKE-NONEXISTENT")
    ok, report = _validate(_mutate(inject))
    assert not ok
    assert any("phantom lineage" in e for e in report["errors"])


def test_unknown_status_fails():
    def inject(data):
        data["decisions"][0]["status"] = "SURE_WHATEVER"
    ok, _ = _validate(_mutate(inject))
    assert not ok


def test_duplicate_decision_id_fails():
    def inject(data):
        dup = copy.deepcopy(data["decisions"][0])
        data["decisions"].append(dup)
    ok, report = _validate(_mutate(inject))
    assert not ok
    assert any("duplicate decision_id" in e for e in report["errors"])


def test_condition_without_conditions_fails():
    def inject(data):
        for d in data["decisions"]:
            if d["status"] == "RATIFIED_WITH_CONDITION":
                d["conditions"] = []
                return
        raise AssertionError("fixture requires a conditional decision to exist")
    ok, report = _validate(_mutate(inject))
    assert not ok
    assert any("requires at least one condition" in e for e in report["errors"])


def test_supersession_cycle_fails():
    def inject(data):
        ids = [d["decision_id"] for d in data["decisions"]]
        a, b = ids[0], ids[1]
        by_id = {d["decision_id"]: d for d in data["decisions"]}
        # DEC-LIC-001/002 pattern: pair-wise supersession would be a real cycle;
        # instead synthesize one deterministically.
        by_id[a]["supersedes_decision_id"] = b
        by_id[b]["supersedes_decision_id"] = a
    ok, report = _validate(_mutate(inject))
    assert not ok
    assert any("supersession cycle" in e for e in report["errors"])


def test_unknown_supersedes_target_fails():
    def inject(data):
        data["decisions"][0]["supersedes_decision_id"] = "DEC-DOES-NOT-EXIST"
    ok, report = _validate(_mutate(inject))
    assert not ok
    assert any("supersedes unknown decision" in e for e in report["errors"])


def test_decision_without_sources_fails():
    def inject(data):
        data["decisions"][0]["source_artifact_ids"] = []
    ok, report = _validate(_mutate(inject))
    assert not ok
    assert any("no source artifacts cited" in e for e in report["errors"])


def test_empty_statement_fails():
    def inject(data):
        data["decisions"][0]["statement"] = ""
    ok, report = _validate(_mutate(inject))
    assert not ok
