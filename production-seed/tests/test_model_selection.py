"""G1 Appendix A — model selection contract tests.

Covers: context eligibility gate, task eligibility, disabled models,
long-form 2x safety target, user choice vs fallback, auto routing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from grant_platform.model.selection import (  # noqa: E402
    LONG_FORM_CONTEXT_MULTIPLIER,
    SelectionContext,
    select_model,
)


def _profile(**kw):
    base = dict(
        model_id="m1", provider_id="openrouter",
        context_window_tokens=16000, max_output_tokens=2048,
        enabled=True, availability="ENABLED", quality_tier="MEDIUM",
        cost_tier="MEDIUM", allowed_tasks=["grant_drafting"],
        full_proposal_eligible=True,
    )
    base.update(kw)
    from grant_platform.model.selection import ModelProfile
    return ModelProfile.from_dict(base)


def test_small_model_rejected_for_large_context_task():
    ctx = SelectionContext(task="full_proposal",
                           estimated_input_tokens=20000,
                           expected_output_tokens=4000, long_form=True)
    result = select_model(ctx, [_profile(context_window_tokens=16000,
                                         max_output_tokens=4096)])
    assert not result.ok
    assert any("context window" in r for r in result.rejected_reasons)


def test_large_context_model_accepted_for_long_form():
    ctx = SelectionContext(task="full_proposal",
                           estimated_input_tokens=20000,
                           expected_output_tokens=4000, long_form=True)
    result = select_model(ctx, [_profile(context_window_tokens=100000,
                                         max_output_tokens=8000)])
    assert result.ok
    assert result.selected.model_id == "m1"


def test_long_form_doubles_working_requirement():
    ctx = SelectionContext(task="full_proposal",
                           estimated_input_tokens=10000,
                           expected_output_tokens=2000, long_form=True)
    assert LONG_FORM_CONTEXT_MULTIPLIER == 2.0
    # 10000+2000 = 12000 working; *2 = 24000 required
    result = select_model(ctx, [_profile(context_window_tokens=20000,
                                         max_output_tokens=8000)])
    assert not result.ok                      # 20000 < 24000
    result2 = select_model(ctx, [_profile(context_window_tokens=24000,
                                          max_output_tokens=8000)])
    assert result2.ok


def test_task_eligibility_enforced():
    ctx = SelectionContext(task="humanizer",
                           estimated_input_tokens=1000,
                           expected_output_tokens=500)
    result = select_model(ctx, [_profile(humanizer_eligible=False)])
    assert not result.ok
    assert any("not eligible" in r for r in result.rejected_reasons)


def test_disabled_model_never_selected():
    ctx = SelectionContext(task="grant_drafting",
                           estimated_input_tokens=1000,
                           expected_output_tokens=500)
    result = select_model(ctx, [_profile(enabled=False)])
    assert not result.ok
    assert "model disabled" in result.rejected_reasons


def test_max_output_gate():
    ctx = SelectionContext(task="grant_drafting",
                           estimated_input_tokens=1000,
                           expected_output_tokens=4000)
    result = select_model(ctx, [_profile(max_output_tokens=2048)])
    assert not result.ok
    assert any("max output" in r for r in result.rejected_reasons)


def test_user_choice_honored_when_eligible():
    ctx = SelectionContext(task="grant_drafting",
                           estimated_input_tokens=1000,
                           expected_output_tokens=500,
                           user_model="m2")
    result = select_model(ctx, [
        _profile(model_id="m1"),
        _profile(model_id="m2", quality_tier="LOW"),
    ])
    assert result.ok
    assert result.selected.model_id == "m2"


def test_fallback_used_when_user_choice_incompatible():
    ctx = SelectionContext(task="full_proposal",
                           estimated_input_tokens=50000,
                           expected_output_tokens=4000, long_form=True,
                           user_model="small", allow_fallback=True)
    result = select_model(ctx, [
        _profile(model_id="small", context_window_tokens=8000),
        _profile(model_id="big", context_window_tokens=200000,
                 max_output_tokens=8000),
    ])
    assert result.ok
    assert result.selected.model_id == "big"
    assert result.fallback_used is True


def test_no_fallback_without_opt_in():
    ctx = SelectionContext(task="full_proposal",
                           estimated_input_tokens=50000,
                           expected_output_tokens=4000, long_form=True,
                           user_model="small", allow_fallback=False)
    result = select_model(ctx, [
        _profile(model_id="small", context_window_tokens=8000),
        _profile(model_id="big", context_window_tokens=200000,
                 max_output_tokens=8000),
    ])
    assert not result.ok


def test_auto_prefers_quality_then_cost():
    ctx = SelectionContext(task="grant_drafting",
                           estimated_input_tokens=1000,
                           expected_output_tokens=500)
    result = select_model(ctx, [
        _profile(model_id="cheap", quality_tier="LOW", cost_tier="LOW"),
        _profile(model_id="good", quality_tier="HIGH", cost_tier="HIGH"),
    ])
    assert result.selected.model_id == "good"
