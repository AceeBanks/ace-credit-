"""G0 Book 2 — B2.C11 requirement & content model helpers.

- A response may only be COMPLETED/SATISFIED when it actually links the
  artifact/evidence that satisfies it (unsupported partnership/testimonial
  content cannot be invented as completed evidence).
- Section content links must resolve to real link targets.
"""
from __future__ import annotations

from prototype.g0.domain.models import RequirementResponse

_COMPLETED_STATES = {"SATISFIED", "VERIFIED", "COMPLETED"}
_EVIDENCE_BEARING_RESPONSE_TYPES = {"section", "attachment", "support_letter",
                                    "certification"}


def completed_response_requires_link(response: RequirementResponse) -> bool:
    """A completed evidence-bearing response MUST point at an artifact version
    (or be a form/budget value that is itself the evidence). Returns True when
    the response is validly completed; False means it claims completion without
    evidence (fail closed)."""
    if response.state not in _COMPLETED_STATES:
        return True                        # not yet claiming completion
    if response.response_type in ("form", "budget"):
        return True                        # the value itself is the evidence
    if response.response_type in _EVIDENCE_BEARING_RESPONSE_TYPES:
        return bool(response.artifact_version_id)
    return False


def section_links_resolve(section, valid_target_ids: set[str]) -> list[str]:
    """Every content alignment link must resolve to a real target."""
    return [ref for ref in section.content_link_refs if ref not in valid_target_ids]
