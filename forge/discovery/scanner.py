"""
GLX FORGE Discovery Scanner

This module defines the scanner system for the GLX FORGE trading infrastructure.
Scanners scan markets for opportunities, patterns, and anomalies.

Version: 0.1.0
Phase: Phase 5 - Discovery Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Callable, Any
from uuid import UUID, uuid4

from forge.discovery.contracts import DiscoveryResult, DiscoveryType, DiscoverySource


class ScannerType(Enum):
    """Scanner type enumeration."""
    OPPORTUNITY = "opportunity"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    ARBITRAGE = "arbitrage"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    CUSTOM = "custom"


class ScannerState(Enum):
    """Scanner state enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    SCANNING = "scanning"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ScannerConfig:
    """Scanner configuration contract."""
    scanner_id: str
    scanner_type: ScannerType
    instrument_ids: List[str]
    parameters: Dict = field(default_factory=dict)
    scan_interval_seconds: int = 60
    max_results: int = 100
    enabled: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.scanner_id, str) or not self.scanner_id:
            raise ValueError("Scanner ID cannot be empty")
        if not isinstance(self.scanner_type, ScannerType):
            raise ValueError("Scanner type must be ScannerType enum")
        if not isinstance(self.instrument_ids, list):
            raise ValueError("Instrument IDs must be a list")
        if not isinstance(self.scan_interval_seconds, int) or self.scan_interval_seconds < 1:
            raise ValueError(f"Scan interval must be >= 1, got {self.scan_interval_seconds}")


@dataclass
class ScanRequest:
    """Scan request contract."""
    request_id: str
    scanner_id: str
    instrument_ids: List[str]
    parameters: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.request_id, str) or not self.request_id:
            self.request_id = str(uuid4())
        if not isinstance(self.scanner_id, str) or not self.scanner_id:
            raise ValueError("Scanner ID cannot be empty")
        if not isinstance(self.instrument_ids, list):
            raise ValueError("Instrument IDs must be a list")
    
    @property
    def is_running(self) -> bool:
        """Check if scan is running."""
        return self.started_at is not None and self.completed_at is None
    
    @property
    def is_completed(self) -> bool:
        """Check if scan is completed."""
        return self.completed_at is not None
    
    @property
    def duration(self) -> Optional[float]:
        """Get scan duration in seconds."""
        if self.started_at is None:
            return None
        end_time = self.completed_at or datetime.now(timezone.utc)
        return (end_time - self.started_at).total_seconds()


@dataclass
class ScanResult:
    """Scan result contract."""
    result_id: str
    request_id: str
    scanner_id: str
    discoveries: List[DiscoveryResult] = field(default_factory=list)
    scanned_count: int = 0
    discovered_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.result_id, str) or not self.result_id:
            self.result_id = str(uuid4())
        if not isinstance(self.request_id, str) or not self.request_id:
            raise ValueError("Request ID cannot be empty")
        if not isinstance(self.scanner_id, str) or not self.scanner_id:
            raise ValueError("Scanner ID cannot be empty")
    
    @property
    def has_discoveries(self) -> bool:
        """Check if scan found discoveries."""
        return self.discovered_count > 0
    
    @property
    def discovery_rate(self) -> float:
        """Get discovery rate (discoveries / scanned)."""
        if self.scanned_count == 0:
            return 0.0
        return self.discovered_count / self.scanned_count


