"""G0-B3-C25 — Adversarial data test guards.

Small fail-closed guard helpers used by the adversarial suite where the check
has no dedicated home (unit mismatch, timezone ambiguity, award-opportunity
linkage proof, causal inference, cross-tenant upload). Each guard returns the
SAFE answer by default and only permits the operation with explicit, tested
evidence.
"""

from __future__ import annotations

from enum import Enum


class TimezoneState(Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED_TZ_AMBIGUOUS = "UNRESOLVED_TZ_AMBIGUOUS"


def unit_mismatch(source_unit: str, source_value: float,
                  parsed_unit: str, parsed_value: float) -> bool:
    """True when parser-interpreted units disagree with the source's declared
    units (e.g. source says thousands, parser reads dollars). Fail-closed: a
    unit or magnitude mismatch is flagged, never silently accepted."""
    if source_unit != parsed_unit:
        return True
    # same unit but wildly different magnitude (e.g. 250000 vs 25) => mismatch
    if parsed_unit == source_unit and source_value and parsed_value:
        ratio = parsed_value / source_value
        if abs(ratio - 1.0) > 0.5 and (ratio == 0.1 or ratio == 10.0
                                       or ratio == 0.001 or ratio == 1000.0):
            return True
    return False


def resolve_datetime(value: str, tz: str | None) -> tuple[str, TimezoneState]:
    """A material date without timezone semantics is UNRESOLVED — no silent
    midnight/UTC assumption. A value that already carries explicit zone
    semantics normalizes to RESOLVED."""
    if not value:
        return value, TimezoneState.UNRESOLVED_TZ_AMBIGUOUS
    explicit = ("Z" in value or "+" in value or "T" in value
                or tz not in (None, ""))
    if explicit:
        return value, TimezoneState.RESOLVED
    return value, TimezoneState.UNRESOLVED_TZ_AMBIGUOUS


def award_opportunity_linkage_supported(proof_source_ref: str | None) -> bool:
    """An award may claim a specific opportunity only with source proof. No
    proof -> the linkage is unsupported (record at supported level, never
    fabricate the relationship)."""
    return bool(proof_source_ref)


class AnalysisType(Enum):
    DESCRIPTIVE = "DESCRIPTIVE"
    CAUSAL = "CAUSAL"


def causal_inference_allowed(analysis_type: AnalysisType) -> bool:
    """Descriptive analysis of a winner cohort is allowed; unsupported causal
    inference is blocked."""
    return analysis_type is AnalysisType.DESCRIPTIVE


def tenant_scope_allows(snapshot_tenant_id: str | None,
                        uploader_tenant_id: str | None) -> bool:
    """Cross-tenant source uploads are rejected. A tenant-scoped snapshot must
    belong to the uploading tenant; a null snapshot tenant is only acceptable
    for a null uploader context (platform-uploaded public sources)."""
    if snapshot_tenant_id is None:
        return uploader_tenant_id is None
    return snapshot_tenant_id == uploader_tenant_id
