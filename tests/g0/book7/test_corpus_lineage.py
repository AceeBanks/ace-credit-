"""B7.C4 — Eval corpus governance & lineage tests.

Fail-closed: immutable versions; additions create new versions; holdout
separation; tenant-private governance; model-label marking; duplicate and
contamination detection; export audit.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.corpus import CorpusRegistry  # noqa: E402
from prototype.g0.evaluation.models import (  # noqa: E402
    EvalCase,
    EvalCorpusVersion,
    EvalError,
)


def _case(case_id: str, *, privacy="PUBLIC_SOURCE",
          label="HUMAN_REVIEWER", assertions=None, **kw) -> dict:
    data = {
        "eval_case_id": case_id,
        "case_type": "eligibility",
        "corpus_version_id": "corpus-ga-v1",
        "source_lineage_refs": ["ref:snap-ga-1"],
        "decision_artifact_refs": ["ref:eldec_ga_1"],
        "input_fixture_refs": [f"fixture:{case_id}"],
        "expected_assertions": assertions if assertions is not None else [
            {"assertion_id": "a1", "kind": "equals", "expected": "ELIGIBLE"}],
        "privacy_class": privacy,
        "tenant_scope": None,
        "label_origin": label,
        "label_reviewer": "rev-1",
        "created_at": "2026-08-26T00:00:00Z",
    }
    data.update(kw)
    return data


def _version(cases: list[dict], **kw) -> EvalCorpusVersion:
    defaults = {
        "corpus_version_id": "corpus-ga-v1",
        "corpus_class": "GOLDEN_HUMAN_REVIEWED",
        "version": 1,
        "case_ids": tuple(c["eval_case_id"] for c in cases),
        "created_at": "2026-08-26T00:00:00Z",
    }
    defaults.update(kw)
    return EvalCorpusVersion(**defaults)


def _registry_with_ga() -> tuple[CorpusRegistry, EvalCorpusVersion]:
    reg = CorpusRegistry()
    cases = [_case("ec-1"), _case("ec-2")]
    v1 = _version(cases)
    reg.add_version(v1, cases)
    return reg, v1


def test_version_add_and_fetch():
    reg, v1 = _registry_with_ga()
    fetched = reg.get(v1.corpus_version_id)
    assert fetched.case_ids == ("ec-1", "ec-2")


def test_version_immutable_hash():
    reg, v1 = _registry_with_ga()
    # tampering with the stored mapping raises on next get
    reg._versions[v1.corpus_version_id] = EvalCorpusVersion(
        corpus_version_id=v1.corpus_version_id, corpus_class="GOLDEN_PUBLIC",
        version=1, case_ids=("ec-1",), created_at=v1.created_at)
    with pytest.raises(EvalError):
        reg.get(v1.corpus_version_id)


def test_duplicate_version_id_rejected():
    reg, v1 = _registry_with_ga()
    with pytest.raises(EvalError):
        reg.add_version(v1, [_case("ec-1"), _case("ec-2")])


def test_next_version_is_append_only():
    reg, v1 = _registry_with_ga()
    v2 = reg.next_version(v1.corpus_version_id, ("ec-3",))
    assert v2.parent_version_id == v1.corpus_version_id
    assert v2.version == 2
    assert v2.case_ids == ("ec-1", "ec-2", "ec-3")
    # old version still has its original content hash
    reg.get(v1.corpus_version_id)


def test_tenant_private_requires_governance():
    reg = CorpusRegistry()
    cases = [_case("ec-p", privacy="TENANT_PRIVATE_APPROVED",
                   tenant_scope="tenant-a")]
    with pytest.raises(EvalError):
        reg.add_version(_version(cases), cases)
    cases[0]["governance_approval"] = "ga-1"
    reg.add_version(_version(cases), cases)  # now allowed


def test_tenant_private_cannot_enter_public_corpus():
    reg = CorpusRegistry()
    cases = [_case("ec-p", privacy="TENANT_PRIVATE_APPROVED",
                   tenant_scope="tenant-a", governance_approval="ga-1")]
    with pytest.raises(EvalError):
        reg.add_version(_version(cases, corpus_class="GOLDEN_PUBLIC"), cases)


def test_holdout_case_cannot_enter_dev_corpus():
    reg = CorpusRegistry()
    cases = [_case("ec-h", split_membership="HOLDOUT")]
    with pytest.raises(EvalError):
        reg.add_version(_version(cases), cases)


def test_model_generated_label_cannot_be_presented_as_human_gold():
    reg = CorpusRegistry()
    cases = [_case("ec-m", label="MODEL_GENERATED",
                   presented_as_human_gold=True)]
    with pytest.raises(EvalError):
        reg.add_version(_version(cases), cases)


def test_exact_duplicates_detected():
    reg = CorpusRegistry()
    cases = [_case("ec-1"), _case("ec-2", assertions=[
        {"assertion_id": "a1", "kind": "equals", "expected": "ELIGIBLE"}])]
    reg.add_version(_version(cases), cases)
    dups = reg.duplicate_report("corpus-ga-v1")
    assert any("ec-1==ec-2" in d for d in dups)


def test_export_audit_excludes_unapproved_private():
    reg = CorpusRegistry()
    pub = _case("ec-pub")
    priv = _case("ec-priv", privacy="TENANT_PRIVATE_APPROVED",
                 tenant_scope="tenant-a")  # no governance_approval
    cases = [pub, priv]
    with pytest.raises(EvalError):
        reg.add_version(_version(cases), cases)
    # governance-approved private IS exportable; but the registry still
    # refused because _govern_case requires approval before add
    priv2 = dict(priv)
    priv2["governance_approval"] = "ga-9"
    reg2 = CorpusRegistry()
    reg2.add_version(_version([pub, priv2]), [pub, priv2])
    audit = reg2.export_audit("corpus-ga-v1")
    assert "ec-priv" in audit["exported_case_ids"]
    assert audit["excluded_case_ids"] == []


def test_contamination_report_detects_holdout_overlap():
    reg = CorpusRegistry()
    cases = [_case("ec-1"), _case("ec-2")]
    v1 = _version(cases, corpus_class="GOLDEN_HUMAN_REVIEWED")
    reg.add_version(v1, cases)
    holdout = _version([_case("ec-1"), _case("ec-h")],
                       corpus_version_id="corpus-holdout-v1",
                       corpus_class="HOLDOUT", split_membership="HOLDOUT",
                       version=1)
    reg.add_version(holdout, [_case("ec-1"), _case("ec-h")])
    findings = reg.contamination_report("corpus-ga-v1")
    assert any("holdout overlap" in f for f in findings)


def test_composition_report_required_fields():
    reg, _ = _registry_with_ga()
    report = reg.composition_report("corpus-ga-v1")
    assert report["case_count"] == 2
    assert "by_case_type" in report
    assert "by_label_origin" in report
    assert "by_privacy_class" in report
    assert "duplicates" in report
    assert "contamination_checks" in report
