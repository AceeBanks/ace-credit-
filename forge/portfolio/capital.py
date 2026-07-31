"""
GLX FORGE Portfolio Capital

This module defines the capital management for the GLX FORGE trading infrastructure.
Capital includes envelopes, allocations, and capital management.

Version: 0.1.0
Phase: Phase 10 - Portfolio Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4


class EnvelopeType(Enum):
    """Envelope type enumeration."""
    STRATEGY = "strategy"
    PORTFOLIO = "portfolio"
    RISK_LIMIT = "risk_limit"
    RESERVE = "reserve"
    CUSTOM = "custom"


class EnvelopeStatus(Enum):
    """Envelope status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    EXHAUSTED = "exhausted"
    CLOSED = "closed"


@dataclass
class CapitalEnvelope:
    """Capital envelope contract."""
    envelope_id: str
    name: str
    envelope_type: EnvelopeType
    total_capital: float
    allocated_capital: float = 0.0
    available_capital: float = 0.0
    status: EnvelopeStatus = EnvelopeStatus.ACTIVE
    max_drawdown_pct: float = 0.20
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.envelope_id, str) or not self.envelope_id:
            self.envelope_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.envelope_type, EnvelopeType):
            raise ValueError("Envelope type must be EnvelopeType enum")
        if not isinstance(self.total_capital, (int, float)):
            raise ValueError(f"Total capital must be numeric, got {type(self.total_capital)}")
        if self.total_capital <= 0:
            raise ValueError(f"Total capital must be positive, got {self.total_capital}")
    
    @property
    def utilization_pct(self) -> float:
        """Get capital utilization percentage."""
        if self.total_capital == 0:
            return 0.0
        return self.allocated_capital / self.total_capital
    
    @property
    def is_exhausted(self) -> bool:
        """Check if envelope is exhausted."""
        return self.available_capital <= 0 or self.status == EnvelopeStatus.EXHAUSTED
    
    @property
    def is_active(self) -> bool:
        """Check if envelope is active."""
        return self.status == EnvelopeStatus.ACTIVE
    
    def allocate(self, amount: float) -> bool:
        """Allocate capital from envelope."""
        if amount > self.available_capital:
            return False
        self.allocated_capital += amount
        self.available_capital -= amount
        self.updated_at = datetime.now(timezone.utc)
        return True
    
    def deallocate(self, amount: float) -> None:
        """Deallocate capital back to envelope."""
        self.allocated_capital -= amount
        self.available_capital += amount
        self.updated_at = datetime.now(timezone.utc)
    
    def pause(self) -> None:
        """Pause the envelope."""
        self.status = EnvelopeStatus.PAUSED
        self.updated_at = datetime.now(timezone.utc)
    
    def close(self) -> None:
        """Close the envelope."""
        self.status = EnvelopeStatus.CLOSED
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class CapitalAllocation:
    """Capital allocation contract."""
    allocation_id: str
    strategy_id: str
    envelope_id: str
    allocated_amount: float
    target_allocation_pct: float  # 0.0 to 1.0
    allocated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.allocation_id, str) or not self.allocation_id:
            self.allocation_id = str(uuid4())
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValueError("Strategy ID cannot be empty")
        if not isinstance(self.envelope_id, str) or not self.envelope_id:
            raise ValueError("Envelope ID cannot be empty")
        if not isinstance(self.allocated_amount, (int, float)):
            raise ValueError(f"Allocated amount must be numeric, got {type(self.allocated_amount)}")
        if self.allocated_amount < 0:
            raise ValueError(f"Allocated amount must be non-negative, got {self.allocated_amount}")
        if not isinstance(self.target_allocation_pct, (int, float)):
            raise ValueError(f"Target allocation must be numeric, got {type(self.target_allocation_pct)}")
        if not 0.0 <= self.target_allocation_pct <= 1.0:
            raise ValueError(f"Target allocation must be between 0.0 and 1.0, got {self.target_allocation_pct}")


@dataclass
class CapitalManager:
    """Capital manager contract."""
    manager_id: str
    name: str
    envelopes: Dict[str, CapitalEnvelope] = field(default_factory=dict)
    allocations: Dict[str, CapitalAllocation] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.manager_id, str) or not self.manager_id:
            raise ValueError("Manager ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
    
    def add_envelope(self, envelope: CapitalEnvelope) -> None:
        """Add a capital envelope."""
        self.envelopes[envelope.envelope_id] = envelope
    
    def remove_envelope(self, envelope_id: str) -> None:
        """Remove a capital envelope."""
        if envelope_id in self.envelopes:
            del self.envelopes[envelope_id]
    
    def get_envelope(self, envelope_id: str) -> Optional[CapitalEnvelope]:
        """Get an envelope by ID."""
        return self.envelopes.get(envelope_id)
    
    def allocate_capital(
        self,
        strategy_id: str,
        envelope_id: str,
        amount: float,
        target_allocation_pct: float = 0.0,
    ) -> Optional[CapitalAllocation]:
        """Allocate capital from an envelope to a strategy."""
        envelope = self.get_envelope(envelope_id)
        if envelope is None:
            return None
        
        if not envelope.allocate(amount):
            return None
        
        allocation = CapitalAllocation(
            allocation_id=str(uuid4()),
            strategy_id=strategy_id,
            envelope_id=envelope_id,
            allocated_amount=amount,
            target_allocation_pct=target_allocation_pct,
        )
        
        self.allocations[allocation.allocation_id] = allocation
        
        return allocation
    
    def deallocate_capital(self, allocation_id: str, amount: float) -> bool:
        """Deallocate capital back to envelope."""
        allocation = self.allocations.get(allocation_id)
        if allocation is None:
            return False
        
        envelope = self.get_envelope(allocation.envelope_id)
        if envelope is None:
            return False
        
        envelope.deallocate(amount)
        
        return True
    
    @property
    def total_capital(self) -> float:
        """Get total capital across all envelopes."""
        return sum(e.total_capital for e in self.envelopes.values())
    
    @property
    def available_capital(self) -> float:
        """Get total available capital across all envelopes."""
        return sum(e.available_capital for e in self.envelopes.values() if e.is_active)
    
    @property
    def envelope_count(self) -> int:
        """Get the number of envelopes."""
        return len(self.envelopes)
    
    @property
    def allocation_count(self) -> int:
        """Get the number of allocations."""
        return len(self.allocations)


def create_capital_envelope(
    name: str,
    envelope_type: EnvelopeType,
    total_capital: float,
) -> CapitalEnvelope:
    """Create a new capital envelope."""
    return CapitalEnvelope(
        envelope_id=str(uuid4()),
        name=name,
        envelope_type=envelope_type,
        total_capital=total_capital,
        available_capital=total_capital,
    )


def create_capital_manager(name: str) -> CapitalManager:
    """Create a new capital manager."""
    return CapitalManager(
        manager_id=str(uuid4()),
        name=name,
    )
