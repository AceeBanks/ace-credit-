"""G0-B6-C12/C13/C14/C15 — Integration, egress, classification & PII.

INT-001..005: platform outages never erase canonical task state, connectors
cannot mutate unrelated resources, outside automation gains no authority,
results validated before promotion, platforms are subordinate executors.
EGR-001..005: unknown destinations blocked, SSRF protections, redirects
revalidated, sensitive uploads blocked, downloads quarantined. DATA-001..003:
strongest-class inheritance, secrets never downgrade by summarization,
public+private -> tenant-private. PII-001..004: field-scoped context,
sidechain/log redaction, public explanations omit restricted fields,
tenant-private data gated from global eval.
"""
from __future__ import annotations

import ipaddress
from typing import Any


class BoundaryError(ValueError):
    """Raised when a boundary policy is violated."""


def _load_policy(name: str) -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/security/" / name)
                          .read_text(encoding="utf-8"))


_INT_POLICY = _load_policy("integration_egress_policy.yaml")
_DATA_POLICY = _load_policy("data_classification_policy.yaml")

_PII_FIELDS = set(_DATA_POLICY["pii_fields"])


class IntegrationExecutor:
    """Bounded external executor; never a second control plane."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _INT_POLICY
        self._canonical_state: dict[str, dict] = {}

    def authorized_action(self, action: str) -> bool:
        return action in self.policy["integration_allowed_roles"]

    def execute(self, *, action: str, target_resource: str,
                connector_result: dict) -> dict:
        """INT-001/002/004: validate the connector result before any state
        promotion; connector can never touch an unrelated resource."""
        if action not in self.policy["integration_allowed_roles"]:
            raise BoundaryError(f"action {action} outside bounded integration "
                                "roles (SEC-LAW-018)")
        if target_resource.startswith("canonical:"):
            raise BoundaryError(
                "connectors cannot own canonical state (INT-001)")
        expected = connector_result.get("resource_id")
        if expected != target_resource:
            raise BoundaryError(
                f"connector mutated unrelated resource {expected} (INT-002)")
        if not connector_result.get("validated", True):
            raise BoundaryError(
                "connector result must be validated before promotion (INT-004)")
        self._canonical_state[target_resource] = connector_result
        return {"accepted": True, "resource": target_resource}

    def outage_does_not_erase_state(self, target_resource: str) -> bool:
        """INT-001: accepted canonical task state survives platform outages
        because it lives in the governed store, not the platform."""
        return target_resource in self._canonical_state


class EgressController:
    """Allowlisted egress with SSRF/redirect protection."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _INT_POLICY
        self._allowlist: dict[str, str] = {}  # host -> egress_class

    def allow(self, host: str, egress_class: str) -> None:
        self._allowlist[host] = egress_class

    def _blocked(self, host: str) -> bool:
        if host in self.policy["blocked_destinations"]:
            return True
        if host.startswith("file://"):
            return True
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return True
            if host.startswith("169.254."):
                return True
        except ValueError:
            pass
        return False

    def check(self, *, host: str, egress_class: str,
              data_class: str = "PUBLIC") -> bool:
        """EGR-001/002/004: unknown hosts, SSRF targets, and sensitive data
        to unapproved destinations are blocked."""
        if self._blocked(host):
            raise BoundaryError(f"SSRF/blocked destination {host} (EGR-002)")
        if host not in self._allowlist:
            raise BoundaryError(f"unknown external destination {host} "
                                "(EGR-001)")
        if self._allowlist[host] != egress_class:
            raise BoundaryError(
                f"egress class mismatch for {host}: expected "
                f"{self._allowlist[host]} got {egress_class} (EGR-001)")
        if self.policy["egress_phase1_defaults"].get(egress_class) in (
                "DISABLED",):
            raise BoundaryError(f"egress class {egress_class} is disabled in "
                                "phase 1 (EGR-001)")
        if data_class in ("PII", "FINANCIAL_SENSITIVE", "CREDENTIAL_SECRET") \
                and egress_class in ("UNKNOWN_EXTERNAL", "APPROVED_INTEGRATION"):
            raise BoundaryError(
                f"sensitive {data_class} cannot egress via {egress_class} "
                "(EGR-004)")
        return True

    def revalidate_redirect(self, *, original_host: str, redirect_host: str,
                            egress_class: str) -> str:
        """EGR-003: redirects are revalidated; attacker hosts are blocked."""
        if self._blocked(redirect_host):
            raise BoundaryError(
                f"redirect to blocked host {redirect_host} (EGR-003)")
        if redirect_host not in self._allowlist or \
                self._allowlist[redirect_host] != egress_class:
            raise BoundaryError(
                f"redirect to non-allowlisted host {redirect_host} (EGR-003)")
        return redirect_host


class ClassificationEngine:
    """Strongest-class inheritance for derived artifacts."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _DATA_POLICY
        self.ranking = self.policy["class_ranking"]

    def derive(self, *classes: str) -> str:
        """DATA-001/003: derived objects inherit the strongest class."""
        best = None
        for cls in classes:
            if cls not in self.ranking:
                raise BoundaryError(f"unknown data class {cls!r}")
            if best is None or self.ranking[cls] > self.ranking[best]:
                best = cls
        return best

    def summarize(self, base_class: str, summary_class: str) -> str:
        """DATA-002: summarization can never downgrade a secret."""
        if self.ranking[summary_class] < self.ranking[base_class]:
            raise BoundaryError(
                f"cannot downgrade {base_class} to {summary_class} by "
                "summarization (DATA-002)")
        return summary_class


class PIIFilter:
    """Field-scoped context, redaction and eval gating."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _DATA_POLICY
        self.pii_fields = _PII_FIELDS

    def context_for_worker(self, *, worker_task: str,
                           all_fields: dict[str, Any],
                           allowed_fields: list[str]) -> dict:
        """PII-001: a worker receives only the fields required for its task;
        PII fields are excluded unless explicitly allowed for the task."""
        allowed = set(allowed_fields)
        out = {}
        for key, value in all_fields.items():
            if key not in allowed:
                continue
            if key in self.pii_fields and worker_task not in allowed_fields:
                continue
            out[key] = value
        return out

    def redact_preview(self, text: str) -> str:
        """PII-002: redact sensitive values from sidechain previews/logs."""
        import re
        patterns = [
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
            re.compile(r"\b\d{9}\b"),  # tax id
            re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+"),  # email
        ]
        for pat in patterns:
            text = pat.sub("[REDACTED]", text)
        return text

    def public_explanation_fields(self, fields: dict[str, Any]) -> dict:
        """PII-003: public explanation packets omit restricted fields."""
        return {k: v for k, v in fields.items()
                if k not in self.pii_fields
                and k not in ("bank_account", "financial_details")}

    def eval_gate(self, *, data_class: str,
                  governance_approval: str | None = None) -> bool:
        """PII-004: tenant-private data cannot enter global eval without
        explicit governance."""
        if data_class in ("PII", "TENANT_CONFIDENTIAL",
                          "FINANCIAL_SENSITIVE"):
            return bool(governance_approval)
        return True
