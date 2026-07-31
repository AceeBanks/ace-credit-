"""
GLX FORGE Portfolio Contracts

This module defines the portfolio contracts for the GLX FORGE trading infrastructure.
Portfolio contracts define the structure and configuration of trading portfolios.

Version: 0.1.0
Phase: Phase 10 - Portfolio Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4

from forge.domain.types import Price, Quantity, InstrumentId


class PortfolioType(Enum):
    """Portfolio type enumeration."""
    SINGLE_STRATEGY = "single_strategy"
    MULTI_STRATEGY = "multi_strategy"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"
    HEDGING = "hedging"
    CUSTOM = "custom"


class PortfolioStatus(Enum):
    """Portfolio status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    LIQUIDATING = "liquidating"
    ERROR = "error"


@dataclass
class PortfolioConfig:
    """Portfolio configuration contract."""
    config_id: str
    portfolio_type: PortfolioType
    base_currency: str = "USD"
    max_positions: int = 10
    max_position_size_pct: float = 0.10
    max_gross_exposure_pct: float = 1.0
    max_net_exposure_pct: float = 0.5
    rebalance_interval: int = 3600  # seconds
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.config_id, str) or not self.config_id:
            raise ValueError("Config ID cannot be empty")
        if not isinstance(self.portfolio_type, PortfolioType):
            raise ValueError("Portfolio type must be PortfolioType enum")
        if not isinstance(self.max_positions, int) or self.max_positions < 1:
            raise ValueError(f"Max positions must be >= 1, got {self.max_positions}")
        if not isinstance(self.max_position_size_pct, (int, float)):
            raise ValueError(f"Max position size must be numeric, got {type(self.max_position_size_pct)}")
        if not 0.0 <= self.max_position_size_pct <= 1.0:
            raise ValueError(f"Max position size must be between 0.0 and 1.0, got {self.max_position_size_pct}")


@dataclass
class Holding:
    """Holding contract."""
    holding_id: str
    instrument_id: InstrumentId
    quantity: Quantity
    avg_entry_price: Price
    current_price: Optional[Price] = None
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.holding_id, str) or not self.holding_id:
            self.holding_id = str(uuid4())
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
    
    @property
    def market_value(self) -> Optional[float]:
        """Get current market value."""
        if self.current_price is None:
            return None
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """Get cost basis."""
        return self.quantity * self.avg_entry_price
    
    @property
    def is_profitable(self) -> bool:
        """Check if holding is profitable."""
        return self.unrealized_pnl > 0
    
    def update_price(self, new_price: Price) -> None:
        """Update current price and recalculate unrealized PnL."""
        self.current_price = new_price
        self.unrealized_pnl = (new_price - self.avg_entry_price) * self.quantity
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class Position:
    """Position contract."""
    position_id: str
    instrument_id: InstrumentId
    side: str  # "long", "short"
    quantity: Quantity
    avg_entry_price: Price
    current_price: Optional[Price] = None
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.position_id, str) or not self.position_id:
            self.position_id = str(uuid4())
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
        if not isinstance(self.side, str) or not self.side:
            raise ValueError("Side cannot be empty")
        if self.side not in ["long", "short"]:
            raise ValueError(f"Side must be 'long' or 'short', got {self.side}")
    
    @property
    def is_long(self) -> bool:
        """Check if position is long."""
        return self.side == "long"
    
    @property
    def is_short(self) -> bool:
        """Check if position is short."""
        return self.side == "short"
    
    @property
    def is_open(self) -> bool:
        """Check if position is open."""
        return self.closed_at is None
    
    @property
    def market_value(self) -> Optional[float]:
        """Get current market value."""
        if self.current_price is None:
            return None
        return self.quantity * self.current_price
    
    @property
    def notional(self) -> float:
        """Get position notional value."""
        return self.quantity * self.avg_entry_price
    
    def update_price(self, new_price: Price) -> None:
        """Update current price and recalculate unrealized PnL."""
        self.current_price = new_price
        if self.is_long:
            self.unrealized_pnl = (new_price - self.avg_entry_price) * self.quantity
        else:
            self.unrealized_pnl = (self.avg_entry_price - new_price) * self.quantity


