"""G0-B5-C9 — dependency graph + selective invalidation tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.dependencies import (  # noqa: E402
    DependencyError,
    DependencyGraph,
)


def _graph() -> DependencyGraph:
    g = DependencyGraph()
    # opp fact -> eligibility decision -> readiness -> alert
    g.add_dependency(dependent_ref="eligibility-decision-1",
                     depends_on_ref="fact:deadline",
                     dependency_type="ELIGIBILITY", materiality="CRITICAL")
    g.add_dependency(dependent_ref="readiness-1",
                     depends_on_ref="eligibility-decision-1",
                     dependency_type="FACTUAL", materiality="CRITICAL")
    g.add_dependency(dependent_ref="alert-1",
                     depends_on_ref="readiness-1",
                     dependency_type="NARRATIVE_ALIGNMENT", materiality="SIGNIFICANT")
    # statistic -> proposal section
    g.add_dependency(dependent_ref="proposal-section-2",
                     depends_on_ref="stat:community-pop",
                     dependency_type="CITATION", materiality="SIGNIFICANT")
    return g


def test_selective_invalidation_no_global_recompute():
    g = _graph()
    event = g.invalidate(changed_upstream_ref="fact:deadline",
                         change_class="MATERIAL")
    assert set(event.affected_downstream_refs) == {
        "eligibility-decision-1", "readiness-1", "alert-1"}
    assert "proposal-section-2" not in event.affected_downstream_refs
    assert event.required_action == "RECOMPUTE"


def test_nonmaterial_change_does_not_invalidate():
    g = _graph()
    event = g.invalidate(changed_upstream_ref="fact:deadline",
                         change_class="NONMATERIAL")
    assert event.affected_downstream_refs == []
    assert event.required_action == "NONE"


def test_transitive_invalidation_bounded_and_inspectable():
    g = _graph()
    affected, cycle = g.transitive_dependents("fact:deadline")
    assert len(affected) == 3  # bounded, exactly the reachable set
    assert cycle is False


def test_cycle_detected_no_storm():
    g = _graph()
    g.add_dependency(dependent_ref="a", depends_on_ref="b",
                     dependency_type="FACTUAL", materiality="MINOR")
    g.add_dependency(dependent_ref="b", depends_on_ref="a",
                     dependency_type="FACTUAL", materiality="MINOR")
    affected, cycle = g.transitive_dependents("a")
    assert cycle is True  # bounded; no infinite invalidation storm
    assert len(affected) <= 8


def test_unknown_dependency_type_rejected():
    g = _graph()
    with pytest.raises(DependencyError, match="unknown dependency type"):
        g.add_dependency(dependent_ref="x", depends_on_ref="y",
                         dependency_type="MAGIC", materiality="MINOR")


def test_stale_dependency_blocks_submission_ready():
    g = _graph()
    event = g.invalidate(changed_upstream_ref="stat:community-pop",
                         change_class="MATERIAL")
    # a material dependency on the draft is still unresolved -> readiness
    # cannot claim false submission-ready (INV-007)
    assert event.priority == "P0"
    assert event.resolved is False
