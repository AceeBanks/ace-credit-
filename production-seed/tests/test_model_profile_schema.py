"""G1 Appendix A — ModelProfile schema enforcement.

The schema is the machine-readable contract for every selectable model.
A profile that fails the schema cannot be registered.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

SCHEMA = _ROOT / "grant_platform/model/model_profile.schema.json"

try:
    import jsonschema  # type: ignore
    HAVE_JSONSCHEMA = True
except Exception:
    HAVE_JSONSCHEMA = False


def _load_schema():
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def _valid_profile(**kw):
    base = {
        "model_id": "minimax/minimax-m3:free",
        "provider_id": "openrouter",
        "provider_type": "aggregator",
        "display_name": "MiniMax M3 (free)",
        "context_window_tokens": 200000,
        "max_output_tokens": 8192,
        "supports_structured_output": True,
        "supports_tools": False,
        "supports_vision": False,
        "input_cost": 0.0,
        "output_cost": 0.0,
        "availability": "ENABLED",
        "quality_tier": "MEDIUM",
        "latency_tier": "MEDIUM",
        "cost_tier": "LOW",
        "evaluation_status": "d2-live-pass",
        "allowed_tasks": ["grant_drafting", "full_proposal"],
        "full_proposal_eligible": True,
        "research_eligible": True,
        "qa_eligible": True,
        "humanizer_eligible": True,
        "extraction_eligible": False,
        "minimum_context_headroom": 2000,
        "fallback_compatible": ["openai/gpt-4o-mini"],
        "enabled": True,
    }
    base.update(kw)
    return base


def test_schema_file_exists_and_is_json():
    data = _load_schema()
    assert data["title"] == "ModelProfile"


def test_schema_requires_eligibility_fields():
    data = _load_schema()
    for f in ("full_proposal_eligible", "research_eligible", "qa_eligible",
              "humanizer_eligible", "extraction_eligible",
              "context_window_tokens", "max_output_tokens"):
        assert f in data["properties"], f"missing schema field {f}"


@pytest.mark.skipif(not HAVE_JSONSCHEMA,
                    reason="jsonschema not installed (dev-only check)")
def test_valid_profile_passes_schema():
    import jsonschema
    jsonschema.validate(_valid_profile(), _load_schema())


@pytest.mark.skipif(not HAVE_JSONSCHEMA,
                    reason="jsonschema not installed (dev-only check)")
def test_invalid_profile_fails_schema():
    import jsonschema
    bad = _valid_profile(context_window_tokens=-5)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema())


def test_schema_forbids_unknown_fields():
    data = _load_schema()
    assert data.get("additionalProperties") is False
