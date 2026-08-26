"""G0-B6-C20..C23 — Token/credential lifecycle, break-glass, revocation,
incident recovery and security observability.

LIF-001..007: short-lived tokens, refresh requires valid principal,
independent grant expiry, transparent rotation, dependent revocation,
bounded decision caches, revoked membership invalidates decisions,
compromised credentials blocked.
BG-001..006: explicit break-glass principal, mandatory reason, elevated
audit, short expiry, no silent use, post-event review, cannot bypass
immutable restrictions.
REV-001..005: tool disable blocks use, compromise never resets Hermes
memory, revoked worker grant fails closed, evidence preserved, revocation
bound.
OBS-001..006: IDs/hashes over raw payloads, alert classes, tenant-filtered
telemetry.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


class LifecycleError(ValueError):
    """Raised on lifecycle/break-glass/revocation/observability violation."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _load_policy(name: str) -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / f"config/g0/security/{name}")
                          .read_text(encoding="utf-8"))


_LIFECYCLE = _load_policy("lifecycle_policy.yaml")
_OBS = _load_policy("observability_policy.yaml")


class LifecycleRegistry:
    """Sessions/tokens/credentials with state transitions and cache bounds."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _LIFECYCLE
        self._tokens: dict[str, dict] = {}
        self._credentials: dict[str, dict] = {}
        self._revoked: dict[str, str] = {}          # object_id -> reason
        self._cache: dict[str, tuple[bool, str]] = {}  # cache_key -> (allow, at)

    # -- token lifecycle ------------------------------------------------

    def issue_token(self, *, token_id: str, principal_id: str,
                    tenant_id: str, ttl_seconds: int = 300) -> dict:
        """LIF-001: short-lived session/service tokens."""
        if ttl_seconds > 3600:
            raise LifecycleError(
                f"token TTL {ttl_seconds}s exceeds short-lived bound (LIF-001)")
        now = _now()
        tok = {
            "token_id": token_id,
            "principal_id": principal_id,
            "tenant_id": tenant_id,
            "state": "ACTIVE",
            "issued_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=ttl_seconds)).isoformat(),
        }
        self._tokens[token_id] = tok
        return tok

    def refresh_token(self, *, token_id: str, principal_id: str) -> dict:
        """LIF-001: refresh requires a valid principal."""
        tok = self._tokens.get(token_id)
        if tok is None:
            raise LifecycleError("unknown token (LIF-001)")
        if tok["state"] == "REVOKED":
            raise LifecycleError("revoked token cannot refresh (LIF-001)")
        if self._is_expired(tok["expires_at"]):
            raise LifecycleError("expired token cannot refresh (LIF-001)")
        if tok["principal_id"] != principal_id:
            raise LifecycleError("refresh requires valid principal (LIF-001)")
        tok["expires_at"] = (_now() + timedelta(seconds=300)).isoformat()
        return tok

    def revoke(self, *, object_id: str, object_type: str,
               reason: str) -> None:
        """LIF-004/REV-001..003: revoke object + dependents."""
        if object_type == "token":
            tok = self._tokens.get(object_id)
            if tok:
                tok["state"] = "REVOKED"
                self._revoked[object_id] = reason
                self._revoke_membership_and_grants(tok["principal_id"])
        elif object_type == "credential":
            cred = self._credentials.get(object_id)
            if cred:
                cred["state"] = "REVOKED"
                self._revoked[object_id] = reason
                # dependent revocation: everything bound to this credential
                for tid, tok in list(self._tokens.items()):
                    if tok.get("credential_id") == object_id:
                        tok["state"] = "REVOKED"
                        self._revoked[tid] = f"dependent: {reason}"
        else:
            self._revoked[object_id] = reason

    def _revoke_membership_and_grants(self, principal_id: str) -> None:
        self._revoked[f"membership:{principal_id}"] = \
            "dependent revocation of token holder (LIF-004)"

    def _is_expired(self, iso: str) -> bool:
        try:
            exp = datetime.fromisoformat(iso)
        except ValueError:
            return True
        return exp <= _now()

    def token_state(self, *, token_id: str, principal_id: str,
                    membership_active: bool) -> str:
        """LIF-001/005/006: revoked membership invalidates decisions."""
        tok = self._tokens.get(token_id)
        if tok is None:
            return "UNKNOWN"
        if tok["state"] == "REVOKED":
            return "REVOKED"
        if self._is_expired(tok["expires_at"]):
            return "EXPIRED"
        if not membership_active:
            return "MEMBERSHIP_REVOKED"
        if tok["principal_id"] != principal_id:
            return "PRINCIPAL_MISMATCH"
        return tok["state"]

    def mark_compromised(self, *, object_id: str, object_type: str) -> None:
        """LIF-007: compromised credential blocked even while valid."""
        if object_type == "credential":
            cred = self._credentials.get(object_id)
            if cred:
                cred["state"] = "COMPROMISED"
                self.revoke(object_id=object_id, object_type="credential",
                            reason="compromise (LIF-007)")
        elif object_type == "token":
            tok = self._tokens.get(object_id)
            if tok:
                tok["state"] = "COMPROMISED"
                self.revoke(object_id=object_id, object_type="token",
                            reason="compromise (LIF-007)")

    # -- credential lifecycle -------------------------------------------

    def register_credential(self, *, credential_id: str,
                            service_identity: str) -> dict:
        """LIF-003: credentials are referenced, never exposed."""
        cred = {
            "credential_id": credential_id,
            "service_identity": service_identity,
            "state": "ACTIVE",
            "rotations": 0,
        }
        self._credentials[credential_id] = cred
        return cred

    def rotate_credential(self, *, credential_id: str) -> dict:
        """LIF-003: rotation transparent; old/new secrets never returned."""
        cred = self._credentials.get(credential_id)
        if cred is None:
            raise LifecycleError("unknown credential (LIF-003)")
        if cred["state"] in ("REVOKED", "COMPROMISED"):
            raise LifecycleError("cannot rotate revoked/compromised "
                                 "credential (LIF-003)")
        cred["rotations"] += 1
        cred["state"] = "ACTIVE"
        return {"credential_id": credential_id,
                "rotations": cred["rotations"]}  # no secret material

    # -- decision cache --------------------------------------------------

    def cache_decision(self, *, cache_key: str, allow: bool) -> None:
        self._cache[cache_key] = (allow, _now().isoformat())

    def cached_allow(self, *, cache_key: str, revoked_after: str) -> bool:
        """LIF-005/REV-005: cached allows cannot survive revocation beyond
        the bound."""
        hit = self._cache.get(cache_key)
        if hit is None:
            return False
        allow, at = hit
        if not allow:
            return False
        bound = self.policy["cache_policy"]["revocation_invalidation_bound_seconds"]

        def _parse(iso: str) -> datetime:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt

        cached_at = _parse(at)
        revoked_at = _parse(revoked_after)
        # if revocation happened after caching and beyond the bound → stale
        if revoked_at > cached_at and \
                (_now() - cached_at).total_seconds() > bound:
            return False
        return True


class BreakGlassRegistry:
    """BG-001..006: explicit, temporary, audited emergency admin."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _LIFECYCLE
        self._actions: list[dict] = []

    def invoke(self, *, actor_id: str, reason: str, purpose: str,
               ttl_seconds: int = 900) -> dict:
        """BG-001/002/004: explicit principal, mandatory reason, short TTL."""
        if purpose not in self.policy["break_glass_purposes"]:
            raise LifecycleError(
                f"purpose {purpose!r} not an allowed break-glass purpose "
                "(BG-001)")
        if not reason or len(reason.strip()) < 8:
            raise LifecycleError("break-glass requires a mandatory reason "
                                 "(BG-002)")
        if ttl_seconds > 3600:
            raise LifecycleError("break-glass TTL must be short (BG-004)")
        entry = {
            "action_id": f"BG-{len(self._actions) + 1:04d}",
            "actor_id": actor_id,
            "purpose": purpose,
            "reason": reason,
            "granted_at": _now().isoformat(),
            "expires_at": (_now() + timedelta(seconds=ttl_seconds)).isoformat(),
            "audit_class": "A4",
            "status": "ACTIVE",
        }
        self._actions.append(entry)
        return entry

    def authorize(self, *, action_id: str, actor_id: str,
                  audit_write_ok: bool) -> bool:
        """BG-003/005/006: elevated audit + no silent use + expiry."""
        for entry in self._actions:
            if entry["action_id"] != action_id:
                continue
            if entry["actor_id"] != actor_id:
                return False
            if not audit_write_ok:
                raise LifecycleError(
                    "break-glass requires elevated audit write (BG-003)")
            if entry["status"] != "ACTIVE":
                return False
            if self._is_expired(entry["expires_at"]):
                entry["status"] = "EXPIRED"
                return False
            return True
        return False

    def list_visible(self) -> list[dict]:
        """BG-005: use is visible in security reports (no silent use)."""
        return [dict(e) for e in self._actions]

    def _is_expired(self, iso: str) -> bool:
        try:
            exp = datetime.fromisoformat(iso)
        except ValueError:
            return True
        return exp <= _now()


