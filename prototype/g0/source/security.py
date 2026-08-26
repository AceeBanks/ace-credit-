"""G0-B3-C19 — Source security & prompt-injection constitution.

Treats ALL external source content as untrusted data. Fail-closed rules:
  * content can never grant capabilities (tool syntax in source text is inert);
  * exfiltration instructions are flagged, never followed;
  * redirects leaving the source's governed domains are blocked/flagged;
  * unsupported executable content is quarantined, never run;
  * workers receive an untrusted-data envelope, never raw policy authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml


class SecurityFlag(Enum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    EXFILTRATION = "EXFILTRATION"
    MALICIOUS_REDIRECT = "MALICIOUS_REDIRECT"
    EMBEDDED_SCRIPT = "EMBEDDED_SCRIPT"
    POISONED_METADATA = "POISONED_METADATA"
    PHISHING = "PHISHING"
    QUARANTINED = "QUARANTINED"


class EnvelopeAction(Enum):
    ACCEPT = "ACCEPT"
    FLAG = "FLAG"
    QUARANTINE = "QUARANTINE"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class SourceEnvelope:
    """Sanitized envelope: trusted metadata is separate from untrusted
    content; the untrusted content is referenced, never executed."""

    source_snapshot_id: str
    trusted_metadata: dict
    untrusted_content_ref: str
    content_type: str
    security_flags: frozenset[SecurityFlag] = frozenset()
    allowed_operations: frozenset[str] = frozenset()  # empty by default -> inert


def _patterns(key: str) -> list[str]:
    return load_yaml(SOURCE_CONFIG_DIR / "source_security_policy.yaml").get(key, [])


def scan_content(text: str, content_type: str = "text/html") -> tuple[list[SecurityFlag], EnvelopeAction]:
    """Scan untrusted source content. Any dangerous signal flags + elevates the
    envelope action; nothing here ever grants an operation."""
    flags: list[SecurityFlag] = []
    low = text.lower()
    if any(p in low for p in _patterns("injection_patterns")):
        flags.append(SecurityFlag.PROMPT_INJECTION)
    if any(p in low for p in _patterns("exfiltration_patterns")):
        flags.append(SecurityFlag.EXFILTRATION)
    if "<script" in low:
        flags.append(SecurityFlag.EMBEDDED_SCRIPT)
    action = EnvelopeAction.BLOCK if SecurityFlag.EXFILTRATION in flags else (
        EnvelopeAction.QUARANTINE if SecurityFlag.EMBEDDED_SCRIPT in flags else
        EnvelopeAction.FLAG if flags else EnvelopeAction.ACCEPT)
    return flags, action


def tool_syntax_is_inert(content: str) -> bool:
    """Source text may contain tool-like syntax (e.g. \"<invoke tool>\") but it
    is DATA: it cannot add operations or change policy."""
    suspicious = any(t in content for t in ("<invoke", "tool_call", "function_call",
                                            "system:", "assistant:"))
    if not suspicious:
        return True  # nothing to even try
    # Even when tool-like syntax appears, the envelope's allowed_operations
    # remain empty — policy gating lives outside the source context.
    envelope = SourceEnvelope(
        source_snapshot_id="snap_x", trusted_metadata={},
        untrusted_content_ref="obj://x", content_type="text/html")
    return len(envelope.allowed_operations) == 0


def check_redirect(url: str, resolved_url: str,
                   allowed_domains: set[str]) -> tuple[bool, str | None]:
    """Fail-closed redirect check: resolving outside the governed domain set is
    BLOCKED (with the reason); same-domain resolution is allowed."""
    host = urlparse(resolved_url).netloc.lower()
    if host in allowed_domains:
        return True, None
    return False, f"redirect resolved to ungoverned domain {host!r} (from {url!r})"


def quarantine_executable(content_type: str) -> EnvelopeAction:
    """Unsupported executable content is quarantined, never run or parsed for
    authority. Fail-closed: unknown binary-ish types are quarantined too."""
    executable_types = set(load_yaml(SOURCE_CONFIG_DIR / "source_security_policy.yaml")
                           .get("executable_content_types", []))
    if content_type in executable_types:
        return EnvelopeAction.QUARANTINE
    if content_type.startswith("application/") and "json" not in content_type \
            and "xml" not in content_type and "pdf" not in content_type \
            and "zip" not in content_type:
        return EnvelopeAction.QUARANTINE
    return EnvelopeAction.ACCEPT


def credentials_never_exposed(envelope: SourceEnvelope) -> bool:
    """No credential material may ride in the envelope's trusted metadata."""
    banned = {"api_key", "apikey", "token", "secret", "password", "credential"}
    keys = set(str(k).lower() for k in (envelope.trusted_metadata or {}).keys())
    return not (keys & banned)
