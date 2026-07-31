"""
GLX FORGE Runtime Worker

This module defines the worker fabric for the GLX FORGE trading infrastructure.
Workers are the execution units that process tasks and jobs.

Version: 0.1.0
Phase: Phase 2 - Runtime Foundry
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Callable, Any
from uuid import UUID, uuid4


class WorkerStatus(Enum):
    """Worker status enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"


class WorkerType(Enum):
    """Worker type enumeration."""
    BACKTEST = "backtest"
    RESEARCH = "research"
    DATA_PROCESSING = "data_processing"
    EXECUTION = "execution"
    GENERAL = "general"


@dataclass
class WorkerConfig:
    """Worker configuration contract."""
    worker_id: str
    worker_type: WorkerType
    max_concurrent_tasks: int = 1
    task_timeout_seconds: int = 300
    heartbeat_interval: int = 30
    log_level: str = "INFO"
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.worker_id, str) or not self.worker_id:
            raise ValueError("Worker ID cannot be empty")
        if not isinstance(self.worker_type, WorkerType):
            raise ValueError("Worker type must be WorkerType enum")
        if not isinstance(self.max_concurrent_tasks, int) or self.max_concurrent_tasks < 1:
            raise ValueError(f"Max concurrent tasks must be >= 1, got {self.max_concurrent_tasks}")
        if not isinstance(self.task_timeout_seconds, int) or self.task_timeout_seconds < 1:
            raise ValueError(f"Task timeout must be >= 1, got {self.task_timeout_seconds}")


@dataclass
class Task:
    """Task contract."""
    task_id: str
    task_type: str
    payload: Dict
    priority: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.task_id, str) or not self.task_id:
            self.task_id = str(uuid4())
        if not isinstance(self.task_type, str) or not self.task_type:
            raise ValueError("Task type cannot be empty")
    
    @property
    def is_pending(self) -> bool:
        """Check if task is pending."""
        return self.status == "pending"
    
    @property
    def is_running(self) -> bool:
        """Check if task is running."""
        return self.status == "running"
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == "completed"
    
    @property
    def is_failed(self) -> bool:
        """Check if task failed."""
        return self.status == "failed"
    
    @property
    def duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.started_at is None:
            return None
        end_time = self.completed_at or datetime.now(timezone.utc)
        return (end_time - self.started_at).total_seconds()
    
    def mark_started(self) -> None:
        """Mark task as started."""
        self.status = "running"
        self.started_at = datetime.now(timezone.utc)
    
    def mark_completed(self, result: Optional[Dict] = None) -> None:
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)
        self.result = result
    
    def mark_failed(self, error: str) -> None:
        """Mark task as failed."""
        self.status = "failed"
        self.completed_at = datetime.now(timezone.utc)
        self.error = error


