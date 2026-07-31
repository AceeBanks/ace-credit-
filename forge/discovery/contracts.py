"""
GLX FORGE Discovery Contracts

This module defines the discovery contracts for the GLX FORGE trading infrastructure.
Discovery contracts define the structure and quality of discovery results.

Version: 0.1.0
Phase: Phase 5 - Discovery Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4


class DiscoveryType(Enum):
    """Discovery type enumeration."""
    INSTRUMENT = "instrument"
    STRATEGY = "strategy"
    SIGNAL = "signal"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    CORRELATION = "correlation"


class DiscoverySource(Enum):
    """Discovery source enumeration."""
    SCANNER = "scanner"
    OBSERVER = "observer"
    MODEL = "model"
    HUMAN = "human"
    EXTERNAL = "external"
    SYSTEM = "system"


class DiscoveryStatus(Enum):
    """Discovery status enumeration."""
    PENDING = "pending"
    DISCOVERED = "discovered"
    VALIDATED = "validated"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class DiscoveryResult:
    """Discovery result contract."""
    result_id: str
    discovery_type: DiscoveryType
    source: DiscoverySource
    instrument_id: str
    status: DiscoveryStatus
    confidence: float  # 0.0 to 1.0
    value: float
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.result_id, str) or not self.result_id:
            self.result_id = str(uuid4())
        if not isinstance(self.discovery_type, DiscoveryType):
            raise ValueError("Discovery type must be DiscoveryType enum")
        if not isinstance(self.source, DiscoverySource):
            raise ValueError("Source must be DiscoverySource enum")
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
        if not isinstance(self.status, DiscoveryStatus):
            raise ValueError("Status must be DiscoveryStatus enum")
        if not isinstance(self.confidence, (int, float)):
            raise ValueError(f"Confidence must be numeric, got {type(self.confidence)}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    @property
    def is_discovered(self) -> bool:
        """Check if discovery is discovered."""
        return self.status == DiscoveryStatus.DISCOVERED
    
    @property
    def is_validated(self) -> bool:
        """Check if discovery is validated."""
        return self.status == DiscoveryStatus.VALIDATED
    
    @property
    def is_rejected(self) -> bool:
        """Check if discovery is rejected."""
        return self.status == DiscoveryStatus.REJECTED
    
    @property
    def is_expired(self) -> bool:
        """Check if discovery is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if discovery has high confidence."""
        return self.confidence >= 0.8
    
    @property
    def time_to_expiry(self) -> Optional[float]:
        """Get time to expiry in seconds."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0, delta.total_seconds())
    
    def validate(self) -> None:
        """Mark discovery as validated."""
        self.status = DiscoveryStatus.VALIDATED
        self.validated_at = datetime.now(timezone.utc)
    
    def reject(self) -> None:
        """Mark discovery as rejected."""
        self.status = DiscoveryStatus.REJECTED


@dataclass
class DiscoveryContract:
    """Discovery contract contract."""
    contract_id: str
    contract_name: str
    discovery_type: DiscoveryType
    source: DiscoverySource
    min_confidence: float
    max_age_seconds: int = 3600  # 1 hour default
    retention_policy: str = "7d"
    access_policy: str = "read_write"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.contract_id, str) or not self.contract_id:
            self.contract_id = str(uuid4())
        if not isinstance(self.contract_name, str) or not self.contract_name:
            raise ValueError("Contract name cannot be empty")
        if not isinstance(self.discovery_type, DiscoveryType):
            raise ValueError("Discovery type must be DiscoveryType enum")
        if not isinstance(self.source, DiscoverySource):
            raise ValueError("Source must be DiscoverySource enum")
        if not isinstance(self.min_confidence, (int, float)):
            raise ValueError(f"Min confidence must be numeric, got {type(self.min_confidence)}")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError(f"Min confidence must be between 0.0 and 1.0, got {self.min_confidence}")
    
    def validate_result(self, result: DiscoveryResult) -> bool:
        """Validate a discovery result against this contract."""
        if result.discovery_type != self.discovery_type:
            return False
        
        if result.source != self.source:
            return False
        
        if result.confidence < self.min_confidence:
            return False
        
        # Check age
        age_seconds = (datetime.now(timezone.utc) - result.timestamp).total_seconds()
        if age_seconds > self.max_age_seconds:
            return False
        
        return True


def create_discovery_result(
    discovery_type: DiscoveryType,
    source: DiscoverySource,
    instrument_id: str,
    confidence: float,
    value: float,
    expires_at: Optional[datetime] = None,
) -> DiscoveryResult:
    """Create a new discovery result."""
    return DiscoveryResult(
        result_id=str(uuid4()),
        discovery_type=discovery_type,
        source=source,
        instrument_id=instrument_id,
        status=DiscoveryStatus.DISCOVERED,
        confidence=confidence,
        value=value,
        timestamp=datetime.now(timezone.utc),
        expires_at=expires_at,
    )


def create_discovery_contract(
    contract_name: str,
    discovery_type: DiscoveryType,
    source: DiscoverySource,
    min_confidence: float = 0.7,
) -> DiscoveryContract:
    """Create a new discovery contract."""
    return DiscoveryContract(
        contract_id=str(uuid4()),
        contract_name=contract_name,
        discovery_type=discovery_type,
        source=source,
        min_confidence=min_confidence,
    )
