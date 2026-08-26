"""G0-B3-C18 — Private/foundation/corporate source protocol.

Supports the client's non-government grant categories without a mandatory paid
data dependency. Fail-closed rules:
  * a private source is only ENABLED after ALL registration requirements are
    met (issuer ownership, pages, update frequency, terms/robots, crawler
    strategy, authority limits, winner support);
  * a missing stable external ID never blocks internal source/opportunity
    identity (uncertainty is preserved, not invented away);
  * a webpage redesign does not silently create a duplicate opportunity —
    identity resolution supports continuity;
  * an old/archived foundation page never outranks the current issuer page.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PrivateSourceStatus(Enum):
    PENDING = "PENDING"
    REGISTERED = "REGISTERED"
    ENABLED = "ENABLED"
    REJECTED = "REJECTED"
    RETIRED = "RETIRED"


# Every registration requirement from private_source_policy.yaml.
REGISTRATION_REQUIREMENTS = [
    "issuer_ownership_verified",
    "relevant_pages_identified",
    "update_frequency_estimated",
    "terms_robots_reviewed",
    "crawler_strategy_tested",
    "authority_limited_to_issuer_controlled_facts",
    "historical_winners_only_where_supported",
]


@dataclass(frozen=True)
class PrivateSource:
    source_id: str                 # governed internal identity (never depends on
                                   # an external stable ID)
    name: str
    base_domains: list[str]
    status: PrivateSourceStatus = PrivateSourceStatus.PENDING
    satisfied_requirements: set[str] = field(default_factory=set)
    external_id: str | None = None  # may be None: uncertainty preserved

    def registration_errors(self) -> list[str]:
        """Fail-closed: ALL requirements must be satisfied to enable."""
        errors: list[str] = []
        for req in REGISTRATION_REQUIREMENTS:
            if req not in self.satisfied_requirements:
                errors.append(f"{self.source_id}: missing registration "
                              f"requirement '{req}'")
        if self.status is PrivateSourceStatus.ENABLED and errors:
            errors.append(f"{self.source_id}: ENABLED despite unmet requirements")
        return errors


@dataclass(frozen=True)
class PageFingerprint:
    """What identity resolution may use to recognize continuity across a
    redesign: canonical URL pattern, issuer-visible opportunity key, and the
    raw page hash of the previous capture."""

    canonical_url: str
    opportunity_key: str | None   # e.g. funder program slug or URL path token
    page_hash: str | None


class RedesignResolution(Enum):
    SAME_OPPORTUNITY = "SAME_OPPORTUNITY"
    NEW_OPPORTUNITY = "NEW_OPPORTUNITY"
    NEEDS_REVIEW = "NEEDS_REVIEW"


def resolve_redesign(prev: PageFingerprint, new: PageFingerprint) -> RedesignResolution:
    """Identity continuity across page redesigns (fail-closed).

    Same canonical URL AND same opportunity key (or an unchanged page hash)
    means the redesign is the SAME opportunity. A changed key on the same
    canonical URL is NEEDS_REVIEW — never silently NEW. A genuinely different
    canonical URL with a different key is a NEW opportunity only when the
    issuer-visible key differs; ambiguous cases need review.
    """
    if new.canonical_url == prev.canonical_url:
        if new.opportunity_key is not None and new.opportunity_key == prev.opportunity_key:
            return RedesignResolution.SAME_OPPORTUNITY
        if new.opportunity_key is None and new.page_hash == prev.page_hash:
            return RedesignResolution.SAME_OPPORTUNITY
        return RedesignResolution.NEEDS_REVIEW
    # different canonical URL
    if (new.opportunity_key is not None and prev.opportunity_key is not None
            and new.opportunity_key != prev.opportunity_key):
        return RedesignResolution.NEW_OPPORTUNITY
    return RedesignResolution.NEEDS_REVIEW


def missing_stable_id_allows_internal_identity(source_id: str, name: str) -> PrivateSource:
    """A private funder without any clean external ID still gets governed
    internal identity (uncertainty preserved, identity never blocked)."""
    return PrivateSource(source_id=source_id, name=name,
                         base_domains=[], external_id=None,
                         status=PrivateSourceStatus.PENDING)
