"""
GLX FORGE Discovery Forge

This module defines the discovery infrastructure for the GLX FORGE trading infrastructure.
Discovery includes contracts, scanner fabric, and ranking.

Version: 0.1.0
Phase: Phase 5 - Discovery Forge
"""

__version__ = "0.1.0"

from forge.discovery.contracts import (
    DiscoveryContract,
    DiscoveryType,
    DiscoverySource,
    DiscoveryResult,
    DiscoveryStatus,
)

from forge.discovery.scanner import (
    Scanner,
    ScannerType,
    ScannerConfig,
    ScannerState,
    ScanRequest,
    ScanResult,
    DEFAULT_SCANNERS,
)

from forge.discovery.ranking import (
    RankingEngine,
    RankingCriteria,
    RankingMethod,
    RankingResult,
    RankedItem,
)

__all__ = [
    # Contracts
    "DiscoveryContract",
    "DiscoveryType",
    "DiscoverySource",
    "DiscoveryResult",
    "DiscoveryStatus",
    # Scanner
    "Scanner",
    "ScannerType",
    "ScannerConfig",
    "ScannerState",
    "ScanRequest",
    "ScanResult",
    "DEFAULT_SCANNERS",
    # Ranking
    "RankingEngine",
    "RankingCriteria",
    "RankingMethod",
    "RankingResult",
    "RankedItem",
]
