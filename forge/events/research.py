"""
GLX FORGE Research Events

This module defines research-related events for the GLX FORGE trading infrastructure.
Research events represent backtest lifecycle, signal generation, and research activities.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from forge.domain.types import (
    Timestamp,
    validate_timestamp,
    ValidationError,
)


@dataclass(frozen=True)
class BacktestStarted:
    """Event emitted when a backtest is started."""
    event_id: str
    backtest_id: str
    strategy_id: str
    instrument_id: str
    start_date: str
    end_date: str
    timestamp: Timestamp
    parameters: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.backtest_id, str) or not self.backtest_id:
            raise ValidationError("Backtest ID cannot be empty")
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValidationError("Strategy ID cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class BacktestCompleted:
    """Event emitted when a backtest completes successfully."""
    event_id: str
    backtest_id: str
    strategy_id: str
    timestamp: Timestamp
    total_trades: int
    total_pnl: float
    total_return: float
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.backtest_id, str) or not self.backtest_id:
            raise ValidationError("Backtest ID cannot be empty")
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValidationError("Strategy ID cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class BacktestFailed:
    """Event emitted when a backtest fails."""
    event_id: str
    backtest_id: str
    strategy_id: str
    timestamp: Timestamp
    error: str
    error_type: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.backtest_id, str) or not self.backtest_id:
            raise ValidationError("Backtest ID cannot be empty")
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValidationError("Strategy ID cannot be empty")
        if not isinstance(self.error, str) or not self.error:
            raise ValidationError("Error message cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class SignalGenerated:
    """Event emitted when a trading signal is generated."""
    event_id: str
    signal_id: str
    strategy_id: str
    instrument_id: str
    signal_type: str  # "entry_long", "entry_short", "exit_long", "exit_short"
    confidence: float  # 0.0 to 1.0
    timestamp: Timestamp
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.signal_id, str) or not self.signal_id:
            raise ValidationError("Signal ID cannot be empty")
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValidationError("Strategy ID cannot be empty")
        if not isinstance(self.signal_type, str) or not self.signal_type:
            raise ValidationError("Signal type cannot be empty")
        if not isinstance(self.confidence, (int, float)):
            raise ValidationError(f"Confidence must be numeric, got {type(self.confidence)}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValidationError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class SignalExpired:
    """Event emitted when a signal expires without being acted upon."""
    event_id: str
    signal_id: str
    strategy_id: str
    instrument_id: str
    timestamp: Timestamp
    reason: str
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.signal_id, str) or not self.signal_id:
            raise ValidationError("Signal ID cannot be empty")
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValidationError("Strategy ID cannot be empty")
        if not isinstance(self.reason, str) or not self.reason:
            raise ValidationError("Expiration reason cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)
