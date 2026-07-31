"""
GLX FORGE Portfolio Forge

This module defines the portfolio infrastructure for the GLX FORGE trading infrastructure.
Portfolio includes contracts, capital envelopes, and stress controls.

Version: 0.1.0
Phase: Phase 10 - Portfolio Forge
"""

__version__ = "0.1.0"

from forge.portfolio.contracts import (
    PortfolioContract,
    PortfolioType,
    PortfolioStatus,
    PortfolioConfig,
    Position,
    Holding,
)

from forge.portfolio.capital import (
    CapitalEnvelope,
    EnvelopeType,
    EnvelopeStatus,
    CapitalAllocation,
    CapitalManager,
)

from forge.portfolio.stress import (
    StressControl,
    StressTest,
    StressScenario,
    StressResult,
    StressLevel,
)

__all__ = [
    # Contracts
    "PortfolioContract",
    "PortfolioType",
    "PortfolioStatus",
    "PortfolioConfig",
    "Position",
    "Holding",
    # Capital
    "CapitalEnvelope",
    "EnvelopeType",
    "EnvelopeStatus",
    "CapitalAllocation",
    "CapitalManager",
    # Stress
    "StressControl",
    "StressTest",
    "StressScenario",
    "StressResult",
    "StressLevel",
]
