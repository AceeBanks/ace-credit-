"""
GLX FORGE Intelligence Observers

This module defines the observer system for the GLX FORGE trading infrastructure.
Observers monitor market data and generate intelligence signals.

Version: 0.1.0
Phase: Phase 4 - Intelligence Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Callable, Any
from uuid import UUID, uuid4

from forge.intelligence.contracts import IntelligenceSignal, IntelligenceType, IntelligenceSource


class ObserverType(Enum):
    """Observer type enumeration."""
    PRICE = "price"
    VOLUME = "volume"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    TREND = "trend"
    MEAN_REVERSION = "mean_reversion"
    CORRELATION = "correlation"
    ANOMALY = "anomaly"
    SENTIMENT = "sentiment"
    CUSTOM = "custom"


class ObserverState(Enum):
    """Observer state enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ObserverConfig:
    """Observer configuration contract."""
    observer_id: str
    observer_type: ObserverType
    instrument_id: str
    parameters: Dict = field(default_factory=dict)
    update_interval_seconds: int = 1
    lookback_periods: int = 100
    enabled: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.observer_id, str) or not self.observer_id:
            raise ValueError("Observer ID cannot be empty")
        if not isinstance(self.observer_type, ObserverType):
            raise ValueError("Observer type must be ObserverType enum")
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
        if not isinstance(self.update_interval_seconds, int) or self.update_interval_seconds < 1:
            raise ValueError(f"Update interval must be >= 1, got {self.update_interval_seconds}")


@dataclass
class ObserverEvent:
    """Observer event contract."""
    event_id: str
    observer_id: str
    event_type: str
    timestamp: datetime
    data: Dict = field(default_factory=dict)
    signal: Optional[IntelligenceSignal] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            self.event_id = str(uuid4())
        if not isinstance(self.observer_id, str) or not self.observer_id:
            raise ValueError("Observer ID cannot be empty")
        if not isinstance(self.event_type, str) or not self.event_type:
            raise ValueError("Event type cannot be empty")