class IncidentRecovery:
    """REV-004/incident sequence: preserve evidence, then recover."""

    def __init__(self) -> None:
        self._evidence_preserved: list[str] = []

    def run(self, sequence: list[str] | None = None) -> list[str]:
        expected = self._load_policy("lifecycle_policy.yaml")[
            "incident_sequence"]
        seq = sequence or expected
        # REV-004: evidence is never deleted during recovery — the canonical
        # sequence must always include preservation and assessment before any
        # repair/restore steps.
        if "PRESERVE_EVIDENCE" not in seq:
            raise LifecycleError("incident sequence missing PRESERVE_EVIDENCE "
                                 "(REV-004)")
        if "ASSESS_AFFECTED_TENANTS_RESOURCES" not in seq:
            raise LifecycleError(
                "incident sequence missing tenant/resource assessment "
                "(REV-004)")
        repair = seq.index("ROTATE_REPAIR") if "ROTATE_REPAIR" in seq else -1
        preserve = seq.index("PRESERVE_EVIDENCE")
        if repair != -1 and preserve > repair:
            raise LifecycleError(
                "evidence must be preserved before repair begins (REV-004)")
        self._evidence_preserved.append(":".join(seq))
        return seq

    def preserved(self) -> list[str]:
        return list(self._evidence_preserved)

    @staticmethod
    def _load_policy(name: str) -> dict:
        import yaml
        from pathlib import Path
        root = Path(__file__).resolve().parents[3]
        return yaml.safe_load((root / f"config/g0/security/{name}")
                              .read_text(encoding="utf-8"))


