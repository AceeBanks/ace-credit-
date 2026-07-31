"""
GLX FORGE Strategy Contracts

This module defines the strategy contracts for the GLX FORGE trading infrastructure.
Strategy contracts define the structure and configuration of trading strategies.

Version: 0.1.0
Phase: Phase 6 - Strategy Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4


class StrategyType(Enum):
    """Strategy type enumeration."""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    TREND_FOLLOWING = "trend_following"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    MACHINE_LEARNING = "machine_learning"
    FUNDAMENTAL = "fundamental"
    CUSTOM = "custom"


class StrategyStatus(Enum):
    """Strategy status enumeration."""
    DRAFT = "draft"
    COMPILED = "compiled"
    VALIDATED = "validated"
    DEPLOYED = "deployed"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class StrategyParameters:
    """Strategy parameters contract."""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a parameter value."""
        return self.parameters.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a parameter value."""
        self.parameters[key] = value
    
    def update(self, parameters: Dict[str, Any]) -> None:
        """Update multiple parameters."""
        self.parameters.update(parameters)
    
    def validate(self, schema: Dict[str, type]) -> bool:
        """Validate parameters against a schema."""
        for key, expected_type in schema.items():
            if key not in self.parameters:
                return False
            if not isinstance(self.parameters[key], expected_type):
                return False
        return True


@dataclass
class StrategyConfig:
    """Strategy configuration contract."""
    strategy_id: str
    name: str
    strategy_type: StrategyType
    instrument_ids: List[str]
    parameters: StrategyParameters
    risk_limits: Dict = field(default_factory=dict)
    capital_allocation: float = 0.0
    max_positions: int = 10
    max_position_size: float = 1.0
    stop_loss_pct: float = 0.05
    take_profit_pct: float = 0.10
    enabled: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValueError("Strategy ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.strategy_type, StrategyType):
            raise ValueError("Strategy type must be StrategyType enum")
        if not isinstance(self.instrument_ids, list):
            raise ValueError("Instrument IDs must be a list")
        if not isinstance(self.parameters, StrategyParameters):
            raise ValueError("Parameters must be a StrategyParameters instance")
        if not isinstance(self.capital_allocation, (int, float)):
            raise ValueError(f"Capital allocation must be numeric, got {type(self.capital_allocation)}")
        if not 0.0 <= self.capital_allocation <= 1.0:
            raise ValueError(f"Capital allocation must be between 0.0 and 1.0, got {self.capital_allocation}")
        if not isinstance(self.max_positions, int) or self.max_positions < 1:
            raise ValueError(f"Max positions must be >= 1, got {self.max_positions}")
        if not isinstance(self.max_position_size, (int, float)):
            raise ValueError(f"Max position size must be numeric, got {type(self.max_position_size)}")
        if self.max_position_size <= 0:
            raise ValueError(f"Max position size must be > 0, got {self.max_position_size}")


@dataclass
class StrategySignal:
    """Strategy signal contract."""
    signal_id: str
    strategy_id: str
    instrument_id: str
    direction: str  # "long", "short", "close"
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    price: Optional[float] = None
    quantity: Optional[float] = None
    reason: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.signal_id, str) or not self.signal_id:
            self.signal_id = str(uuid4())
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValueError("Strategy ID cannot be empty")
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
        if not isinstance(self.direction, str) or not self.direction:
            raise ValueError("Direction cannot be empty")
        if self.direction not in ["long", "short", "close"]:
            raise ValueError(f"Direction must be 'long', 'short', or 'close', got {self.direction}")
        if not isinstance(self.strength, (int, float)):
            raise ValueError(f"Strength must be numeric, got {type(self.strength)}")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"Strength must be between 0.0 and 1.0, got {self.strength}")
        if not isinstance(self.confidence, (int, float)):
            raise ValueError(f"Confidence must be numeric, got {type(self.confidence)}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    @property
    def is_long(self) -> bool:
        """Check if signal is long."""
        return self.direction == "long"
    
    @property
    def is_short(self) -> bool:
        """Check if signal is short."""
        return self.direction == "short"
    
    @property
    def is_close(self) -> bool:
        """Check if signal is close."""
        return self.direction == "close"
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if signal has high confidence."""
        return self.confidence >= 0.8
    
    @property
    def is_strong(self) -> bool:
        """Check if signal is strong."""
        return self.strength >= 0.7