@dataclass
class Observer:
    """Observer contract."""
    observer_id: str
    name: str
    observer_type: ObserverType
    config: ObserverConfig
    state: ObserverState
    signals: List[IntelligenceSignal] = field(default_factory=list)
    events: List[ObserverEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.observer_id, str) or not self.observer_id:
            raise ValueError("Observer ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.observer_type, ObserverType):
            raise ValueError("Observer type must be ObserverType enum")
        if not isinstance(self.config, ObserverConfig):
            raise ValueError("Config must be an ObserverConfig instance")
        if not isinstance(self.state, ObserverState):
            raise ValueError("State must be ObserverState enum")
    
    @property
    def is_running(self) -> bool:
        """Check if observer is running."""
        return self.state == ObserverState.RUNNING
    
    @property
    def is_stopped(self) -> bool:
        """Check if observer is stopped."""
        return self.state == ObserverState.STOPPED
    
    @property
    def is_error(self) -> bool:
        """Check if observer is in error state."""
        return self.state == ObserverState.ERROR
    
    @property
    def signal_count(self) -> int:
        """Get the number of generated signals."""
        return len(self.signals)
    
    @property
    def event_count(self) -> int:
        """Get the number of generated events."""
        return len(self.events)
    
    @property
    def uptime(self) -> Optional[float]:
        """Get observer uptime in seconds."""
        if self.started_at is None:
            return None
        if self.stopped_at is not None:
            return (self.stopped_at - self.started_at).total_seconds()
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()
    
    def start(self) -> None:
        """Start the observer."""
        self.state = ObserverState.STARTING
        self.started_at = datetime.now(timezone.utc)
        self.state = ObserverState.RUNNING
    
    def stop(self) -> None:
        """Stop the observer."""
        self.state = ObserverState.STOPPED
        self.stopped_at = datetime.now(timezone.utc)
    
    def pause(self) -> None:
        """Pause the observer."""
        self.state = ObserverState.PAUSED
    
    def resume(self) -> None:
        """Resume the observer."""
        self.state = ObserverState.RUNNING
    
    def mark_error(self, error: str) -> None:
        """Mark observer as in error state."""
        self.error_count += 1
        self.last_error = error
        self.state = ObserverState.ERROR
    
    def add_signal(self, signal: IntelligenceSignal) -> None:
        """Add a signal to the observer."""
        self.signals.append(signal)
    
    def add_event(self, event: ObserverEvent) -> None:
        """Add an event to the observer."""
        self.events.append(event)
    
    def get_recent_signals(self, limit: int = 100) -> List[IntelligenceSignal]:
        """Get recent signals."""
        return self.signals[-limit:]
    
    def get_recent_events(self, limit: int = 100) -> List[ObserverEvent]:
        """Get recent events."""
        return self.events[-limit:]


# Default observers for common intelligence types
DEFAULT_OBSERVERS = {
    "price_momentum": Observer(
        observer_id="observer-price-momentum",
        name="Price Momentum Observer",
        observer_type=ObserverType.MOMENTUM,
        config=ObserverConfig(
            observer_id="observer-price-momentum",
            observer_type=ObserverType.MOMENTUM,
            instrument_id="BTCUSDT",
            parameters={"period": 14, "threshold": 0.02},
            update_interval_seconds=60,
        ),
        state=ObserverState.STOPPED,
    ),
    
    "volatility": Observer(
        observer_id="observer-volatility",
        name="Volatility Observer",
        observer_type=ObserverType.VOLATILITY,
        config=ObserverConfig(
            observer_id="observer-volatility",
            observer_type=ObserverType.VOLATILITY,
            instrument_id="BTCUSDT",
            parameters={"period": 20, "threshold": 0.05},
            update_interval_seconds=300,
        ),
        state=ObserverState.STOPPED,
    ),
    
    "trend": Observer(
        observer_id="observer-trend",
        name="Trend Observer",
        observer_type=ObserverType.TREND,
        config=ObserverConfig(
            observer_id="observer-trend",
            observer_type=ObserverType.TREND,
            instrument_id="BTCUSDT",
            parameters={"short_period": 10, "long_period": 30},
            update_interval_seconds=300,
        ),
        state=ObserverState.STOPPED,
    ),
    
    "mean_reversion": Observer(
        observer_id="observer-mean-reversion",
        name="Mean Reversion Observer",
        observer_type=ObserverType.MEAN_REVERSION,
        config=ObserverConfig(
            observer_id="observer-mean-reversion",
            observer_type=ObserverType.MEAN_REVERSION,
            instrument_id="BTCUSDT",
            parameters={"period": 20, "std_dev_threshold": 2.0},
            update_interval_seconds=60,
        ),
        state=ObserverState.STOPPED,
    ),
    
    "anomaly": Observer(
        observer_id="observer-anomaly",
        name="Anomaly Observer",
        observer_type=ObserverType.ANOMALY,
        config=ObserverConfig(
            observer_id="observer-anomaly",
            observer_type=ObserverType.ANOMALY,
            instrument_id="BTCUSDT",
            parameters={"window": 100, "z_score_threshold": 3.0},
            update_interval_seconds=60,
        ),
        state=ObserverState.STOPPED,
    ),
}


def create_observer(
    observer_id: str,
    name: str,
    observer_type: ObserverType,
    instrument_id: str,
    parameters: Optional[Dict] = None,
    config: Optional[ObserverConfig] = None,
) -> Observer:
    """Create a new observer."""
    if config is None:
        config = ObserverConfig(
            observer_id=observer_id,
            observer_type=observer_type,
            instrument_id=instrument_id,
            parameters=parameters or {},
        )
    
    return Observer(
        observer_id=observer_id,
        name=name,
        observer_type=observer_type,
        config=config,
        state=ObserverState.STOPPED,
    )


def create_observer_event(
    observer_id: str,
    event_type: str,
    data: Optional[Dict] = None,
    signal: Optional[IntelligenceSignal] = None,
) -> ObserverEvent:
    """Create a new observer event."""
    return ObserverEvent(
        event_id=str(uuid4()),
        observer_id=observer_id,
        event_type=event_type,
        timestamp=datetime.now(timezone.utc),
        data=data or {},
        signal=signal,
    )
