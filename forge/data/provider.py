"""
GLX FORGE Data Provider

This module defines the data provider system for the GLX FORGE trading infrastructure.
Providers are the sources of market data and reference data.

Version: 0.1.0
Phase: Phase 3 - Data Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Set
from uuid import UUID, uuid4

from forge.data.contracts import DataType, DataQuality


class ProviderType(Enum):
    """Provider type enumeration."""
    EXCHANGE = "exchange"
    VENDOR = "vendor"
    INTERNAL = "internal"
    SIMULATION = "simulation"


class ProviderStatus(Enum):
    """Provider status enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class ProviderCapabilities:
    """Provider capabilities contract."""
    data_types: Set[DataType] = field(default_factory=set)
    supports_historical: bool = False
    supports_realtime: bool = False
    supports_streaming: bool = False
    supports_websocket: bool = False
    supports_rest: bool = False
    supports_fix: bool = False
    max_instruments: int = 1000
    max_subscriptions: int = 100
    
    def __post_init__(self):
        if not isinstance(self.data_types, set):
            self.data_types = set(self.data_types)
    
    def supports_data_type(self, data_type: DataType) -> bool:
        """Check if provider supports a data type."""
        return data_type in self.data_types


@dataclass
class ProviderConfig:
    """Provider configuration contract."""
    provider_id: str
    provider_type: ProviderType
    name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    endpoint: str = ""
    ws_endpoint: str = ""
    timeout_seconds: int = 30
    rate_limit_per_second: int = 10
    retry_attempts: int = 3
    retry_delay_seconds: int = 1
    environment: str = "production"
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.provider_id, str) or not self.provider_id:
            raise ValueError("Provider ID cannot be empty")
        if not isinstance(self.provider_type, ProviderType):
            raise ValueError("Provider type must be ProviderType enum")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.timeout_seconds, int) or self.timeout_seconds < 1:
            raise ValueError(f"Timeout must be >= 1, got {self.timeout_seconds}")
        if not isinstance(self.rate_limit_per_second, int) or self.rate_limit_per_second < 1:
            raise ValueError(f"Rate limit must be >= 1, got {self.rate_limit_per_second}")


