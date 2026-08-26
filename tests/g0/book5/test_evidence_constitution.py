"""G0-B5-C1 — Evidence constitution tests.

EVID-LAW-001..015 are frozen as machine-readable law with fail-closed
enforcement; the validator rejects any missing/unknown/weak law.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0.validate_evidence_constitution import (  # noqa: E402
    check,
    validate,
)

CFG = yaml.safe_load(
    (_ROOT / "config/g0/evidence/evidence_constitution.yaml").read_text(
        encoding="utf-8"))


def test_all_15_laws_present():
    ids = [law["id"] for law in CFG["laws"]]
    assert ids == [f"EVID-LAW-{i:03d}" for i in range(1, 16)]


def test_every_law_has_fail_closed_or_append_only_enforcement():
    for law in CFG["laws"]:
        assert law["enforcement"] in ("FAIL_CLOSED", "APPEND_ONLY")
        assert len(law["text"]) > 20


def test_validator_passes_on_live_config():
    assert check(CFG)[0] is True


def test_missing_law_fails():
    broken = {
        "laws": [law for law in CFG["laws"] if law["id"] != "EVID-LAW-001"],
        "required_law_ids": CFG["required_law_ids"],
    }
    errors: list[str] = []
    validate(errors, cfg=broken)
    assert any("missing required laws" in e for e in errors)


def test_unknown_law_fails():
    broken = dict(CFG)
    broken["laws"] = CFG["laws"] + [
        {"id": "EVID-LAW-099", "name": "phantom", "text": "x" * 30,
         "enforcement": "FAIL_CLOSED"}]
    errors: list[str] = []
    validate(errors, cfg=broken)
    assert any("unknown law ids" in e for e in errors)


def test_weak_enforcement_fails():
    broken = dict(CFG)
    laws = [dict(law) for law in CFG["laws"]]
    laws[0]["enforcement"] = "BEST_EFFORT"
    broken["laws"] = laws
    errors: list[str] = []
    validate(errors, cfg=broken)
    assert any("enforcement" in e for e in errors)


def test_law_002_generated_text_not_evidence():
    law = next(l for l in CFG["laws"] if l["id"] == "EVID-LAW-002")
    assert "cannot become evidence" in law["text"]


def test_law_007_replay_uses_historical_state():
    law = next(l for l in CFG["laws"] if l["id"] == "EVID-LAW-007")
    assert "historical" in law["text"] and "substitute" in law["text"]


def test_law_014_confidence_cannot_override_contradiction():
    law = next(l for l in CFG["laws"] if l["id"] == "EVID-LAW-014")
    assert "cannot silently resolve" in law["text"]


def test_law_015_storage_replaceable():
    law = next(l for l in CFG["laws"] if l["id"] == "EVID-LAW-015")
    assert "No external framework owns" in law["text"]
