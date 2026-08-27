"""G1 Pilot — checkpoint integrity tests.

The pilot evidence must be honest: measurable fields recorded, submission
disabled, cold reconstruction without raw chat, STOP boundary explicit,
and no fake production claims.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

EVIDENCE = _ROOT / "docs" / "grant-sector" / "g1" / "pilot" / "G1_PILOT_EVIDENCE.json"


def test_pilot_evidence_exists_and_wellformed():
    assert EVIDENCE.exists()
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["label"] == "MOCK_NON_SUBMISSION"
    assert data["submission_enabled"] is False


def test_pilot_quality_gates_pass_honestly():
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    q = data["quality"]
    assert q["status"] == "SUBMISSION_READY_MOCK"
    assert q["qa_fail"] == 0
    assert q["within_ceiling"] is True


def test_cold_reconstruction_requires_no_raw_chat():
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    r = data["cold_reconstruction"]
    assert r["raw_chat_required"] is False
    assert all(r["completeness"].values())


def test_stop_boundary_explicit():
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    s = data["stop_boundary"]
    assert s["production_hardening"] == "NOT STARTED (post-review Wave 6)"
    assert s["public_launch"] == "NOT STARTED"
    assert s["g2_architecture"] == "NOT STARTED"
    assert s["submission"] == "DISABLED"


def test_pilot_reports_open_issues_not_fake_green():
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    issues = data["open_issues"]
    assert len(issues) >= 3
    assert any("deterministic" in i for i in issues)      # honest lane
    assert any("NOT_PERFORMED" in i for i in issues)      # honest review


def test_pilot_checkpoint_doc_records_stop():
    doc = (_ROOT / "docs" / "grant-sector" / "g1" /
           "G1_PILOT_CHECKPOINT.md").read_text(encoding="utf-8")
    assert "STOP boundary" in doc.lower()
    assert "structurally disabled" in doc
    assert "does not self-claim" in doc
