"""
GLX FORGE Execution Adapters

This module defines the adapter fabric for the GLX FORGE trading infrastructure.
Adapters provide a unified interface to different exchange execution APIs.

Version: 0.1.0
Phase: Phase 9 - Execution Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Callable, Any
from uuid import UUID, uuid4

from forge.execution.contracts import ExecutionOrder, ExecutionFill, ExecutionStatus


class AdapterType(Enum):
    """Adapter type enumeration."""
    BINANCE = "binance"
    COINBASE = "coinbase"
    KRAKEN = "kraken"
    POLYGON = "polygon"
    ALPACA = "alpaca"
    IBKR = "ibkr"
    CUSTOM = "custom"


class AdapterStatus(Enum):
    """Adapter status enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    ERROR = "error"


@dataclass
class AdapterConfig:
    """Adapter configuration contract."""
    adapter_id: str
    adapter_type: AdapterType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    endpoint: str = ""
    testnet: bool = False
    rate_limit_per_second: int = 10
    timeout_seconds: int = 30
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.adapter_id, str) or not self.adapter_id:
            raise ValueError("Adapter ID cannot be empty")
        if not isinstance(self.adapter_type, AdapterType):
            raise ValueError("Adapter type must be AdapterType enum")
        if not isinstance(self.rate_limit_per_second, int) or self.rate_limit_per_second < 1:
            raise ValueError(f"Rate limit must be >= 1, got {self.rate_limit_per_second}")


