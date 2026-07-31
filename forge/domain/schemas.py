"""
GLX FORGE Domain Schemas

This module defines the data schemas for the GLX FORGE trading infrastructure.
Schemas are mutable domain objects that represent actual trading data.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from forge.domain.contracts import (
    Instrument,
    Side,
    OrderType,
    TimeInForce,
    OrderStatus,
    PositionSide,
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
    validate_price,
    validate_quantity,
    validate_timestamp,
    generate_order_id,
    generate_trade_id,
    generate_position_id,
    ValidationError,
)


@dataclass
class Quote:
    """Market quote for an instrument."""
    instrument_id: InstrumentId
    symbol: Symbol
    bid_price: Price
    ask_price: Price
    bid_size: Quantity
    ask_size: Quantity
    timestamp: Timestamp
    exchange: str
    
    def __post_init__(self):
        self.bid_price = validate_price(self.bid_price)
        self.ask_price = validate_price(self.ask_price)
        self.bid_size = validate_quantity(self.bid_size)
        self.ask_size = validate_quantity(self.ask_size)
        self.timestamp = validate_timestamp(self.timestamp)
        
        if self.bid_price >= self.ask_price:
            raise ValidationError(f"Bid price {self.bid_price} must be less than ask price {self.ask_price}")
    
    @property
    def spread(self) -> Price:
        """Calculate bid-ask spread."""
        return Price(self.ask_price - self.bid_price)
    
    @property
    def mid_price(self) -> Price:
        """Calculate mid price."""
        return Price((self.bid_price + self.ask_price) / 2.0)


@dataclass
class Tick:
    """Individual trade tick."""
    instrument_id: InstrumentId
    symbol: Symbol
    price: Price
    size: Quantity
    side: Side
    timestamp: Timestamp
    exchange: str
    trade_id: Optional[TradeId] = None
    
    def __post_init__(self):
        self.price = validate_price(self.price)
        self.size = validate_quantity(self.size)
        self.timestamp = validate_timestamp(self.timestamp)
        if not isinstance(self.side, Side):
            raise ValidationError(f"Side must be Side enum, got {type(self.side)}")
        if self.trade_id is not None and not isinstance(self.trade_id, str):
            raise ValidationError(f"Trade ID must be string, got {type(self.trade_id)}")


@dataclass
class Bar:
    """OHLCV bar data."""
    instrument_id: InstrumentId
    symbol: Symbol
    open: Price
    high: Price
    low: Price
    close: Price
    volume: Quantity
    timestamp: Timestamp
    exchange: str
    
    def __post_init__(self):
        self.open = validate_price(self.open)
        self.high = validate_price(self.high)
        self.low = validate_price(self.low)
        self.close = validate_price(self.close)
        self.volume = validate_quantity(self.volume)
        self.timestamp = validate_timestamp(self.timestamp)
        
        if self.high < max(self.open, self.close):
            raise ValidationError(f"High {self.high} must be >= max(open, close)")
        if self.low > min(self.open, self.close):
            raise ValidationError(f"Low {self.low} must be <= min(open, close)")
        if self.high < self.low:
            raise ValidationError(f"High {self.high} must be >= low {self.low}")
    
    @property
    def range(self) -> Price:
        """Calculate price range."""
        return Price(self.high - self.low)
    
    @property
    def body(self) -> Price:
        """Calculate candle body."""
        return Price(abs(self.close - self.open))


@dataclass
class Order:
    """Order schema."""
    order_id: OrderId
    instrument_id: InstrumentId
    symbol: Symbol
    side: Side
    order_type: OrderType
    quantity: Quantity
    price: Optional[Price] = None
    stop_price: Optional[Price] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus = OrderStatus.PENDING_NEW
    filled_quantity: Quantity = Quantity(0.0)
    avg_fill_price: Optional[Price] = None
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(datetime.now(timezone.utc)))
    exchange: str = ""
    client_order_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.order_id, str) or not self.order_id:
            self.order_id = generate_order_id()
        
        self.quantity = validate_quantity(self.quantity)
        self.filled_quantity = validate_quantity(self.filled_quantity)
        self.timestamp = validate_timestamp(self.timestamp)
        
        if self.price is not None:
            self.price = validate_price(self.price)
        if self.stop_price is not None:
            self.stop_price = validate_price(self.stop_price)
        if self.avg_fill_price is not None:
            self.avg_fill_price = validate_price(self.avg_fill_price)
        
        if not isinstance(self.side, Side):
            raise ValidationError(f"Side must be Side enum, got {type(self.side)}")
        if not isinstance(self.order_type, OrderType):
            raise ValidationError(f"Order type must be OrderType enum, got {type(self.order_type)}")
        if not isinstance(self.time_in_force, TimeInForce):
            raise ValidationError(f"Time in force must be TimeInForce enum, got {type(self.time_in_force)}")
        if not isinstance(self.status, OrderStatus):
            raise ValidationError(f"Status must be OrderStatus enum, got {type(self.status)}")
        
        if self.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT, OrderType.LIMIT_MAKER, OrderType.LIMIT_TAKER] and self.price is None:
            raise ValidationError(f"Limit orders require a price")
        if self.order_type in [OrderType.STOP_MARKET, OrderType.STOP_LIMIT] and self.stop_price is None:
            raise ValidationError(f"Stop orders require a stop price")
        
        if self.filled_quantity > self.quantity:
            raise ValidationError(f"Filled quantity {self.filled_quantity} cannot exceed order quantity {self.quantity}")
    
    @property
    def remaining_quantity(self) -> Quantity:
        """Calculate remaining quantity to fill."""
        return Quantity(self.quantity - self.filled_quantity)
    
    @property
    def is_filled(self) -> bool:
        """Check if order is fully filled."""
        return self.filled_quantity >= self.quantity
    
    @property
    def is_working(self) -> bool:
        """Check if order is working."""
        return self.status in [OrderStatus.ACCEPTED, OrderStatus.WORKING]
    
    @property
    def is_terminal(self) -> bool:
        """Check if order is in terminal state."""
        return self.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.FAILED]


@dataclass
class Trade:
    """Trade schema."""
    trade_id: TradeId
    order_id: OrderId
    instrument_id: InstrumentId
    symbol: Symbol
    side: Side
    quantity: Quantity
    price: Price
    timestamp: Timestamp
    exchange: str
    commission: Optional[float] = None
    commission_currency: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.trade_id, str) or not self.trade_id:
            self.trade_id = generate_trade_id()
        
        self.quantity = validate_quantity(self.quantity)
        self.price = validate_price(self.price)
        self.timestamp = validate_timestamp(self.timestamp)
        
        if not isinstance(self.side, Side):
            raise ValidationError(f"Side must be Side enum, got {type(self.side)}")
        
        if self.commission is not None:
            if not isinstance(self.commission, (int, float)):
                raise ValidationError(f"Commission must be numeric, got {type(self.commission)}")
            if self.commission < 0:
                raise ValidationError(f"Commission must be non-negative, got {self.commission}")
    
    @property
    def notional(self) -> float:
        """Calculate trade notional value."""
        return self.quantity * self.price


@dataclass
class Position:
    """Position schema."""
    position_id: PositionId
    instrument_id: InstrumentId
    symbol: Symbol
    side: PositionSide
    quantity: Quantity
    avg_entry_price: Price
    current_price: Optional[Price] = None
    unrealized_pnl: Optional[float] = None
    realized_pnl: float = 0.0
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(datetime.now(timezone.utc)))
    
    def __post_init__(self):
        if not isinstance(self.position_id, str) or not self.position_id:
            self.position_id = generate_position_id()
        
        self.quantity = validate_quantity(self.quantity)
        self.avg_entry_price = validate_price(self.avg_entry_price)
        self.timestamp = validate_timestamp(self.timestamp)
        
        if self.current_price is not None:
            self.current_price = validate_price(self.current_price)
        
        if not isinstance(self.side, PositionSide):
            raise ValidationError(f"Side must be PositionSide enum, got {type(self.side)}")
        
        if self.side == PositionSide.FLAT and self.quantity != 0:
            raise ValidationError(f"Flat position must have zero quantity, got {self.quantity}")
    
    @property
    def notional(self) -> float:
        """Calculate position notional value."""
        return self.quantity * self.avg_entry_price
    
    @property
    def market_value(self) -> Optional[float]:
        """Calculate current market value."""
        if self.current_price is None:
            return None
        return self.quantity * self.current_price
    
    @property
    def unrealized_pnl_calculated(self) -> Optional[float]:
        """Calculate unrealized PnL from current price."""
        if self.current_price is None:
            return None
        if self.side == PositionSide.LONG:
            return (self.current_price - self.avg_entry_price) * self.quantity
        elif self.side == PositionSide.SHORT:
            return (self.avg_entry_price - self.current_price) * self.quantity
        return 0.0
    
    @property
    def is_flat(self) -> bool:
        """Check if position is flat."""
        return self.side == PositionSide.FLAT or self.quantity == 0