@dataclass
class Worker:
    """Worker contract."""
    worker_id: str
    name: str
    worker_type: WorkerType
    config: WorkerConfig
    status: WorkerStatus
    current_task: Optional[Task] = None
    completed_tasks: List[Task] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.worker_id, str) or not self.worker_id:
            raise ValueError("Worker ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.worker_type, WorkerType):
            raise ValueError("Worker type must be WorkerType enum")
        if not isinstance(self.config, WorkerConfig):
            raise ValueError("Config must be a WorkerConfig instance")
        if not isinstance(self.status, WorkerStatus):
            raise ValueError("Status must be WorkerStatus enum")
    
    @property
    def is_idle(self) -> bool:
        """Check if worker is idle."""
        return self.status == WorkerStatus.IDLE
    
    @property
    def is_busy(self) -> bool:
        """Check if worker is busy."""
        return self.status == WorkerStatus.BUSY
    
    @property
    def can_accept_task(self) -> bool:
        """Check if worker can accept a new task."""
        return self.is_idle and len(self.completed_tasks) < self.config.max_concurrent_tasks
    
    @property
    def task_count(self) -> int:
        """Get the number of completed tasks."""
        return len(self.completed_tasks)
    
    @property
    def uptime(self) -> Optional[float]:
        """Get worker uptime in seconds."""
        if self.started_at is None:
            return None
        if self.stopped_at is not None:
            return (self.stopped_at - self.started_at).total_seconds()
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()
    
    def start(self) -> None:
        """Start the worker."""
        self.status = WorkerStatus.STARTING
        self.started_at = datetime.now(timezone.utc)
        self.status = WorkerStatus.IDLE
    
    def stop(self) -> None:
        """Stop the worker."""
        self.status = WorkerStatus.STOPPING
        self.stopped_at = datetime.now(timezone.utc)
        self.status = WorkerStatus.IDLE
    
    def assign_task(self, task: Task) -> None:
        """Assign a task to the worker."""
        if not self.can_accept_task:
            raise RuntimeError(f"Worker {self.worker_id} cannot accept task (status: {self.status})")
        
        self.current_task = task
        self.status = WorkerStatus.BUSY
        task.mark_started()
    
    def complete_task(self, result: Optional[Dict] = None) -> None:
        """Complete the current task."""
        if self.current_task is None:
            raise RuntimeError(f"Worker {self.worker_id} has no current task")
        
        self.current_task.mark_completed(result)
        self.completed_tasks.append(self.current_task)
        self.current_task = None
        self.status = WorkerStatus.IDLE
    
    def fail_task(self, error: str) -> None:
        """Fail the current task."""
        if self.current_task is None:
            raise RuntimeError(f"Worker {self.worker_id} has no current task")
        
        self.current_task.mark_failed(error)
        self.completed_tasks.append(self.current_task)
        self.current_task = None
        self.status = WorkerStatus.IDLE
    
    def mark_error(self) -> None:
        """Mark worker as in error state."""
        self.status = WorkerStatus.ERROR
    
    def get_task_history(self, limit: int = 100) -> List[Task]:
        """Get task history."""
        return self.completed_tasks[-limit:]


@dataclass
class WorkerPool:
    """Worker pool contract."""
    pool_id: str
    name: str
    worker_type: WorkerType
    workers: Dict[str, Worker] = field(default_factory=dict)
    task_queue: List[Task] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.pool_id, str) or not self.pool_id:
            self.pool_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.worker_type, WorkerType):
            raise ValueError("Worker type must be WorkerType enum")
    
    def add_worker(self, worker: Worker) -> None:
        """Add a worker to the pool."""
        if worker.worker_type != self.worker_type:
            raise ValueError(f"Worker type mismatch: expected {self.worker_type}, got {worker.worker_type}")
        self.workers[worker.worker_id] = worker
    
    def remove_worker(self, worker_id: str) -> None:
        """Remove a worker from the pool."""
        if worker_id in self.workers:
            del self.workers[worker_id]
    
    def get_worker(self, worker_id: str) -> Optional[Worker]:
        """Get a worker by ID."""
        return self.workers.get(worker_id)
    
    def get_idle_workers(self) -> List[Worker]:
        """Get all idle workers."""
        return [worker for worker in self.workers.values() if worker.is_idle]
    
    def get_busy_workers(self) -> List[Worker]:
        """Get all busy workers."""
        return [worker for worker in self.workers.values() if worker.is_busy]
    
    def submit_task(self, task: Task) -> None:
        """Submit a task to the pool."""
        self.task_queue.append(task)
    
    def assign_next_task(self) -> Optional[Worker]:
        """Assign the next task to an available worker."""
        if not self.task_queue:
            return None
        
        idle_workers = self.get_idle_workers()
        if not idle_workers:
            return None
        
        task = self.task_queue.pop(0)
        worker = idle_workers[0]
        worker.assign_task(task)
        
        return worker
    
    @property
    def worker_count(self) -> int:
        """Get the number of workers in the pool."""
        return len(self.workers)
    
    @property
    def idle_count(self) -> int:
        """Get the number of idle workers."""
        return len(self.get_idle_workers())
    
    @property
    def busy_count(self) -> int:
        """Get the number of busy workers."""
        return len(self.get_busy_workers())
    
    @property
    def queue_size(self) -> int:
        """Get the size of the task queue."""
        return len(self.task_queue)


def create_worker(worker_id: str, name: str, worker_type: WorkerType, config: Optional[WorkerConfig] = None) -> Worker:
    """Create a new worker."""
    if config is None:
        config = WorkerConfig(
            worker_id=worker_id,
            worker_type=worker_type,
        )
    
    return Worker(
        worker_id=worker_id,
        name=name,
        worker_type=worker_type,
        config=config,
        status=WorkerStatus.IDLE,
    )


def create_worker_pool(name: str, worker_type: WorkerType) -> WorkerPool:
    """Create a new worker pool."""
    return WorkerPool(
        pool_id=str(uuid4()),
        name=name,
        worker_type=worker_type,
    )


def create_task(task_type: str, payload: Dict, priority: int = 0) -> Task:
    """Create a new task."""
    return Task(
        task_id=str(uuid4()),
        task_type=task_type,
        payload=payload,
        priority=priority,
    )
