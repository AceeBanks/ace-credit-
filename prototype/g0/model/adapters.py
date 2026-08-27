"""G0-B7-PHASE-B — Provider adapters behind the governed Model Gateway.

Adapters are subordinate: they receive an already-authorized ModelRequest
and a server-side-resolved credential, and return a normalized raw payload
that the gateway wraps into the typed ModelResponse. Provider details live
inside the adapter; the gateway and callers stay provider-independent.

OpenRouterAdapter is the bounded real adapter (DEV_RUNTIME_ONLY credential
mode, pinned origin, pinned model list, timeout/retry/cost metadata). A
FakeAdapter is provided for deterministic unit tests with network mocked.
"""
from __future__ import annotations

import json
import time
import urllib.parse
from typing import Any

from prototype.g0.model.gateway import ModelError

_OPENROUTER_ORIGIN = "https://openrouter.ai"
_OPENROUTER_CHAT_PATH = "/api/v1/chat/completions"


class OpenRouterAdapter:
    """Bounded OpenRouter chat-completions adapter.

    Pinned behavior (MR-003): the only reachable destination is the
    configured origin + chat path; any redirect off-origin is refused; the
    model must be in the profile's allowed list (re-checked here as
    defense-in-depth); cost metadata follows OpenRouter usage fields when
    present. The credential is injected server-side by the gateway.
    """

    def __init__(self, *, timeout_seconds: int = 60,
                 max_retries: int = 1) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @staticmethod
    def _check_redirect(location: str) -> None:
        """EGR-003: redirects revalidated before following — off-origin
        redirects are refused."""
        target = urllib.parse.urlparse(location)
        origin = urllib.parse.urlparse(_OPENROUTER_ORIGIN)
        if target.scheme != origin.scheme or target.hostname != origin.hostname:
            raise ModelError(
                f"redirect to unapproved destination {location!r} refused "
                "(MR-003/EGR-003)")

    def invoke(self, *, model_request: dict,
               credential: str) -> dict:
        import requests  # available in this environment (validated)

        model_id = model_request.get("model_id")
        if not model_id:
            raise ModelError("missing model_id (MR-002)")
        url = _OPENROUTER_ORIGIN + _OPENROUTER_CHAT_PATH
        payload = {
            "model": model_id,
            "messages": model_request.get("messages", []),
        }
        if model_request.get("temperature") is not None:
            payload["temperature"] = model_request["temperature"]
        if model_request.get("max_output_tokens"):
            payload["max_completion_tokens"] = \
                model_request["max_output_tokens"]
        if model_request.get("structured_output_schema_ref"):
            payload["response_format"] = {
                "type": "json_object",
                "schema_ref": model_request["structured_output_schema_ref"],
            }

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    url, json=payload, timeout=self.timeout_seconds,
                    headers={
                        "Authorization": f"Bearer {credential}",
                        "Content-Type": "application/json",
                    },
                    allow_redirects=False)
            except Exception as exc:  # network-level failure -> retry
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(0.2 * (attempt + 1))
                continue

            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("Location", "")
                self._check_redirect(location)
                raise ModelError(
                    f"redirect {location!r} refused (MR-003)")

            if response.status_code >= 400:
                # retry transient provider errors once
                if response.status_code in (429, 500, 502, 503, 504) and \
                        attempt < self.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    last_error = ModelError(
                        f"provider HTTP {response.status_code}")
                    continue
                raise ModelError(
                    f"provider HTTP {response.status_code}: "
                    f"{_redact_body(response.text)}")

            data = response.json()
            choice = (data.get("choices") or [{}])[0]
            usage = data.get("usage") or {}
            cost = None
            if data.get("cost") is not None:
                cost = float(data["cost"])
            return {
                "model_version_if_available": data.get("model"),
                "output_text_or_structured_payload":
                    (choice.get("message") or {}).get("content") or
                    choice.get("text") or "",
                "finish_reason": choice.get("finish_reason"),
                "input_tokens": int(usage.get("prompt_tokens", 0)),
                "output_tokens": int(usage.get("completion_tokens", 0)),
                "cost_usd_if_known": cost,
                "provider_request_id": data.get("id"),
                "retry_count": attempt,
                "safety_or_filter_metadata": {
                    "status_code": response.status_code,
                    "provider_usage": usage,
                },
            }
        raise ModelError(f"provider request failed after retries: "
                         f"{last_error}")

    def egress_origin(self) -> str:
        return _OPENROUTER_ORIGIN


def _redact_body(text: str) -> str:
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "error" in data:
            err = data["error"]
            if isinstance(err, dict):
                return str(err.get("message", text))
    except Exception:
        pass
    return text[:300]


class FakeAdapter:
    """Deterministic adapter for unit tests (network mocked)."""

    def __init__(self, *, provider: str = "openrouter",
                 output_text: str | None = None,
                 fail: bool = False,
                 redirect_to: str | None = None,
                 leak_credential: bool = False) -> None:
        self.provider = provider
        self.output_text = output_text or "FAKE_MODEL_OUTPUT"
        self.fail = fail
        self.redirect_to = redirect_to
        self.leak_credential = leak_credential
        self.calls: list[dict] = []

    def invoke(self, *, model_request: dict, credential: str) -> dict:
        self.calls.append({"model_request": model_request,
                           "credential_len": len(credential)})
        if self.fail:
            raise ModelError("provider unavailable (test fake)")
        if self.redirect_to:
            return {"redirect": self.redirect_to}
        payload = self.output_text
        if self.leak_credential:
            payload = payload + credential
        return {
            "model_version_if_available": "fake-1.0",
            "output_text_or_structured_payload": payload,
            "finish_reason": "stop",
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd_if_known": 0.0001,
            "provider_request_id": "fake-provider-req-1",
            "retry_count": 0,
            "safety_or_filter_metadata": {"fake": True},
        }
