"""B3.C10-C12 tests — Promotion, Conflict, and Source-Change governance.

Fail-closed:
  * promotion states / enums are from known sets;
  * confidence exposes components and a non-opaque decision reason;
  * critical fact classes require official/direct source; client-intent facts
    are controlled by client approval;
  * lower-authority stale value becomes SUPERSEDED, not deleted;
  * equal-authority contradiction blocks critical use;
  * human resolution references evidence and actor;
  * deadline amendment classified P0; formatting change classified P2;
  * parser-output change with unchanged raw source is NOT a true source change.
"""
from __future__ import annotations

import copy
import pytest

from prototype.g0.source.conflict import (
    CRITICAL_BLOCK_FACT_CLASSES,
    Conflict,
    ConflictRegistry,
    ConflictType,
    ResolutionMethod,
    ResolutionStatus,
    supersede_old,
)
from prototype.g0.source.promotion import (
    Confidence,
    CONFIDENCE_COMPONENTS,
    PromotionGovernor,
    PromotionState,
    make_rule,
)
from prototype.g0.source.source_change import (
    ChangeClass,
    Materiality,
    SourceChangeEvent,
    classify_change,
    is_true_source_change,
)
from tools.g0._common import REPO_ROOT, SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_promotion_conflict import (
    KNOWN_CONFLICT_TYPES,
    KNOWN_MATERIALITY,
    KNOWN_PROMOTION_STATES,
    KNOWN_RESOLUTION_METHODS,
    validate,
)

CFG = SOURCE_CONFIG_DIR / "promotion_conflict.yaml"


def test_validator_live_config_passes():
    ok, report = validate(CFG)
    assert ok, report["errors"]


def test_enum_sets_covered_by_config():
    cfg = load_yaml(CFG)
    assert set(cfg["promotion_states"]) == KNOWN_PROMOTION_STATES
    assert set(cfg["conflict_types"]) == KNOWN_CONFLICT_TYPES
    assert set(cfg["resolution_methods"]) == KNOWN_RESOLUTION_METHODS
    assert set(cfg["materiality_classes"]) == KNOWN_MATERIALITY
    assert set(cfg["confidence_components"]) == CONFIDENCE_COMPONENTS


# --- C10 promotion ----------------------------------------------------------

def test_confidence_is_not_opaque():
    c = Confidence({"source_authority": 0.9, "directness_of_support": 0.8,
                    "corroboration": 0.7})
    assert c.total_score == pytest.approx(0.8, abs=1e-6)
    assert c.explain()["source_authority"] == 0.9  # components always available


def test_critical_deadline_requires_official_source():
    gov = PromotionGovernor({})
    rule = make_rule("opportunity_deadline", critical=True)
    state = gov.promote("c1", "f_deadline", rule,
                        source_classes=["USER_PROVIDED"],
                        confidence=Confidence({"source_authority": 0.3}))
    assert state == PromotionState.CONFLICTED
    ev = gov.events[-1]
    assert "critical_fact_without_official_or_direct_source" in ev.reason_codes


def test_critical_deadline_official_source_verifies():
    gov = PromotionGovernor({})
    rule = make_rule("opportunity_deadline", critical=True)
    state = gov.promote("c2", "f_deadline", rule,
                        source_classes=["OFFICIAL_ISSUER"],
                        confidence=Confidence({"source_authority": 0.9,
                                               "directness_of_support": 0.9,
                                               "extraction_quality": 0.9}))
    assert state == PromotionState.VERIFIED


def test_client_approval_controls_client_intent():
    gov = PromotionGovernor({})
    rule = make_rule("internal_project_goals", client_controls=True)
    assert gov.promote("c3", "f_goals", rule, source_classes=["USER_PROVIDED"],
                       confidence=Confidence({}), client_approved=False) == \
        PromotionState.PROVISIONAL
    assert gov.promote("c4", "f_goals", rule, source_classes=["USER_PROVIDED"],
                       confidence=Confidence({}), client_approved=True) == \
        PromotionState.VERIFIED


def test_narrative_context_allows_multiple_institutional():
    gov = PromotionGovernor({})
    rule = make_rule("community_statistics", narrative=True)
    state = gov.promote("c5", "f_stat", rule,
                        source_classes=["TRUSTED_CURATED", "OFFICIAL_STATISTICAL"],
                        confidence=Confidence({"source_authority": 0.9,
                                               "corroboration": 0.8}))
    assert state == PromotionState.VERIFIED


# --- C11 conflict -----------------------------------------------------------

def test_lower_authority_stale_value_superseded_not_deleted():
    marker = supersede_old(Conflict(conflict_id="c", subject_entity_id="e",
                                    fact_class="opportunity_deadline"),
                           "claim:old_deadline")
    assert marker.startswith("SUPERSEDED:")
    assert "old_deadline" in marker


def test_equal_authority_contradiction_blocks_critical_use():
    reg = ConflictRegistry()
    c = Conflict(conflict_id="c1", subject_entity_id="opp1",
                 fact_class="opportunity_deadline",
                 claim_refs=["cA", "cB"], conflict_type=ConflictType.VALUE_CONFLICT)
    reg.register(c)
    assert not reg.readiness_allows({"opportunity_deadline"})  # blocks
    assert reg.readiness_allows({"funder_identity"})  # non-critical not blocked


