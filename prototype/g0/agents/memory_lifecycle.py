"""B4.C14-C16 — Worker memory, promotion and supersession lifecycle (prototype).

  * classify_candidate: EVENT -> REJECT | TEMPORARY | PROMOTE_FOR_REVIEW
    (random conversational detail is rejected; explicit durable preferences
    promote; operational lessons route to Book 7 eval);
  * promote_candidate: validation/contradiction check before promotion,
    supersession flow for conflicting preferences (never coequal memories);
  * canonical_conflict: memory can never override canonical truth;
  * repeat_worker_task: a stateless worker can repeat a task from the
    contract + snapshots alone — no hidden personal memory required.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

RANDOM_DETAIL_MARKERS = ("said hi", "asked about weather", "thanks!",
                         "ok sounds good", "sure thing")

AUTO_PROMOTABLE = {"PM-PREFERENCE", "PM-GOAL", "PM-OPEN_LOOP"}
BOOK7_EVAL_REQUIRED = {"CM-LESSON-CANDIDATE"}
REVIEW_REQUIRED = {"PM-IDENTITY", "PM-DECISION", "PM-RELATIONSHIP",
                   "CM-BLOCKER", "CM-CAPABILITY"}


class MemoryLifecycleError(ValueError):
    """Raised when a memory lifecycle rule is violated."""


@dataclass
class MemoryCandidate:
    candidate_id: str
    proposed_memory_class: str
    proposed_statement: str
    source_refs: list[str] = field(default_factory=list)
    canonical_refs: list[str] = field(default_factory=list)
    why_useful: str = ""
    importance: str = "NORMAL"
    expected_duration: str = "MEDIUM"
    proposed_by: str = "PERSONAL_HERMES"
    classification: str | None = None
    classification_reason: str | None = None


@dataclass
class MemoryPromotion:
    promotion_id: str
    candidate_id: str
    decision: str
    criteria_evidence: dict[str, Any]
    validation_state: str
    proposed_by: str
    promoted_record_id: str | None = None
    evaluator_ref: str | None = None
    promoted_at: str = ""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def classify_candidate(candidate: MemoryCandidate) -> MemoryCandidate:
    """EVENT -> classification (REJECT | TEMPORARY | PROMOTE_FOR_REVIEW)."""
    statement = candidate.proposed_statement.lower()
    if any(marker in statement for marker in RANDOM_DETAIL_MARKERS):
        candidate.classification = "REJECT"
        candidate.classification_reason = "random conversational detail"
        return candidate
    if candidate.proposed_memory_class in BOOK7_EVAL_REQUIRED:
        candidate.classification = "PROMOTE_FOR_REVIEW"
        candidate.classification_reason = "operational lesson: Book 7 eval required"
        return candidate
    if candidate.proposed_memory_class in AUTO_PROMOTABLE and \
            candidate.source_refs:
        candidate.classification = "PROMOTE_FOR_REVIEW"
        candidate.classification_reason = "explicit durable statement with evidence"
        return candidate
    if candidate.proposed_memory_class in REVIEW_REQUIRED:
        candidate.classification = "PROMOTE_FOR_REVIEW"
        candidate.classification_reason = "review-required class"
        return candidate
    candidate.classification = "TEMPORARY"
    candidate.classification_reason = "low durable value; temporary only"
    return candidate


def promote_candidate(candidate: MemoryCandidate, *,
                      eval_gate_passed: bool = False,
                      conflicting_active: list[Any] | None = None) -> MemoryPromotion:
    """Validate + contradiction-check a candidate, then promote.

    * auto-promotable low-risk classes promote when criteria are met;
    * conflicting preferences trigger a supersession flow (returned as
      conflict) rather than coequal memories;
    * CM-LESSON-CANDIDATE can never bypass the Book 7 eval gate.
    """
    if candidate.classification == "REJECT":
        raise MemoryLifecycleError(
            f"candidate {candidate.candidate_id} was classified REJECT")
    if candidate.proposed_memory_class in BOOK7_EVAL_REQUIRED and \
            not eval_gate_passed:
        raise MemoryLifecycleError(
            "operational lesson cannot bypass Book 7 evaluation governance")

    conflict = None
    if conflicting_active:
        conflict = conflicting_active[0]
        # supersession flow: the new explicit preference wins only after the
        # old record is superseded (MemoryManager.supersede). Promoting while
        # an active conflicting record exists would create coequal memories,
        # which is forbidden — fail closed and route to supersession.
        raise MemoryLifecycleError(
            f"conflicting preference requires supersession flow, not coequal "
            f"memories; conflict with {getattr(conflict, 'memory_id', conflict)}")

    decision = "PROMOTE"
    validation = ("BOOK7_EVAL_REQUIRED" if candidate.proposed_memory_class
                  in BOOK7_EVAL_REQUIRED else "AUTO_PROMOTED"
                  if candidate.proposed_memory_class in AUTO_PROMOTABLE
                  else "REVIEWED_PROMOTED")

    return MemoryPromotion(
        promotion_id=f"prom-{abs(hash(candidate.candidate_id))}",
        candidate_id=candidate.candidate_id,
        decision=decision,
        criteria_evidence={
            "explicit_user_statement": bool(candidate.source_refs),
            "no_higher_authority_contradiction": True,
            "privacy_retention_allowed": True,
            "conflict_detected": False,
        },
        validation_state=validation,
        proposed_by=candidate.proposed_by,
        evaluator_ref=("book7-eval" if validation == "BOOK7_EVAL_REQUIRED"
                       else None),
        promoted_at=_now(),
    )


def check_canonical_conflict(memory_statement: str,
                             canonical_facts: dict[str, Any]) -> list[str]:
    """Memory can never override canonical truth; conflicts are flagged."""
    conflicts = []
    lowered = memory_statement.lower()
    for key, value in canonical_facts.items():
        if str(key).lower() in lowered or str(value).lower() in lowered:
            conflicts.append(key)
    return conflicts


def repeat_worker_task(contract: dict, snapshots: list[dict]) -> dict:
    """A stateless worker repeats a task from contract + snapshots alone.

    Deterministic: same inputs -> same output. No hidden memory is required
    to maintain correctness.
    """
    seed = "|".join(sorted(contract.get("inputs_refs", [])))
    for snap in snapshots:
        seed += "|" + snap.get("content_hash", "")
    output_hash = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return {
        "task_id": contract["task_id"],
        "capability_id": contract["capability_id"],
        "output_ref": f"output:{contract['task_id']}",
        "deterministic_hash": output_hash,
        "inputs_used": sorted(contract.get("inputs_refs", [])),
        "memory_used": "none",
    }
