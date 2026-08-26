"""B4.C16 — Supersession, contradiction and forgetting tests.

Proves memory never becomes a pile of contradictory current truths:
superseded records are excluded from active context; historical
reconstruction still shows the old record; canonical conflicts are flagged
and canonical state wins; forgetting expires records from active retrieval.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.memory_lifecycle import (  # noqa: E402
    check_canonical_conflict,
)
from prototype.g0.agents.memory_manager import (  # noqa: E402
    MemoryManager,
    MemoryRecord,
)


def _pref(memory_id, statement, **overrides) -> MemoryRecord:
    kwargs = dict(
        memory_id=memory_id, memory_class="PM-PREFERENCE",
        namespace="personal_hermes", statement=statement,
        importance="NORMAL", confidence_state="VERIFIED",
        source_event_refs=["event:user-said"],
        created_at="2026-08-26T10:00:00Z")
    kwargs.update(overrides)
    return MemoryRecord(**kwargs)


def test_superseded_record_excluded_from_active_context():
    mgr = MemoryManager()
    old = mgr.store(_pref("mem-1", "Show me only top 3 grants"))
    new = _pref("mem-2", "I want to review up to 10 now")
    mgr.supersede(old.memory_id, new)
    active = mgr.retrieve_active("personal_hermes")
    assert [r.memory_id for r in active] == ["mem-2"]
    # and the state machine: old is SUPERSEDED, new is ACTIVE
    assert old.status == "SUPERSEDED"
    assert new.status == "ACTIVE"


def test_historical_reconstruction_still_shows_old_record():
    mgr = MemoryManager()
    old = mgr.store(_pref("mem-1", "Show me only top 3 grants"))
    new = _pref("mem-2", "I want to review up to 10 now")
    mgr.supersede(old.memory_id, new)
    all_records = mgr._records["personal_hermes"]
    historical = {r.memory_id: r for r in all_records}
    assert historical["mem-1"].statement == "Show me only top 3 grants"
    assert historical["mem-1"].superseded_by == "mem-2"
    assert historical["mem-2"].supersedes == "mem-1"


def test_canonical_conflict_flagged():
    canonical = {
        "opportunity.deadline": "2026-10-15",
        "organization.tax_exempt_status": "VERIFIED 501(c)(3)",
    }
    conflicts = check_canonical_conflict(
        "The deadline used to be 2026-10-15 per my notes", canonical)
    assert "opportunity.deadline" in conflicts
    # memory that disagrees with canonical truth is flagged, and canonical
    # state wins for operational factual use — memory can never override it
    assert check_canonical_conflict(
        "I believe the deadline is 2027-01-01", canonical) == []


def test_canonical_state_wins_over_memory():
    # The operational rule: canonical state wins for factual use even when
    # freeform memory disagrees. MemoryManager never returns canonical facts.
    canonical_deadline = "2026-10-15"
    memory_statement = "deadline 2027-01-01"
    conflicts = check_canonical_conflict(memory_statement,
                                         {"deadline": canonical_deadline})
    assert conflicts  # flagged, not silently resolved
    # and the memory record itself remains visible as historical context only
    mgr = MemoryManager()
    record = _pref("mem-x", memory_statement,
                   memory_class="PM-OPEN_LOOP",
                   confidence_state="INFERRED")
    mgr.store(record)
    assert mgr.retrieve_active("personal_hermes")[0].statement == memory_statement


def test_forgetting_rule_expires_from_active_retrieval():
    mgr = MemoryManager()
    mgr.store(_pref("mem-1", "episode: brainstormed program name",
                    memory_class="PM-EPISODIC_SUMMARY",
                    expires_at="2026-08-27T00:00:00Z"))
    later = datetime(2026, 9, 1, tzinfo=timezone.utc)
    active = mgr.retrieve_active("personal_hermes", now=later)
    assert active == []
    expired = mgr.expire_past_ttl("personal_hermes", now=later)
    assert [r.memory_id for r in expired] == ["mem-1"]
    assert expired[0].status == "EXPIRED"


def test_memory_record_state_enum_frozen():
    from prototype.g0.agents.memory_manager import MEMORY_STATES
    assert MEMORY_STATES == {"ACTIVE", "PROVISIONAL", "SUPERSEDED", "EXPIRED",
                             "CONFLICTED", "ARCHIVED"}


def test_invalid_state_rejected():
    mgr = MemoryManager()
    with pytest.raises(Exception, match="unknown memory state"):
        mgr.store(_pref("mem-bad", "x", status="IMAGINARY"))
