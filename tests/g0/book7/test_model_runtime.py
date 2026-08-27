"""G0-B7-PHASE-B — governed model runtime tests (mission §13 A..O).

Every scenario runs the real chain (PrincipalRegistry → GrantRegistry →
Authorizer → ModelGateway → provider adapter) with registry-sealed
decisions. No AuthorizationDecision is hand-built; denial scenarios are
provable by flipping the defense.
"""
from __future__ import annotations

import copy
import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.model.adapters import FakeAdapter, OpenRouterAdapter  # noqa: E402
from prototype.g0.model.gateway import (  # noqa: E402
    DevRuntimeCredentialResolver,
    ModelError,
)
from tests.g0.book7._model_seam import ModelSeamStack, T0  # noqa: E402


class _EmptyResolver(DevRuntimeCredentialResolver):
    def __call__(self, *, provider: str) -> str:
        raise ModelError("provider secret absent; fail closed (H)")


class _FixedResolver(DevRuntimeCredentialResolver):
    def __init__(self, value: str = "sk-test1234567890abcdef") -> None:
        self._value = value

    def __call__(self, *, provider: str) -> str:
        return self._value


# ---------------------------------------------------------------- helpers

def _stack(**kw) -> ModelSeamStack:
    return ModelSeamStack(credential_resolver=_FixedResolver(), **kw)


def test_A_authorized_worker_approved_model_allowed():
    """A. authorized worker + approved model => allowed."""
    s = _stack()
    s.grant_model(principal_id="worker-a", project_id="proj-a",
                  parent_ceiling="L1")
    resp = s.allow(principal_id="worker-a", project_id="proj-a")
    assert resp["provider"] == "openrouter"
    assert resp["model_id"] == "openai/gpt-4o-mini"
    assert resp["output_text_or_structured_payload"] == "OK"
    assert resp["total_tokens"] == 15
    audit = s.gateway.audit_trail()
    assert audit[-1]["credential_ref"] == "ref:openrouter_dev"
    assert "sk-test" not in str(audit)


def test_B_unknown_provider_denied():
    """B. unknown provider => denied."""
    s = _stack()
    s.grant_model()
    with pytest.raises(ModelError, match="unknown provider profile"):
        s.allow(provider_profile_id="pp_nonexistent")


def test_C_unknown_model_denied():
    """C. unknown model => denied."""
    s = _stack()
    s.grant_model()
    with pytest.raises(ModelError, match="not allowed by profile"):
        s.allow(model_id="openai/gpt-5")


def test_D_personal_uses_ceo_only_profile_denied():
    """D. Personal Hermes uses CEO-only profile => denied."""
    s = _stack()
    s.grant_model(principal_id="personal", project_id="proj-a")
    with pytest.raises(ModelError, match="principal type"):
        s.allow(principal_id="personal", project_id="proj-a")


def test_E_worker_outside_project_denied():
    """E. worker outside its bound project => denied (PROJECT_DENIED)."""
    s = _stack()
    s.grant_model(principal_id="worker-a", project_id="proj-a",
                  parent_ceiling="L1")
    req = s.request(principal_id="worker-a", project_id="proj-b",
                    resource_id="res:model-b")
    decision = s.decision(req)
    assert decision["decision"] == "DENY"
    assert decision["reason_code"] == "PROJECT_DENIED"
    with pytest.raises(ModelError):
        s.invoke(req, decision)


def test_F_cross_tenant_request_denied():
    """F. cross-tenant request => denied (context mismatch)."""
    s = _stack()
    s.grant_model(project_id="proj-a")
    req = s.request(project_id="proj-a")
    decision = s.decision(req)
    # gateway called with a different tenant than the decision binds
    forged = dict(req, tenant_id="tenant-b")
    with pytest.raises(ModelError, match="context mismatch on tenant_id"):
        s.gateway.invoke(model_request=forged,
                         authorization_decision=decision,
                         actor="ceo", principal_type="HERMES_CEO",
                         tenant_id="tenant-b", project_id="proj-a",
                         resource_id="res:model-a")


