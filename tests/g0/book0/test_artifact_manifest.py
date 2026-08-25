"""B0.C1 tests — R0/G0 artifact manifest validator.

Proves the manifest is structurally sound AND that the validator actually
fails on injected defects (no fake green).
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

from tools.g0.validate_artifact_manifest import validate

LIVE = Path("config/g0/ratification/artifact_manifest.yaml")


def _load_live() -> dict:
    data = yaml.safe_load((Path(__file__).resolve().parents[3] / LIVE).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _validate_copy(tmp_path: Path, data: dict):
    p = tmp_path / "artifact_manifest.yaml"
    p.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return validate(p)


def test_live_manifest_passes():
    ok, report = validate(LIVE)
    assert ok, report["errors"]
    assert report["status"] == "PASS"
    assert report["artifact_count"] >= 20
    assert report["unique_ids"] == report["artifact_count"]
    # every authority class in the declared taxonomy is exercised or the
    # taxonomy is at least fully declared
    assert len(report["authority_class_counts"]) >= 4
    assert not report["stale_content"]
    assert not report["supersession_cycles"]
    # binding candidates must exist — Book 1 cannot inherit from nothing
    assert report["authority_class_counts"].get("binding_candidate", 0) > 0
    assert report["authority_class_counts"].get("reject_ledger", 0) == 1


def test_duplicate_artifact_id_fails(tmp_path):
    data = _load_live()
    dup = copy.deepcopy(data["artifacts"][0])
    dup["path"] = "docs/grant-sector/R0_GAP_MAP_v0.1.md"  # keep path valid/unique
    data["artifacts"].append(dup)
    ok, report = _validate_copy(tmp_path, data)
    assert not ok
    assert any("duplicate artifact_id" in e for e in report["errors"])


def test_missing_referenced_file_fails(tmp_path):
    data = _load_live()
    data["artifacts"][0]["path"] = "docs/grant-sector/DOES_NOT_EXIST.md"
    ok, report = _validate_copy(tmp_path, data)
    assert not ok
    assert any("does not exist" in e for e in report["errors"])


def test_content_drift_fails(tmp_path):
    """If a pinned artifact changes after manifest pinning, validation fails."""
    data = _load_live()
    art = data["artifacts"][0]
    real_sha = art["blob_sha"]
    art["blob_sha"] = "0" * 40
    ok, report = _validate_copy(tmp_path, data)
    assert not ok
    assert any("drift" in e for e in report["errors"])
    art["blob_sha"] = real_sha
    ok, _ = _validate_copy(tmp_path, data)
    assert ok  # restoring truth restores PASS — proves the check is live


def test_supersession_cycle_fails(tmp_path):
    data = _load_live()
    a = data["artifacts"][0]
    b = data["artifacts"][1]
    a["superseded_by"] = b["artifact_id"]
    b["superseded_by"] = a["artifact_id"]
    b["status"] = "superseded"
    ok, report = _validate_copy(tmp_path, data)
    assert not ok
    assert report["supersession_cycles"], "cycle must be detected"


def test_unknown_authority_class_fails(tmp_path):
    data = _load_live()
    data["artifacts"][0]["authority_class"] = "looks_good"
    ok, report = _validate_copy(tmp_path, data)
    assert not ok
    assert any("unknown authority_class" in e for e in report["errors"])


def test_missing_required_field_fails(tmp_path):
    data = _load_live()
    del data["artifacts"][2]["version"]
    ok, report = _validate_copy(tmp_path, data)
    assert not ok
    assert any("required field 'version'" in e for e in report["errors"])
