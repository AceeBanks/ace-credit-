"""
GLX FORGE Operations Command Center

This module defines the command center for the GLX FORGE trading infrastructure.
Command center manages operational commands and responses.

Version: 0.1.0
Phase: Phase 11 - Sovereign Operations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Callable, Any
from uuid import UUID, uuid4


class CommandType(Enum):
    """Command type enumeration."""
    DEPLOY = "deploy"
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    SCALE = "scale"
    PAUSE = "pause"
    RESUME = "resume"
    STATUS = "status"
    HEALTH_CHECK = "health_check"
    CUSTOM = "custom"


class CommandStatus(Enum):
    """Command status enumeration."""
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CommandResponse:
    """Command response contract."""
    response_id: str
    command_id: str
    success: bool
    message: str
    data: Dict = field(default_factory=dict)
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_seconds: float = 0.0
    
    def __post_init__(self):
        if not isinstance(self.response_id, str) or not self.response_id:
            self.response_id = str(uuid4())
        if not isinstance(self.command_id, str) or not self.command_id:
            raise ValueError("Command ID cannot be empty")


@dataclass
class Command:
    """Command contract."""
    command_id: str
    command_type: CommandType
    target_id: str  # strategy_id, service_id, etc.
    parameters: Dict = field(default_factory=dict)
    status: CommandStatus = CommandStatus.QUEUED
    priority: int = 0  # Higher = higher priority
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    response: Optional[CommandResponse] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.command_id, str) or not self.command_id:
            self.command_id = str(uuid4())
        if not isinstance(self.target_id, str) or not self.target_id:
            raise ValueError("Target ID cannot be empty")
        if not isinstance(self.command_type, CommandType):
            raise ValueError("Command type must be CommandType enum")
        if not isinstance(self.status, CommandStatus):
            raise ValueError("Status must be CommandStatus enum")
    
    @property
    def is_executing(self) -> bool:
        """Check if command is executing."""
        return self.status == CommandStatus.EXECUTING
    
    @property
    def is_terminal(self) -> bool:
        """Check if command is in terminal state."""
        return self.status in [CommandStatus.COMPLETED, CommandStatus.FAILED, CommandStatus.CANCELLED]
    
    @property
    def duration(self) -> Optional[float]:
        """Get command duration in seconds."""
        if self.started_at is None:
            return None
        end_time = self.completed_at or datetime.now(timezone.utc)
        return (end_time - self.started_at).total_seconds()
    
    def execute(self, handler: Callable) -> CommandResponse:
        """Execute the command."""
        self.status = CommandStatus.EXECUTING
        self.started_at = datetime.now(timezone.utc)
        
        try:
            result = handler(self)
            
            response = CommandResponse(
                response_id=str(uuid4()),
                command_id=self.command_id,
                success=True,
                message="Command executed successfully",
                data=result if isinstance(result, dict) else {},
                execution_time_seconds=self.duration or 0.0,
            )
            
            self.status = CommandStatus.COMPLETED
            self.completed_at = datetime.now(timezone.utc)
            self.response = response
            
            return response
        except Exception as e:
            response = CommandResponse(
                response_id=str(uuid4()),
                command_id=self.command_id,
                success=False,
                message=f"Command failed: {str(e)}",
                execution_time_seconds=self.duration or 0.0,
            )
            
            self.status = CommandStatus.FAILED
            self.completed_at = datetime.now(timezone.utc)
            self.response = response
            self.error = str(e)
            
            return response
    
    def cancel(self) -> None:
        """Cancel the command."""
        self.status = CommandStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)


@dataclass
class CommandCenter:
    """Command center contract."""
    center_id: str
    name: str
    commands: Dict[str, Command] = field(default_factory=dict)
    command_queue: List[str] = field(default_factory=list)  # command_ids
    handlers: Dict[CommandType, Callable] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.center_id, str) or not self.center_id:
            raise ValueError("Center ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
    
    def register_handler(self, command_type: CommandType, handler: Callable) -> None:
        """Register a command handler."""
        self.handlers[command_type] = handler
    
    def submit_command(
        self,
        command_type: CommandType,
        target_id: str,
        parameters: Optional[Dict] = None,
        priority: int = 0,
    ) -> Command:
        """Submit a command to the queue."""
        command = Command(
            command_id=str(uuid4()),
            command_type=command_type,
            target_id=target_id,
            parameters=parameters or {},
            priority=priority,
        )
        
        self.commands[command.command_id] = command
        self.command_queue.append(command.command_id)
        
        # Sort queue by priority (higher first)
        self.command_queue.sort(
            key=lambda cid: self.commands[cid].priority,
            reverse=True
        )
        
        return command
    
    def execute_next(self) -> Optional[CommandResponse]:
        """Execute the next command in the queue."""
        if not self.command_queue:
            return None
        
        command_id = self.command_queue.pop(0)
        command = self.commands.get(command_id)
        
        if command is None:
            return None
        
        handler = self.handlers.get(command.command_type)
        if handler is None:
            command.status = CommandStatus.FAILED
            command.error = f"No handler registered for command type: {command.command_type}"
            return None
        
        return command.execute(handler)
    
    def execute_all(self) -> List[CommandResponse]:
        """Execute all commands in the queue."""
        responses = []
        while self.command_queue:
            response = self.execute_next()
            if response:
                responses.append(response)
        return responses
    
    def get_command(self, command_id: str) -> Optional[Command]:
        """Get a command by ID."""
        return self.commands.get(command_id)
    
    def get_commands_by_target(self, target_id: str) -> List[Command]:
        """Get all commands for a target."""
        return [c for c in self.commands.values() if c.target_id == target_id]
    
    def get_commands_by_status(self, status: CommandStatus) -> List[Command]:
        """Get all commands with a status."""
        return [c for c in self.commands.values() if c.status == status]
    
    @property
    def command_count(self) -> int:
        """Get the number of commands."""
        return len(self.commands)
    
    @property
    def queue_size(self) -> int:
        """Get the size of the command queue."""
        return len(self.command_queue)
    
    @property
    def success_rate(self) -> float:
        """Get command success rate."""
        terminal_commands = [c for c in self.commands.values() if c.is_terminal]
        if not terminal_commands:
            return 0.0
        successful = sum(1 for c in terminal_commands if c.status == CommandStatus.COMPLETED)
        return successful / len(terminal_commands)


def create_command_center(name: str) -> CommandCenter:
    """Create a new command center."""
    return CommandCenter(
        center_id=str(uuid4()),
        name=name,
    )


def create_command(
    command_type: CommandType,
    target_id: str,
    parameters: Optional[Dict] = None,
) -> Command:
    """Create a new command."""
    return Command(
        command_id=str(uuid4()),
        command_type=command_type,
        target_id=target_id,
        parameters=parameters or {},
    )
