"""G1 Appendix A — Model selection engine.

Implements the model capability & selection contract:

- context eligibility gate (window + output + headroom, 2x long-form
  safety target PROVISIONAL_G1_DEFAULT);
- task-eligibility gate (model must declare the task);
- availability / enabled gate;
- governed fallback (user-opted) when the primary is incompatible;
- AUTO routing over task type, eligibility, cost tier, availability.

Selection never bypasses the gateway's PDP/egress/credential rules — it
only picks WHICH eligible model a request may use. The actual model used is
recorded by the caller on ModelRun / ArtifactVersion / DecisionRecord.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# long-form safety target: available context >= MULTIPLIER * working input
LONG_FORM_CONTEXT_MULTIPLIER = 2.0  # PROVISIONAL_G1_DEFAULT


@dataclass
class ModelProfile:
    model_id: str
    provider_id: str
    context_window_tokens: int
    max_output_tokens: int
    free_pool_approved: bool = False
    context_verified: bool = False
    supports_structured_output: bool = False
    supports_long_form: bool = False
    supports_reasoning: bool = False
    observed_latency_ms: int | None = None
    observed_failure_rate: float | None = None
    last_verified_at: str | None = None
    enabled: bool = True
    availability: str = "ENABLED"      # ENABLED | BETA | DISABLED
    full_proposal_eligible: bool = False
    research_eligible: bool = False
    qa_eligible: bool = False
    humanizer_eligible: bool = False
    extraction_eligible: bool = False
    allowed_tasks: list[str] = field(default_factory=list)
    minimum_context_headroom: int = 0
    fallback_compatible: list[str] = field(default_factory=list)
    cost_tier: str = "MEDIUM"          # LOW | MEDIUM | HIGH
    latency_tier: str = "MEDIUM"       # FAST | MEDIUM | SLOW
    quality_tier: str = "UNRATED"      # HIGH | MEDIUM | LOW | UNRATED

    @classmethod
    def from_dict(cls, d: dict) -> "ModelProfile":
        return cls(**{k: v for k, v in d.items()
                      if k in cls.__dataclass_fields__})


@dataclass
class SelectionContext:
    task: str                        # e.g. grant_drafting, research, qa
    estimated_input_tokens: int
    expected_output_tokens: int
    system_overhead_tokens: int = 0
    long_form: bool = False          # 2x safety target applies
    user_provider: str | None = None
    user_model: str | None = None
    allow_fallback: bool = False


@dataclass
class SelectionResult:
    selected: ModelProfile | None
    rejected_reasons: list[str] = field(default_factory=list)
    fallback_used: bool = False

    @property
    def ok(self) -> bool:
        return self.selected is not None


def _task_eligible(profile: ModelProfile, task: str) -> bool:
    if task in profile.allowed_tasks:
        return True
    return {
        "full_proposal": profile.full_proposal_eligible,
        "research": profile.research_eligible,
        "qa": profile.qa_eligible,
        "humanizer": profile.humanizer_eligible,
        "extraction": profile.extraction_eligible,
    }.get(task, False)


def _required_context(ctx: SelectionContext) -> int:
    working = (ctx.estimated_input_tokens + ctx.expected_output_tokens
               + ctx.system_overhead_tokens)
    if ctx.long_form:
        working = int(working * LONG_FORM_CONTEXT_MULTIPLIER)
    return working


def _reject_reasons(profile: ModelProfile, ctx: SelectionContext,
                    required: int) -> list[str]:
    reasons: list[str] = []
    if not profile.enabled or profile.availability == "DISABLED":
        reasons.append("model disabled")
    if not _task_eligible(profile, ctx.task):
        reasons.append(f"not eligible for task {ctx.task}")
    if profile.context_window_tokens < required:
        reasons.append(
            f"context window {profile.context_window_tokens} < required "
            f"{required}")
    if profile.context_window_tokens <= 0 or (profile.provider_id == "openrouter"
                                             and profile.model_id.endswith(":free")
                                             and not profile.context_verified):
        reasons.append("context capacity unverified")
    if profile.max_output_tokens < ctx.expected_output_tokens:
        reasons.append(
            f"max output {profile.max_output_tokens} < required "
            f"{ctx.expected_output_tokens}")
    return reasons


def _select_preferred(ctx: SelectionContext, profiles: list[ModelProfile],
                      prefer_model_id: str | None,
                      prefer_provider: str | None) -> SelectionResult:
    """User preference: ONLY the exact chosen model/provider is considered.
    If incompatible, reject — never silently substitute another model here
    (substitution only happens via governed fallback)."""
    required = _required_context(ctx)
    if prefer_model_id:
        exact = [p for p in profiles if p.model_id == prefer_model_id]
        if not exact:
            # unknown model: DENY (Appendix A §9 — never silently treat a
            # misspelled/unregistered model as "no preference")
            return SelectionResult(
                selected=None,
                rejected_reasons=[f"unknown model {prefer_model_id} "
                                  "(not in governed registry)"])
        candidates = exact
    elif prefer_provider:
        prov = [p for p in profiles if p.provider_id == prefer_provider]
        if not prov:
            return SelectionResult(
                selected=None,
                rejected_reasons=[f"unknown provider {prefer_provider} "
                                  "(not in governed registry)"])
        candidates = prov
    else:
        candidates = profiles
    reasons: list[str] = []
    for p in candidates:
        reasons = _reject_reasons(p, ctx, required)
        if not reasons:
            return SelectionResult(selected=p)
    return SelectionResult(selected=None, rejected_reasons=reasons)


def _select_auto(ctx: SelectionContext,
                 profiles: list[ModelProfile]) -> SelectionResult:
    """Auto: score only the governed approved free pool when selecting
    free models; never discover or route through a generic free router."""
    required = _required_context(ctx)
    eligible = []
    all_reasons: list[str] = []
    for p in profiles:
        if p.model_id.endswith(":free") and not p.free_pool_approved:
            all_reasons.append(f"free model {p.model_id} not in approved pool")
            continue
        if p.model_id.endswith(":free") and not p.context_verified:
            all_reasons.append(f"model {p.model_id} context unverified")
            continue
        reasons = _reject_reasons(p, ctx, required)
        if not reasons:
            eligible.append(p)
        else:
            all_reasons.extend(reasons)
    if eligible:
        approved_order = {
            "z-ai/glm-5.2:free": 3,
            "thinkingmachines/inkling-small:free": 2,
            "minimax/minimax-m3:free": 1,
        }
        ordered = sorted(eligible,
                         key=lambda p: (approved_order.get(p.model_id, 0),
                                        _TASK_QUALITY(p, ctx.task),
                                        _COST_SCORE(p)),
                         reverse=True)
        return SelectionResult(selected=ordered[0])
    return SelectionResult(selected=None,
                           rejected_reasons=all_reasons or
                           ["no eligible model for task"])


def _TASK_QUALITY(p: ModelProfile, task: str) -> int:
    return {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(p.quality_tier, 0)


def _COST_SCORE(p: ModelProfile) -> int:
    return {"LOW": 3, "MEDIUM": 2, "HIGH": 1}.get(p.cost_tier, 0)


def select_model(ctx: SelectionContext, profiles: list[ModelProfile]) \
        -> SelectionResult:
    """Public entry: honors user choice, then governed fallback, then auto."""
    has_preference = ctx.user_model is not None \
        or ctx.user_provider is not None
    if has_preference:
        primary = _select_preferred(ctx, profiles,
                                    prefer_model_id=ctx.user_model,
                                    prefer_provider=ctx.user_provider)
        if primary.ok or not ctx.allow_fallback:
            return primary
        # governed fallback: user's choice failed; try any other eligible
        # model (substitution only happens here, never silently)
        fallback = _select_auto(ctx, profiles)
        if fallback.ok:
            return SelectionResult(selected=fallback.selected,
                                   fallback_used=True,
                                   rejected_reasons=primary.rejected_reasons)
        return SelectionResult(
            selected=None,
            rejected_reasons=primary.rejected_reasons
            + ["fallback unavailable"])
    return _select_auto(ctx, profiles)
