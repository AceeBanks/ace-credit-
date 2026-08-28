"""G1 Appendix A — governed Model Registry.

Project-owned registry of approved model profiles. Providers remain
replaceable adapters; no provider is architectural truth. The registry is
the single source the API model picker reads — unknown models are simply
not present (deny-by-default), and selection goes through the engine in
`selection.py`.
"""
from __future__ import annotations

from grant_platform.model.selection import ModelProfile

# Approved default profiles (Appendix A §5 contract fields).
# OpenRouter remains the primary aggregation path; direct providers may be
# added later. Free-tier pricing is NOT a production cost assumption.
DEFAULT_PROFILES = [
    # Default drafting model (G1-QUALITY): registered first so the AUTO
    # selection engine's stable tie-break prefers it among equal
    # quality/cost profiles.
    ModelProfile(
        model_id="nvidia/nemotron-3.5-lightning:free", provider_id="openrouter",
        context_window_tokens=128_000, max_output_tokens=4_096,
        enabled=True, availability="BETA",
        full_proposal_eligible=True, research_eligible=True,
        qa_eligible=True, humanizer_eligible=False, extraction_eligible=True,
        allowed_tasks=["grant_drafting", "full_proposal", "research",
                       "qa", "extraction"],
        minimum_context_headroom=2_000,
        fallback_compatible=["minimax/minimax-m3:free",
                             "deepseek/deepseek-chat-v3-0324:free"],
        cost_tier="LOW", latency_tier="FAST", quality_tier="MEDIUM"),
    ModelProfile(
        model_id="minimax/minimax-m3:free", provider_id="openrouter",
        context_window_tokens=245_000, max_output_tokens=4_096,
        enabled=True, availability="BETA",
        full_proposal_eligible=True, research_eligible=True,
        qa_eligible=True, humanizer_eligible=False, extraction_eligible=True,
        allowed_tasks=["grant_drafting", "full_proposal", "research",
                       "extraction"],
        minimum_context_headroom=2_000,
        fallback_compatible=["deepseek/deepseek-chat-v3-0324:free"],
        cost_tier="LOW", latency_tier="MEDIUM", quality_tier="MEDIUM"),
    ModelProfile(
        model_id="deepseek/deepseek-chat-v3-0324:free", provider_id="openrouter",
        context_window_tokens=64_000, max_output_tokens=4_096,
        enabled=True, availability="BETA",
        full_proposal_eligible=True, research_eligible=True,
        qa_eligible=True, humanizer_eligible=False, extraction_eligible=True,
        allowed_tasks=["grant_drafting", "full_proposal", "research",
                       "qa", "extraction"],
        minimum_context_headroom=2_000,
        fallback_compatible=["minimax/minimax-m3:free"],
        cost_tier="LOW", latency_tier="MEDIUM", quality_tier="MEDIUM"),
    ModelProfile(
        model_id="anthropic/claude-3.5-sonnet", provider_id="openrouter",
        context_window_tokens=200_000, max_output_tokens=8_192,
        enabled=False, availability="DISABLED",
        full_proposal_eligible=True, research_eligible=True,
        qa_eligible=True, humanizer_eligible=False, extraction_eligible=True,
        allowed_tasks=["grant_drafting", "full_proposal", "research", "qa"],
        minimum_context_headroom=4_000,
        fallback_compatible=[],
        cost_tier="HIGH", latency_tier="FAST", quality_tier="HIGH"),
]


class ModelRegistry:
    """Deny-by-default registry. Unknown models raise KeyError."""

    def __init__(self, profiles: list[ModelProfile] | None = None):
        self._profiles = {p.model_id: p for p in (profiles or [])}

    @classmethod
    def load_default(cls) -> "ModelRegistry":
        return cls(list(DEFAULT_PROFILES))

    def register(self, profile: ModelProfile) -> None:
        self._profiles[profile.model_id] = profile

    def get(self, model_id: str) -> ModelProfile:
        if model_id not in self._profiles:
            raise KeyError(f"unknown model {model_id}")
        return self._profiles[model_id]

    def all(self) -> list[ModelProfile]:
        return list(self._profiles.values())
