"""
GLX FORGE Operations Contracts

This module defines the operations contracts for the GLX FORGE trading infrastructure.
Operations contracts define the structure and configuration of operational activities.

Version: 0.1.0
Phase: Phase 11 - Sovereign Operations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4


class OperationType(Enum):
    """Operation type enumeration."""
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    MAINTENANCE = "maintenance"
    BACKUP = "backup"
    AUDIT = "audit"
    RECOVERY = "recovery"
    CUSTOM = "custom"


class OperationStatus(Enum):
    """Operation status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OperationConfig:
    """Operation configuration contract."""
    config_id: str
    operation_type: OperationType
    timeout_seconds: int = 3600
    retry_attempts: int = 3
    auto_retry: bool = True
    notification_on_success: bool = True
    notification_on_failure: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.config_id, str) or not self.config_id:
            raise ValueError("Config ID cannot be empty")
        if not isinstance(self.operation_type, OperationType):
            raise ValueError("Operation type must be OperationType enum")
        if not isinstance(self.timeout_seconds, int) or self.timeout_seconds < 1:
            raise ValueError(f"Timeout must be >= 1, got {self.timeout_seconds}")


@dataclass
class OperationLog:
    """Operation log contract."""
    log_id: str
    operation_id: str
    level: str  # "INFO", "WARNING", "ERROR", "DEBUG"
    message: str
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.log_id, str) or not self.log_id:
            self.log_id = str(uuid4())
        if not isinstance(self.operation_id, str) or not self.operation_id:
            raise ValueError("Operation ID cannot be empty")
        if not isinstance(self.level, str) or not self.level:
            raise ValueError("Level cannot be empty")
        if self.level not in ["INFO", "WARNING", "ERROR", "DEBUG"]:
            raise ValueError(f"Level must be one of INFO, WARNING, ERROR, DEBUG, got {self.level}")


@dataclass
class OperationsContract:
    """Operations contract contract."""
    contract_id: str
    contract_name: str
    operation_type: OperationType
    config: OperationConfig
    status: OperationStatus
    logs: List[OperationLog] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.contract_id, str) or not self.contract_id:
            self.contract_id = str(uuid4())
        if not isinstance(self.contract_name, str) or not self.contract_name:
            raise ValueError("Contract name cannot be empty")
        if not isinstance(self.operation_type, OperationType):
            raise ValueError("Operation type must be OperationType enum")
        if not isinstance(self.config, OperationConfig):
            raise ValueError("Config must be an OperationConfig instance")
        if not isinstance(self.status, OperationStatus):
            raise ValueError("Status must be OperationStatus enum")
    
    @property
    def is_running(self) -> bool:
        """Check if operation is running."""
        return self.status == OperationStatus.RUNNING
    
    @property
    def is_terminal(self) -> bool:
        """Check if operation is in terminal state."""
        return self.status in [OperationStatus.COMPLETED, OperationStatus.FAILED, OperationStatus.CANCELLED]
    
    @property
    def duration(self) -> Optional[float]:
        """Get operation duration in seconds."""
        if self.started_at is None:
            return None
        end_time = self.completed_at or datetime.now(timezone.utc)
        return (end_time - self.started_at).total_seconds()
    
    def start(self) -> None:
        """Start the operation."""
        self.status = OperationStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)
        self.add_log("INFO", "Operation started")
    
    def complete(self) -> None:
        """Complete the operation."""
        self.status = OperationStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.add_log("INFO", "Operation completed")
    
    def fail(self, error: str) -> None:
        """Fail the operation."""
        self.status = OperationStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.error = error
        self.add_log("ERROR", f"Operation failed: {error}")
    
    def cancel(self) -> None:
        """Cancel the operation."""
        self.status = OperationStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)
        self.add_log("INFO", "Operation cancelled")
    
    def add_log(self, level: str, message: str, metadata: Optional[Dict] = None) -> None:
        """Add a log entry."""
        log = OperationLog(
            log_id=str(uuid4()),
            operation_id=self.contract_id,
            level=level,
            message=message,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
        )
        self.logs.append(log)
    
    def get_logs_by_level(self, level: str) -> List[OperationLog]:
        """Get logs by level."""
        return [log for log in self.logs if log.level == level]
    
    @property
    def log_count(self) -> int:
        """Get the number of logs."""
        return len(self.logs)


def create_operation_config(
    operation_type: OperationType,
    timeout_seconds: int = 3600,
) -> OperationConfig:
    """Create a new operation configuration."""
    return OperationConfig(
        config_id=str(uuid4()),
        operation_type=operation_type,
        timeout_seconds=timeout_seconds,
    )


def create_operations_contract(
    contract_name: str,
    operation_type: OperationType,
    config: OperationConfig,
) -> OperationsContract:
    """Create a new operations contract."""
    return OperationsContract(
        contract_id=str(uuid4()),
        contract_name=contract_name,
        operation_type=operation_type,
        config=config,
        status=OperationStatus.PENDING,
    )
