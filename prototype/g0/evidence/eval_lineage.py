"""G0-B5-C19 — Eval case lineage prototype.

Each benchmark/eval example derived from system work records full lineage:
sources, fixtures, decision/artifact refs, label origin/reviewer, privacy
classification and split membership. Enforces EVAL-001..005: lineage
required, label provenance required, immutability via content_hash,
synthetic labeling, and governance gate on private cases entering global
eval.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


class EvalLineageError(ValueError):
    """Raised when an eval case violates lineage policy."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/evidence/"
                           "eval_lineage_policy.yaml").read_text(encoding="utf-8"))


_POLICY = _load_policy()


def case_hash(case: dict) -> str:
    canonical = json.dumps(case, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]


def validate_eval_case(*, case: dict, policy: dict | None = None) -> dict:
    """Validate lineage for an eval case; returns the case (immutable)."""
    policy = policy or _POLICY

    # EVAL-001: lineage required — sources or fixtures, plus decision refs
    sources = case.get("source_snapshot_refs", []) or []
    fixtures = case.get("domain_fixture_refs", []) or []
    decision_refs = case.get("decision_artifact_refs", []) or []
    if not sources and not fixtures:
        raise EvalLineageError(
            "eval case without source or fixture lineage (EVAL-001)")
    if not decision_refs:
        raise EvalLineageError(
            "eval case without decision/artifact refs (EVAL-001)")

    # EVAL-002: label provenance required
    origin = case.get("label_origin")
    reviewer = case.get("label_reviewer")
    if origin not in policy["label_origins"]:
        raise EvalLineageError(f"invalid label_origin {origin!r} (EVAL-002)")
    if not reviewer:
        raise EvalLineageError("label_reviewer required (EVAL-002)")
    if origin == "SYNTHETIC" and not case.get("synthetic"):
        raise EvalLineageError(
            "synthetic case must be labeled synthetic (EVAL-004)")

    # EVAL-005: private cases need governance for global eval
    privacy = case.get("privacy_classification")
    if privacy not in policy["privacy_classifications"]:
        raise EvalLineageError(f"invalid privacy class {privacy!r}")
    if privacy in policy["governance_required_classes"]:
        if not case.get("governance_approval"):
            raise EvalLineageError(
                f"{privacy} case requires governance_approval before global "
                "eval (EVAL-005)")

    if case.get("split_membership") not in policy["split_memberships"]:
        raise EvalLineageError(
            f"invalid split_membership {case.get('split_membership')!r}")

    # EVAL-003: pin content_hash at creation; immutable thereafter
    out = dict(case)
    out["content_hash"] = out.get("content_hash") or case_hash(out)
    return out


def assert_unchanged(*, recorded: dict, current: dict) -> None:
    """EVAL-003: a changed source must not silently mutate a historical case."""
    if case_hash(current) != recorded.get("content_hash"):
        raise EvalLineageError(
            "historical eval case mutated (EVAL-003); changed source must "
            "produce a new case, never silently alter the recorded one")


def global_eval_export(*, case: dict, policy: dict | None = None) -> bool:
    """EVAL-005: may this case enter generalized eval/training?"""
    policy = policy or _POLICY
    privacy = case.get("privacy_classification")
    if privacy in policy["governance_required_classes"]:
        return bool(case.get("governance_approval"))
    return True
