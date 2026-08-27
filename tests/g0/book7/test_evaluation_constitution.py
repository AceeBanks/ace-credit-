"""B7.C1 — Evaluation & promotion constitution tests.

Fail-closed coverage of the 15 EVAL-LAWs: exact ID set, required fields,
FAIL_CLOSED enforcement, and the non-dilution guarantees that Book 7
inherits Books 1-6 boundaries (security and privacy non-compensatory,
evidence authority, no self-promotion, no online self-modification).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0.validate_evaluation_constitution import (  # noqa: E402
    CONSTITUTION_PATH,
    EXPECTED_LAW_COUNT,
    validate,
)
from tools.g0._common import load_yaml  # noqa: E402


def _constitution() -> dict:
    return load_yaml(CONSTITUTION_PATH)


def test_constitution_has_exactly_15_laws():
    data = _constitution()
    laws = data["laws"]
    assert len(laws) == EXPECTED_LAW_COUNT == 15


def test_law_ids_are_contiguous_eval_law_001_to_015():
    data = _constitution()
    ids = [law["id"] for law in data["laws"]]
    assert ids == [f"EVAL-LAW-{n:03d}" for n in range(1, 16)]


def test_every_law_carries_required_fields():
    data = _constitution()
    for law in data["laws"]:
        for field in ("id", "name", "text", "enforcement"):
            assert law.get(field), f"{law.get('id')} missing {field}"


def test_all_laws_fail_closed():
    data = _constitution()
    for law in data["laws"]:
        assert law["enforcement"] == "FAIL_CLOSED"


def test_validator_passes_on_clean_constitution():
    ok, report = validate(_constitution())
    assert ok is True, report


def test_validator_fails_on_missing_law():
    data = _constitution()
    data["laws"] = data["laws"][:-1]
    ok, report = validate(data)
    assert ok is False
    assert any("missing expected law ids" in e for e in report["errors"])


def test_validator_fails_on_duplicate_law():
    data = _constitution()
    data["laws"] = [dict(data["laws"][0])] + list(data["laws"])
    ok, report = validate(data)
    assert ok is False
    assert any("duplicate law ids" in e for e in report["errors"])


def test_validator_fails_on_permissive_enforcement():
    data = _constitution()
    data["laws"][0]["enforcement"] = "BEST_EFFORT"
    ok, report = validate(data)
    assert ok is False
    assert any("enforcement must be FAIL_CLOSED" in e for e in report["errors"])


# --- Non-dilution invariants (constitutional inheritance) -------------------

NON_DILUTION_INVARIANTS = (
    "Personal Hermes and CEO Hermes are distinct optimization targets",
    "Workers remain bounded and non-sovereign",
    "Agent memory is not canonical truth",
    "evidence authority cannot be replaced by evaluator opinion",
    "security gates cannot be traded away",
    "External grant submission remains disabled",
    "may not be the sole judge of its own promotion",
    "Generated output is not evidence merely because another model scores it",
    "Tenant-private data cannot silently become global training",
    "No external skill/evolution framework may write directly into production",
    "Improvement must be reversible",
    "Promotion decisions are first-class auditable DecisionRecords",
    "Quality claims require versioned evidence",
)


@pytest.mark.parametrize("phrase", NON_DILUTION_INVARIANTS)
def test_constitution_doc_preserves_non_dilution(phrase):
    text = _ROOT / "docs/grant-sector/g0/07-evaluation/G0_B7_EVALUATION_CONSTITUTION.md"
    # collapse newlines/spaces so prose wrapping never fakes a drift
    normalized = " ".join(text.read_text(encoding="utf-8").lower().split())
    assert phrase.lower() in normalized, phrase


def test_security_and_privacy_laws_are_present_and_non_compensatory():
    data = _constitution()
    by_id = {law["id"]: law["text"] for law in data["laws"]}
    assert "security" in by_id["EVAL-LAW-010"].lower()
    assert "tenant" in by_id["EVAL-LAW-011"].lower()
    assert "vetoes" in by_id["EVAL-LAW-010"].lower()


def test_no_silent_self_modification_law_present():
    data = _constitution()
    text = data["laws"][-1]["text"]
    assert "silently" in text and "self" in text or "its own" in text


def test_evaluation_constitution_validator_cli_exits_zero():
    import subprocess
    import sys as _sys
    proc = subprocess.run(
        [_sys.executable, "tools/g0/validate_evaluation_constitution.py"],
        cwd=_ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
