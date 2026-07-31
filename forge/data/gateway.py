"""
GLX FORGE Data Gateway

This module defines the data gateway for the GLX FORGE trading infrastructure.
The gateway manages data subscriptions and routing from providers to consumers.

Version: 0.1.0
Phase: Phase 3 - Data Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Set
from uuid import UUID, uuid4

from forge.data.provider import DataProvider, ProviderStatus
from forge.data.contracts import DataType


class SubscriptionStatus(Enum):
    """Subscription status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SubscriptionRequest:
    """Subscription request contract."""
    subscription_id: str
    instrument_id: str
    data_types: Set[DataType]
    provider_id: str
    status: SubscriptionStatus
    created_at: datetime
    activated_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.subscription_id, str) or not self.subscription_id:
            self.subscription_id = str(uuid4())
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
        if not isinstance(self.data_types, set):
            self.data_types = set(self.data_types)
        if not isinstance(self.provider_id, str) or not self.provider_id:
            raise ValueError("Provider ID cannot be empty")
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status == SubscriptionStatus.ACTIVE
    
    @property
    def is_pending(self) -> bool:
        """Check if subscription is pending."""
        return self.status == SubscriptionStatus.PENDING
    
    @property
    def is_failed(self) -> bool:
        """Check if subscription failed."""
        return self.status == SubscriptionStatus.FAILED
    
    def activate(self) -> None:
        """Activate the subscription."""
        self.status = SubscriptionStatus.ACTIVE
        self.activated_at = datetime.now(timezone.utc)
    
    def cancel(self) -> None:
        """Cancel the subscription."""
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = datetime.now(timezone.utc)
    
    def fail(self, error: str) -> None:
        """Mark subscription as failed."""
        self.status = SubscriptionStatus.FAILED
        self.error = error


@dataclass
class GatewayConfig:
    """Gateway configuration contract."""
    gateway_id: str
    name: str
    max_subscriptions: int = 1000
    max_subscriptions_per_provider: int = 100
    heartbeat_interval: int = 30
    auto_reconnect: bool = True
    reconnect_delay_seconds: int = 5
    log_level: str = "INFO"
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.gateway_id, str) or not self.gateway_id:
            raise ValueError("Gateway ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.max_subscriptions, int) or self.max_subscriptions < 1:
            raise ValueError(f"Max subscriptions must be >= 1, got {self.max_subscriptions}")


@dataclass
class DataGateway:
    """Data gateway contract."""
    gateway_id: str
    name: str
    config: GatewayConfig
    providers: Dict[str, DataProvider] = field(default_factory=dict)
    subscriptions: Dict[str, SubscriptionRequest] = field(default_factory=dict)
    instrument_subscriptions: Dict[str, Set[str]] = field(default_factory=dict)  # instrument_id -> subscription_ids
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.gateway_id, str) or not self.gateway_id:
            raise ValueError("Gateway ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.config, GatewayConfig):
            raise ValueError("Config must be a GatewayConfig instance")
    
    def register_provider(self, provider: DataProvider) -> None:
        """Register a data provider."""
        self.providers[provider.provider_id] = provider
        self.updated_at = datetime.now(timezone.utc)
    
    def unregister_provider(self, provider_id: str) -> None:
        """Unregister a data provider."""
        if provider_id in self.providers:
            del self.providers[provider_id]
            # Cancel all subscriptions for this provider
            for sub_id, sub in list(self.subscriptions.items()):
                if sub.provider_id == provider_id:
                    self.cancel_subscription(sub_id)
            self.updated_at = datetime.now(timezone.utc)
    
    def get_provider(self, provider_id: str) -> Optional[DataProvider]:
        """Get a provider by ID."""
        return self.providers.get(provider_id)
    
    def get_connected_providers(self) -> List[DataProvider]:
        """Get all connected providers."""
        return [
            provider for provider in self.providers.values()
            if provider.is_connected
        ]
    
    def subscribe(
        self,
        instrument_id: str,
        data_types: Set[DataType],
        provider_id: str,
    ) -> SubscriptionRequest:
        """Subscribe to an instrument."""
        provider = self.get_provider(provider_id)
        if provider is None:
            raise ValueError(f"Provider not found: {provider_id}")
        
        if not provider.is_connected:
            raise ValueError(f"Provider not connected: {provider_id}")
        
        subscription = SubscriptionRequest(
            subscription_id=str(uuid4()),
            instrument_id=instrument_id,
            data_types=data_types,
            provider_id=provider_id,
            status=SubscriptionStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        
        # Update instrument subscriptions index
        if instrument_id not in self.instrument_subscriptions:
            self.instrument_subscriptions[instrument_id] = set()
        self.instrument_subscriptions[instrument_id].add(subscription.subscription_id)
        
        # Subscribe on provider
        provider.subscribe(instrument_id)
        subscription.activate()
        
        self.updated_at = datetime.now(timezone.utc)
        
        return subscription
    
    def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from an instrument."""
        subscription = self.subscriptions.get(subscription_id)
        if subscription is None:
            return
        
        subscription.cancel()
        
        # Unsubscribe on provider
        provider = self.get_provider(subscription.provider_id)
        if provider:
            provider.unsubscribe(subscription.instrument_id)
        
        # Update instrument subscriptions index
        if subscription.instrument_id in self.instrument_subscriptions:
            self.instrument_subscriptions[subscription.instrument_id].discard(subscription_id)
            if not self.instrument_subscriptions[subscription.instrument_id]:
                del self.instrument_subscriptions[subscription.instrument_id]
        
        self.updated_at = datetime.now(timezone.utc)
    
    def cancel_subscription(self, subscription_id: str) -> None:
        """Cancel a subscription."""
        self.unsubscribe(subscription_id)
    
    def get_subscription(self, subscription_id: str) -> Optional[SubscriptionRequest]:
        """Get a subscription by ID."""
        return self.subscriptions.get(subscription_id)
    
    def get_subscriptions_for_instrument(self, instrument_id: str) -> List[SubscriptionRequest]:
        """Get all subscriptions for an instrument."""
        if instrument_id not in self.instrument_subscriptions:
            return []
        
        subscription_ids = self.instrument_subscriptions[instrument_id]
        return [
            self.subscriptions[sub_id]
            for sub_id in subscription_ids
            if sub_id in self.subscriptions
        ]
    
    def get_active_subscriptions(self) -> List[SubscriptionRequest]:
        """Get all active subscriptions."""
        return [
            sub for sub in self.subscriptions.values()
            if sub.is_active
        ]
    
    @property
    def provider_count(self) -> int:
        """Get the number of registered providers."""
        return len(self.providers)
    
    @property
    def subscription_count(self) -> int:
        """Get the number of active subscriptions."""
        return len(self.get_active_subscriptions())
    
    @property
    def instrument_count(self) -> int:
        """Get the number of instruments with subscriptions."""
        return len(self.instrument_subscriptions)


def create_gateway(name: str, config: Optional[GatewayConfig] = None) -> DataGateway:
    """Create a new data gateway."""
    if config is None:
        config = GatewayConfig(
            gateway_id=str(uuid4()),
            name=name,
        )
    
    return DataGateway(
        gateway_id=config.gateway_id,
        name=name,
        config=config,
    )
