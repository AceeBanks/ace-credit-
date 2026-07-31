"""
GLX FORGE Simulation Forge

This module defines the simulation infrastructure for the GLX FORGE trading infrastructure.
Simulation includes deployment manager, runtime health, and paper/shadow trading.

Version: 0.1.0
Phase: Phase 8 - Simulation Forge
"""

__version__ = "0.1.0"

from forge.simulation.deployment import (
    DeploymentManager,
    DeploymentConfig,
    DeploymentStatus,
    DeploymentResult,
)

from forge.simulation.health import (
    HealthMonitor,
    HealthStatus,
    HealthMetric,
    HealthAlert,
    DEFAULT_HEALTH_METRICS,
)

from forge.simulation.paper_trading import (
    PaperTradingEngine,
    PaperTradeConfig,
    PaperTradeResult,
    PaperPortfolio,
)

from forge.simulation.shadow_trading import (
    ShadowTradingEngine,
    ShadowTradeConfig,
    ShadowTradeResult,
    ShadowComparison,
)

__all__ = [
    # Deployment
    "DeploymentManager",
    "DeploymentConfig",
    "DeploymentStatus",
    "DeploymentResult",
    # Health
    "HealthMonitor",
    "HealthStatus",
    "HealthMetric",
    "HealthAlert",
    "DEFAULT_HEALTH_METRICS",
    # Paper Trading
    "PaperTradingEngine",
    "PaperTradeConfig",
    "PaperTradeResult",
    "PaperPortfolio",
    # Shadow Trading
    "ShadowTradingEngine",
    "ShadowTradeConfig",
    "ShadowTradeResult",
    "ShadowComparison",
]
