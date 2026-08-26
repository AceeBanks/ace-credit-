"""G0 Book 2 — B2.C4 identity semantics.

- opaque stable internal IDs validated against the B2.C3 prefix scheme;
- entity resolution produces an explicit status; name similarity may PROPOSE
  a merge but never silently merges protected entities (LAW-B1-022);
- opportunity identity rule: same number + amendment -> same opportunity new
  revision; issuer reissue semantics decide new-opportunity cases explicitly.
"""
from __future__ import annotations

import re
from enum import Enum

from prototype.g0.domain.models import (
    ExternalIdentifier,
    Organization,
    ResolutionStatus,
    VerificationState,
)

# B2.C3 identity prefixes (kept in lockstep with config/g0/domain/entity_types.yaml)
_PREFIXES = {
    "Organization": "org_", "Person": "person_", "OrganizationRole": "role_",
    "ExternalIdentifier": "extid_", "Program": "program_",
    "GrantOpportunity": "opp_", "OpportunityRevision": "opp_rev_",
    "EligibilityRule": "rule_", "EligibilityDecision": "eldec_",
    "Award": "award_", "ApplicationProject": "app_",
    "ApplicationRevision": "app_rev_", "Requirement": "req_", "Budget": "budget_",
    "CanonicalFact": "fact_", "EvidenceClaim": "claim_",
    "StatisticObservation": "stat_", "Artifact": "artifact_",
    "OutcomeFeedback": "outcome_", "Relationship": "rel_",
    "CommonGrantsExtension": "cgx_",
}


def validate_internal_id(entity_type: str, internal_id: str) -> bool:
    """B2.C4 — an internal ID must carry the entity's semantic prefix."""
    prefix = _PREFIXES.get(entity_type)
    if not prefix:
        return False
    return bool(re.fullmatch(re.escape(prefix) + r"[A-Za-z0-9_\-]+", internal_id))


def resolve_organizations(
    a: Organization,
    b: Organization,
    ids_a: list[ExternalIdentifier] | None = None,
    ids_b: list[ExternalIdentifier] | None = None,
) -> ResolutionStatus:
    """B2.C4 8.3 — resolution rule.

    - any shared VERIFIED external identifier (same namespace+value) that is
      issuer-authoritative (EIN/UEI) => MATCH_CONFIRMED;
    - otherwise, near-identical names without verified shared ID =>
      MATCH_PROBABLE_REVIEW (propose, never silently merge);
    - conflicting VERIFIED identifiers in the same namespace =>
      DISTINCT_CONFIRMED;
    - otherwise UNRESOLVED.
    """
    ids_a = ids_a or []
    ids_b = ids_b or []

    def verified(ids):
        return [i for i in ids if i.verification_state is VerificationState.VERIFIED]

    va, vb = verified(ids_a), verified(ids_b)
    shared = {(i.namespace, i.value) for i in va} & {(i.namespace, i.value) for i in vb}
    if shared and any(ns in {"EIN", "UEI"} for ns, _ in shared):
        return ResolutionStatus.MATCH_CONFIRMED

    # conflicting verified IDs in the same authoritative namespace => distinct
    by_ns_a = {i.namespace: {i.value} for i in va}
    by_ns_b = {i.namespace: {i.value} for i in vb}
    for ns in set(by_ns_a) & set(by_ns_b):
        if ns in {"EIN", "UEI"} and by_ns_a[ns] != by_ns_b[ns]:
            return ResolutionStatus.DISTINCT_CONFIRMED

    if _name_similar(a.legal_name, b.legal_name):
        return ResolutionStatus.MATCH_PROBABLE_REVIEW
    return ResolutionStatus.UNRESOLVED


def _name_similar(name_a: str, name_b: str) -> bool:
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())  # noqa: E731
    return norm(name_a) == norm(name_b)


def classify_opportunity_identity(number_a: str, number_b: str, *,
                                  same_issuer: bool = True,
                                  reissued_by_issuer: bool = False) -> str:
    """B2.C4 8.5 — same opportunity vs reissued opportunity.

    - same number, same issuer, no reissue => SAME_OPPORTUNITY
      (any amendment creates an OpportunityRevision, never a new root);
    - same number but issuer explicitly reissued (new cycle/semantics) =>
      REISSUED_NEW_OPPORTUNITY (explicit decision rule);
    - different number => REISSUED_NEW_OPPORTUNITY.
    """
    if number_a == number_b and same_issuer and not reissued_by_issuer:
        return "SAME_OPPORTUNITY"
    return "REISSUED_NEW_OPPORTUNITY"


def award_dedupe_candidate(record_a: dict, record_b: dict) -> bool:
    """B2.C4 8.6 — never merge awards solely on recipient/funder/amount."""
    issuer_id_a = record_a.get("issuer_award_id")
    issuer_id_b = record_b.get("issuer_award_id")
    if issuer_id_a and issuer_id_b:
        return issuer_id_a == issuer_id_b
    # without issuer IDs, matching on amount+recipient+funder alone is NOT
    # enough to dedupe — return False (distinct unless proven)
    return False
