"""G0-B5-C4 — Evidence quality model tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.contradictions import (  # noqa: E402
    EvidenceQualityError,
    authoritative_conflict_guard,
    score_quality,
)
from tools.g0.validate_quality_contradiction import (  # noqa: E402
    validate,
)

QUALITY_CFG = yaml.safe_load(
    (_ROOT / "config/g0/evidence/evidence_quality_dimensions.yaml").read_text(
        encoding="utf-8"))


def _dims(**overrides):
    base = {"authority": 0.9, "directness": 0.9, "freshness": 0.9,
            "specificity": 0.8, "corroboration": 0.6,
            "extraction_quality": 0.8, "identity_certainty": 0.9,
            "temporal_fit": 0.9}
    base.update(overrides)
    return base


def test_high_authority_plus_stale_is_not_high_confidence():
    q = score_quality(evidence_ref="ev-1", dimensions=_dims(freshness=0.1))
    assert q.quality_class == "STALE"
    assert q.quality_class != "VERIFIED_HIGH"


def test_verified_high_requires_all_dimensions():
    q = score_quality(evidence_ref="ev-2", dimensions=_dims())
    assert q.quality_class == "VERIFIED_HIGH"


def test_low_extraction_quality_visible_in_dimensions():
    q = score_quality(evidence_ref="ev-3",
                      dimensions=_dims(extraction_quality=0.2, directness=0.5,
                                       corroboration=0.2))
    assert q.dimensions["extraction_quality"] == 0.2
    # composite stays reproducible
    q2 = score_quality(evidence_ref="ev-3",
                       dimensions=_dims(extraction_quality=0.2, directness=0.5,
                                        corroboration=0.2))
    assert q.composite_score == q2.composite_score


def test_conflicting_authoritative_cannot_be_averaged():
    q1 = score_quality(evidence_ref="ev-a", dimensions=_dims(authority=0.9))
    q2 = score_quality(evidence_ref="ev-b", dimensions=_dims(authority=0.95))
    q1.quality_class = "VERIFIED_HIGH"
    q2.quality_class = "CONFLICTED"
    with pytest.raises(EvidenceQualityError, match="CONFLICTED"):
        authoritative_conflict_guard([q1, q2])


def test_missing_dimension_fails():
    with pytest.raises(EvidenceQualityError, match="missing dimensions"):
        score_quality(evidence_ref="ev-4",
                      dimensions={k: v for k, v in _dims().items()
                                  if k != "authority"})


def test_validator_passes_on_live_configs():
    errors: list[str] = []
    validate(errors)
    assert errors == []


def test_validator_fails_on_missing_dimension():
    broken = dict(QUALITY_CFG)
    broken["dimensions"] = [d for d in QUALITY_CFG["dimensions"]
                            if d["id"] != "authority"]
    errors: list[str] = []
    validate(errors, quality=broken)
    assert any("dimensions mismatch" in e for e in errors)
