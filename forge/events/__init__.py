"""
GLX FORGE Event Contracts

This module defines the event contracts for the GLX FORGE trading infrastructure.
Events are immutable domain objects that represent significant state changes.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

__version__ = "0.1.0"

from forge.events.trading import (
    OrderSubmitted,
    OrderAccepted,
    OrderRejected,
    OrderFilled,
    OrderCancelled,
    OrderExpired,
    OrderFailed,
    PositionOpened,
    PositionModified,
    PositionClosed,
    TradeExecuted,
)

from forge.events.research import (
    BacktestStarted,
    BacktestCompleted,
    BacktestFailed,
    SignalGenerated,
    SignalExpired,
)

from forge.events.system import (
    ServiceStarted,
    ServiceStopped,
    ServiceError,
    PhaseTransitioned,
    GateValidationPassed,
    GateValidationFailed,
)

__all__ = [
    # Trading events
    "OrderSubmitted",
    "OrderAccepted",
    "OrderRejected",
    "OrderFilled",
    "OrderCancelled",
    "OrderExpired",
    "OrderFailed",
    "PositionOpened",
    "PositionModified",
    "PositionClosed",
    "TradeExecuted",
    # Research events
    "BacktestStarted",
    "BacktestCompleted",
    "BacktestFailed",
    "SignalGenerated",
    "SignalExpired",
    # System events
    "ServiceStarted",
    "ServiceStopped",
    "ServiceError",
    "PhaseTransitioned",
    "GateValidationPassed",
    "GateValidationFailed",
]
