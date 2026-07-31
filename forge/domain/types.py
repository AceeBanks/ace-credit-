"""
GLX FORGE Domain Types

This module defines the foundational type system for the GLX FORGE trading infrastructure.
All types are strongly typed and validated using Python's type hints and runtime checks.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import NewType, Union
from uuid import UUID, uuid4


# Primitive types with NewType for type safety
Price = NewType("Price", float)
Quantity = NewType("Quantity", float)
Timestamp = NewType("Timestamp", datetime)
Symbol = NewType("Symbol", str)
InstrumentId = NewType("InstrumentId", str)
OrderId = NewType("OrderId", str)
PositionId = NewType("PositionId", str)
TradeId = NewType("TradeId", str)
AccountId = NewType("AccountId", str)
StrategyId = NewType("StrategyId", str)
PortfolioId = NewType("PortfolioId", str)


class ValidationError(Exception):
    """Raised when domain type validation fails."""
    pass


def validate_price(value: float) -> Price:
    """Validate and construct a Price type."""
    if not isinstance(value, (int, float)):
        raise ValidationError(f"Price must be numeric, got {type(value)}")
    if value < 0:
        raise ValidationError(f"Price must be non-negative, got {value}")
    return Price(float(value))


def validate_quantity(value: float) -> Quantity:
    """Validate and construct a Quantity type."""
    if not isinstance(value, (int, float)):
        raise ValidationError(f"Quantity must be numeric, got {type(value)}")
    if value < 0:
        raise ValidationError(f"Quantity must be non-negative, got {value}")
    return Quantity(float(value))


def validate_timestamp(value: Union[datetime, int, str]) -> Timestamp:
    """Validate and construct a Timestamp type."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return Timestamp(value)
    elif isinstance(value, (int, float)):
        return Timestamp(datetime.fromtimestamp(value, tz=timezone.utc))
    elif isinstance(value, str):
        try:
            return Timestamp(datetime.fromisoformat(value))
        except ValueError:
            raise ValidationError(f"Invalid timestamp string: {value}")
    else:
        raise ValidationError(f"Timestamp must be datetime, int, or str, got {type(value)}")


def validate_symbol(value: str) -> Symbol:
    """Validate and construct a Symbol type."""
    if not isinstance(value, str):
        raise ValidationError(f"Symbol must be string, got {type(value)}")
    if not value or not value.strip():
        raise ValidationError("Symbol cannot be empty")
    return Symbol(value.strip().upper())


def generate_order_id() -> OrderId:
    """Generate a unique OrderId."""
    return OrderId(str(uuid4()))


def generate_position_id() -> PositionId:
    """Generate a unique PositionId."""
    return PositionId(str(uuid4()))


def generate_trade_id() -> TradeId:
    """Generate a unique TradeId."""
    return TradeId(str(uuid4()))


@dataclass(frozen=True)
class Money:
    """Represents a monetary amount with currency."""
    amount: float
    currency: str  # ISO 4217 currency code (e.g., USD, EUR)
    
    def __post_init__(self):
        if not isinstance(self.amount, (int, float)):
            raise ValidationError(f"Money amount must be numeric, got {type(self.amount)}")
        if self.amount < 0:
            raise ValidationError(f"Money amount must be non-negative, got {self.amount}")
        if not isinstance(self.currency, str) or len(self.currency) != 3:
            raise ValidationError(f"Currency must be 3-letter ISO code, got {self.currency}")
    
    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValidationError(f"Cannot add Money with different currencies: {self.currency} vs {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValidationError(f"Cannot subtract Money with different currencies: {self.currency} vs {other.currency}")
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, factor: float) -> Money:
        return Money(self.amount * factor, self.currency)
    
    def __truediv__(self, factor: float) -> Money:
        return Money(self.amount / factor, self.currency)


@dataclass(frozen=True)
class Percentage:
    """Represents a percentage value."""
    value: float  # 0.0 to 1.0
    
    def __post_init__(self):
        if not isinstance(self.value, (int, float)):
            raise ValidationError(f"Percentage must be numeric, got {type(self.value)}")
        if not 0.0 <= self.value <= 1.0:
            raise ValidationError(f"Percentage must be between 0.0 and 1.0, got {self.value}")
    
    @classmethod
    def from_basis_points(cls, basis_points: int) -> Percentage:
        """Create a Percentage from basis points (1/100 of 1%)."""
        return cls(basis_points / 10000.0)
    
    @classmethod
    def from_percent(cls, percent: float) -> Percentage:
        """Create a Percentage from percent (e.g., 50.0 for 50%)."""
        return cls(percent / 100.0)
    
    def to_percent(self) -> float:
        """Convert to percent (e.g., 0.5 to 50.0)."""
        return self.value * 100.0
    
    def to_basis_points(self) -> int:
        """Convert to basis points (e.g., 0.01 to 100)."""
        return int(self.value * 10000)