@dataclass
class StrategyContract:
    """Strategy contract contract."""
    contract_id: str
    contract_name: str
    strategy_type: StrategyType
    config: StrategyConfig
    status: StrategyStatus
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.contract_id, str) or not self.contract_id:
            self.contract_id = str(uuid4())
        if not isinstance(self.contract_name, str) or not self.contract_name:
            raise ValueError("Contract name cannot be empty")
        if not isinstance(self.strategy_type, StrategyType):
            raise ValueError("Strategy type must be StrategyType enum")
        if not isinstance(self.config, StrategyConfig):
            raise ValueError("Config must be a StrategyConfig instance")
        if not isinstance(self.status, StrategyStatus):
            raise ValueError("Status must be StrategyStatus enum")
    
    @property
    def is_deployed(self) -> bool:
        """Check if strategy is deployed."""
        return self.status in [StrategyStatus.DEPLOYED, StrategyStatus.RUNNING]
    
    @property
    def is_running(self) -> bool:
        """Check if strategy is running."""
        return self.status == StrategyStatus.RUNNING
    
    @property
    def is_compiled(self) -> bool:
        """Check if strategy is compiled."""
        return self.status in [StrategyStatus.COMPILED, StrategyStatus.VALIDATED, StrategyStatus.DEPLOYED, StrategyStatus.RUNNING]
    
    def mark_compiled(self) -> None:
        """Mark strategy as compiled."""
        self.status = StrategyStatus.COMPILED
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_validated(self) -> None:
        """Mark strategy as validated."""
        self.status = StrategyStatus.VALIDATED
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_deployed(self) -> None:
        """Mark strategy as deployed."""
        self.status = StrategyStatus.DEPLOYED
        self.deployed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_running(self) -> None:
        """Mark strategy as running."""
        self.status = StrategyStatus.RUNNING
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_paused(self) -> None:
        """Mark strategy as paused."""
        self.status = StrategyStatus.PAUSED
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_stopped(self) -> None:
        """Mark strategy as stopped."""
        self.status = StrategyStatus.STOPPED
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_error(self) -> None:
        """Mark strategy as in error state."""
        self.status = StrategyStatus.ERROR
        self.updated_at = datetime.now(timezone.utc)


def create_strategy_config(
    strategy_id: str,
    name: str,
    strategy_type: StrategyType,
    instrument_ids: List[str],
    parameters: Optional[Dict[str, Any]] = None,
) -> StrategyConfig:
    """Create a new strategy configuration."""
    return StrategyConfig(
        strategy_id=strategy_id,
        name=name,
        strategy_type=strategy_type,
        instrument_ids=instrument_ids,
        parameters=StrategyParameters(parameters=parameters or {}),
    )


def create_strategy_signal(
    strategy_id: str,
    instrument_id: str,
    direction: str,
    strength: float,
    confidence: float,
    price: Optional[float] = None,
    quantity: Optional[float] = None,
    reason: str = "",
) -> StrategySignal:
    """Create a new strategy signal."""
    return StrategySignal(
        signal_id=str(uuid4()),
        strategy_id=strategy_id,
        instrument_id=instrument_id,
        direction=direction,
        strength=strength,
        confidence=confidence,
        timestamp=datetime.now(timezone.utc),
        price=price,
        quantity=quantity,
        reason=reason,
    )


def create_strategy_contract(
    contract_name: str,
    strategy_type: StrategyType,
    config: StrategyConfig,
    description: str = "",
    author: str = "",
) -> StrategyContract:
    """Create a new strategy contract."""
    return StrategyContract(
        contract_id=str(uuid4()),
        contract_name=contract_name,
        strategy_type=strategy_type,
        config=config,
        status=StrategyStatus.DRAFT,
        description=description,
        author=author,
    )
