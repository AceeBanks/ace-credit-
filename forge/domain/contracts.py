"""
GLX FORGE Domain Contracts

This module defines the foundational contracts for the GLX FORGE trading infrastructure.
Contracts are immutable domain objects that define the core business entities.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from forge.domain.types import (
    Symbol,
    InstrumentId,
    ValidationError,
)


class AssetClass(Enum):
    """Asset class enumeration."""
    EQUITY = "equity"
    FOREX = "forex"
    CRYPTO = "crypto"
    COMMODITY = "commodity"
    BOND = "bond"
    INDEX = "index"
    OPTION = "option"
    FUTURE = "future"
    SPOT = "spot"


class InstrumentType(Enum):
    """Instrument type enumeration."""
    SPOT = "spot"
    PERPETUAL = "perpetual"
    FUTURE = "future"
    OPTION = "option"
    SWAP = "swap"


class Side(Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    LIMIT_MAKER = "limit_maker"
    LIMIT_TAKER = "limit_taker"


class TimeInForce(Enum):
    """Time in force enumeration."""
    GTC = "gtc"  # Good Till Cancelled
    IOC = "ioc"  # Immediate Or Cancel
    FOK = "fok"  # Fill Or Kill
    GTD = "gtd"  # Good Till Date


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING_NEW = "pending_new"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WORKING = "working"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PositionSide(Enum):
    """Position side enumeration."""
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


@dataclass(frozen=True)
class Currency:
    """Currency contract."""
    code: str  # ISO 4217 currency code (e.g., USD, EUR)
    name: str  # Full name (e.g., United States Dollar)
    symbol: str  # Currency symbol (e.g., $, €)
    precision: int  # Decimal precision (e.g., 2 for USD)
    
    def __post_init__(self):
        if not isinstance(self.code, str) or len(self.code) != 3:
            raise ValidationError(f"Currency code must be 3-letter ISO code, got {self.code}")
        if not self.code.isalpha() or not self.code.isupper():
            raise ValidationError(f"Currency code must be uppercase letters, got {self.code}")
        if not isinstance(self.name, str) or not self.name:
            raise ValidationError("Currency name cannot be empty")
        if not isinstance(self.symbol, str) or not self.symbol:
            raise ValidationError("Currency symbol cannot be empty")
        if not isinstance(self.precision, int) or self.precision < 0 or self.precision > 18:
            raise ValidationError(f"Currency precision must be 0-18, got {self.precision}")
    
    @classmethod
    def usd(cls) -> Currency:
        """USD currency."""
        return cls(code="USD", name="United States Dollar", symbol="$", precision=2)
    
    @classmethod
    def eur(cls) -> Currency:
        """EUR currency."""
        return cls(code="EUR", name="Euro", symbol="€", precision=2)
    
    @classmethod
    def gbp(cls) -> Currency:
        """GBP currency."""
        return cls(code="GBP", name="British Pound", symbol="£", precision=2)
    
    @classmethod
    def jpy(cls) -> Currency:
        """JPY currency."""
        return cls(code="JPY", name="Japanese Yen", symbol="¥", precision=0)


@dataclass(frozen=True)
class Exchange:
    """Exchange contract."""
    id: str
    name: str
    venue: str  # Exchange venue (e.g., NYSE, NASDAQ)
    country: str  # ISO 3166-1 alpha-2 country code (e.g., US, GB)
    currency: Currency
    
    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id:
            raise ValidationError("Exchange ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValidationError("Exchange name cannot be empty")
        if not isinstance(self.venue, str) or not self.venue:
            raise ValidationError("Exchange venue cannot be empty")
        if not isinstance(self.country, str) or len(self.country) != 2:
            raise ValidationError(f"Country must be 2-letter ISO code, got {self.country}")
        if not isinstance(self.currency, Currency):
            raise ValidationError("Currency must be a Currency instance")
    
    @classmethod
    def nyse(cls) -> Exchange:
        """New York Stock Exchange."""
        return cls(
            id="NYSE",
            name="New York Stock Exchange",
            venue="NYSE",
            country="US",
            currency=Currency.usd(),
        )
    
    @classmethod
    def nasdaq(cls) -> Exchange:
        """NASDAQ."""
        return cls(
            id="NASDAQ",
            name="NASDAQ",
            venue="NASDAQ",
            country="US",
            currency=Currency.usd(),
        )
    
    @classmethod
    def binance(cls) -> Exchange:
        """Binance."""
        return cls(
            id="BINANCE",
            name="Binance",
            venue="BINANCE",
            country="MT",  # Malta
            currency=Currency.usd(),
        )


@dataclass(frozen=True)
class Asset:
    """Asset contract."""
    id: str
    symbol: Symbol
    name: str
    asset_class: AssetClass
    base_currency: Optional[Currency] = None
    quote_currency: Optional[Currency] = None
    
    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id:
            raise ValidationError("Asset ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValidationError("Asset name cannot be empty")
        if not isinstance(self.asset_class, AssetClass):
            raise ValidationError("Asset class must be an AssetClass enum")
        if self.base_currency is not None and not isinstance(self.base_currency, Currency):
            raise ValidationError("Base currency must be a Currency instance")
        if self.quote_currency is not None and not isinstance(self.quote_currency, Currency):
            raise ValidationError("Quote currency must be a Currency instance")


@dataclass(frozen=True)
class Instrument:
    """Instrument contract."""
    id: InstrumentId
    symbol: Symbol
    name: str
    asset_class: AssetClass
    instrument_type: InstrumentType
    exchange: Exchange
    base_currency: Currency
    quote_currency: Currency
    price_precision: int = 2
    size_precision: int = 8
    min_quantity: float = 0.0
    max_quantity: float = float("inf")
    tick_size: float = 0.01
    lot_size: float = 1.0
    contract_size: float = 1.0
    is_tradable: bool = True
    
    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id:
            raise ValidationError("Instrument ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValidationError("Instrument name cannot be empty")
        if not isinstance(self.asset_class, AssetClass):
            raise ValidationError("Asset class must be an AssetClass enum")
        if not isinstance(self.instrument_type, InstrumentType):
            raise ValidationError("Instrument type must be an InstrumentType enum")
        if not isinstance(self.exchange, Exchange):
            raise ValidationError("Exchange must be an Exchange instance")
        if not isinstance(self.base_currency, Currency):
            raise ValidationError("Base currency must be a Currency instance")
        if not isinstance(self.quote_currency, Currency):
            raise ValidationError("Quote currency must be a Currency instance")
        if not isinstance(self.price_precision, int) or self.price_precision < 0 or self.price_precision > 18:
            raise ValidationError(f"Price precision must be 0-18, got {self.price_precision}")
        if not isinstance(self.size_precision, int) or self.size_precision < 0 or self.size_precision > 18:
            raise ValidationError(f"Size precision must be 0-18, got {self.size_precision}")
        if self.min_quantity < 0:
            raise ValidationError(f"Min quantity must be non-negative, got {self.min_quantity}")
        if self.max_quantity <= 0:
            raise ValidationError(f"Max quantity must be positive, got {self.max_quantity}")
        if self.tick_size <= 0:
            raise ValidationError(f"Tick size must be positive, got {self.tick_size}")
        if self.lot_size <= 0:
            raise ValidationError(f"Lot size must be positive, got {self.lot_size}")
        if self.contract_size <= 0:
            raise ValidationError(f"Contract size must be positive, got {self.contract_size}")
    
    @classmethod
    def btc_usdt(cls) -> Instrument:
        """BTC/USDT perpetual contract."""
        return cls(
            id=InstrumentId("BTCUSDT"),
            symbol=Symbol("BTCUSDT"),
            name="Bitcoin USDT Perpetual",
            asset_class=AssetClass.CRYPTO,
            instrument_type=InstrumentType.PERPETUAL,
            exchange=Exchange.binance(),
            base_currency=Currency.usd(),
            quote_currency=Currency.usd(),
            price_precision=2,
            size_precision=8,
            tick_size=0.01,
            lot_size=0.001,
        )
    
    @classmethod
    def spy(cls) -> Instrument:
        """SPY ETF."""
        return cls(
            id=InstrumentId("SPY"),
            symbol=Symbol("SPY"),
            name="SPDR S&P 500 ETF Trust",
            asset_class=AssetClass.EQUITY,
            instrument_type=InstrumentType.SPOT,
            exchange=Exchange.nyse(),
            base_currency=Currency.usd(),
            quote_currency=Currency.usd(),
            price_precision=2,
            size_precision=0,
            tick_size=0.01,
            lot_size=1.0,
        )