@dataclass
class ExecutionAdapter:
    """Execution adapter contract."""
    adapter_id: str
    name: str
    adapter_type: AdapterType
    config: AdapterConfig
    status: AdapterStatus
    orders: Dict[str, ExecutionOrder] = field(default_factory=dict)
    fills: List[ExecutionFill] = field(default_factory=list)
    connected_at: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.adapter_id, str) or not self.adapter_id:
            raise ValueError("Adapter ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.adapter_type, AdapterType):
            raise ValueError("Adapter type must be AdapterType enum")
        if not isinstance(self.config, AdapterConfig):
            raise ValueError("Config must be an AdapterConfig instance")
        if not isinstance(self.status, AdapterStatus):
            raise ValueError("Status must be AdapterStatus enum")
    
    @property
    def is_connected(self) -> bool:
        """Check if adapter is connected."""
        return self.status in [AdapterStatus.CONNECTED, AdapterStatus.AUTHENTICATED]
    
    @property
    def is_authenticated(self) -> bool:
        """Check if adapter is authenticated."""
        return self.status == AdapterStatus.AUTHENTICATED
    
    @property
    def is_error(self) -> bool:
        """Check if adapter is in error state."""
        return self.status == AdapterStatus.ERROR
    
    @property
    def order_count(self) -> int:
        """Get the number of orders."""
        return len(self.orders)
    
    @property
    def fill_count(self) -> int:
        """Get the number of fills."""
        return len(self.fills)
    
    def connect(self) -> None:
        """Connect to the exchange."""
        self.status = AdapterStatus.CONNECTING
        self.connected_at = datetime.now(timezone.utc)
        self.status = AdapterStatus.CONNECTED
    
    def authenticate(self) -> None:
        """Authenticate with the exchange."""
        if not self.is_connected:
            raise RuntimeError("Adapter must be connected before authentication")
        self.status = AdapterStatus.AUTHENTICATED
    
    def disconnect(self) -> None:
        """Disconnect from the exchange."""
        self.status = AdapterStatus.DISCONNECTED
        self.connected_at = None
    
    def submit_order(self, order: ExecutionOrder) -> ExecutionOrder:
        """Submit an order to the exchange."""
        if not self.is_authenticated:
            raise RuntimeError("Adapter must be authenticated before submitting orders")
        
        order.update_status(ExecutionStatus.SUBMITTED)
        self.orders[order.order_id] = order
        
        # Simulate order acknowledgement
        order.update_status(ExecutionStatus.ACKNOWLEDGED)
        
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        order = self.orders.get(order_id)
        if order is None:
            return False
        
        if order.is_terminal:
            return False
        
        order.update_status(ExecutionStatus.CANCELLED)
        return True
    
    def add_fill(self, fill: ExecutionFill) -> None:
        """Add a fill to the adapter."""
        self.fills.append(fill)
        
        # Update order status
        order = self.orders.get(fill.order_id)
        if order:
            order.filled_quantity = order.filled_quantity + fill.filled_quantity
            if order.avg_fill_price is None:
                order.avg_fill_price = fill.fill_price
            else:
                # Update average fill price
                total_notional = (order.avg_fill_price * (order.filled_quantity - fill.filled_quantity) + 
                               fill.fill_price * fill.filled_quantity)
                order.avg_fill_price = total_notional / order.filled_quantity
            
            if order.filled_quantity >= order.quantity:
                order.update_status(ExecutionStatus.FILLED)
            elif order.filled_quantity > 0:
                order.update_status(ExecutionStatus.PARTIALLY_FILLED)
    
    def mark_error(self, error: str) -> None:
        """Mark adapter as in error state."""
        self.error_count += 1
        self.last_error = error
        self.status = AdapterStatus.ERROR


# Default execution adapters for common exchanges
DEFAULT_ADAPTERS = {
    "binance": ExecutionAdapter(
        adapter_id="adapter-binance",
        name="Binance Adapter",
        adapter_type=AdapterType.BINANCE,
        config=AdapterConfig(
            adapter_id="adapter-binance",
            adapter_type=AdapterType.BINANCE,
            endpoint="https://api.binance.com",
            testnet=False,
        ),
        status=AdapterStatus.DISCONNECTED,
    ),
    
    "coinbase": ExecutionAdapter(
        adapter_id="adapter-coinbase",
        name="Coinbase Adapter",
        adapter_type=AdapterType.COINBASE,
        config=AdapterConfig(
            adapter_id="adapter-coinbase",
            adapter_type=AdapterType.COINBASE,
            endpoint="https://api.exchange.coinbase.com",
            testnet=False,
        ),
        status=AdapterStatus.DISCONNECTED,
    ),
    
    "kraken": ExecutionAdapter(
        adapter_id="adapter-kraken",
        name="Kraken Adapter",
        adapter_type=AdapterType.KRAKEN,
        config=AdapterConfig(
            adapter_id="adapter-kraken",
            adapter_type=AdapterType.KRAKEN,
            endpoint="https://api.kraken.com",
            testnet=False,
        ),
        status=AdapterStatus.DISCONNECTED,
    ),
    
    "alpaca": ExecutionAdapter(
        adapter_id="adapter-alpaca",
        name="Alpaca Adapter",
        adapter_type=AdapterType.ALPACA,
        config=AdapterConfig(
            adapter_id="adapter-alpaca",
            adapter_type=AdapterType.ALPACA,
            endpoint="https://api.alpaca.markets",
            testnet=True,
        ),
        status=AdapterStatus.DISCONNECTED,
    ),
}


def create_execution_adapter(
    name: str,
    adapter_type: AdapterType,
    config: Optional[AdapterConfig] = None,
) -> ExecutionAdapter:
    """Create a new execution adapter."""
    if config is None:
        config = AdapterConfig(
            adapter_id=str(uuid4()),
            adapter_type=adapter_type,
        )
    
    return ExecutionAdapter(
        adapter_id=config.adapter_id,
        name=name,
        adapter_type=adapter_type,
        config=config,
        status=AdapterStatus.DISCONNECTED,
    )


def create_adapter_config(
    adapter_type: AdapterType,
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
) -> AdapterConfig:
    """Create a new adapter configuration."""
    return AdapterConfig(
        adapter_id=str(uuid4()),
        adapter_type=adapter_type,
        api_key=api_key,
        api_secret=api_secret,
    )