@dataclass
class Scanner:
    """Scanner contract."""
    scanner_id: str
    name: str
    scanner_type: ScannerType
    config: ScannerConfig
    state: ScannerState
    results: List[ScanResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.scanner_id, str) or not self.scanner_id:
            raise ValueError("Scanner ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.scanner_type, ScannerType):
            raise ValueError("Scanner type must be ScannerType enum")
        if not isinstance(self.config, ScannerConfig):
            raise ValueError("Config must be a ScannerConfig instance")
        if not isinstance(self.state, ScannerState):
            raise ValueError("State must be ScannerState enum")
    
    @property
    def is_scanning(self) -> bool:
        """Check if scanner is scanning."""
        return self.state == ScannerState.SCANNING
    
    @property
    def is_stopped(self) -> bool:
        """Check if scanner is stopped."""
        return self.state == ScannerState.STOPPED
    
    @property
    def is_error(self) -> bool:
        """Check if scanner is in error state."""
        return self.state == ScannerState.ERROR
    
    @property
    def result_count(self) -> int:
        """Get the number of scan results."""
        return len(self.results)
    
    @property
    def total_discoveries(self) -> int:
        """Get the total number of discoveries."""
        return sum(result.discovered_count for result in self.results)
    
    @property
    def uptime(self) -> Optional[float]:
        """Get scanner uptime in seconds."""
        if self.started_at is None:
            return None
        if self.stopped_at is not None:
            return (self.stopped_at - self.started_at).total_seconds()
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()
    
    def start(self) -> None:
        """Start the scanner."""
        self.state = ScannerState.STARTING
        self.started_at = datetime.now(timezone.utc)
        self.state = ScannerState.SCANNING
    
    def stop(self) -> None:
        """Stop the scanner."""
        self.state = ScannerState.STOPPED
        self.stopped_at = datetime.now(timezone.utc)
    
    def pause(self) -> None:
        """Pause the scanner."""
        self.state = ScannerState.PAUSED
    
    def resume(self) -> None:
        """Resume the scanner."""
        self.state = ScannerState.SCANNING
    
    def mark_error(self, error: str) -> None:
        """Mark scanner as in error state."""
        self.error_count += 1
        self.last_error = error
        self.state = ScannerState.ERROR
    
    def add_result(self, result: ScanResult) -> None:
        """Add a scan result to the scanner."""
        self.results.append(result)
    
    def get_recent_results(self, limit: int = 100) -> List[ScanResult]:
        """Get recent scan results."""
        return self.results[-limit:]
    
    def get_results_with_discoveries(self) -> List[ScanResult]:
        """Get results that found discoveries."""
        return [result for result in self.results if result.has_discoveries]


# Default scanners for common discovery types
DEFAULT_SCANNERS = {
    "opportunity": Scanner(
        scanner_id="scanner-opportunity",
        name="Opportunity Scanner",
        scanner_type=ScannerType.OPPORTUNITY,
        config=ScannerConfig(
            scanner_id="scanner-opportunity",
            scanner_type=ScannerType.OPPORTUNITY,
            instrument_ids=["BTCUSDT", "ETHUSDT"],
            parameters={"min_profit_potential": 0.02, "max_risk": 0.01},
            scan_interval_seconds=60,
        ),
        state=ScannerState.STOPPED,
    ),
    
    "pattern": Scanner(
        scanner_id="scanner-pattern",
        name="Pattern Scanner",
        scanner_type=ScannerType.PATTERN,
        config=ScannerConfig(
            scanner_id="scanner-pattern",
            scanner_type=ScannerType.PATTERN,
            instrument_ids=["BTCUSDT", "ETHUSDT"],
            parameters={"pattern_types": ["double_bottom", "head_shoulders"]},
            scan_interval_seconds=300,
        ),
        state=ScannerState.STOPPED,
    ),
    
    "anomaly": Scanner(
        scanner_id="scanner-anomaly",
        name="Anomaly Scanner",
        scanner_type=ScannerType.ANOMALY,
        config=ScannerConfig(
            scanner_id="scanner-anomaly",
            scanner_type=ScannerType.ANOMALY,
            instrument_ids=["BTCUSDT", "ETHUSDT"],
            parameters={"z_score_threshold": 3.0, "window": 100},
            scan_interval_seconds=60,
        ),
        state=ScannerState.STOPPED,
    ),
    
    "correlation": Scanner(
        scanner_id="scanner-correlation",
        name="Correlation Scanner",
        scanner_type=ScannerType.CORRELATION,
        config=ScannerConfig(
            scanner_id="scanner-correlation",
            scanner_type=ScannerType.CORRELATION,
            instrument_ids=["BTCUSDT", "ETHUSDT"],
            parameters={"min_correlation": 0.8, "window": 100},
            scan_interval_seconds=300,
        ),
        state=ScannerState.STOPPED,
    ),
    
    "arbitrage": Scanner(
        scanner_id="scanner-arbitrage",
        name="Arbitrage Scanner",
        scanner_type=ScannerType.ARBITRAGE,
        config=ScannerConfig(
            scanner_id="scanner-arbitrage",
            scanner_type=ScannerType.ARBITRAGE,
            instrument_ids=["BTCUSDT", "ETHUSDT"],
            parameters={"min_spread": 0.005, "exchanges": ["binance", "coinbase"]},
            scan_interval_seconds=10,
        ),
        state=ScannerState.STOPPED,
    ),
}


def create_scanner(
    scanner_id: str,
    name: str,
    scanner_type: ScannerType,
    instrument_ids: List[str],
    parameters: Optional[Dict] = None,
    config: Optional[ScannerConfig] = None,
) -> Scanner:
    """Create a new scanner."""
    if config is None:
        config = ScannerConfig(
            scanner_id=scanner_id,
            scanner_type=scanner_type,
            instrument_ids=instrument_ids,
            parameters=parameters or {},
        )
    
    return Scanner(
        scanner_id=scanner_id,
        name=name,
        scanner_type=scanner_type,
        config=config,
        state=ScannerState.STOPPED,
    )


def create_scan_request(
    scanner_id: str,
    instrument_ids: List[str],
    parameters: Optional[Dict] = None,
) -> ScanRequest:
    """Create a new scan request."""
    return ScanRequest(
        request_id=str(uuid4()),
        scanner_id=scanner_id,
        instrument_ids=instrument_ids,
        parameters=parameters or {},
    )


def create_scan_result(
    request_id: str,
    scanner_id: str,
    discoveries: Optional[List[DiscoveryResult]] = None,
) -> ScanResult:
    """Create a new scan result."""
    return ScanResult(
        result_id=str(uuid4()),
        request_id=request_id,
        scanner_id=scanner_id,
        discoveries=discoveries or [],
        discovered_count=len(discoveries or []),
    )
