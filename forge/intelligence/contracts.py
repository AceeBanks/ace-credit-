"""
GLX FORGE Intelligence Contracts

This module defines the intelligence contracts for the GLX FORGE trading infrastructure.
Intelligence contracts define the structure and quality of trading intelligence.

Version: 0.1.0
Phase: Phase 4 - Intelligence Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4


class IntelligenceType(Enum):
    """Intelligence type enumeration."""
    SIGNAL = "signal"
    PREDICTION = "prediction"
    ANOMALY = "anomaly"
    PATTERN = "pattern"
    CORRELATION = "correlation"
    SENTIMENT = "sentiment"
    FUNDAMENTAL = "fundamental"
    TECHNICAL = "technical"


class IntelligenceSource(Enum):
    """Intelligence source enumeration."""
    OBSERVER = "observer"
    MODEL = "model"
    HUMAN = "human"
    EXTERNAL = "external"
    SYSTEM = "system"


class IntelligenceQuality(Enum):
    """Intelligence quality enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class SignalStrength(Enum):
    """Signal strength enumeration."""
    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    VERY_WEAK = "very_weak"


class SignalConfidence(Enum):
    """Signal confidence enumeration."""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass
class IntelligenceSignal:
    """Intelligence signal contract."""
    signal_id: str
    intelligence_type: IntelligenceType
    source: IntelligenceSource
    instrument_id: str
    strength: SignalStrength
    confidence: SignalConfidence
    direction: str  # "long", "short", "neutral"
    timestamp: datetime
    value: float
    metadata: Dict = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    quality: IntelligenceQuality = IntelligenceQuality.UNKNOWN
    
    def __post_init__(self):
        if not isinstance(self.signal_id, str) or not self.signal_id:
            self.signal_id = str(uuid4())
        if not isinstance(self.intelligence_type, IntelligenceType):
            raise ValueError("Intelligence type must be IntelligenceType enum")
        if not isinstance(self.source, IntelligenceSource):
            raise ValueError("Source must be IntelligenceSource enum")
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
        if not isinstance(self.strength, SignalStrength):
            raise ValueError("Strength must be SignalStrength enum")
        if not isinstance(self.confidence, SignalConfidence):
            raise ValueError("Confidence must be SignalConfidence enum")
        if not isinstance(self.direction, str) or not self.direction:
            raise ValueError("Direction cannot be empty")
        if self.direction not in ["long", "short", "neutral"]:
            raise ValueError(f"Direction must be 'long', 'short', or 'neutral', got {self.direction}")
    
    @property
    def is_long(self) -> bool:
        """Check if signal is long."""
        return self.direction == "long"
    
    @property
    def is_short(self) -> bool:
        """Check if signal is short."""
        return self.direction == "short"
    
    @property
    def is_neutral(self) -> bool:
        """Check if signal is neutral."""
        return self.direction == "neutral"
    
    @property
    def is_expired(self) -> bool:
        """Check if signal is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def time_to_expiry(self) -> Optional[float]:
        """Get time to expiry in seconds."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0, delta.total_seconds())
    
    @property
    def is_high_quality(self) -> bool:
        """Check if signal is high quality."""
        return self.quality == IntelligenceQuality.HIGH
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if signal is high confidence."""
        return self.confidence in [SignalConfidence.VERY_HIGH, SignalConfidence.HIGH]


@dataclass
class IntelligenceContract:
    """Intelligence contract contract."""
    contract_id: str
    contract_name: str
    intelligence_type: IntelligenceType
    source: IntelligenceSource
    quality_requirement: IntelligenceQuality
    min_confidence: SignalConfidence
    min_strength: SignalStrength
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
        if not isinstance(self.intelligence_type, IntelligenceType):
            raise ValueError("Intelligence type must be IntelligenceType enum")
        if not isinstance(self.source, IntelligenceSource):
            raise ValueError("Source must be IntelligenceSource enum")
        if not isinstance(self.quality_requirement, IntelligenceQuality):
            raise ValueError("Quality requirement must be IntelligenceQuality enum")
        if not isinstance(self.min_confidence, SignalConfidence):
            raise ValueError("Min confidence must be SignalConfidence enum")
        if not isinstance(self.min_strength, SignalStrength):
            raise ValueError("Min strength must be SignalStrength enum")
    
    def validate_signal(self, signal: IntelligenceSignal) -> bool:
        """Validate a signal against this contract."""
        if signal.intelligence_type != self.intelligence_type:
            return False
        
        if signal.source != self.source:
            return False
        
        if signal.quality != IntelligenceQuality.UNKNOWN and signal.quality != self.quality_requirement:
            return False
        
        # Check confidence threshold
        confidence_order = {
            SignalConfidence.VERY_LOW: 0,
            SignalConfidence.LOW: 1,
            SignalConfidence.MEDIUM: 2,
            SignalConfidence.HIGH: 3,
            SignalConfidence.VERY_HIGH: 4,
        }
        if confidence_order[signal.confidence] < confidence_order[self.min_confidence]:
            return False
        
        # Check strength threshold
        strength_order = {
            SignalStrength.VERY_WEAK: 0,
            SignalStrength.WEAK: 1,
            SignalStrength.MODERATE: 2,
            SignalStrength.STRONG: 3,
            SignalStrength.VERY_STRONG: 4,
        }
        if strength_order[signal.strength] < strength_order[self.min_strength]:
            return False
        
        # Check age
        age_seconds = (datetime.now(timezone.utc) - signal.timestamp).total_seconds()
        if age_seconds > self.max_age_seconds:
            return False
        
        return True


def create_intelligence_signal(
    intelligence_type: IntelligenceType,
    source: IntelligenceSource,
    instrument_id: str,
    strength: SignalStrength,
    confidence: SignalConfidence,
    direction: str,
    value: float,
    expires_at: Optional[datetime] = None,
) -> IntelligenceSignal:
    """Create a new intelligence signal."""
    return IntelligenceSignal(
        signal_id=str(uuid4()),
        intelligence_type=intelligence_type,
        source=source,
        instrument_id=instrument_id,
        strength=strength,
        confidence=confidence,
        direction=direction,
        timestamp=datetime.now(timezone.utc),
        value=value,
        expires_at=expires_at,
    )


def create_intelligence_contract(
    contract_name: str,
    intelligence_type: IntelligenceType,
    source: IntelligenceSource,
    quality_requirement: IntelligenceQuality = IntelligenceQuality.HIGH,
    min_confidence: SignalConfidence = SignalConfidence.MEDIUM,
    min_strength: SignalStrength = SignalStrength.MODERATE,
) -> IntelligenceContract:
    """Create a new intelligence contract."""
    return IntelligenceContract(
        contract_id=str(uuid4()),
        contract_name=contract_name,
        intelligence_type=intelligence_type,
        source=source,
        quality_requirement=quality_requirement,
        min_confidence=min_confidence,
        min_strength=min_strength,
    )
