"""G0-B5-C19 — Eval case lineage tests.

Required coverage (plan):
- eval case without lineage rejected;
- label provenance required;
- historical benchmark reproducible;
- private tenant data not exported into global eval by default.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.eval_lineage import (  # noqa: E402
    EvalLineageError,
    assert_unchanged,
    global_eval_export,
    validate_eval_case,
)


def _case(**kw) -> dict:
    base = dict(
        case_id="eval-1", source_snapshot_refs=["snap:official"],
        decision_artifact_refs=["decision:eligibility-1"],
        label_origin="HUMAN_REVIEWER", label_reviewer="reviewer:r1",
        privacy_classification="PUBLIC_SOURCE", split_membership="TEST",
        created_at="2026-08-26T00:00:00+00:00",
    )
    base.update(kw)
    return base


def test_eval_case_without_lineage_rejected():
    with pytest.raises(EvalLineageError):
        validate_eval_case(case=_case(source_snapshot_refs=[],
                                      domain_fixture_refs=[]))
    with pytest.raises(EvalLineageError):
        validate_eval_case(case=_case(decision_artifact_refs=[]))


def test_label_provenance_required():
    with pytest.raises(EvalLineageError):
        validate_eval_case(case=_case(label_reviewer=""))
    with pytest.raises(EvalLineageError):
        validate_eval_case(case=_case(label_origin="GUESSED"))


def test_historical_benchmark_reproducible():
    recorded = validate_eval_case(case=_case())
    assert recorded["content_hash"]
    # identical content reproduces the same hash
    assert_unchanged(recorded=recorded, current=_case())
    # a mutated case is rejected, never silently accepted
    with pytest.raises(EvalLineageError):
        assert_unchanged(recorded=recorded,
                         current=_case(decision_artifact_refs=["decision:x"]))


def test_private_data_not_exported_by_default():
    private = _case(privacy_classification="TENANT_PRIVATE")
    assert global_eval_export(case=private) is False
    # governance approval enables export
    approved = _case(privacy_classification="TENANT_PRIVATE",
                     governance_approval="gov:approval-1")
    assert global_eval_export(case=approved) is True
    public = _case()
    assert global_eval_export(case=public) is True


def test_synthetic_case_must_be_labeled():
    with pytest.raises(EvalLineageError):
        validate_eval_case(case=_case(label_origin="SYNTHETIC"))
    ok = validate_eval_case(
        case=_case(label_origin="SYNTHETIC", synthetic=True))
    assert ok["label_origin"] == "SYNTHETIC"
