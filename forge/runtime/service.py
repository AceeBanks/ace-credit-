"""
GLX FORGE Runtime Service

This module defines the service contract for the GLX FORGE trading infrastructure.
Services are the fundamental units of the runtime fabric.

Version: 0.1.0
Phase: Phase 2 - Runtime Foundry
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


class ServiceType(Enum):
    """Service type enumeration."""
    DATA_PROVIDER = "data_provider"
    EXECUTION = "execution"
    BACKTEST = "backtest"
    RESEARCH = "research"
    CONTROL_PLANE = "control_plane"
    GATEWAY = "gateway"
    STORAGE = "storage"
    MONITORING = "monitoring"
    WORKER = "worker"


class ServiceStatus(Enum):
    """Service status enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    DEGRADED = "degraded"


@dataclass
class ServiceConfig:
    """Service configuration contract."""
    service_id: str
    service_type: ServiceType
    host: str
    port: int
    version: str = "0.1.0"
    max_workers: int = 1
    timeout_seconds: int = 30
    health_check_interval: int = 10
    log_level: str = "INFO"
    environment: str = "development"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.service_id, str) or not self.service_id:
            raise ValueError("Service ID cannot be empty")
        if not isinstance(self.service_type, ServiceType):
            raise ValueError("Service type must be ServiceType enum")
        if not isinstance(self.host, str) or not self.host:
            raise ValueError("Host cannot be empty")
        if not isinstance(self.port, int) or not 1 <= self.port <= 65535:
            raise ValueError(f"Port must be 1-65535, got {self.port}")
        if not isinstance(self.max_workers, int) or self.max_workers < 1:
            raise ValueError(f"Max workers must be >= 1, got {self.max_workers}")
        if not isinstance(self.timeout_seconds, int) or self.timeout_seconds < 1:
            raise ValueError(f"Timeout must be >= 1, got {self.timeout_seconds}")
    
    @property
    def endpoint(self) -> str:
        """Get service endpoint URL."""
        return f"{self.host}:{self.port}"


@dataclass
class ServiceHealth:
    """Service health contract."""
    service_id: str
    status: ServiceStatus
    uptime_seconds: float = 0.0
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.service_id, str) or not self.service_id:
            raise ValueError("Service ID cannot be empty")
        if not isinstance(self.status, ServiceStatus):
            raise ValueError("Status must be ServiceStatus enum")
    
    @property
    def is_healthy(self) -> bool:
        """Check if service is healthy."""
        return self.status in [ServiceStatus.RUNNING, ServiceStatus.STARTING]
    
    @property
    def is_degraded(self) -> bool:
        """Check if service is degraded."""
        return self.status == ServiceStatus.DEGRADED
    
    @property
    def is_error(self) -> bool:
        """Check if service is in error state."""
        return self.status == ServiceStatus.ERROR
    
    def record_error(self, error: str) -> None:
        """Record an error for this service."""
        self.error_count += 1
        self.last_error = error
        self.last_error_time = datetime.now(timezone.utc)
    
    def update_status(self, status: ServiceStatus) -> None:
        """Update service status."""
        self.status = status
        self.last_health_check = datetime.now(timezone.utc)


@dataclass
class Service:
    """Service contract."""
    service_id: str
    name: str
    service_type: ServiceType
    config: ServiceConfig
    health: ServiceHealth
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.service_id, str) or not self.service_id:
            raise ValueError("Service ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.service_type, ServiceType):
            raise ValueError("Service type must be ServiceType enum")
        if not isinstance(self.config, ServiceConfig):
            raise ValueError("Config must be a ServiceConfig instance")
        if not isinstance(self.health, ServiceHealth):
            raise ValueError("Health must be a ServiceHealth instance")
    
    @property
    def is_running(self) -> bool:
        """Check if service is running."""
        return self.health.status == ServiceStatus.RUNNING
    
    @property
    def is_stopped(self) -> bool:
        """Check if service is stopped."""
        return self.health.status == ServiceStatus.STOPPED
    
    @property
    def uptime(self) -> float:
        """Get service uptime in seconds."""
        if self.started_at is None:
            return 0.0
        if self.stopped_at is not None:
            return (self.stopped_at - self.started_at).total_seconds()
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()
    
    def start(self) -> None:
        """Start the service."""
        self.started_at = datetime.now(timezone.utc)
        self.stopped_at = None
        self.health.update_status(ServiceStatus.STARTING)
    
    def stop(self) -> None:
        """Stop the service."""
        self.stopped_at = datetime.now(timezone.utc)
        self.health.update_status(ServiceStatus.STOPPING)
    
    def mark_running(self) -> None:
        """Mark service as running."""
        self.health.update_status(ServiceStatus.RUNNING)
    
    def mark_stopped(self) -> None:
        """Mark service as stopped."""
        self.health.update_status(ServiceStatus.STOPPED)
    
    def mark_error(self, error: str) -> None:
        """Mark service as in error state."""
        self.health.record_error(error)
        self.health.update_status(ServiceStatus.ERROR)
    
    def mark_degraded(self) -> None:
        """Mark service as degraded."""
        self.health.update_status(ServiceStatus.DEGRADED)


# Default service configurations for common services
DEFAULT_SERVICE_CONFIGS = {
    "data_provider": ServiceConfig(
        service_id="service-data-provider",
        service_type=ServiceType.DATA_PROVIDER,
        host="localhost",
        port=8001,
        max_workers=4,
    ),
    "execution": ServiceConfig(
        service_id="service-execution",
        service_type=ServiceType.EXECUTION,
        host="localhost",
        port=8002,
        max_workers=2,
    ),
    "backtest": ServiceConfig(
        service_id="service-backtest",
        service_type=ServiceType.BACKTEST,
        host="localhost",
        port=8003,
        max_workers=4,
    ),
    "research": ServiceConfig(
        service_id="service-research",
        service_type=ServiceType.RESEARCH,
        host="localhost",
        port=8004,
        max_workers=2,
    ),
    "control_plane": ServiceConfig(
        service_id="service-control-plane",
        service_type=ServiceType.CONTROL_PLANE,
        host="localhost",
        port=8000,
        max_workers=1,
    ),
    "gateway": ServiceConfig(
        service_id="service-gateway",
        service_type=ServiceType.GATEWAY,
        host="localhost",
        port=8080,
        max_workers=4,
    ),
    "storage": ServiceConfig(
        service_id="service-storage",
        service_type=ServiceType.STORAGE,
        host="localhost",
        port=8005,
        max_workers=2,
    ),
    "monitoring": ServiceConfig(
        service_id="service-monitoring",
        service_type=ServiceType.MONITORING,
        host="localhost",
        port=8006,
        max_workers=1,
    ),
}


def create_service(service_id: str, name: str, service_type: ServiceType, config: Optional[ServiceConfig] = None) -> Service:
    """Create a new service."""
    if config is None:
        config = ServiceConfig(
            service_id=service_id,
            service_type=service_type,
            host="localhost",
            port=8000,
        )
    
    health = ServiceHealth(service_id=service_id, status=ServiceStatus.STOPPED)
    
    return Service(
        service_id=service_id,
        name=name,
        service_type=service_type,
        config=config,
        health=health,
    )
