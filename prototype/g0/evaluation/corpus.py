"""G0-B7-C4 — Eval corpus governance.

Rules from the Book 7 plan chapter C4: versions immutable; additions create
a new version; train/dev/eval/holdout separation; model-generated labels
marked; tenant-private examples never become global by default; duplicates
and near-duplicates tracked; contamination/leakage analysis; historical cases
retain source/effective-date context; benchmark composition report required.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from prototype.g0.evaluation.models import (
    EvalCorpusVersion,
    EvalError,
    content_hash,
)

GOVERNANCE_REQUIRED = ("TENANT_PRIVATE_APPROVED",)

_NEAR_DUP_THRESHOLD = 0.9  # token-overlap ratio above which cases are flagged


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CorpusRegistry:
    """Versioned corpus store with immutability + governance enforcement."""

    def __init__(self) -> None:
        self._versions: dict[str, EvalCorpusVersion] = {}
        self._recorded_hashes: dict[str, str] = {}
        self._cases: dict[str, dict] = {}
        self._duplicates: dict[str, list[str]] = {}

    # ---- version management --------------------------------------------

    def add_version(self, version: EvalCorpusVersion,
                    cases: list[dict]) -> EvalCorpusVersion:
        if version.corpus_version_id in self._versions:
            raise EvalError(
                f"corpus version {version.corpus_version_id} already exists "
                "(versions are immutable)")
        for case in cases:
            self._govern_case(case, version.corpus_class)
        for case_id in version.case_ids:
            if case_id not in {c["eval_case_id"] for c in cases}:
                raise EvalError(f"case {case_id} missing from version payload")
        self._versions[version.corpus_version_id] = version
        # record the exact payload hash at creation; get() re-derives and
        # compares so tampering after add_version is detected
        self._recorded_hashes[version.corpus_version_id] = \
            content_hash(version._payload())
        for case in cases:
            self._cases[case["eval_case_id"]] = case
        self._detect_duplicates(version.corpus_version_id, cases)
        return version

    def next_version(self, previous_id: str,
                     new_case_ids: tuple[str, ...],
                     corpus_class: str | None = None,
                     split_membership: str | None = None) -> EvalCorpusVersion:
        """Additions create a NEW version; the old one never mutates."""
        prev = self.get(previous_id)
        cls = corpus_class or prev.corpus_class
        split = split_membership or prev.split_membership
        return EvalCorpusVersion(
            corpus_version_id=f"{previous_id}-v{prev.version + 1}",
            corpus_class=cls,
            version=prev.version + 1,
            case_ids=tuple(dict.fromkeys((*prev.case_ids, *new_case_ids))),
            created_at=_now(),
            split_membership=split,
            parent_version_id=previous_id,
        )

    def get(self, corpus_version_id: str) -> EvalCorpusVersion:
        version = self._versions.get(corpus_version_id)
        if version is None:
            raise EvalError(f"unknown corpus version {corpus_version_id}")
        recorded = self._recorded_hashes.get(corpus_version_id)
        if recorded is not None and content_hash(version._payload()) != recorded:
            raise EvalError(
                f"corpus {corpus_version_id} mutated after registration; "
                "versions are immutable")
        version.assert_unchanged()
        return version

    def assert_immutable(self, corpus_version_id: str) -> None:
        self.get(corpus_version_id)  # raises on mutation

    # ---- governance -------------------------------------------------------

    def _govern_case(self, case: dict, corpus_class: str) -> None:
        privacy = case.get("privacy_class")
        # CORPUS-005: tenant-private never enters global corpus by default
        if privacy == "TENANT_PRIVATE_APPROVED":
            if not case.get("governance_approval"):
                raise EvalError(
                    "TENANT_PRIVATE_APPROVED case requires governance_approval "
                    "before entering any corpus (EVAL-005)")
            if corpus_class in ("GOLDEN_PUBLIC",):
                raise EvalError(
                    "tenant-private case cannot enter a GOLDEN_PUBLIC corpus")
        # CORPUS-004: model-generated labels marked
        if case.get("label_origin") == "MODEL_GENERATED":
            if case.get("presented_as_human_gold"):
                raise EvalError(
                    "model-generated label presented as human gold (C29-19)")
        # HOLDOUT separation: a case already in HOLDOUT cannot join dev/eval
        if case.get("split_membership") == "HOLDOUT" and corpus_class in (
                "GOLDEN_PUBLIC", "GOLDEN_SYNTHETIC", "GOLDEN_HUMAN_REVIEWED",
                "ADVERSARIAL", "REGRESSION", "SHADOW_PRODUCTION"):
            raise EvalError(
                "HOLDOUT case cannot enter development/eval corpus "
                "(contamination guard)")

    def _detect_duplicates(self, version_id: str, cases: list[dict]) -> None:
        texts = {c["eval_case_id"]: c.get("expected_assertions", [])
                 for c in cases}
        for i, (a_id, a_text) in enumerate(texts.items()):
            for b_id, b_text in list(texts.items())[i + 1:]:
                if a_text == b_text:
                    pair = tuple(sorted((a_id, b_id)))
                    self._duplicates.setdefault(version_id, []).append(
                        f"{pair[0]}=={pair[1]} (exact)")
                elif _overlap(a_text, b_text) > _NEAR_DUP_THRESHOLD:
                    pair = tuple(sorted((a_id, b_id)))
                    self._duplicates.setdefault(version_id, []).append(
                        f"{pair[0]}~{pair[1]} (near, overlap "
                        f"{_overlap(a_text, b_text):.2f})")

    def duplicate_report(self, corpus_version_id: str) -> list[str]:
        return list(self._duplicates.get(corpus_version_id, []))

    def composition_report(self, corpus_version_id: str) -> dict:
        """CORPUS-9: benchmark composition report required."""
        version = self.get(corpus_version_id)
        cases = [self._cases[cid] for cid in version.case_ids
                 if cid in self._cases]
        by_type: dict[str, int] = {}
        by_label: dict[str, int] = {}
        by_privacy: dict[str, int] = {}
        for case in cases:
            by_type[case["case_type"]] = by_type.get(case["case_type"], 0) + 1
            by_label[case["label_origin"]] = by_label.get(
                case["label_origin"], 0) + 1
            by_privacy[case["privacy_class"]] = by_privacy.get(
                case["privacy_class"], 0) + 1
        return {
            "corpus_version_id": corpus_version_id,
            "case_count": len(cases),
            "by_case_type": by_type,
            "by_label_origin": by_label,
            "by_privacy_class": by_privacy,
            "duplicates": self.duplicate_report(corpus_version_id),
            "contamination_checks": self.contamination_report(
                corpus_version_id),
        }

    def contamination_report(self, corpus_version_id: str) -> list[str]:
        """CORPUS-7: leakage analysis — holdout overlap across versions."""
        version = self.get(corpus_version_id)
        findings: list[str] = []
        for other_id, other in self._versions.items():
            if other_id == corpus_version_id:
                continue
            if other.split_membership == "HOLDOUT":
                overlap = set(other.case_ids) & set(version.case_ids)
                if overlap:
                    findings.append(
                        f"holdout overlap with {other_id}: {sorted(overlap)}")
        return findings

    def global_export_allowed(self, corpus_version_id: str) -> list[str]:
        """Which cases in this version may enter generalized eval/training."""
        version = self.get(corpus_version_id)
        allowed: list[str] = []
        for case_id in version.case_ids:
            case = self._cases.get(case_id, {})
            privacy = case.get("privacy_class")
            if privacy in GOVERNANCE_REQUIRED:
                if case.get("governance_approval"):
                    allowed.append(case_id)
            else:
                allowed.append(case_id)
        return allowed

    def export_audit(self, corpus_version_id: str) -> dict:
        """CORPUS-10: audit of corpus exports — never includes unauthorized
        tenant cases."""
        version = self.get(corpus_version_id)
        return {
            "corpus_version_id": corpus_version_id,
            "exported_case_ids": self.global_export_allowed(corpus_version_id),
            "excluded_case_ids": sorted(
                set(version.case_ids)
                - set(self.global_export_allowed(corpus_version_id))),
            "tenant_private_included": [
                c for c in version.case_ids
                if self._cases.get(c, {}).get("privacy_class")
                == "TENANT_PRIVATE_APPROVED"
                and c in self.global_export_allowed(corpus_version_id)],
        }


def _overlap(a, b) -> float:
    """Token-overlap ratio for near-duplicate detection."""
    if not a and not b:
        return 1.0
    ta = {str(x) for x in a}
    tb = {str(x) for x in b}
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))
