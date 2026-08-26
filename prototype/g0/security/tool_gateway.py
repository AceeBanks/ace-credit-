"""G0-B6-C9/C10/C11 — Tool registry, gateway and Hermes MCP facade.

TOOL-001..011: unknown/disabled tools denied, version changes with side
effects require review, tools cannot declare capabilities outside the
registry, discovered tools never auto-authorize, gateway enforces the
AuthorizationDecision independently (tool availability != permission),
credentials injected server-side and invisible to callers, egress on
redirects, external side effects need their own capability, returned
payloads never contain credentials, and role surfaces are filtered
(Personal vs CEO vs worker manifests).
"""
from __future__ import annotations

from typing import Any


class ToolError(ValueError):
    """Raised when a tool/gateway operation violates policy."""


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/security/"
                           "tool_registry_policy.yaml")
                          .read_text(encoding="utf-8"))


_POLICY = _load_policy()

_SIDE_EFFECT_RANK = {"NONE": 0, "READ_ONLY": 1, "INTERNAL_MUTATION": 2,
                     "EXTERNAL_SEND": 3, "EXTERNAL_SUBMIT": 4}


class ToolRegistry:
    """Governed, versioned tool definitions."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY
        self._tools: dict[str, dict] = {}
        self._approved_capabilities: set[str] = set()

    def approve_capability(self, capability_id: str) -> None:
        self._approved_capabilities.add(capability_id)

    def register(self, definition: dict, *, reviewed: bool = False) -> dict:
        """Register a tool. Discovered tools require the full review path
        (TOOL-005); version changes altering side effects/schema require
        review (TOOL-002)."""
        tool_id = definition["tool_id"]
        status = definition.get("status", "EXPERIMENTAL")
        if status not in self.policy["tool_statuses"]:
            raise ToolError(f"unknown tool status {status!r}")
        if definition.get("side_effect_class") not in \
                self.policy["side_effect_classes"]:
            raise ToolError(
                f"unknown side_effect_class "
                f"{definition.get('side_effect_class')!r}")

        # TOOL-003: tool cannot declare capabilities outside the registry
        for cap in definition.get("capability_ids", []):
            if cap not in self._approved_capabilities:
                raise ToolError(
                    f"tool {tool_id} declares unknown capability {cap} "
                    "(TOOL-003)")

        # TOOL-005: discovered tools start EXPERIMENTAL and need review to
        # reach APPROVED_PRODUCTION
        if definition.get("discovered"):
            if status in ("APPROVED_INTERNAL", "APPROVED_PRODUCTION"):
                raise ToolError(
                    "discovered tools cannot be auto-authorized to "
                    "production (TOOL-005); review required")

        # TOOL-002: version change with side effect/schema change needs review
        existing = self._tools.get(tool_id)
        if existing and existing["version"] != definition["version"]:
            side_changed = existing["side_effect_class"] != \
                definition.get("side_effect_class")
            schema_changed = existing.get("input_schema_ref") != \
                definition.get("input_schema_ref") or \
                existing.get("output_schema_ref") != \
                definition.get("output_schema_ref")
            if (side_changed or schema_changed) and not reviewed:
                raise ToolError(
                    f"tool {tool_id} version change alters side effects/"
                    "schema; review required (TOOL-002)")

        self._tools[tool_id] = dict(definition)
        return self._tools[tool_id]

    def get(self, tool_id: str) -> dict:
        tool = self._tools.get(tool_id)
        if tool is None:
            raise ToolError(f"unknown tool {tool_id} (TOOL-001)")
        return tool

    def enabled(self, tool_id: str) -> bool:
        try:
            return self.get(tool_id)["status"] != "DISABLED"
        except ToolError:
            return False


class ToolGateway:
    """Executes governed requests; enforces policy independently."""

    def __init__(self, registry: ToolRegistry,
                 policy: dict | None = None) -> None:
        self.registry = registry
        self.policy = policy or _POLICY
        self._audit: list[dict] = []
        self._executed: dict[str, str] = {}  # request_id -> tool_id

    def _idempotency_key(self, request_body: dict) -> str | None:
        return request_body.get("request_id") or request_body.get("nonce")

    def _assert_not_replayed(self, tool: dict, request_body: dict) -> None:
        """TOOL-012: an external-side-effect tool request with a reused
        request_id/nonce is a replay; the gateway refuses to execute it a
        second time."""
        key = self._idempotency_key(request_body)
        if key is None:
            return
        if tool["side_effect_class"] in ("EXTERNAL_SEND",
                                          "EXTERNAL_SUBMIT"):
            if key in self._executed:
                raise ToolError(
                    f"replay detected: request {key} already executed by "
                    f"{self._executed[key]} (TOOL-012)")
            self._executed[key] = tool["tool_id"]

    def dispatch(self, *, tool_id: str, request_body: dict,
                 authorization_decision: dict, actor: str,
                 credential_ref_id: str | None = None,
                 vault=None, tenant_id: str = "") -> dict:
        """TOOL-006: the gateway enforces the decision; availability is not
        permission."""
        tool = self.registry.get(tool_id)
        if tool["status"] == "DISABLED":
            raise ToolError(f"tool {tool_id} is disabled (TOOL-004)")

        # the AuthorizationDecision must ALLOW for the tool's capability;
        # a missing/erroring decision fails closed (no availability = no
        # permission)
        if authorization_decision is None or \
                authorization_decision.get("decision") != "ALLOW":
            reason = ((authorization_decision or {})
                      .get("reason_code") or "DECISION_UNAVAILABLE")
            raise ToolError(
                f"tool {tool_id} denied by AuthorizationDecision "
                f"({reason}) (TOOL-006)")

        capability_ids = tool["capability_ids"]
        granted = authorization_decision.get("granted_capability_id")
        if granted and granted not in capability_ids:
            raise ToolError(
                f"capability/tool mismatch: {granted} not declared by "
                f"{tool_id} (TOOL-003)")

        # TOOL-009: external side effects require the matching capability
        side = tool["side_effect_class"]
        if side in ("EXTERNAL_SEND", "EXTERNAL_SUBMIT"):
            if granted not in ("egress.send_external", "submission.execute"):
                raise ToolError(
                    f"tool {tool_id} has external side effect {side}; "
                    "requires side-effect capability (TOOL-009)")

        # TOOL-008: destination must be in the tool's allowlist
        destination = request_body.get("destination")
        if destination and destination not in tool.get("network_destinations", []):
            raise ToolError(
                f"destination {destination} not allowed for {tool_id} "
                "(TOOL-008)")

        # TOOL-012: replay/idempotency guard before any side effect
        self._assert_not_replayed(tool, request_body)

        # TOOL-007: credentials injected server-side; caller can't override
        headers = dict(request_body.get("headers") or {})
        if any("authorization" in k.lower() for k in headers):
            raise ToolError(
                "caller cannot override the injected auth header (TOOL-007)")
        secret_payload = None
        if credential_ref_id:
            if vault is None:
                raise ToolError("credential reference requires a vault")
            secret_payload = vault.resolve(
                ref_id=credential_ref_id, requesting_tenant=tenant_id,
                capability_id=granted or capability_ids[0],
                destination=destination)

        result = self._execute(tool, request_body)

        # TOOL-010: returned payload never contains credential material
        if secret_payload and secret_payload in str(result):
            raise ToolError(
                "credential leaked into returned payload (TOOL-010)")

        self._audit.append({"tool_id": tool_id, "actor": actor,
                            "side_effect_class": side,
                            "request_id": request_body.get("request_id")})
        return result

    def _execute(self, tool: dict, body: dict) -> dict:
        # prototype executor: deterministic, schema-bounded result
        return {"tool_id": tool["tool_id"], "status": "OK",
                "result_size": len(str(body))}

    def audit_trail(self) -> list[dict]:
        return list(self._audit)


class MCPFacade:
    """Filtered product facade: role surfaces + hidden capabilities."""

    def __init__(self, registry: ToolRegistry,
                 policy: dict | None = None) -> None:
        self.registry = registry
        self.policy = policy or _POLICY
        self._tool_capabilities: dict[str, list[str]] = {}

    def bind_tool(self, tool_id: str, capabilities: list[str]) -> None:
        self._tool_capabilities[tool_id] = list(capabilities)

    def surface_for(self, role: str) -> list[str]:
        """Personal, CEO, or worker manifests (TOOL-011)."""
        if role == "PERSONAL_HERMES":
            allowed = set(self.policy["personal_surface_capabilities"])
        elif role == "CEO_HERMES":
            allowed = set(self.policy["ceo_surface_capabilities"])
        elif role == "WORKER":
            # workers receive reduced manifests: no operational state
            # mutations, no approval/credential/egress surfaces
            allowed = set(self.policy["ceo_surface_capabilities"]) - {
                "operational.state_bounded"}
        else:
            raise ToolError(f"unknown role {role!r}")
        out = []
        for tool_id, caps in self._tool_capabilities.items():
            if not self.registry.enabled(tool_id):
                continue
            if any(c in allowed for c in caps):
                out.append(tool_id)
        return out

    def discover(self, tool_id: str) -> dict:
        """A CEO cannot discover hidden submission tools (TOOL-011)."""
        tool = self.registry.get(tool_id)
        if any(c in tool.get("capability_ids", [])
               for c in self.policy["hidden_never_capabilities"]):
            raise ToolError(f"tool {tool_id} is hidden (never discoverable)")
        return tool
