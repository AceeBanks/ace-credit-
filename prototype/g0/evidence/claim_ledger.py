"""G0-B5-C16 — Application Claim Ledger prototype.

Makes grant drafts auditable at the claim level. Each entry carries a
claim_class, evidence refs, and a support status decided by policy rules
CLAIM-001..007: synthetic testimonials fail support, future targets are not
misclassified as achieved outcomes, numeric claims trace to statistics/
facts/budgets, and text rewrites must re-version rather than sever the
claim-to-ledger mapping silently.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from prototype.g0.evidence.models import EvidenceGraph

SUPPORTED = "SUPPORTED"
SUPPORTED_WITH_QUALIFICATION = "SUPPORTED_WITH_QUALIFICATION"
USER_ATTESTED = "USER_ATTESTED"
ASSUMPTION = "ASSUMPTION"
UNSUPPORTED = "UNSUPPORTED"
CONFLICTED = "CONFLICTED"
STALE = "STALE"


class ClaimLedgerError(ValueError):
    """Raised when a claim entry violates the ledger policy."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/evidence/"
                           "claim_ledger_policy.yaml").read_text(encoding="utf-8"))


_POLICY = _load_policy()


class ClaimLedger:
    """Claim-level audit ledger for one artifact version."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY
        self._entries: dict[str, dict] = {}

    def classify(self, claim_class: str) -> None:
        if claim_class not in self.policy["claim_classes"]:
            raise ClaimLedgerError(f"unknown claim_class {claim_class!r} (CLAIM-001)")

    def assess(self, *, entry: dict, graph: EvidenceGraph) -> dict:
        """Return a copy of the entry with support_status decided."""
        out = dict(entry)
        cls = out["claim_class"]
        refs = list(out.get("evidence_refs", []) or [])

        # CLAIM-004: future target must not be an achieved historical outcome
        text = out.get("claim_text_or_structured_ref", "")
        is_target = out.get("is_target", False)
        if cls == "MEASURABLE_OUTCOME_HISTORICAL" and not is_target:
            lowered = text.lower()
            if any(m in lowered for m in self.policy["future_markers"]):
                raise ClaimLedgerError(
                    "future target presented as achieved outcome (CLAIM-004); "
                    "set is_target=true or reclassify")

        # CLAIM-007: assumptions are future plans, never historical facts
        if out.get("support_status") == ASSUMPTION and not is_target:
            lowered = text.lower()
            if not any(m in lowered for m in self.policy["future_markers"]):
                raise ClaimLedgerError(
                    "assumption must be represented as future plan/assumption "
                    "(CLAIM-007)")

        # CLAIM-008: community statistics must match declared geography/unit
        if cls == "POPULATION_COMMUNITY_STATISTICS" and \
                (out.get("geography") or out.get("unit")):
            for ref_id in refs:
                resolved = graph.resolve_or_tombstone(ref_id)
                if resolved.get("tombstoned"):
                    continue
                loc = resolved.get("locator") or {}
                if out.get("geography") and loc.get("geography") \
                        and loc["geography"] != out["geography"]:
                    raise ClaimLedgerError(
                        f"statistic {ref_id} geography mismatch (CLAIM-008)")
                if out.get("unit") and loc.get("unit") \
                        and loc["unit"] != out["unit"]:
                    raise ClaimLedgerError(
                        f"statistic {ref_id} unit mismatch (CLAIM-008)")

        # CLAIM-005: numeric claims trace to statistic/fact/budget
        if cls in self.policy["numeric_classes"]:
            numeric_ok = False
            for ref_id in refs:
                resolved = graph.resolve_or_tombstone(ref_id)
                if resolved.get("tombstoned"):
                    continue
                if resolved.get("ref_type") in self.policy["numeric_evidence_types"]:
                    numeric_ok = True
                    break
            if not numeric_ok:
                raise ClaimLedgerError(
                    f"numeric claim {out['claim_id']} lacks a statistic/fact/"
                    "budget trace (CLAIM-005)")

        # CLAIM-002/003: support requires resolvable, non-tombstoned refs;
        # synthetic/unverifiable testimonials fail support.
        if cls == "TESTIMONIAL_SUPPORT":
            for ref_id in refs:
                resolved = graph.resolve_or_tombstone(ref_id)
                if resolved.get("tombstoned"):
                    out["support_status"] = STALE
                    out["qa_status"] = "REVIEW_REQUIRED"
                    return out
                origin = ((resolved.get("locator") or {}).get("origin") or "").upper()
                if origin in ("SYNTHETIC", "AI_GENERATED", "UNVERIFIABLE"):
                    out["support_status"] = UNSUPPORTED
                    out["qa_status"] = "FAILED"
                    return out
            if not refs:
                out["support_status"] = UNSUPPORTED
                out["qa_status"] = "FAILED"
                return out

        if out.get("support_status") in (ASSUMPTION, USER_ATTESTED,
                                         UNSUPPORTED, CONFLICTED):
            return out

        # missing (never existed) is UNSUPPORTED; tombstoned (deleted by
        # governance) is STALE — a fabricated ref is never just 'old'.
        missing = [r for r in refs if r not in graph._refs]
        stale = [r for r in refs if r in graph._refs
                 and graph.resolve_or_tombstone(r).get("tombstoned")]
        if stale:
            out["support_status"] = STALE
            out["qa_status"] = "REVIEW_REQUIRED"
        elif missing or not refs:
            out["support_status"] = UNSUPPORTED
            out["qa_status"] = "FAILED"
        else:
            out["support_status"] = SUPPORTED
            out["qa_status"] = "PASSED"
        return out

    def put(self, *, entry: dict, graph: EvidenceGraph) -> dict:
        """Validate, assess and record an entry (fail-closed)."""
        self.classify(entry["claim_class"])
        assessed = self.assess(entry=entry, graph=graph)
        self._entries[assessed["claim_id"]] = assessed
        return assessed

    def reversion(self, *, artifact_version_id: str,
                  claim_id: str, new_text: str) -> dict:
        """CLAIM-006: rewriting claim text must produce a new version, never
        silently mutate the original mapping."""
        original = self._entries.get(claim_id)
        if original is None:
            raise ClaimLedgerError(f"unknown claim {claim_id}")
        if new_text == original["claim_text_or_structured_ref"]:
            return original
        if artifact_version_id == original["artifact_version_id"]:
            raise ClaimLedgerError(
                "claim text changed without a new artifact_version_id "
                "(CLAIM-006); humanization must not sever the mapping silently")
        revised = dict(original)
        revised["artifact_version_id"] = artifact_version_id
        revised["claim_text_or_structured_ref"] = new_text
        revised["claim_id"] = f"{original['claim_id']}-v2"
        revised["support_status"] = "PENDING"
        revised["qa_status"] = "PENDING"
        self._entries[revised["claim_id"]] = revised
        return revised

    def entry(self, claim_id: str) -> dict | None:
        return self._entries.get(claim_id)
