"""G0-B6-C1 — Security constitution tests.

All 20 laws present, fail-closed enforcement, no drift from the plan's law
list, and defect injection flips validation.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0.validate_security_constitution import (  # noqa: E402
    check,
    validate,
)

PLAN_LAW_IDS = [f"SEC-LAW-{i:03d}" for i in range(1, 21)]


@pytest.fixture(scope="module")
def config() -> dict:
    from tools.g0._common import load_yaml
    return load_yaml(_ROOT / "config/g0/security/security_constitution.yaml")


def test_all_plan_laws_present(config):
    ids = [l["id"] for l in config["laws"]]
    assert ids == PLAN_LAW_IDS


def test_laws_have_required_fields(config):
    for law in config["laws"]:
        assert law["name"]
        assert len(law["text"]) >= 20
        assert law["enforcement"] == "FAIL_CLOSED"


def test_key_laws_text_present(config):
    by_id = {l["id"]: l for l in config["laws"]}
    assert "prompt compliance is not a security boundary" in \
        by_id["SEC-LAW-007"]["text"].lower()
    assert "raw secrets" in by_id["SEC-LAW-006"]["text"].lower()
    assert "workers never inherit parent authority" in \
        by_id["SEC-LAW-005"]["text"].lower()


def test_validator_ok(config):
    assert check(config)[0] is True


def test_defect_injection_missing_law(config):
    bad = copy.deepcopy(config)
    bad["laws"] = [l for l in bad["laws"] if l["id"] != "SEC-LAW-011"]
    errors = []
    validate(errors, cfg=bad)
    assert errors
    assert check(bad)[0] is False


def test_defect_injection_unknown_law(config):
    bad = copy.deepcopy(config)
    bad["laws"].append({"id": "SEC-LAW-099", "name": "x",
                        "text": "a law that should not exist",
                        "enforcement": "FAIL_CLOSED"})
    assert check(bad)[0] is False
