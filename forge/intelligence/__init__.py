"""
GLX FORGE Intelligence Forge

This module defines the intelligence infrastructure for the GLX FORGE trading infrastructure.
Intelligence includes contracts, observers, and causal mapping.

Version: 0.1.0
Phase: Phase 4 - Intelligence Forge
"""

__version__ = "0.1.0"

from forge.intelligence.contracts import (
    IntelligenceContract,
    IntelligenceType,
    IntelligenceSource,
    IntelligenceQuality,
    IntelligenceSignal,
    SignalStrength,
    SignalConfidence,
)

from forge.intelligence.observers import (
    Observer,
    ObserverType,
    ObserverConfig,
    ObserverEvent,
    ObserverState,
    DEFAULT_OBSERVERS,
)

from forge.intelligence.causal import (
    CausalGraph,
    CausalNode,
    CausalEdge,
    CausalRelationship,
    CausalInference,
    CausalModel,
)

__all__ = [
    # Contracts
    "IntelligenceContract",
    "IntelligenceType",
    "IntelligenceSource",
    "IntelligenceQuality",
    "IntelligenceSignal",
    "SignalStrength",
    "SignalConfidence",
    # Observers
    "Observer",
    "ObserverType",
    "ObserverConfig",
    "ObserverEvent",
    "ObserverState",
    "DEFAULT_OBSERVERS",
    # Causal
    "CausalGraph",
    "CausalNode",
    "CausalEdge",
    "CausalRelationship",
    "CausalInference",
    "CausalModel",
]
