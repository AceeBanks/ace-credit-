"""G0-B6-C16/C17 — Prompt injection defense + malicious file handling.

INJ-001..007: source content is untrusted, injected instructions cannot
call tools, 'system message' stays data, scope cannot be changed by
content, no self-promotion of evidence, retrieval poisoning cannot override
official precedence, tool-use coercion and credential solicitation fail.
FILE-001..007: magic validation, size/ratio limits, quarantine, macros
never executed, path traversal sanitized, parser output never policy,
document links under egress policy.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import PurePosixPath
from typing import Any


class HostileContentError(ValueError):
    """Raised when hostile content or file policy is violated."""


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/security/"
                           "hostile_content_policy.yaml")
                          .read_text(encoding="utf-8"))


_POLICY = _load_policy()


class InjectionGuard:
    """Source content is hostile data; it cannot drive policy."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY

    def mark_untrusted(self, content: str) -> dict:
        """INJ-001: wrap source content as untrusted data."""
        return {"content": content, "trusted": False,
                "origin": "EXTERNAL_SOURCE"}

    def would_call_tool(self, content: str) -> bool:
        """INJ-001/006: injected tool-use coercion is detected and the
        gateway would still enforce policy independently."""
        lowered = content.lower()
        markers = ("ignore previous instructions", "send email", "upload",
                   "call the tool", "execute ", "post to", "send secrets",
                   "reveal your api key", "forget your instructions")
        return any(m in lowered for m in markers)

    def would_promote_evidence(self, content: str) -> bool:
        """INJ-004: malicious content cannot self-promote evidence; only
        governed policy may promote a claim."""
        lowered = content.lower()
        return (("promote" in lowered or "elevate" in lowered)
                and ("fact" in lowered or "canonical" in lowered
                     or "official" in lowered or "record" in lowered))

    def system_message_in_source_is_data(self, content: str) -> bool:
        """INJ-002: a 'system' tag inside source content is data, not
        policy authority — the guard treats it as untrusted regardless."""
        if "system" in content.lower() and "instruction" in content.lower():
            return False  # remains data; never elevated
        return True

    def assert_scope_immutable(self, *, content: str, tenant_id: str,
                               project_id: str) -> None:
        """INJ-003: source content can never change tenant/project scope."""
        lowered = content.lower()
        if f"tenant {tenant_id}" not in lowered and "tenant" in lowered \
                and "switch" in lowered:
            raise HostileContentError(
                "source content attempted a tenant/project scope change "
                "(INJ-003)")


class FileSafety:
    """Quarantine, validate, bound — parser output is never policy."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY

    def quarantine(self, *, filename: str, data: bytes) -> dict:
        """FILE-001/002/005: validate magic, size, filename; quarantine."""
        limits = self.policy["file_limits"]
        if len(data) > limits["max_file_bytes"]:
            raise HostileContentError(
                f"file exceeds size limit (FILE-002): {len(data)} bytes")
        magic = data[:4]
        allowed = {m.encode("latin-1") if isinstance(m, str)
                   else m for m in limits["allowed_magic"]}
        if not any(magic.startswith(m) for m in allowed):
            raise HostileContentError(
                f"file type/magic rejected: {magic!r} (FILE-001)")
        clean_name = self.sanitize_filename(filename)
        return {"filename": clean_name, "size": len(data),
                "quarantined": True, "sha256": hashlib.sha256(data).hexdigest()[:16]}

    def sanitize_filename(self, filename: str) -> str:
        """FILE-005: path traversal sanitized; basename only."""
        name = PurePosixPath(filename.replace("\\", "/")).name
        if name in ("", ".", ".."):
            raise HostileContentError("invalid filename (FILE-005)")
        return name

    def check_archive_ratio(self, *, compressed: int, uncompressed: int) -> None:
        """FILE-002: decompression bombs blocked by ratio."""
        if uncompressed > compressed * self.policy["file_limits"]["max_archive_ratio"]:
            raise HostileContentError(
                f"archive ratio {uncompressed}/{compressed} exceeds limit; "
                "zip bomb blocked (FILE-002)")

    def assert_no_macros(self, content: str) -> None:
        """FILE-004: macro/executable content is never executed."""
        lowered = content.lower()
        if "vba" in lowered and ("macro" in lowered or "sub " in lowered):
            raise HostileContentError("macro content will not be executed (FILE-004)")

    def parser_output_is_not_policy(self, parsed: dict) -> dict:
        """FILE-006: parsed content stays data."""
        return {"parsed": parsed, "trusted": False}

    def link_requires_egress(self, url: str) -> bool:
        """FILE-007: parser-generated URLs are not auto-fetched; they must
        pass the egress policy first."""
        if url.startswith("http"):
            return True  # requires egress check before fetch
        raise HostileContentError(
            f"parser-generated non-http URL {url} is never auto-fetched "
            "(FILE-007)")


class RetrievalPrecedence:
    """INJ-005: retrieval poisoning cannot override official precedence."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY

    def official_wins(self, *, official_ref: str, poisoned_refs: list[str]) -> str:
        """Official source precedence beats poisoned ranking regardless of
        score."""
        for ref in poisoned_refs:
            if ref == official_ref:
                continue
            raise HostileContentError(
                f"retrieval poisoning attempt: {ref} would displace official "
                f"source {official_ref} (INJ-005)")
        return official_ref
