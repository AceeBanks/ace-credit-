"""
GLX FORGE Domain Language

This module defines the foundational contracts, schemas, and types for the GLX FORGE
trading infrastructure. All domain objects are strongly typed and validated.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

__version__ = "0.1.0"

from forge.domain.contracts import (
    Asset,
    AssetClass,
    Currency,
    Exchange,
    Instrument,
    InstrumentType,
    Side,
    OrderType,
    TimeInForce,
    OrderStatus,
    PositionSide,
)

from forge.domain.schemas import (
    Order,
    Position,
    Trade,
    Quote,
    Bar,
    Tick,
)

from forge.domain.types import (
    Price,
    Quantity,
    Timestamp,
    Symbol,
    InstrumentId,
    OrderId,
    PositionId,
    TradeId,
)

__all__ = [
    # Contracts
    "Asset",
    "AssetClass",
    "Currency",
    "Exchange",
    "Instrument",
    "InstrumentType",
    "Side",
    "OrderType",
    "TimeInForce",
    "OrderStatus",
    "PositionSide",
    # Schemas
    "Order",
    "Position",
    "Trade",
    "Quote",
    "Bar",
    "Tick",
    # Types
    "Price",
    "Quantity",
    "Timestamp",
    "Symbol",
    "InstrumentId",
    "OrderId",
    "PositionId",
    "TradeId",
]