def test_resolve_unblocks_critical_use():
    reg = ConflictRegistry()
    c = Conflict(conflict_id="c2", subject_entity_id="opp1",
                 fact_class="opportunity_deadline")
    reg.register(c)
    reg.resolve(c, ResolutionMethod.HUMAN_REVIEW, resolved_value_ref="claim:cX",
                actor="human:reviewer@ops", resolved_at="2026-08-01T00:00:00Z")
    assert c.resolution_status == ResolutionStatus.RESOLVED
    assert c.resolver_actor == "human:reviewer@ops"
    assert reg.readiness_allows({"opportunity_deadline"})


def test_human_resolution_references_evidence_and_actor():
    reg = ConflictRegistry()
    c = Conflict(conflict_id="c3", subject_entity_id="org1", fact_class="legal_organization_name",
                 claim_refs=["c1", "c2"], source_refs=["s1", "s2"])
    reg.register(c)
    reg.resolve(c, ResolutionMethod.HUMAN_REVIEW, resolved_value_ref="claim:c1",
                actor="human:auditor", resolved_at="2026-08-02T00:00:00Z")
    ev = reg._events[-1]
    assert ev["method"] == "HUMAN_REVIEW" and ev["actor"] == "human:auditor"
    # source refs retained on the conflict object (evidence lineage intact)
    assert c.source_refs == ["s1", "s2"]


def test_unresolved_user_official_conflict_blocks_on_legal_identity():
    reg = ConflictRegistry()
    c = Conflict(conflict_id="c4", subject_entity_id="org2",
                 fact_class="legal_organization_name",
                 conflict_type=ConflictType.USER_OFFICIAL_CONFLICT)
    reg.register(c)
    assert not reg.readiness_allows({"legal_organization_name"})


# --- C12 source change ------------------------------------------------------

def test_deadline_amendment_classified_p0():
    ev = SourceChangeEvent(change_event_id="e1", source_id="src_ga",
                           entity_type="opportunity", entity_id="opp1",
                           old_snapshot_id="s1", new_snapshot_id="s2",
                           detected_at="t", change_class=ChangeClass.UPDATED,
                           materiality=Materiality.P0, affected_fields=["deadline"])
    assert classify_change(ev.change_class, ev.signals, ev.affected_fields) == Materiality.P0


def test_formatting_change_classified_p2():
    ev = SourceChangeEvent(change_event_id="e2", source_id="src_ga",
                           entity_type="opportunity", entity_id="opp1",
                           old_snapshot_id="s1", new_snapshot_id="s2",
                           detected_at="t", change_class=ChangeClass.METADATA_CHANGE,
                           materiality=Materiality.P2, affected_fields=["formatting"])
    assert classify_change(ev.change_class, ev.signals, ev.affected_fields) == Materiality.P2


def test_program_description_change_p1():
    ev = SourceChangeEvent(change_event_id="e3", source_id="src_ga",
                           entity_type="opportunity", entity_id="opp1",
                           old_snapshot_id="s1", new_snapshot_id="s2",
                           detected_at="t", change_class=ChangeClass.UPDATED,
                           materiality=Materiality.P1,
                           affected_fields=["description"])
    ev.signals.append("program_description_changed")
    assert classify_change(ev.change_class, ev.signals, ev.affected_fields) == Materiality.P1


def test_parser_output_change_not_true_source_change():
    ev = SourceChangeEvent(change_event_id="e4", source_id="src_ga",
                           entity_type="opportunity", entity_id="opp1",
                           old_snapshot_id="s1", new_snapshot_id="s1",
                           detected_at="t", change_class=ChangeClass.PARSER_OUTPUT_CHANGE,
                           materiality=Materiality.P2)
    # same raw source (unchanged) => NOT a true source change
    assert is_true_source_change(ev, raw_same=True) is False


def test_real_source_update_is_true_change_with_identical_parser_output():
    ev = SourceChangeEvent(change_event_id="e5", source_id="src_ga",
                           entity_type="opportunity", entity_id="opp1",
                           old_snapshot_id="s1", new_snapshot_id="s2",
                           detected_at="t", change_class=ChangeClass.UPDATED,
                           materiality=Materiality.P0, affected_fields=["deadline"])
    assert is_true_source_change(ev, raw_same=True) is False  # raw unchanged
    assert is_true_source_change(ev, raw_same=False) is True   # raw changed => true change


def test_opportunity_cancellation_p0():
    ev = SourceChangeEvent(change_event_id="e6", source_id="src_ga",
                           entity_type="opportunity", entity_id="opp1",
                           old_snapshot_id="s1", new_snapshot_id="s2",
                           detected_at="t", change_class=ChangeClass.CANCELLED,
                           materiality=Materiality.P0)
    assert classify_change(ev.change_class, ev.signals, ev.affected_fields) == Materiality.P0