"""
GLX FORGE Runtime Control Plane

This module defines the control plane for the GLX FORGE trading infrastructure.
The control plane manages service lifecycle and orchestration.

Version: 0.1.0
Phase: Phase 2 - Runtime Foundry
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4

from forge.runtime.service import Service, ServiceStatus
from forge.runtime.topology import ServiceTopology


class ControlCommandType(Enum):
    """Control command type enumeration."""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    SCALE = "scale"
    DEPLOY = "deploy"
    UNDEPLOY = "undeploy"
    HEALTH_CHECK = "health_check"
    STATUS = "status"


class ControlCommandStatus(Enum):
    """Control command status enumeration."""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ControlCommand:
    """Control command contract."""
    command_id: str
    command_type: ControlCommandType
    target_service_id: str
    status: ControlCommandStatus
    created_at: datetime
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parameters: Dict = field(default_factory=dict)
    result: Optional[Dict] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.command_id, str) or not self.command_id:
            self.command_id = str(uuid4())
        if not isinstance(self.command_type, ControlCommandType):
            raise ValueError("Command type must be ControlCommandType enum")
        if not isinstance(self.target_service_id, str) or not self.target_service_id:
            raise ValueError("Target service ID cannot be empty")
        if not isinstance(self.status, ControlCommandStatus):
            raise ValueError("Status must be ControlCommandStatus enum")
    
    @property
    def is_pending(self) -> bool:
        """Check if command is pending."""
        return self.status == ControlCommandStatus.PENDING
    
    @property
    def is_executing(self) -> bool:
        """Check if command is executing."""
        return self.status == ControlCommandStatus.EXECUTING
    
    @property
    def is_succeeded(self) -> bool:
        """Check if command succeeded."""
        return self.status == ControlCommandStatus.SUCCEEDED
    
    @property
    def is_failed(self) -> bool:
        """Check if command failed."""
        return self.status == ControlCommandStatus.FAILED
    
    def mark_executing(self) -> None:
        """Mark command as executing."""
        self.status = ControlCommandStatus.EXECUTING
        self.executed_at = datetime.now(timezone.utc)
    
    def mark_succeeded(self, result: Optional[Dict] = None) -> None:
        """Mark command as succeeded."""
        self.status = ControlCommandStatus.SUCCEEDED
        self.completed_at = datetime.now(timezone.utc)
        self.result = result
    
    def mark_failed(self, error: str) -> None:
        """Mark command as failed."""
        self.status = ControlCommandStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.error = error
    
    def mark_cancelled(self) -> None:
        """Mark command as cancelled."""
        self.status = ControlCommandStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)


@dataclass
class ControlPlane:
    """Control plane contract."""
    control_plane_id: str
    topology: ServiceTopology
    services: Dict[str, Service] = field(default_factory=dict)
    commands: Dict[str, ControlCommand] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.control_plane_id, str) or not self.control_plane_id:
            self.control_plane_id = str(uuid4())
        if not isinstance(self.topology, ServiceTopology):
            raise ValueError("Topology must be a ServiceTopology instance")
    
    def register_service(self, service: Service) -> None:
        """Register a service with the control plane."""
        self.services[service.service_id] = service
        self.updated_at = datetime.now(timezone.utc)
    
    def unregister_service(self, service_id: str) -> None:
        """Unregister a service from the control plane."""
        if service_id in self.services:
            del self.services[service_id]
            self.updated_at = datetime.now(timezone.utc)
    
    def get_service(self, service_id: str) -> Optional[Service]:
        """Get a service by ID."""
        return self.services.get(service_id)
    
    def get_all_services(self) -> List[Service]:
        """Get all registered services."""
        return list(self.services.values())
    
    def get_services_by_type(self, service_type) -> List[Service]:
        """Get services by type."""
        return [
            service for service in self.services.values()
            if service.service_type == service_type
        ]
    
    def get_running_services(self) -> List[Service]:
        """Get all running services."""
        return [
            service for service in self.services.values()
            if service.is_running
        ]
    
    def get_stopped_services(self) -> List[Service]:
        """Get all stopped services."""
        return [
            service for service in self.services.values()
            if service.is_stopped
        ]
    
    def submit_command(self, command: ControlCommand) -> None:
        """Submit a control command for execution."""
        self.commands[command.command_id] = command
        self.updated_at = datetime.now(timezone.utc)
    
    def get_command(self, command_id: str) -> Optional[ControlCommand]:
        """Get a command by ID."""
        return self.commands.get(command_id)
    
    def get_pending_commands(self) -> List[ControlCommand]:
        """Get all pending commands."""
        return [
            command for command in self.commands.values()
            if command.is_pending
        ]
    
    def get_executing_commands(self) -> List[ControlCommand]:
        """Get all executing commands."""
        return [
            command for command in self.commands.values()
            if command.is_executing
        ]
    
    def execute_command(self, command: ControlCommand) -> None:
        """Execute a control command."""
        command.mark_executing()
        
        service = self.get_service(command.target_service_id)
        if service is None:
            command.mark_failed(f"Service not found: {command.target_service_id}")
            return
        
        try:
            if command.command_type == ControlCommandType.START:
                service.start()
                service.mark_running()
                command.mark_succeeded({"status": "running"})
            elif command.command_type == ControlCommandType.STOP:
                service.stop()
                service.mark_stopped()
                command.mark_succeeded({"status": "stopped"})
            elif command.command_type == ControlCommandType.RESTART:
                service.stop()
                service.mark_stopped()
                service.start()
                service.mark_running()
                command.mark_succeeded({"status": "running"})
            elif command.command_type == ControlCommandType.HEALTH_CHECK:
                health = {
                    "status": service.health.status.value,
                    "healthy": service.health.is_healthy,
                    "uptime": service.uptime,
                }
                command.mark_succeeded(health)
            elif command.command_type == ControlCommandType.STATUS:
                status = {
                    "service_id": service.service_id,
                    "name": service.name,
                    "status": service.health.status.value,
                    "uptime": service.uptime,
                    "endpoint": service.config.endpoint,
                }
                command.mark_succeeded(status)
            else:
                command.mark_failed(f"Command type not implemented: {command.command_type}")
        except Exception as e:
            command.mark_failed(str(e))
        
        self.updated_at = datetime.now(timezone.utc)
    
    @property
    def service_count(self) -> int:
        """Get the number of registered services."""
        return len(self.services)
    
    @property
    def command_count(self) -> int:
        """Get the number of commands."""
        return len(self.commands)


def create_control_plane(topology: ServiceTopology) -> ControlPlane:
    """Create a new control plane."""
    return ControlPlane(
        control_plane_id=str(uuid4()),
        topology=topology,
    )


def create_start_command(service_id: str) -> ControlCommand:
    """Create a start command."""
    return ControlCommand(
        command_id=str(uuid4()),
        command_type=ControlCommandType.START,
        target_service_id=service_id,
        status=ControlCommandStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )


def create_stop_command(service_id: str) -> ControlCommand:
    """Create a stop command."""
    return ControlCommand(
        command_id=str(uuid4()),
        command_type=ControlCommandType.STOP,
        target_service_id=service_id,
        status=ControlCommandStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )


def create_restart_command(service_id: str) -> ControlCommand:
    """Create a restart command."""
    return ControlCommand(
        command_id=str(uuid4()),
        command_type=ControlCommandType.RESTART,
        target_service_id=service_id,
        status=ControlCommandStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )


def create_health_check_command(service_id: str) -> ControlCommand:
    """Create a health check command."""
    return ControlCommand(
        command_id=str(uuid4()),
        command_type=ControlCommandType.HEALTH_CHECK,
        target_service_id=service_id,
        status=ControlCommandStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )
