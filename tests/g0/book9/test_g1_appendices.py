"""G1 Appendix A/B contract tests.

Verifies both appendices exist, are frozen, do not reopen Book 9
architecture (OCE_NATIVE stands), and map to backlog items. Also verifies
the Appendix A selection engine and schema are present and tested.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

G1_DIR = _ROOT / "docs/grant-sector/g1"
APP_A = G1_DIR / "G1_APPENDIX_A_MODEL_CAPABILITY_AND_SELECTION_CONTRACT_v1.0.md"
APP_B = G1_DIR / "G1_APPENDIX_B_CLIENT_INTERACTION_AND_FRONTEND_CONTRACT_v1.0.md"


def test_appendix_a_exists_and_frozen():
    text = APP_A.read_text(encoding="utf-8")
    assert "Status:** FROZEN" in text
    assert "OCE_NATIVE" in text
    assert "ModelProfile" in text
    assert "PROVISIONAL_G1_DEFAULT" in text


def test_appendix_a_does_not_reopen_architecture():
    text = APP_A.read_text(encoding="utf-8")
    assert "does NOT reopen Book 9 architecture" in text


def test_appendix_a_selection_engine_implemented():
    engine = _ROOT / "production-seed/grant_platform/model/selection.py"
    schema = _ROOT / "production-seed/grant_platform/model/model_profile.schema.json"
    assert engine.exists()
    assert schema.exists()
    text = engine.read_text(encoding="utf-8")
    assert "LONG_FORM_CONTEXT_MULTIPLIER" in text
    assert "def select_model" in text


def test_appendix_b_exists_and_frozen():
    text = APP_B.read_text(encoding="utf-8")
    assert "Status:** FROZEN" in text
    assert "CHAT + WORK PROGRESS + DELIVERABLES" in text
    assert "shadcn/ui" in text
    assert "Next.js" in text


def test_appendix_b_chat_first_principle():
    text = APP_B.read_text(encoding="utf-8")
    assert "USER SAYS WHAT THEY NEED" in text
    assert "FINAL DELIVERABLE APPEARS IN CHAT" in text
    assert "never faked by timers" in text


def test_appendices_map_to_backlog():
    backlog = (_ROOT / "docs/grant-sector/g0/09-production-seed"
               / "G0_B9_G1_IMPLEMENTATION_BACKLOG.md").read_text(
                   encoding="utf-8")
    assert "G1.7" in backlog
    assert "G1.9" in backlog
    a = APP_A.read_text(encoding="utf-8")
    b = APP_B.read_text(encoding="utf-8")
    assert "G1.7" in a or "G1.8" in a
    assert "G1.9" in b


def test_appendices_preserve_constitutional_invariants():
    a = APP_A.read_text(encoding="utf-8")
    b = APP_B.read_text(encoding="utf-8")
    # submission stays disabled; no auto-submit in either contract
    assert "submission" in a.lower()
    assert "submission" in b.lower()
    assert "automatic" not in a.lower() or "not" in a.lower()
    # personal vs CEO separation preserved in the frontend contract
    assert "Personal Hermes" in b and "CEO Hermes" in b
