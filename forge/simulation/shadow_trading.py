"""
GLX FORGE Simulation Shadow Trading

This module defines the shadow trading engine for the GLX FORGE trading infrastructure.
Shadow trading compares strategy performance against a benchmark or live execution.

Version: 0.1.0
Phase: Phase 8 - Simulation Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4


class ShadowMode(Enum):
    """Shadow mode enumeration."""
    PARALLEL = "parallel"  # Run alongside live without execution
    DELAYED = "delayed"  # Run with time delay
    REPLAY = "replay"  # Replay historical data


@dataclass
class ShadowTradeConfig:
    """Shadow trade configuration contract."""
    config_id: str
    benchmark_id: str  # Strategy or benchmark to compare against
    mode: ShadowMode
    delay_seconds: int = 0
    max_slippage_pct: float = 0.01
    commission_rate: float = 0.001
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.config_id, str) or not self.config_id:
            raise ValueError("Config ID cannot be empty")
        if not isinstance(self.benchmark_id, str) or not self.benchmark_id:
            raise ValueError("Benchmark ID cannot be empty")
        if not isinstance(self.mode, ShadowMode):
            raise ValueError("Mode must be ShadowMode enum")


@dataclass
class ShadowComparison:
    """Shadow comparison contract."""
    comparison_id: str
    strategy_id: str
    benchmark_id: str
    strategy_return: float
    benchmark_return: float
    excess_return: float
    strategy_sharpe: float
    benchmark_sharpe: float
    strategy_drawdown: float
    benchmark_drawdown: float
    win_rate: float  # Percentage of trades where strategy outperformed
    trade_count: int
    compared_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.comparison_id, str) or not self.comparison_id:
            self.comparison_id = str(uuid4())
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValueError("Strategy ID cannot be empty")
        if not isinstance(self.benchmark_id, str) or not self.benchmark_id:
            raise ValueError("Benchmark ID cannot be empty")
    
    @property
    def outperformed(self) -> bool:
        """Check if strategy outperformed benchmark."""
        return self.excess_return > 0
    
    @property
    def alpha(self) -> float:
        """Get alpha (excess return)."""
        return self.excess_return
    
    @property
    def tracking_error(self) -> float:
        """Get tracking error (difference in returns)."""
        return abs(self.strategy_return - self.benchmark_return)


@dataclass
class ShadowTradeResult:
    """Shadow trade result contract."""
    result_id: str
    strategy_id: str
    benchmark_id: str
    instrument_id: str
    strategy_price: float
    benchmark_price: float
    strategy_quantity: float
    benchmark_quantity: float
    slippage_pct: float
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.result_id, str) or not self.result_id:
            self.result_id = str(uuid4())
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValueError("Strategy ID cannot be empty")
        if not isinstance(self.benchmark_id, str) or not self.benchmark_id:
            raise ValueError("Benchmark ID cannot be empty")
    
    @property
    def price_diff(self) -> float:
        """Get price difference."""
        return self.strategy_price - self.benchmark_price
    
    @property
    def quantity_diff(self) -> float:
        """Get quantity difference."""
        return self.strategy_quantity - self.benchmark_quantity


@dataclass
class ShadowTradingEngine:
    """Shadow trading engine contract."""
    engine_id: str
    name: str
    config: ShadowTradeConfig
    results: List[ShadowTradeResult] = field(default_factory=list)
    comparisons: List[ShadowComparison] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.engine_id, str) or not self.engine_id:
            raise ValueError("Engine ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.config, ShadowTradeConfig):
            raise ValueError("Config must be a ShadowTradeConfig instance")
    
    def execute_shadow_trade(
        self,
        strategy_id: str,
        instrument_id: str,
        strategy_price: float,
        strategy_quantity: float,
        benchmark_price: float,
        benchmark_quantity: float,
    ) -> ShadowTradeResult:
        """Execute a shadow trade comparison."""
        # Calculate slippage
        price_diff_pct = abs(strategy_price - benchmark_price) / benchmark_price
        slippage = min(price_diff_pct, self.config.max_slippage_pct)
        
        result = ShadowTradeResult(
            result_id=str(uuid4()),
            strategy_id=strategy_id,
            benchmark_id=self.config.benchmark_id,
            instrument_id=instrument_id,
            strategy_price=strategy_price,
            benchmark_price=benchmark_price,
            strategy_quantity=strategy_quantity,
            benchmark_quantity=benchmark_quantity,
            slippage_pct=slippage,
        )
        
        self.results.append(result)
        
        return result
    
    def generate_comparison(
        self,
        strategy_id: str,
        strategy_return: float,
        strategy_sharpe: float,
        strategy_drawdown: float,
        benchmark_return: float,
        benchmark_sharpe: float,
        benchmark_drawdown: float,
    ) -> ShadowComparison:
        """Generate a shadow comparison."""
        excess_return = strategy_return - benchmark_return
        
        # Calculate win rate (percentage of trades where strategy had better execution)
        better_trades = sum(
            1 for r in self.results
            if r.strategy_id == strategy_id and r.slippage_pct < 0.005
        )
        win_rate = better_trades / len(self.results) if self.results else 0.0
        
        comparison = ShadowComparison(
            comparison_id=str(uuid4()),
            strategy_id=strategy_id,
            benchmark_id=self.config.benchmark_id,
            strategy_return=strategy_return,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            strategy_sharpe=strategy_sharpe,
            benchmark_sharpe=benchmark_sharpe,
            strategy_drawdown=strategy_drawdown,
            benchmark_drawdown=benchmark_drawdown,
            win_rate=win_rate,
            trade_count=len(self.results),
        )
        
        self.comparisons.append(comparison)
        
        return comparison
    
    @property
    def result_count(self) -> int:
        """Get the number of shadow trade results."""
        return len(self.results)
    
    @property
    def comparison_count(self) -> int:
        """Get the number of comparisons."""
        return len(self.comparisons)
    
    def get_results_by_strategy(self, strategy_id: str) -> List[ShadowTradeResult]:
        """Get results for a strategy."""
        return [r for r in self.results if r.strategy_id == strategy_id]
    
    def get_latest_comparison(self, strategy_id: str) -> Optional[ShadowComparison]:
        """Get the latest comparison for a strategy."""
        for comparison in reversed(self.comparisons):
            if comparison.strategy_id == strategy_id:
                return comparison
        return None


def create_shadow_trading_engine(
    name: str,
    benchmark_id: str,
    mode: ShadowMode = ShadowMode.PARALLEL,
    config: Optional[ShadowTradeConfig] = None,
) -> ShadowTradingEngine:
    """Create a new shadow trading engine."""
    if config is None:
        config = ShadowTradeConfig(
            config_id=str(uuid4()),
            benchmark_id=benchmark_id,
            mode=mode,
        )
    
    return ShadowTradingEngine(
        engine_id=str(uuid4()),
        name=name,
        config=config,
    )


def create_shadow_comparison(
    strategy_id: str,
    benchmark_id: str,
    strategy_return: float,
    benchmark_return: float,
) -> ShadowComparison:
    """Create a shadow comparison."""
    return ShadowComparison(
        comparison_id=str(uuid4()),
        strategy_id=strategy_id,
        benchmark_id=benchmark_id,
        strategy_return=strategy_return,
        benchmark_return=benchmark_return,
        excess_return=strategy_return - benchmark_return,
        strategy_sharpe=0.0,
        benchmark_sharpe=0.0,
        strategy_drawdown=0.0,
        benchmark_drawdown=0.0,
        win_rate=0.0,
        trade_count=0,
    )
