"""
GLX FORGE Execution Contracts

This module defines the execution contracts for the GLX FORGE trading infrastructure.
Execution contracts define the structure and configuration of order execution.

Version: 0.1.0
Phase: Phase 9 - Execution Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4

from forge.domain.types import Price, Quantity, OrderId, TradeId


class ExecutionType(Enum):
    """Execution type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"


class ExecutionStatus(Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class ExecutionConfig:
    """Execution configuration contract."""
    config_id: str
    execution_type: ExecutionType
    time_in_force: str = "GTC"
    max_slippage_pct: float = 0.01
    min_fill_pct: float = 0.0
    retry_on_failure: bool = True
    max_retries: int = 3
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.config_id, str) or not self.config_id:
            raise ValueError("Config ID cannot be empty")
        if not isinstance(self.execution_type, ExecutionType):
            raise ValueError("Execution type must be ExecutionType enum")
        if not isinstance(self.max_slippage_pct, (int, float)):
            raise ValueError(f"Max slippage must be numeric, got {type(self.max_slippage_pct)}")
        if not 0.0 <= self.max_slippage_pct <= 1.0:
            raise ValueError(f"Max slippage must be between 0.0 and 1.0, got {self.max_slippage_pct}")


@dataclass
class ExecutionOrder:
    """Execution order contract."""
    order_id: OrderId
    instrument_id: str
    side: str  # "buy", "sell"
    quantity: Quantity
    price: Optional[Price] = None
    stop_price: Optional[Price] = None
    execution_type: ExecutionType = ExecutionType.MARKET
    status: ExecutionStatus = ExecutionStatus.PENDING
    filled_quantity: Quantity = Quantity(0.0)
    avg_fill_price: Optional[Price] = None
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    exchange_order_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.order_id, str) or not self.order_id:
            self.order_id = OrderId(str(uuid4()))
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
        if not isinstance(self.side, str) or not self.side:
            raise ValueError("Side cannot be empty")
        if self.side not in ["buy", "sell"]:
            raise ValueError(f"Side must be 'buy' or 'sell', got {self.side}")
        if not isinstance(self.execution_type, ExecutionType):
            raise ValueError("Execution type must be ExecutionType enum")
        if not isinstance(self.status, ExecutionStatus):
            raise ValueError("Status must be ExecutionStatus enum")
    
    @property
    def is_filled(self) -> bool:
        """Check if order is filled."""
        return self.status == ExecutionStatus.FILLED
    
    @property
    def is_partially_filled(self) -> bool:
        """Check if order is partially filled."""
        return self.status == ExecutionStatus.PARTIALLY_FILLED
    
    @property
    def is_terminal(self) -> bool:
        """Check if order is in terminal state."""
        return self.status in [ExecutionStatus.FILLED, ExecutionStatus.CANCELLED, ExecutionStatus.REJECTED, ExecutionStatus.EXPIRED, ExecutionStatus.FAILED]
    
    @property
    def remaining_quantity(self) -> Quantity:
        """Calculate remaining quantity."""
        return Quantity(self.quantity - self.filled_quantity)
    
    def update_status(self, status: ExecutionStatus) -> None:
        """Update order status."""
        self.status = status
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class ExecutionFill:
    """Execution fill contract."""
    fill_id: TradeId
    order_id: OrderId
    instrument_id: str
    side: str
    filled_quantity: Quantity
    fill_price: Price
    commission: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    exchange_order_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.fill_id, str) or not self.fill_id:
            self.fill_id = TradeId(str(uuid4()))
        if not isinstance(self.order_id, str) or not self.order_id:
            raise ValueError("Order ID cannot be empty")
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
    
    @property
    def notional(self) -> float:
        """Calculate fill notional value."""
        return self.filled_quantity * self.fill_price


@dataclass
class ExecutionContract:
    """Execution contract contract."""
    contract_id: str
    contract_name: str
    execution_type: ExecutionType
    config: ExecutionConfig
    orders: List[ExecutionOrder] = field(default_factory=list)
    fills: List[ExecutionFill] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.contract_id, str) or not self.contract_id:
            self.contract_id = str(uuid4())
        if not isinstance(self.contract_name, str) or not self.contract_name:
            raise ValueError("Contract name cannot be empty")
        if not isinstance(self.execution_type, ExecutionType):
            raise ValueError("Execution type must be ExecutionType enum")
        if not isinstance(self.config, ExecutionConfig):
            raise ValueError("Config must be an ExecutionConfig instance")
    
    def add_order(self, order: ExecutionOrder) -> None:
        """Add an order to the contract."""
        self.orders.append(order)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_fill(self, fill: ExecutionFill) -> None:
        """Add a fill to the contract."""
        self.fills.append(fill)
        self.updated_at = datetime.now(timezone.utc)
    
    def get_order(self, order_id: OrderId) -> Optional[ExecutionOrder]:
        """Get an order by ID."""
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None
    
    def get_fills_for_order(self, order_id: OrderId) -> List[ExecutionFill]:
        """Get all fills for an order."""
        return [f for f in self.fills if f.order_id == order_id]
    
    @property
    def order_count(self) -> int:
        """Get the number of orders."""
        return len(self.orders)
    
    @property
    def fill_count(self) -> int:
        """Get the number of fills."""
        return len(self.fills)


def create_execution_order(
    instrument_id: str,
    side: str,
    quantity: Quantity,
    price: Optional[Price] = None,
    execution_type: ExecutionType = ExecutionType.MARKET,
) -> ExecutionOrder:
    """Create a new execution order."""
    return ExecutionOrder(
        order_id=OrderId(str(uuid4())),
        instrument_id=instrument_id,
        side=side,
        quantity=quantity,
        price=price,
        execution_type=execution_type,
    )


def create_execution_fill(
    order_id: OrderId,
    instrument_id: str,
    side: str,
    filled_quantity: Quantity,
    fill_price: Price,
) -> ExecutionFill:
    """Create a new execution fill."""
    return ExecutionFill(
        fill_id=TradeId(str(uuid4())),
        order_id=order_id,
        instrument_id=instrument_id,
        side=side,
        filled_quantity=filled_quantity,
        fill_price=fill_price,
    )


def create_execution_config(
    execution_type: ExecutionType,
    max_slippage_pct: float = 0.01,
) -> ExecutionConfig:
    """Create a new execution configuration."""
    return ExecutionConfig(
        config_id=str(uuid4()),
        execution_type=execution_type,
        max_slippage_pct=max_slippage_pct,
    )
