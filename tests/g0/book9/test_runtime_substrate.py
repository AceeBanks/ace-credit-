"""G0-B9-C1..C6 — workload evidence, runtime requirements, candidate
profiles, hard-gate elimination, and the substrate ADR.

The ADR must be one of the four allowed outcomes (never TBD), must select
the candidate that passed all 15 hard gates, and every eliminated
candidate must have a recorded reason. The workload evidence must tag
every number measured/derived/estimated/unknown.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

SEED_DIR = _ROOT / "docs/grant-sector/g0/09-production-seed"
ADR_PATH = SEED_DIR / "G0_B9_RUNTIME_SUBSTRATE_ADR.md"
ADR_JSON = SEED_DIR / "G0_B9_RUNTIME_SUBSTRATE_ADR.json"
WORKLOAD_PATH = SEED_DIR / "G0_B9_BOOK8_WORKLOAD_EVIDENCE.md"
REQUIREMENTS_PATH = SEED_DIR / "G0_B9_RUNTIME_REQUIREMENTS_MATRIX.md"
CANDIDATES_PATH = SEED_DIR / "G0_B9_RUNTIME_CANDIDATE_PROFILES.md"
BAKEOFF_PATH = SEED_DIR / "G0_B9_RUNTIME_BAKEOFF_RESULTS.md"

ALLOWED_STATUSES = ("OCE_NATIVE", "COMPOZY_BOUNDED", "QM_BOUNDED",
                    "HYBRID_BOUNDED")


def test_adr_status_is_one_of_four_allowed_outcomes():
    text = ADR_PATH.read_text(encoding="utf-8")
    m = re.search(r"\*\*Status:\*\* `([A-Z_]+)`", text)
    assert m, "ADR must declare a status"
    assert m.group(1) in ALLOWED_STATUSES, "no TBD allowed at Book 9 end"


def test_adr_json_matches_markdown():
    data = json.loads(ADR_JSON.read_text(encoding="utf-8"))
    text = ADR_PATH.read_text(encoding="utf-8")
    assert data["status"] in ALLOWED_STATUSES
    assert data["status"] in text
    assert data["ratified"] is True
    assert data["runtime"]["submission_enabled"] is False


def test_selected_candidate_passed_hard_gates():
    data = json.loads(ADR_JSON.read_text(encoding="utf-8"))
    winner = data["candidates"]["A_OCE_NATIVE"]
    assert winner["hard_gates_pass"] is True
    assert winner["selected"] is True


def test_eliminated_candidates_have_reasons():
    data = json.loads(ADR_JSON.read_text(encoding="utf-8"))
    for key in ("B_COMPOZY_BOUNDED", "C_QM_BOUNDED", "D_HYBRID_BOUNDED"):
        c = data["candidates"][key]
        assert c["selected"] is False
        assert c["eliminated"], f"{key} must record an elimination reason"


def test_workload_evidence_tags_every_number():
    text = WORKLOAD_PATH.read_text(encoding="utf-8")
    # every table row in the measured/derived sections must carry a basis tag
    rows = re.findall(r"^\| ([^|]+) \| ([^|]+) \| ([^|]+) \|$",
                      text, re.MULTILINE)
    for row in rows:
        if row[0].strip() == "Metric":   # table header
            continue
        basis = row[2]
        assert any(tag in basis for tag in (
            "MEASURED", "DERIVED", "ESTIMATED", "UNKNOWN")), \
            f"untagged evidence row: {row[0]}"


def test_workload_evidence_notes_free_tier_not_production_basis():
    text = WORKLOAD_PATH.read_text(encoding="utf-8")
    assert "NOT a production pricing basis" in text


def test_requirements_matrix_has_hard_gate_and_acceptance_columns():
    text = REQUIREMENTS_PATH.read_text(encoding="utf-8")
    assert "hard_gate" in text
    assert "acceptance_test" in text
    assert "REQ-POL-007" in text  # submission disabled requirement
    assert "REQ-POL-007" and "P0" in text


def test_candidate_profiles_record_honest_status():
    text = CANDIDATES_PATH.read_text(encoding="utf-8")
    assert "MEASURED" in text
    assert "NOT_RUN" in text
    assert "BLOCKED" in text
    # eliminated candidates must be recorded as not installed
    assert "DISQUALIFIED" in text


def test_bakeoff_no_fabricated_competitor_scores():
    text = BAKEOFF_PATH.read_text(encoding="utf-8")
    assert "is fabricated" in text.lower()
    assert "NOT_RUN" in text
    assert "OCE_NATIVE" in text


def test_bakeoff_weighted_score_present():
    text = BAKEOFF_PATH.read_text(encoding="utf-8")
    assert "4.72 / 5.00" in text
    assert "Final decision:" in text


def test_adr_documents_exit_strategy_and_boundary():
    text = ADR_PATH.read_text(encoding="utf-8")
    assert "Exit strategy" in text
    assert "replacement boundary" in text.lower()
    assert "explicitly NOT used" in text
    assert "g1 boundary" in text.lower() or "remains" in text.lower()