def test_G_caller_includes_api_key_rejected():
    """G. caller includes API key => rejected/redacted (never used)."""
    s = _stack()
    s.grant_model()
    with pytest.raises(ModelError, match="caller-supplied api_key"):
        s.allow(api_key="sk-live1234567890abcdef")
    with pytest.raises(ModelError, match="raw secret shape"):
        s.allow(messages=[{"role": "user",
                           "content": "use sk-live1234567890abcdef"}])
    # nothing was executed
    assert s.gateway.audit_trail() == []


def test_H_provider_secret_absent_fails_closed():
    """H. provider secret absent => fail closed."""
    s = ModelSeamStack(credential_resolver=_EmptyResolver())
    s.grant_model()
    with pytest.raises(ModelError, match="secret absent"):
        s.allow()


def test_I_secret_never_appears_in_logs_response():
    """I. secret never appears in logs/response/audit."""
    secret = "sk-secret1234567890abcdefghijkl"
    s = ModelSeamStack(credential_resolver=_FixedResolver(secret))
    s.grant_model()
    leak_adapter = FakeAdapter(leak_credential=True)
    s.gateway.register_adapter("openrouter", leak_adapter)
    with pytest.raises(ModelError, match="credential leaked"):
        s.allow()
    # response/audit never carried the raw secret
    assert secret not in str(s.gateway.audit_trail())


def test_J_arbitrary_base_url_denied():
    """J. arbitrary base URL => denied (destination != frozen origin).

    Defense is layered: the PDP rejects unknown egress destinations
    (EGRESS_DENIED), and the gateway independently rejects any destination
    that is not the frozen profile origin. Both layers are exercised.
    """
    s = _stack()
    s.grant_model()
    # PDP layer: the authorizer egress policy blocks the unknown host
    req = s.request(destination="https://evil.example.com")
    decision = s.decision(req)
    assert decision["decision"] == "DENY"
    assert decision["reason_code"] == "EGRESS_DENIED"
    with pytest.raises(ModelError):
        s.invoke(req, decision)
    # gateway layer: issue an ALLOW with the valid origin, then forge a
    # different destination on the request — the gateway must refuse it
    ok_req = s.request(destination="https://openrouter.ai")
    ok_decision = s.decision(ok_req)
    forged = dict(ok_req, destination="https://evil.example.com")
    with pytest.raises(ModelError, match="not the frozen profile origin"):
        s.gateway.invoke(model_request=forged,
                         authorization_decision=ok_decision,
                         actor="ceo", principal_type="HERMES_CEO",
                         tenant_id="tenant-a", project_id="proj-a",
                         resource_id="res:model-a")


def test_K_metadata_localhost_redirect_denied():
    """K. metadata/localhost destination or redirect => denied."""
    s = _stack()
    s.grant_model()
    # PDP layer blocks the metadata/loopback destinations
    for dest in ("http://169.254.169.254", "http://localhost:8080"):
        req = s.request(destination=dest)
        decision = s.decision(req)
        assert decision["decision"] == "DENY"
        assert decision["reason_code"] == "EGRESS_DENIED"
        with pytest.raises(ModelError):
            s.invoke(req, decision)
    # gateway layer: ALLOW for valid origin, forged metadata destination
    ok_req = s.request(destination="https://openrouter.ai")
    ok_decision = s.decision(ok_req)
    forged = dict(ok_req, destination="http://169.254.169.254")
    with pytest.raises(ModelError, match="blocked"):
        s.gateway.invoke(model_request=forged,
                         authorization_decision=ok_decision,
                         actor="ceo", principal_type="HERMES_CEO",
                         tenant_id="tenant-a", project_id="proj-a",
                         resource_id="res:model-a")
    # adapter-level redirect revalidation (EGR-003)
    adapter = OpenRouterAdapter()
    with pytest.raises(ModelError, match="redirect to unapproved"):
        adapter._check_redirect("http://169.254.169.254/latest/meta-data")


