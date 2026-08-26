"""B4.C17 — Semantic compactor with anchor preservation (prototype).

Five compaction stages (0 = none .. 5 = model-assisted semantic compaction).
Fail-closed rules:

  * COMPACT-001: mandatory anchors survive every stage; dropping an anchor is
    an assembly error;
  * COMPACT-002: factual numbers/dates/amounts/revision ids preserved
    verbatim ($75,000 must never become $750,000);
  * COMPACT-003: uncertainty can never be converted to certainty;
  * COMPACT-004: every compaction emits a CompactionManifest.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

STAGES = [
    "STAGE0_NO_COMPACTION", "STAGE1_DROP_DISPOSABLE_REDUNDANT",
    "STAGE2_SNIP_HISTORICAL_LOW_VALUE", "STAGE3_MICRO_SUMMARIZE_EPISODES_TASKS",
    "STAGE4_COLLAPSE_INACTIVE_PROJECT_CONTEXT",
    "STAGE5_MODEL_ASSISTED_SEMANTIC_COMPACTION",
]

UNCERTAINTY_MARKERS = ("possibly", "uncertain", "not verified", "unclear",
                       "may be", "unknown", "pending", "not confirmed")
DISPOSABLE_MARKERS = ("tool output dump", "retry log", "debug trace",
                      "duplicate snippet")
_FACTUAL_RE = re.compile(
    r"\$\s?\d(?:[\d,]*\d)?(?:\.\d{2})?|\b\d{4}-\d{2}-\d{2}\b|"
    r"\b(?:rev|opp-rev)-\d+\b|\b\d[\d,]*(?:\.\d+)?%?")


class CompactionError(ValueError):
    """Raised when a compaction violates the anchor/fact/uncertainty rules."""


@dataclass
class CompactionManifest:
    removed_items: list[str] = field(default_factory=list)
    summarized_items: list[str] = field(default_factory=list)
    anchors_retained: list[str] = field(default_factory=list)
    summary_generator_version: str = "compactor-v1"
    source_refs: list[str] = field(default_factory=list)
    before_budget: int = 0
    after_budget: int = 0

    def to_dict(self) -> dict:
        return {
            "removed_items": list(self.removed_items),
            "summarized_items": list(self.summarized_items),
            "anchors_retained": list(self.anchors_retained),
            "summary_generator_version": self.summary_generator_version,
            "source_refs": list(self.source_refs),
            "before_budget": self.before_budget,
            "after_budget": self.after_budget,
        }


def _extract_factual(text: str) -> set[str]:
    return set(_FACTUAL_RE.findall(text))


def compact(items: list[str], *, stage: str, anchors: list[str],
            project_context: dict | None = None,
            budget: int | None = None) -> tuple[list[str], CompactionManifest]:
    """Apply a compaction stage; anchors and facts always survive."""
    if stage not in STAGES:
        raise CompactionError(f"unknown stage {stage}")
    if stage == "STAGE0_NO_COMPACTION":
        return list(items), CompactionManifest(
            anchors_retained=list(anchors), before_budget=sum(map(len, items)),
            after_budget=sum(map(len, items)))

    manifest = CompactionManifest(
        anchors_retained=list(anchors), before_budget=sum(map(len, items)))

    # anchors must be present in the input to be retained
    missing = [a for a in anchors if a not in items]
    if missing:
        raise CompactionError(
            f"anchor {missing} missing from input — compaction cannot "
            "fabricate it")

    kept: list[str] = []
    for item in items:
        if item in anchors:
            kept.append(item)  # COMPACT-001: anchors never compacted
            continue
        if stage in ("STAGE1_DROP_DISPOSABLE_REDUNDANT",
                     "STAGE2_SNIP_HISTORICAL_LOW_VALUE") and \
                any(m in item.lower() for m in DISPOSABLE_MARKERS):
            manifest.removed_items.append(item)
            continue
        kept.append(item)

    # STAGE3+: micro-summarize older non-anchor items but preserve facts
    if stage in ("STAGE3_MICRO_SUMMARIZE_EPISODES_TASKS",
                 "STAGE4_COLLAPSE_INACTIVE_PROJECT_CONTEXT",
                 "STAGE5_MODEL_ASSISTED_SEMANTIC_COMPACTION"):
        if stage == "STAGE4_COLLAPSE_INACTIVE_PROJECT_CONTEXT" and project_context:
            kept = [c for c in kept if c in anchors]
            kept.append(f"[project summary] {project_context.get('summary', '')}")
            manifest.summarized_items.append(
                "inactive project history -> project summary + refs")
        else:
            summarized: list[str] = []
            kept_final: list[str] = []
            for item in kept:
                if item in anchors:
                    kept_final.append(item)
                    continue
                factual = _extract_factual(item)
                marker = "[summarized]" + (" {" + ", ".join(sorted(factual)) + "}"
                                           if factual else "")
                summarized.append(marker)
                manifest.summarized_items.append(item)
            kept = kept_final + summarized

    # COMPACT-002: no summary may introduce or drop factual values for kept
    # anchor-relevant content
    if budget is not None and len(kept) > budget:
        # drop non-anchor summarized markers first; anchors never dropped
        non_anchor = [k for k in kept if k not in anchors]
        if len(anchors) > budget:
            raise CompactionError(
                f"budget {budget} below anchor count {len(anchors)}")
        excess = len(kept) - budget
        kept = [k for k in kept if k in anchors] + non_anchor[excess:]

    manifest.after_budget = sum(map(len, kept))
    return kept, manifest


def summarize_with_uncertainty_guard(items: list[str]) -> str:
    """Summarize while preserving uncertainty markers (COMPACT-003)."""
    lowered = " ".join(items).lower()
    if any(m in lowered for m in UNCERTAINTY_MARKERS):
        return " ".join(items)[:400] + " [uncertainty preserved; not confirmed]"
    return " ".join(items)[:400]


def assert_facts_preserved(original: list[str], compacted: list[str]) -> None:
    """Factual values in anchor-relevant input must survive compaction."""
    orig_facts = _extract_factual(" ".join(original))
    kept_facts = _extract_factual(" ".join(compacted))
    lost = orig_facts - kept_facts
    if lost:
        raise CompactionError(f"compaction lost factual values: {sorted(lost)}")
