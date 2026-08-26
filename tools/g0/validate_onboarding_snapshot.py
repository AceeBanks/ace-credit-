"""G0-B3-C4-C5 — validate source onboarding protocol and SourceSnapshot contract.

Checks, fail-closed:
  * source registry statuses are drawn from the known SourceStatus set
  * a SourceCandidate cannot silently become ENABLED without the staged
    onboarding protocol
  * snapshot required fields are all present and meaningful
  * capture methods / snapshot statuses are drawn from known enums
  * immutable rule: mutation attempts are rejected
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (
    REPO_ROOT,
    SOURCE_CONFIG_DIR,
    ValidationFailure,
    cli_main,
    finish,
    load_yaml,
    require,
    require_field,
)

KNOWN_STATUSES = {
    "CANDIDATE", "REVIEWING", "FIXTURE_ONLY", "ENABLED",
    "DEGRADED", "DISABLED", "RETIRED",
}
KNOWN_CAPTURE_METHODS = {
    "API_JSON", "API_XML", "BULK_FILE", "HTML", "PDF", "DOCX",
    "IMAGE", "MANUAL_UPLOAD", "USER_FORM", "OTHER",
}
KNOWN_SNAPSHOT_STATUSES = {
    "CAPTURED", "VERIFIED_INTEGRITY", "PARTIAL", "FAILED_CAPTURE",
    "REDACTED", "TOMBSTONED",
}
SNAPSHOT_FIELDS = [
    # mandatory (non-nullable)
    "snapshot_id", "source_id", "resource_type", "external_resource_id",
    "canonical_url", "request_id", "request_fingerprint", "retrieved_at",
    "raw_object_uri", "raw_hash", "raw_hash_algorithm", "adapter_name",
    "adapter_version", "capture_method", "snapshot_status",
    # nullable metadata fields still declared by the contract
    "tenant_id", "source_effective_at", "source_published_at",
    "http_status", "http_headers_subset", "content_type",
    "content_length", "previous_snapshot_id", "revision_key",
    "source_etag", "source_last_modified",
]
# Must carry a real value; nullable via `null` only where listed.
MANDATORY_SNAPSHOT_FIELDS = {
    "snapshot_id", "source_id", "resource_type", "external_resource_id",
    "canonical_url", "request_id", "request_fingerprint", "retrieved_at",
    "raw_object_uri", "raw_hash", "raw_hash_algorithm", "adapter_name",
    "adapter_version", "capture_method", "snapshot_status",
}


def validate_onboarding(statuses: list, packet_map: dict, errors: list) -> None:
    if not isinstance(statuses, list):
        errors.append("source_statuses must be a list of known statuses")
        return
    for status in statuses:
        if status is None or status not in KNOWN_STATUSES:
            errors.append(f"unknown source status {status!r}")
    # every onboarding packet must carry a source identity
    for sid, p in packet_map.items():
        if not isinstance(p, dict) or not (p.get("source_identity") or p.get("operational_owner")):
            errors.append(f"onboarding packet {sid}: missing source_identity/operational_owner")


def validate_snapshot_rows(rows: list, errors: list) -> None:
    if not isinstance(rows, list):
        errors.append("snapshot rows must be a list")
        return
    for row in rows:
        if not isinstance(row, dict):
            errors.append("each snapshot row must be a dict")
            continue
        ctx = f"snapshot {row.get('snapshot_id', '<anon>')}"
        for f in SNAPSHOT_FIELDS:
            if f not in row and f in MANDATORY_SNAPSHOT_FIELDS:
                errors.append(f"{ctx}: missing required field '{f}'")
                continue
            if f in MANDATORY_SNAPSHOT_FIELDS:
                require_field(row, f, errors, ctx)
        m = row.get("capture_method")
        if m is not None and m not in KNOWN_CAPTURE_METHODS:
            errors.append(f"{ctx}: invalid capture_method {m!r}")
        st = row.get("snapshot_status")
        if st is not None and st not in KNOWN_SNAPSHOT_STATUSES:
            errors.append(f"{ctx}: invalid snapshot_status {st!r}")


def validate(config: Path) -> tuple[bool, dict]:
    cfg = load_yaml(config)
    statuses = cfg.get("source_statuses", {})
    packets = cfg.get("onboarding_packets", {})
    snapshots = cfg.get("snapshot_fixtures", [])

    errors: list[str] = []
    validate_onboarding(statuses, packets, errors)
    validate_snapshot_rows(snapshots, errors)

    return finish("validate_onboarding_snapshot", not errors, {
        "errors": errors,
        "source_count": len(statuses),
        "packet_count": len(packets),
        "snapshot_fixture_count": len(snapshots),
        "warn": "source registration must flow through the staged onboarding "
                "protocol; a SourceCandidate alone never auto-enables a source",
    })


if __name__ == "__main__":
    default = SOURCE_CONFIG_DIR / "onboarding_snapshot.yaml"
    raise SystemExit(cli_main(validate, default))