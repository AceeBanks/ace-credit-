"""
GLX FORGE Execution Forge

This module defines the execution infrastructure for the GLX FORGE trading infrastructure.
Execution includes contracts, adapter fabric, and lifecycle management.

Version: 0.1.0
Phase: Phase 9 - Execution Forge
"""

__version__ = "0.1.0"

from forge.execution.contracts import (
    ExecutionContract,
    ExecutionType,
    ExecutionStatus,
    ExecutionConfig,
    ExecutionOrder,
    ExecutionFill,
)

from forge.execution.adapters import (
    ExecutionAdapter,
    AdapterType,
    AdapterConfig,
    AdapterStatus,
    DEFAULT_ADAPTERS,
)

from forge.execution.lifecycle import (
    ExecutionLifecycle,
    LifecycleState,
    LifecycleEvent,
    LifecycleManager,
)

__all__ = [
    # Contracts
    "ExecutionContract",
    "ExecutionType",
    "ExecutionStatus",
    "ExecutionConfig",
    "ExecutionOrder",
    "ExecutionFill",
    # Adapters
    "ExecutionAdapter",
    "AdapterType",
    "AdapterConfig",
    "AdapterStatus",
    "DEFAULT_ADAPTERS",
    # Lifecycle
    "ExecutionLifecycle",
    "LifecycleState",
    "LifecycleEvent",
    "LifecycleManager",
]