def test_L_model_disabled_denied():
    """L. disabled profile/model => denied."""
    s = _stack()
    s.grant_model()
    # flip the profile to DISABLED — the defense must flip with it
    s.profiles._profiles["pp_openrouter_dev"]["status"] = "DISABLED"
    with pytest.raises(ModelError, match="disabled"):
        s.allow()


def test_M_request_replay_denied():
    """M. request replay (one-shot semantics) => denied."""
    s = _stack()
    s.grant_model()
    req = s.request()
    decision = s.decision(req)
    ok = s.invoke(req, decision)
    assert ok["finish_reason"] == "stop"
    with pytest.raises(ModelError, match="replay"):
        s.invoke(req, decision)


def test_N_structured_output_unsupported_model_denied():
    """N. structured-output task + unsupported model => denied."""
    s = _stack()
    s.grant_model()
    with pytest.raises(ModelError, match="not allowed by profile"):
        s.allow(model_id="openai/gpt-5",
                structured_output_schema_ref="schemas/g0/foo.json")
    # supported model with structured output works
    resp = s.allow(model_id="openai/gpt-4o-mini",
                   structured_output_schema_ref="schemas/g0/foo.json")
    assert resp["model_id"] == "openai/gpt-4o-mini"


def test_O_submission_capability_remains_disabled():
    """O. submission-related capability remains disabled."""
    s = _stack()
    s.grant_model()
    # no grant can exist for submission.execute (phase-disabled)
    with pytest.raises(Exception):
        s.grants.issue(grant_id="g-submit", principal_id="ceo",
                       capability_id="submission.execute", tenant_id="tenant-a",
                       authority_level="L5", valid_from=T0,
                       expires_at="2027-12-31T00:00:00+00:00",
                       issued_by="admin")
    # a caller asking the gateway to execute under submission capability is
    # denied because model.invoke is required and submission is not a model cap
    req = s.request(capability_id="submission.execute")
    req["capability_id"] = "submission.execute"
    decision = s.decision(req)
    assert decision["decision"] != "ALLOW"
    with pytest.raises(ModelError):
        s.invoke(req, decision)


# ------------------------------------------------------ red-green provable

def test_red_green_unknown_provider():
    """The unknown-provider defense is real: with a valid profile the same
    request succeeds; with an unknown profile it fails."""
    s = _stack()
    s.grant_model()
    s.allow(provider_profile_id="pp_openrouter_dev")  # green path
    with pytest.raises(ModelError):
        s.allow(provider_profile_id="pp_unknown")


def test_red_green_replay_guard():
    """Replay guard is real: identical request_id is refused once seen."""
    s = _stack()
    s.grant_model()
    req = s.request(request_id="fixed-req-1")
    decision = s.decision(req)
    s.invoke(req, decision)
    req2 = dict(req)  # same request id -> replay
    with pytest.raises(ModelError, match="replay"):
        s.invoke(req2, decision)


def test_secret_absent_red_green():
    """The fail-closed credential path is real: with a resolver the request
    executes; with an absent secret it fails closed."""
    s = ModelSeamStack(credential_resolver=_FixedResolver())
    s.grant_model()
    s.allow()
    s2 = ModelSeamStack(credential_resolver=_EmptyResolver())
    s2.grant_model()
    with pytest.raises(ModelError, match="secret absent"):
        s2.allow()


def test_audit_contains_no_raw_secret():
    """Audit carries credential REFERENCE only, never the raw value."""
    s = _stack()
    s.grant_model()
    s.allow()
    serialized = str(s.gateway.audit_trail())
    assert "sk-test" not in serialized
    assert "credential_ref" in serialized
