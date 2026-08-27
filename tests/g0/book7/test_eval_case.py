"""B7.C3 — EvalCase contract tests.

Fail-closed: no case without lineage; label provenance required;
immutability via content_hash; synthetic labels marked; private governance;
tenant scope; deterministic hashing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.models import (  # noqa: E402
    EvalCase,
    EvalError,
)


def _base_case(**overrides) -> dict:
    data = {
        "eval_case_id": "ec-1",
        "case_type": "eligibility",
        "corpus_version_id": "corpus-ga-v1",
        "source_lineage_refs": ["ref:snap-ga-1"],
        "decision_artifact_refs": ["ref:eldec_ga_1"],
        "input_fixture_refs": ["fixture:GA-1"],
        "expected_assertions": [
            {"assertion_id": "a1", "kind": "equals", "expected": "ELIGIBLE"}],
        "privacy_class": "PUBLIC_SOURCE",
        "tenant_scope": None,
        "label_origin": "HUMAN_REVIEWER",
        "label_reviewer": "rev-1",
        "created_at": "2026-08-26T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_valid_case_constructs():
    case = EvalCase.from_governed_dict(_base_case())
    assert case.eval_case_id == "ec-1"
    assert case.content_hash  # pinned at creation


def test_case_without_lineage_rejected():
    data = _base_case()
    data["source_lineage_refs"] = []
    data["input_fixture_refs"] = []
    data["domain_fixture_refs"] = []
    with pytest.raises(EvalError):
        EvalCase.from_governed_dict(data)


def test_case_without_decision_or_input_refs_rejected():
    data = _base_case()
    data["decision_artifact_refs"] = []
    data["input_fixture_refs"] = []
    with pytest.raises(EvalError):
        EvalCase.from_governed_dict(data)


def test_case_unknown_case_type_rejected():
    data = _base_case(case_type="magic_score")
    with pytest.raises(EvalError):
        EvalCase.from_governed_dict(data)


def test_case_model_generated_label_must_be_marked():
    data = _base_case(label_origin="MODEL_GENERATED",
                      label_reviewer="model-x")
    case = EvalCase.from_governed_dict(data)
    assert case.label_origin == "MODEL_GENERATED"
    # presented_as_human_gold is rejected by lineage governance
    data2 = _base_case(label_origin="MODEL_GENERATED", label_reviewer="m",
                       presented_as_human_gold=True)
    with pytest.raises(EvalError):
        EvalCase.from_governed_dict(data2)


def test_case_synthetic_must_be_labeled_synthetic():
    data = _base_case(label_origin="SYNTHETIC", label_reviewer="tool-1",
                      synthetic=True)
    case = EvalCase.from_governed_dict(data)
    assert case.label_origin == "SYNTHETIC"


def test_case_private_requires_governance():
    data = _base_case(privacy_class="TENANT_PRIVATE_APPROVED",
                      tenant_scope="tenant-a")
    with pytest.raises(EvalError):
        EvalCase.from_governed_dict(data)
    data["governance_approval"] = "ga-1"
    case = EvalCase.from_governed_dict(data)
    assert case.privacy_class == "TENANT_PRIVATE_APPROVED"


def test_case_unknown_privacy_class_rejected():
    with pytest.raises(EvalError):
        EvalCase.from_governed_dict(_base_case(privacy_class="PUBLIC_NOPE"))


def test_content_hash_is_deterministic():
    a = EvalCase.from_governed_dict(_base_case())
    b = EvalCase.from_governed_dict(_base_case())
    assert a.content_hash == b.content_hash


def test_content_hash_changes_with_input():
    a = EvalCase.from_governed_dict(_base_case())
    data = _base_case()
    data["expected_assertions"] = [
        {"assertion_id": "a1", "kind": "equals", "expected": "INELIGIBLE"}]
    b = EvalCase.from_governed_dict(data)
    assert a.content_hash != b.content_hash


def test_to_dict_round_trip_preserves_fields():
    case = EvalCase.from_governed_dict(_base_case())
    d = case.to_dict()
    assert d["eval_case_id"] == "ec-1"
    assert d["content_hash"] == case.content_hash
    assert d["label_origin"] == "HUMAN_REVIEWER"
