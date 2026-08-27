"""G0-B7-C8 — Factuality & evidence metrics.

Measures material claim support, citation precision/recall, unsupported and
contradicted claims, stale-evidence usage, and future-target/historical
classification. The hard gate (C8): a candidate that increases prose quality
while increasing unsupported material claims cannot promote.
"""
from __future__ import annotations

from typing import Any

SUPPORTED_STATUSES = ("SUPPORTED", "SUPPORTED_WITH_QUALIFICATION",
                      "USER_ATTESTED")


def claim_support_metrics(entries: list[dict]) -> dict:
    """material claim support rate over a claim ledger entry list."""
    total = len(entries)
    if total == 0:
        return {"material_claim_support_rate": 0.0, "supported": 0,
                "unsupported": 0, "total": 0, "conflicted": 0, "stale": 0}
    supported = sum(1 for e in entries
                    if e.get("support_status") in SUPPORTED_STATUSES)
    unsupported = sum(1 for e in entries
                      if e.get("support_status") == "UNSUPPORTED")
    conflicted = sum(1 for e in entries
                     if e.get("support_status") == "CONFLICTED")
    stale = sum(1 for e in entries if e.get("support_status") == "STALE")
    return {
        "material_claim_support_rate": round(supported / total, 4),
        "supported": supported,
        "unsupported": unsupported,
        "conflicted": conflicted,
        "stale": stale,
        "total": total,
    }


def citation_metrics(*, citations: list[dict]) -> dict:
    """Citation precision/recall over declared citations.

    Each citation: {"claim_id", "cited_ref", "resolves": bool,
    "supports_claim": bool, "required": bool}
    """
    total = len(citations)
    if total == 0:
        return {"citation_precision": 0.0, "citation_recall": 0.0,
                "resolvable": 0, "supporting": 0, "total": 0}
    resolvable = sum(1 for c in citations if c.get("resolves"))
    supporting = sum(1 for c in citations
                     if c.get("resolves") and c.get("supports_claim"))
    required = [c for c in citations if c.get("required")]
    recalled = sum(1 for c in required
                   if c.get("resolves") and c.get("supports_claim"))
    precision = supporting / total if total else 0.0
    recall = recalled / len(required) if required else 0.0
    return {
        "citation_precision": round(precision, 4),
        "citation_recall": round(recall, 4),
        "resolvable": resolvable,
        "supporting": supporting,
        "required_count": len(required),
        "total": total,
    }


def unsupported_material_claims(entries: list[dict]) -> list[dict]:
    """List the unsupported material claims (hard-gate input)."""
    return [e for e in entries if e.get("support_status") == "UNSUPPORTED"
            and e.get("material", True)]


def factuality_hard_gate(*, baseline_metrics: dict,
                         candidate_metrics: dict) -> dict:
    """C8 hard gate: prose improvement cannot offset factuality regression.

    Returns {"pass": bool, "reason": str}. Fails when the candidate has
    MORE unsupported material claims than the baseline, or lower claim
    support rate beyond a small tolerance.
    """
    base_unsupported = baseline_metrics.get("unsupported", 0)
    cand_unsupported = candidate_metrics.get("unsupported", 0)
    base_rate = baseline_metrics.get("material_claim_support_rate", 0.0)
    cand_rate = candidate_metrics.get("material_claim_support_rate", 0.0)
    if cand_unsupported > base_unsupported:
        return {"pass": False,
                "reason": (f"unsupported claims rose {base_unsupported} -> "
                           f"{cand_unsupported}; prose cannot offset "
                           "factuality regression (C8 hard gate)")}
    if cand_rate < base_rate - 0.01:
        return {"pass": False,
                "reason": (f"claim support rate fell {base_rate:.3f} -> "
                           f"{cand_rate:.3f}")}
    return {"pass": True, "reason": "factuality preserved"}


def requirement_coverage(*, requirements: list[dict],
                         responses: list[dict]) -> dict:
    """Deterministic requirement coverage: mandatory requirements that have
    a completed response artifact."""
    mandatory = [r for r in requirements if r.get("mandatory", True)]
    responded = {r["requirement_id"] for r in responses
                 if r.get("state") in ("COMPLETED", "APPROVED_INTERNAL",
                                       "SUBMISSION_READY")}
    covered = [r for r in mandatory if r["requirement_id"] in responded]
    return {
        "coverage": round(len(covered) / len(mandatory), 4)
        if mandatory else 1.0,
        "covered": len(covered),
        "mandatory_total": len(mandatory),
        "missing": [r["requirement_id"] for r in mandatory
                    if r["requirement_id"] not in responded],
    }


def future_vs_historical_classification(*, claims: list[dict]) -> dict:
    """Future-target vs historical-achievement classification accuracy.

    claims: {"claim_id", "is_target": bool, "classified_as_target": bool}
    """
    total = len(claims)
    if total == 0:
        return {"accuracy": 1.0, "mismatches": [], "total": 0}
    mismatches = [c["claim_id"] for c in claims
                  if c.get("is_target") != c.get("classified_as_target")]
    return {
        "accuracy": round(1 - len(mismatches) / total, 4),
        "mismatches": mismatches,
        "total": total,
    }
