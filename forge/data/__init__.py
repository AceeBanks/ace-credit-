"""
GLX FORGE Data Forge

This module defines the data infrastructure for the GLX FORGE trading infrastructure.
Data includes contracts, provider gateway, and market reference lake.

Version: 0.1.0
Phase: Phase 3 - Data Forge
"""

__version__ = "0.1.0"

from forge.data.contracts import (
    DataContract,
    DataType,
    DataQuality,
    DataSchema,
    FieldDefinition,
    DataRecord,
)

from forge.data.provider import (
    DataProvider,
    ProviderType,
    ProviderStatus,
    ProviderConfig,
    ProviderCapabilities,
    DEFAULT_PROVIDERS,
)

from forge.data.gateway import (
    DataGateway,
    GatewayConfig,
    SubscriptionRequest,
    SubscriptionStatus,
)

from forge.data.market_lake import (
    MarketReferenceLake,
    LakeConfig,
    DataPartition,
    PartitionType,
    QueryRequest,
    QueryResult,
)

__all__ = [
    # Contracts
    "DataContract",
    "DataType",
    "DataQuality",
    "DataSchema",
    "FieldDefinition",
    "DataRecord",
    # Provider
    "DataProvider",
    "ProviderType",
    "ProviderStatus",
    "ProviderConfig",
    "ProviderCapabilities",
    "DEFAULT_PROVIDERS",
    # Gateway
    "DataGateway",
    "GatewayConfig",
    "SubscriptionRequest",
    "SubscriptionStatus",
    # Market Lake
    "MarketReferenceLake",
    "LakeConfig",
    "DataPartition",
    "PartitionType",
    "QueryRequest",
    "QueryResult",
]
