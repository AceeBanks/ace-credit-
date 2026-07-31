"""
GLX FORGE Simulation Paper Trading

This module defines the paper trading engine for the GLX FORGE trading infrastructure.
Paper trading allows strategy testing without real money.

Version: 0.1.0
Phase: Phase 8 - Simulation Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4


class TradeStatus(Enum):
    """Trade status enumeration."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class PaperTradeConfig:
    """Paper trade configuration contract."""
    config_id: str
    initial_capital: float
    commission_rate: float = 0.001  # 0.1%
    slippage_rate: float = 0.0005  # 0.05%
    latency_ms: int = 10
    fill_mode: str = "immediate"  # "immediate", "realistic"
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.config_id, str) or not self.config_id:
            raise ValueError("Config ID cannot be empty")
        if not isinstance(self.initial_capital, (int, float)):
            raise ValueError(f"Initial capital must be numeric, got {type(self.initial_capital)}")
        if self.initial_capital <= 0:
            raise ValueError(f"Initial capital must be positive, got {self.initial_capital}")


@dataclass
class PaperPortfolio:
    """Paper portfolio contract."""
    portfolio_id: str
    cash: float
    positions: Dict[str, float] = field(default_factory=dict)  # instrument_id -> quantity
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    total_trades: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.portfolio_id, str) or not self.portfolio_id:
            self.portfolio_id = str(uuid4())
        if not isinstance(self.cash, (int, float)):
            raise ValueError(f"Cash must be numeric, got {type(self.cash)}")
    
    @property
    def total_value(self) -> float:
        """Get total portfolio value (cash + positions)."""
        return self.cash + self.unrealized_pnl
    
    @property
    def total_return(self) -> float:
        """Get total return percentage."""
        if self.cash == 0:
            return 0.0
        return (self.total_value - self.cash) / self.cash
    
    def add_position(self, instrument_id: str, quantity: float) -> None:
        """Add to a position."""
        self.positions[instrument_id] = self.positions.get(instrument_id, 0.0) + quantity
    
    def remove_position(self, instrument_id: str, quantity: float) -> None:
        """Remove from a position."""
        current = self.positions.get(instrument_id, 0.0)
        new_quantity = current - quantity
        if new_quantity <= 0:
            del self.positions[instrument_id]
        else:
            self.positions[instrument_id] = new_quantity


@dataclass
class PaperTradeResult:
    """Paper trade result contract."""
    result_id: str
    instrument_id: str
    side: str  # "buy", "sell"
    quantity: float
    price: float
    status: TradeStatus
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    commission: float = 0.0
    slippage: float = 0.0
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.result_id, str) or not self.result_id:
            self.result_id = str(uuid4())
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
        if not isinstance(self.side, str) or not self.side:
            raise ValueError("Side cannot be empty")
        if self.side not in ["buy", "sell"]:
            raise ValueError(f"Side must be 'buy' or 'sell', got {self.side}")
        if not isinstance(self.status, TradeStatus):
            raise ValueError("Status must be TradeStatus enum")
    
    @property
    def is_filled(self) -> bool:
        """Check if trade is filled."""
        return self.status == TradeStatus.FILLED
    
    @property
    def notional(self) -> float:
        """Get trade notional value."""
        return self.filled_quantity * self.avg_fill_price


@dataclass
class PaperTradingEngine:
    """Paper trading engine contract."""
    engine_id: str
    name: str
    config: PaperTradeConfig
    portfolio: PaperPortfolio
    trades: List[PaperTradeResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.engine_id, str) or not self.engine_id:
            raise ValueError("Engine ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.config, PaperTradeConfig):
            raise ValueError("Config must be a PaperTradeConfig instance")
        if not isinstance(self.portfolio, PaperPortfolio):
            raise ValueError("Portfolio must be a PaperPortfolio instance")
    
    def execute_trade(
        self,
        instrument_id: str,
        side: str,
        quantity: float,
        price: float,
    ) -> PaperTradeResult:
        """Execute a paper trade."""
        # Calculate commission
        commission = price * quantity * self.config.commission_rate
        
        # Calculate slippage
        slippage = price * quantity * self.config.slippage_rate
        
        # Adjust price for slippage
        if side == "buy":
            execution_price = price * (1 + self.config.slippage_rate)
        else:
            execution_price = price * (1 - self.config.slippage_rate)
        
        # Check if enough cash for buy
        if side == "buy":
            required = execution_price * quantity + commission
            if self.portfolio.cash < required:
                return PaperTradeResult(
                    result_id=str(uuid4()),
                    instrument_id=instrument_id,
                    side=side,
                    quantity=quantity,
                    price=price,
                    status=TradeStatus.REJECTED,
                    error="Insufficient cash",
                )
        
        # Check if enough position for sell
        if side == "sell":
            current_position = self.portfolio.positions.get(instrument_id, 0.0)
            if current_position < quantity:
                return PaperTradeResult(
                    result_id=str(uuid4()),
                    instrument_id=instrument_id,
                    side=side,
                    quantity=quantity,
                    price=price,
                    status=TradeStatus.REJECTED,
                    error="Insufficient position",
                )
        
        # Execute trade
        result = PaperTradeResult(
            result_id=str(uuid4()),
            instrument_id=instrument_id,
            side=side,
            quantity=quantity,
            price=price,
            status=TradeStatus.FILLED,
            filled_quantity=quantity,
            avg_fill_price=execution_price,
            commission=commission,
            slippage=slippage,
        )
        
        # Update portfolio
        if side == "buy":
            self.portfolio.cash -= (execution_price * quantity + commission)
            self.portfolio.add_position(instrument_id, quantity)
        else:
            self.portfolio.cash += (execution_price * quantity - commissioner)
            self.portfolio.remove_position(instrument_id, quantity)
        
        self.portfolio.total_trades += 1
        self.trades.append(result)
        
        return result
    
    @property
    def trade_count(self) -> int:
        """Get the number of trades."""
        return len(self.trades)
    
    def get_trades_by_instrument(self, instrument_id: str) -> List[PaperTradeResult]:
        """Get trades for an instrument."""
        return [t for t in self.trades if t.instrument_id == instrument_id]


def create_paper_trading_engine(
    name: str,
    initial_capital: float,
    config: Optional[PaperTradeConfig] = None,
) -> PaperTradingEngine:
    """Create a new paper trading engine."""
    if config is None:
        config = PaperTradeConfig(
            config_id=str(uuid4()),
            initial_capital=initial_capital,
        )
    
    portfolio = PaperPortfolio(
        portfolio_id=str(uuid4()),
        cash=initial_capital,
    )
    
    return PaperTradingEngine(
        engine_id=str(uuid4()),
        name=name,
        config=config,
        portfolio=portfolio,
    )


def create_paper_portfolio(initial_capital: float) -> PaperPortfolio:
    """Create a new paper portfolio."""
    return PaperPortfolio(
        portfolio_id=str(uuid4()),
        cash=initial_capital,
    )
