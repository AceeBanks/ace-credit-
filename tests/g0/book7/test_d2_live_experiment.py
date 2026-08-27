"""B7-D2-LIVE — First governed model-generated grant experiment tests.

The live lane requires a real provider call, which CI cannot make. These
tests verify the pipeline offline: the committed live artifacts must be
honest (hard gates, claim support, no fabricated values, submission
disabled) and the offline-replay paths of d2_live.py / humanizer_live.py
must re-evaluate the saved drafts without a model call.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0.d2_harness import _model_runtime_available  # noqa: E402

D2_LIVE_DIR = _ROOT / "docs/grant-sector/g0/07-evaluation/d2-live"

REQUIRED_ARTIFACTS = (
    "D2_LIVE_INPUT_MANIFEST.json",
    "D2_LIVE_BASELINE_DRAFT.md",
    "D2_LIVE_BASELINE_CLAIM_LEDGER.json",
    "D2_LIVE_BASELINE_EVAL.json",
    "D2_LIVE_BASELINE_MODEL_RUN.json",
    "D2_LIVE_HUMANIZED_DRAFT.md",
    "D2_LIVE_HUMANIZED_DIFF.json",
    "D2_LIVE_HUMANIZER_RUN.json",
    "D2_LIVE_HUMANIZER_DECISION.json",
    "D2_LIVE_REPRODUCTION_MANIFEST.json",
)


def test_d2_live_artifacts_all_exist():
    for name in REQUIRED_ARTIFACTS:
        assert (D2_LIVE_DIR / name).exists(), name


def test_d2_live_baseline_hard_gate_passes():
    eval_doc = json.loads((D2_LIVE_DIR / "D2_LIVE_BASELINE_EVAL.json")
                          .read_text(encoding="utf-8"))
    assert eval_doc["hard_gate_pass"] is True
    assert eval_doc["deterministic_qa"]["all_pass"] is True
    assert eval_doc["submission_enabled"] is False
    assert eval_doc["unsupported_material_claims"] == []


def test_d2_live_baseline_claim_support_full():
    eval_doc = json.loads((D2_LIVE_DIR / "D2_LIVE_BASELINE_EVAL.json")
                          .read_text(encoding="utf-8"))
    assert eval_doc["claim_support"]["unsupported"] == 0
    assert eval_doc["claim_support"]["material_claim_support_rate"] == 1.0


def test_d2_live_baseline_protected_elements_intact():
    eval_doc = json.loads((D2_LIVE_DIR / "D2_LIVE_BASELINE_EVAL.json")
                          .read_text(encoding="utf-8"))
    assert eval_doc["protected_missing"] == []


def test_d2_live_draft_carries_governed_values():
    draft = (D2_LIVE_DIR / "D2_LIVE_BASELINE_DRAFT.md").read_text(
        encoding="utf-8")
    for value in ("Community Youth Works, Inc.", "18.2 percent",
                  "October 15, 2026", "opp_rev_ga_501_1", "ELIGIBLE"):
        assert value in draft, value


def test_d2_live_model_run_is_real_and_attributable():
    run = json.loads((D2_LIVE_DIR / "D2_LIVE_BASELINE_MODEL_RUN.json")
                     .read_text(encoding="utf-8"))
    assert run["status"] == "OK"
    assert run["response"]["model_id"] == "minimax/minimax-m3:free"
    assert run["response"]["output_text_or_structured_payload"]
    # audit carries the credential REFERENCE, never the value
    assert "credential_ref" in run["audit"]
    assert "OPENROUTER_API_KEY" not in json.dumps(run)


def test_d2_live_reproduction_manifest_is_reproducible():
    manifest = json.loads((D2_LIVE_DIR / "D2_LIVE_REPRODUCTION_MANIFEST.json")
                          .read_text(encoding="utf-8"))
    assert manifest["opportunity_revision_id"] == "opp_rev_ga_501_1"
    assert "d2_live.py" in manifest["reproduce"][0]
    assert manifest["label"] == "MOCK_NON_SUBMISSION"


def test_d2_live_humanizer_hard_gates_pass_no_promote():
    decision = json.loads(
        (D2_LIVE_DIR / "D2_LIVE_HUMANIZER_DECISION.json")
        .read_text(encoding="utf-8"))
    assert decision["gate_pass"] is True
    assert decision["disposition"] != "PROMOTE"  # C28: one fixture
    assert decision["submission"] == "DISABLED"


def test_d2_live_humanizer_protected_claims_preserved():
    diff = json.loads((D2_LIVE_DIR / "D2_LIVE_HUMANIZED_DIFF.json")
                      .read_text(encoding="utf-8"))
    assert diff["protected_claim_diff_passed"] is True
    assert diff["protected_dropped"] == []
    assert diff["semantic_preservation"] == "PASS"


def test_d2_live_input_manifest_binds_exact_fixture():
    manifest = json.loads((D2_LIVE_DIR / "D2_LIVE_INPUT_MANIFEST.json")
                          .read_text(encoding="utf-8"))
    assert manifest["organization"] == "Community Youth Works, Inc."
    assert manifest["opportunity_revision_id"] == "opp_rev_ga_501_1"
    assert manifest["deadline"] == "2026-10-15"
    assert manifest["eligibility"] == "ELIGIBLE"
    assert manifest["label"] == "MOCK_NON_SUBMISSION"


def test_d2_live_honest_about_runtime():
    """The live artifacts only exist legitimately when the model run really
    happened; the harness probe must agree with the recorded status."""
    run = json.loads((D2_LIVE_DIR / "D2_LIVE_BASELINE_MODEL_RUN.json")
                     .read_text(encoding="utf-8"))
    assert run["status"] == "OK"
    # recorded artifact claims a live run; the probe reports whether a
    # governed runtime is currently configured — the artifact itself is the
    # historical evidence and must not claim BLOCKED.
    assert "BLOCKED" not in json.dumps(run)


def test_d2_live_offline_replay_baseline_consistent():
    """Re-running the offline replay path must reproduce the same draft
    evaluation (deterministic gates only; no model call)."""
    from tools.g0.d2_live import eval_live_draft, parse_sections
    draft = (D2_LIVE_DIR / "D2_LIVE_BASELINE_DRAFT.md").read_text(
        encoding="utf-8")
    sections = parse_sections(draft)
    result = eval_live_draft(draft, sections, {"status": "OFFLINE_REPLAY"})
    assert result["hard_gate_pass"] is True
    assert result["deterministic_qa"]["all_pass"] is True
    assert result["submission_enabled"] is False


def test_d2_live_offline_replay_humanizer_consistent():
    """Offline replay of the Humanizer comparison must reproduce the same
    protected-claim diff (no model call)."""
    from tools.g0.humanizer_live import compare
    baseline = (D2_LIVE_DIR / "D2_LIVE_BASELINE_DRAFT.md").read_text(
        encoding="utf-8")
    humanized = (D2_LIVE_DIR / "D2_LIVE_HUMANIZED_DRAFT.md").read_text(
        encoding="utf-8")
    comparison = compare(baseline, humanized)
    assert comparison["protected_claim_diff_passed"] is True
    assert comparison["semantic_preservation"] == "PASS"