@dataclass
class PortfolioContract:
    """Portfolio contract contract."""
    contract_id: str
    contract_name: str
    portfolio_type: PortfolioType
    config: PortfolioConfig
    status: PortfolioStatus
    positions: Dict[str, Position] = field(default_factory=dict)
    cash: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.contract_id, str) or not self.contract_id:
            self.contract_id = str(uuid4())
        if not isinstance(self.contract_name, str) or not self.contract_name:
            raise ValueError("Contract name cannot be empty")
        if not isinstance(self.portfolio_type, PortfolioType):
            raise ValueError("Portfolio type must be PortfolioType enum")
        if not isinstance(self.config, PortfolioConfig):
            raise ValueError("Config must be a PortfolioConfig instance")
        if not isinstance(self.status, PortfolioStatus):
            raise ValueError("Status must be PortfolioStatus enum")
    
    @property
    def position_count(self) -> int:
        """Get the number of positions."""
        return len(self.positions)
    
    @property
    def total_value(self) -> float:
        """Get total portfolio value (cash + positions)."""
        positions_value = sum(p.market_value or 0 for p in self.positions.values())
        return self.cash + positions_value
    
    @property
    def gross_exposure(self) -> float:
        """Get gross exposure (absolute value of all positions)."""
        return sum(abs(p.market_value or 0) for p in self.positions.values())
    
    @property
    def net_exposure(self) -> float:
        """Get net exposure (long - short)."""
        long_value = sum(p.market_value or 0 for p in self.positions.values() if p.is_long)
        short_value = sum(p.market_value or 0 for p in self.positions.values() if p.is_short)
        return long_value - short_value
    
    @property
    def total_unrealized_pnl(self) -> float:
        """Get total unrealized PnL."""
        return sum(p.unrealized_pnl for p in self.positions.values())
    
    @property
    def total_realized_pnl(self) -> float:
        """Get total realized PnL."""
        return sum(p.realized_pnl for p in self.positions.values())
    
    def add_position(self, position: Position) -> None:
        """Add a position to the portfolio."""
        self.positions[position.position_id] = position
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_position(self, position_id: str) -> None:
        """Remove a position from the portfolio."""
        if position_id in self.positions:
            del self.positions[position_id]
            self.updated_at = datetime.now(timezone.utc)
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """Get a position by ID."""
        return self.positions.get(position_id)
    
    def get_positions_by_instrument(self, instrument_id: InstrumentId) -> List[Position]:
        """Get all positions for an instrument."""
        return [p for p in self.positions.values() if p.instrument_id == instrument_id]
    
    def update_cash(self, amount: float) -> None:
        """Update cash balance."""
        self.cash += amount
        self.updated_at = datetime.now(timezone.utc)


def create_portfolio_config(
    portfolio_type: PortfolioType,
    max_positions: int = 10,
) -> PortfolioConfig:
    """Create a new portfolio configuration."""
    return PortfolioConfig(
        config_id=str(uuid4()),
        portfolio_type=portfolio_type,
        max_positions=max_positions,
    )


def create_position(
    instrument_id: InstrumentId,
    side: str,
    quantity: Quantity,
    avg_entry_price: Price,
) -> Position:
    """Create a new position."""
    return Position(
        position_id=str(uuid4()),
        instrument_id=instrument_id,
        side=side,
        quantity=quantity,
        avg_entry_price=avg_entry_price,
    )


def create_portfolio_contract(
    contract_name: str,
    portfolio_type: PortfolioType,
    config: PortfolioConfig,
    initial_cash: float = 0.0,
) -> PortfolioContract:
    """Create a new portfolio contract."""
    return PortfolioContract(
        contract_id=str(uuid4()),
        contract_name=contract_name,
        portfolio_type=portfolio_type,
        config=config,
        status=PortfolioStatus.ACTIVE,
        cash=initial_cash,
    )
