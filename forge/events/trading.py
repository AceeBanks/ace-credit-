"""
GLX FORGE Trading Events

This module defines trading-related events for the GLX FORGE trading infrastructure.
Trading events represent order lifecycle, position changes, and trade execution.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from forge.domain.contracts import Side, OrderStatus, PositionSide
from forge.domain.types import (
    OrderId,
    InstrumentId,
    PositionId,
    TradeId,
    Price,
    Quantity,
    Timestamp,
    validate_timestamp,
    ValidationError,
)


@dataclass(frozen=True)
class OrderSubmitted:
    """Event emitted when an order is submitted to an exchange."""
    event_id: str
    order_id: OrderId
    instrument_id: InstrumentId
    side: Side
    quantity: Quantity
    price: Optional[Price]
    order_type: str
    timestamp: Timestamp
    exchange: str
    account_id: Optional[str] = None
    strategy_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class OrderAccepted:
    """Event emitted when an exchange accepts an order."""
    event_id: str
    order_id: OrderId
    instrument_id: InstrumentId
    timestamp: Timestamp
    exchange: str
    exchange_order_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class OrderRejected:
    """Event emitted when an exchange rejects an order."""
    event_id: str
    order_id: OrderId
    instrument_id: InstrumentId
    timestamp: Timestamp
    exchange: str
    reason: str
    exchange_order_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.reason, str) or not self.reason:
            raise ValidationError("Rejection reason cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class OrderFilled:
    """Event emitted when an order is partially or fully filled."""
    event_id: str
    order_id: OrderId
    trade_id: TradeId
    instrument_id: InstrumentId
    side: Side
    filled_quantity: Quantity
    fill_price: Price
    timestamp: Timestamp
    exchange: str
    commission: Optional[float] = None
    commission_currency: Optional[str] = None
    exchange_order_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)
    
    @property
    def notional(self) -> float:
        """Calculate fill notional value."""
        return self.filled_quantity * self.fill_price


@dataclass(frozen=True)
class OrderCancelled:
    """Event emitted when an order is cancelled."""
    event_id: str
    order_id: OrderId
    instrument_id: InstrumentId
    timestamp: Timestamp
    exchange: str
    reason: Optional[str] = None
    cancelled_quantity: Optional[Quantity] = None
    exchange_order_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class OrderExpired:
    """Event emitted when an order expires."""
    event_id: str
    order_id: OrderId
    instrument_id: InstrumentId
    timestamp: Timestamp
    exchange: str
    exchange_order_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class OrderFailed:
    """Event emitted when an order fails due to system error."""
    event_id: str
    order_id: OrderId
    instrument_id: InstrumentId
    timestamp: Timestamp
    exchange: str
    error: str
    error_code: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.error, str) or not self.error:
            raise ValidationError("Error message cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class PositionOpened:
    """Event emitted when a new position is opened."""
    event_id: str
    position_id: PositionId
    instrument_id: InstrumentId
    side: PositionSide
    quantity: Quantity
    avg_entry_price: Price
    timestamp: Timestamp
    strategy_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class PositionModified:
    """Event emitted when a position is modified (added to or reduced)."""
    event_id: str
    position_id: PositionId
    instrument_id: InstrumentId
    side: PositionSide
    quantity: Quantity
    avg_entry_price: Price
    timestamp: Timestamp
    modification_type: str  # "add" or "reduce"
    strategy_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if self.modification_type not in ["add", "reduce"]:
            raise ValidationError(f"Modification type must be 'add' or 'reduce', got {self.modification_type}")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class PositionClosed:
    """Event emitted when a position is closed."""
    event_id: str
    position_id: PositionId
    instrument_id: InstrumentId
    side: PositionSide
    quantity: Quantity
    avg_entry_price: Price
    avg_exit_price: Price
    realized_pnl: float
    timestamp: Timestamp
    strategy_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class TradeExecuted:
    """Event emitted when a trade is executed."""
    event_id: str
    trade_id: TradeId
    order_id: OrderId
    instrument_id: InstrumentId
    side: Side
    quantity: Quantity
    price: Price
    timestamp: Timestamp
    exchange: str
    commission: Optional[float] = None
    commission_currency: Optional[str] = None
    strategy_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)
    
    @property
    def notional(self) -> float:
        """Calculate trade notional value."""
        return self.quantity * self.price
