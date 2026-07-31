"""
GLX FORGE Simulation Deployment

This module defines the deployment manager for the GLX FORGE trading infrastructure.
Deployment manager handles strategy deployment and lifecycle management.

Version: 0.1.0
Phase: Phase 8 - Simulation Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4


class DeploymentStatus(Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentConfig:
    """Deployment configuration contract."""
    deployment_id: str
    strategy_id: str
    environment: str  # "simulation", "paper", "shadow", "live"
    auto_start: bool = True
    health_check_interval: int = 30
    max_retries: int = 3
    rollback_on_failure: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.deployment_id, str) or not self.deployment_id:
            raise ValueError("Deployment ID cannot be empty")
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValueError("Strategy ID cannot be empty")
        if not isinstance(self.environment, str) or not self.environment:
            raise ValueError("Environment cannot be empty")
        if self.environment not in ["simulation", "paper", "shadow", "live"]:
            raise ValueError(f"Environment must be one of simulation, paper, shadow, live, got {self.environment}")


@dataclass
class DeploymentResult:
    """Deployment result contract."""
    result_id: str
    deployment_id: str
    status: DeploymentStatus
    deployed_at: Optional[datetime] = None
    error: Optional[str] = None
    metrics: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.result_id, str) or not self.result_id:
            self.result_id = str(uuid4())
        if not isinstance(self.deployment_id, str) or not self.deployment_id:
            raise ValueError("Deployment ID cannot be empty")
        if not isinstance(self.status, DeploymentStatus):
            raise ValueError("Status must be DeploymentStatus enum")
    
    @property
    def is_success(self) -> bool:
        """Check if deployment succeeded."""
        return self.status in [DeploymentStatus.DEPLOYED, DeploymentStatus.RUNNING]
    
    @property
    def is_failed(self) -> bool:
        """Check if deployment failed."""
        return self.status == DeploymentStatus.FAILED


@dataclass
class DeploymentManager:
    """Deployment manager contract."""
    manager_id: str
    name: str
    deployments: Dict[str, DeploymentConfig] = field(default_factory=dict)
    results: List[DeploymentResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.manager_id, str) or not self.manager_id:
            raise ValueError("Manager ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
    
    def add_deployment(self, config: DeploymentConfig) -> None:
        """Add a deployment configuration."""
        self.deployments[config.deployment_id] = config
    
    def remove_deployment(self, deployment_id: str) -> None:
        """Remove a deployment configuration."""
        if deployment_id in self.deployments:
            del self.deployments[deployment_id]
    
    def get_deployment(self, deployment_id: str) -> Optional[DeploymentConfig]:
        """Get a deployment configuration by ID."""
        return self.deployments.get(deployment_id)
    
    def deploy(self, deployment_id: str) -> DeploymentResult:
        """Deploy a strategy."""
        config = self.get_deployment(deployment_id)
        if config is None:
            return DeploymentResult(
                result_id=str(uuid4()),
                deployment_id=deployment_id,
                status=DeploymentStatus.FAILED,
                error=f"Deployment not found: {deployment_id}",
            )
        
        result = DeploymentResult(
            result_id=str(uuid4()),
            deployment_id=deployment_id,
            status=DeploymentStatus.DEPLOYING,
        )
        
        # Simulate deployment
        result.status = DeploymentStatus.DEPLOYED
        result.deployed_at = datetime.now(timezone.utc)
        
        if config.auto_start:
            result.status = DeploymentStatus.RUNNING
        
        self.results.append(result)
        
        return result
    
    def rollback(self, deployment_id: str) -> DeploymentResult:
        """Rollback a deployment."""
        result = DeploymentResult(
            result_id=str(uuid4()),
            deployment_id=deployment_id,
            status=DeploymentStatus.ROLLING_BACK,
        )
        
        # Simulate rollback
        result.status = DeploymentStatus.ROLLED_BACK
        
        self.results.append(result)
        
        return result
    
    @property
    def deployment_count(self) -> int:
        """Get the number of deployments."""
        return len(self.deployments)
    
    @property
    def result_count(self) -> int:
        """Get the number of results."""
        return len(self.results)
    
    def get_success_rate(self) -> float:
        """Get deployment success rate."""
        if not self.results:
            return 0.0
        successful = sum(1 for r in self.results if r.is_success)
        return successful / len(self.results)


def create_deployment_manager(name: str) -> DeploymentManager:
    """Create a new deployment manager."""
    return DeploymentManager(
        manager_id=str(uuid4()),
        name=name,
    )


def create_deployment_config(
    strategy_id: str,
    environment: str,
    auto_start: bool = True,
) -> DeploymentConfig:
    """Create a new deployment configuration."""
    return DeploymentConfig(
        deployment_id=str(uuid4()),
        strategy_id=strategy_id,
        environment=environment,
        auto_start=auto_start,
    )