class SecurityObservability:
    """OBS-001..006: structured, tenant-filtered, redaction-aware signals."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _OBS
        self._events: list[dict] = []

    def record(self, *, tenant_id: str, signal: str, reason_code: str,
               detail: dict | None = None, raw: str | None = None) -> dict:
        """OBS-001: IDs/hashes/reason codes, never raw sensitive payloads."""
        if signal not in self.policy["signal_classes"]:
            raise LifecycleError(
                f"unknown observability signal {signal!r} (OBS-001)")
        detail = detail or {}
        if raw is not None:
            # redact anything that looks like a secret value
            redacted = "REDACTED" if self._looks_secret(raw) else raw
            detail = {**detail, "raw": redacted}
        ev = {
            "tenant_id": tenant_id,
            "signal": signal,
            "reason_code": reason_code,
            "detail": detail,
            "alert_class": self.policy["class_thresholds"].get(
                signal, "INFO"),
            "at": _now().isoformat(),
        }
        self._events.append(ev)
        return ev

    def _looks_secret(self, value: str) -> bool:
        low = value.lower()
        markers = ("sk-", "secret", "api_key", "password", "token=",
                   "bearer ")
        return any(m in low for m in markers)

    def tenant_events(self, *, tenant_id: str) -> list[dict]:
        """OBS-006: tenant-filtered telemetry."""
        return [e for e in self._events if e["tenant_id"] == tenant_id]

    def alerts_above(self, threshold: str) -> list[dict]:
        order = ["INFO", "WARNING", "HIGH", "CRITICAL_P0"]
        t = order.index(threshold)
        return [e for e in self._events
                if order.index(e["alert_class"]) >= t]

    def all_events(self) -> list[dict]:
        return [dict(e) for e in self._events]
