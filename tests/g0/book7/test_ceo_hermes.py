"""B7.C12 — CEO Hermes evaluation tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.agent_eval import (  # noqa: E402
    ceo_feed_forward_drift,
    ceo_hermes_eval,
)


def test_ceo_hermes_clean_pass():
    r = ceo_hermes_eval(
        interpreted_intent_correctly=True,
        plan_decomposition_quality=0.9,
        correct_worker_selection=True,
        task_bounding_ok=True,
        used_raw_transcript=False,
        unnecessary_tool_calls=0,
        synthesis_correct=True,
        completion_state_correct=True,
        relationship_memory_pollution=False)
    assert r["all_pass"] is True


def test_ceo_hermes_raw_transcript_fails():
    r = ceo_hermes_eval(
        interpreted_intent_correctly=True,
        plan_decomposition_quality=0.9,
        correct_worker_selection=True,
        task_bounding_ok=True,
        used_raw_transcript=True,
        unnecessary_tool_calls=0,
        synthesis_correct=True,
        completion_state_correct=True,
        relationship_memory_pollution=False)
    assert r["all_pass"] is False


def test_ceo_hermes_relationship_memory_pollution_fails():
    r = ceo_hermes_eval(
        interpreted_intent_correctly=True,
        plan_decomposition_quality=0.9,
        correct_worker_selection=True,
        task_bounding_ok=True,
        used_raw_transcript=False,
        unnecessary_tool_calls=0,
        synthesis_correct=True,
        completion_state_correct=True,
        relationship_memory_pollution=True)
    assert r["all_pass"] is False


def test_ceo_hermes_unnecessary_tool_calls_fail():
    r = ceo_hermes_eval(
        interpreted_intent_correctly=True,
        plan_decomposition_quality=0.9,
        correct_worker_selection=True,
        task_bounding_ok=True,
        used_raw_transcript=False,
        unnecessary_tool_calls=3,
        synthesis_correct=True,
        completion_state_correct=True,
        relationship_memory_pollution=False)
    assert r["all_pass"] is False


def test_feed_forward_no_drift():
    stages = [
        {"stage": "client_idea", "key_terms": "youth workforce Georgia"},
        {"stage": "personal", "key_terms": "youth workforce Georgia"},
        {"stage": "intent_contract", "key_terms": "youth workforce Georgia"},
        {"stage": "ceo_plan", "key_terms": "youth workforce Georgia"},
        {"stage": "workers", "key_terms": "youth workforce Georgia"},
        {"stage": "synthesis", "key_terms": "youth workforce Georgia"},
        {"stage": "explanation", "key_terms": "youth workforce Georgia"},
    ]
    r = ceo_feed_forward_drift(stages=stages)
    assert r["pass"] is True
    assert r["semantic_drift_boundaries"] == []


def test_feed_forward_drift_detected():
    stages = [
        {"stage": "client_idea", "key_terms": "youth workforce Georgia"},
        {"stage": "personal", "key_terms": "youth workforce Georgia"},
        {"stage": "intent_contract", "key_terms": "office furniture"},
        {"stage": "ceo_plan", "key_terms": "office furniture"},
    ]
    r = ceo_feed_forward_drift(stages=stages)
    assert r["pass"] is False
    assert len(r["semantic_drift_boundaries"]) == 1


def test_feed_forward_requires_all_stages():
    r = ceo_feed_forward_drift(stages=[
        {"stage": "client_idea", "key_terms": "a"},
        {"stage": "personal", "key_terms": "a"},
    ])
    assert r["stage_count"] == 2