@dataclass
class DataProvider:
    """Data provider contract."""
    provider_id: str
    name: str
    provider_type: ProviderType
    config: ProviderConfig
    capabilities: ProviderCapabilities
    status: ProviderStatus
    connected_at: Optional[datetime] = None
    disconnected_at: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    subscriptions: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.provider_id, str) or not self.provider_id:
            raise ValueError("Provider ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.provider_type, ProviderType):
            raise ValueError("Provider type must be ProviderType enum")
        if not isinstance(self.config, ProviderConfig):
            raise ValueError("Config must be a ProviderConfig instance")
        if not isinstance(self.capabilities, ProviderCapabilities):
            raise ValueError("Capabilities must be a ProviderCapabilities instance")
        if not isinstance(self.status, ProviderStatus):
            raise ValueError("Status must be ProviderStatus enum")
    
    @property
    def is_connected(self) -> bool:
        """Check if provider is connected."""
        return self.status == ProviderStatus.CONNECTED
    
    @property
    def is_stopped(self) -> bool:
        """Check if provider is stopped."""
        return self.status == ProviderStatus.STOPPED
    
    @property
    def is_error(self) -> bool:
        """Check if provider is in error state."""
        return self.status == ProviderStatus.ERROR
    
    @property
    def subscription_count(self) -> int:
        """Get the number of active subscriptions."""
        return len(self.subscriptions)
    
    def connect(self) -> None:
        """Connect to the provider."""
        self.status = ProviderStatus.STARTING
        self.connected_at = datetime.now(timezone.utc)
        self.status = ProviderStatus.CONNECTED
    
    def disconnect(self) -> None:
        """Disconnect from the provider."""
        self.status = ProviderStatus.DISCONNECTED
        self.disconnected_at = datetime.now(timezone.utc)
        self.subscriptions.clear()
    
    def mark_error(self, error: str) -> None:
        """Mark provider as in error state."""
        self.error_count += 1
        self.last_error = error
        self.status = ProviderStatus.ERROR
    
    def subscribe(self, instrument_id: str) -> None:
        """Subscribe to an instrument."""
        self.subscriptions.add(instrument_id)
    
    def unsubscribe(self, instrument_id: str) -> None:
        """Unsubscribe from an instrument."""
        self.subscriptions.discard(instrument_id)
    
    def get_subscriptions(self) -> List[str]:
        """Get all active subscriptions."""
        return list(self.subscriptions)


# Default data providers for common exchanges
DEFAULT_PROVIDERS = {
    "binance": DataProvider(
        provider_id="provider-binance",
        name="Binance",
        provider_type=ProviderType.EXCHANGE,
        config=ProviderConfig(
            provider_id="provider-binance",
            provider_type=ProviderType.EXCHANGE,
            name="Binance",
            endpoint="https://api.binance.com",
            ws_endpoint="wss://stream.binance.com:9443/ws",
            environment="production",
        ),
        capabilities=ProviderCapabilities(
            data_types={DataType.TICK, DataType.QUOTE, DataType.BAR, DataType.ORDER_BOOK},
            supports_historical=True,
            supports_realtime=True,
            supports_streaming=True,
            supports_websocket=True,
            supports_rest=True,
            max_instruments=10000,
            max_subscriptions=1024,
        ),
        status=ProviderStatus.STOPPED,
    ),
    
    "coinbase": DataProvider(
        provider_id="provider-coinbase",
        name="Coinbase",
        provider_type=ProviderType.EXCHANGE,
        config=ProviderConfig(
            provider_id="provider-coinbase",
            provider_type=ProviderType.EXCHANGE,
            name="Coinbase",
            endpoint="https://api.exchange.coinbase.com",
            ws_endpoint="wss://ws-feed.exchange.coinbase.com",
            environment="production",
        ),
        capabilities=ProviderCapabilities(
            data_types={DataType.TICK, DataType.QUOTE, DataType.BAR},
            supports_historical=True,
            supports_realtime=True,
            supports_streaming=True,
            supports_websocket=True,
            supports_rest=True,
            max_instruments=5000,
            max_subscriptions=512,
        ),
        status=ProviderStatus.STOPPED,
    ),
    
    "polygon": DataProvider(
        provider_id="provider-polygon",
        name="Polygon.io",
        provider_type=ProviderType.VENDOR,
        config=ProviderConfig(
            provider_id="provider-polygon",
            provider_type=ProviderType.VENDOR,
            name="Polygon.io",
            endpoint="https://api.polygon.io",
            environment="production",
        ),
        capabilities=ProviderCapabilities(
            data_types={DataType.TICK, DataType.QUOTE, DataType.BAR, DataType.FUNDAMENTAL},
            supports_historical=True,
            supports_realtime=True,
            supports_streaming=True,
            supports_websocket=True,
            supports_rest=True,
            max_instruments=100000,
            max_subscriptions=1000,
        ),
        status=ProviderStatus.STOPPED,
    ),
    
    "simulation": DataProvider(
        provider_id="provider-simulation",
        name="Simulation Provider",
        provider_type=ProviderType.SIMULATION,
        config=ProviderConfig(
            provider_id="provider-simulation",
            provider_type=ProviderType.SIMULATION,
            name="Simulation Provider",
            endpoint="",
            environment="development",
        ),
        capabilities=ProviderCapabilities(
            data_types={DataType.TICK, DataType.QUOTE, DataType.BAR, DataType.ORDER_BOOK},
            supports_historical=True,
            supports_realtime=True,
            supports_streaming=False,
            supports_websocket=False,
            supports_rest=False,
            max_instruments=1000,
            max_subscriptions=100,
        ),
        status=ProviderStatus.STOPPED,
    ),
}


def create_provider(
    provider_id: str,
    name: str,
    provider_type: ProviderType,
    config: Optional[ProviderConfig] = None,
    capabilities: Optional[ProviderCapabilities] = None,
) -> DataProvider:
    """Create a new data provider."""
    if config is None:
        config = ProviderConfig(
            provider_id=provider_id,
            provider_type=provider_type,
            name=name,
        )
    
    if capabilities is None:
        capabilities = ProviderCapabilities()
    
    return DataProvider(
        provider_id=provider_id,
        name=name,
        provider_type=provider_type,
        config=config,
        capabilities=capabilities,
        status=ProviderStatus.STOPPED,
    )
