"""
GLX FORGE Governance Policies

This module defines the policy system for the GLX FORGE trading infrastructure.
Policies define rules that govern actions and decisions in the system.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Callable, Any
from uuid import UUID, uuid4


class PolicyType(Enum):
    """Policy type enumeration."""
    PHASE_TRANSITION = "phase_transition"
    STRATEGY_DEPLOYMENT = "strategy_deployment"
    CAPITAL_ALLOCATION = "capital_allocation"
    RISK_LIMIT = "risk_limit"
    DATA_ACCESS = "data_access"
    SYSTEM_OPERATION = "system_operation"


class PolicyEffect(Enum):
    """Policy effect enumeration."""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass
class Policy:
    """Policy contract."""
    policy_id: str
    name: str
    policy_type: PolicyType
    effect: PolicyEffect
    description: str
    conditions: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if not isinstance(self.policy_id, str) or not self.policy_id:
            self.policy_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.policy_type, PolicyType):
            raise ValueError("Policy type must be PolicyType enum")
        if not isinstance(self.effect, PolicyEffect):
            raise ValueError("Policy effect must be PolicyEffect enum")
        if not isinstance(self.description, str) or not self.description:
            raise ValueError("Description cannot be empty")
    
    def evaluate(self, context: dict) -> PolicyEffect:
        """Evaluate this policy against a context."""
        if not self.is_active:
            return PolicyEffect.ALLOW
        
        # Check if all conditions are met
        for key, expected_value in self.conditions.items():
            actual_value = context.get(key)
            if actual_value != expected_value:
                return PolicyEffect.ALLOW
        
        return self.effect
    
    def activate(self) -> None:
        """Activate this policy."""
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self) -> None:
        """Deactivate this policy."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)


# Default policies for the GLX FORGE system
DEFAULT_POLICIES = {
    # Phase transition policies
    "phase_transition_requires_approval": Policy(
        policy_id="policy-phase-transition-approval",
        name="Phase Transition Requires Approval",
        policy_type=PolicyType.PHASE_TRANSITION,
        effect=PolicyEffect.REQUIRE_APPROVAL,
        description="All phase transitions require approval from an administrator",
        conditions={
            "phase_transition": True,
        },
    ),
    
    "phase_0_to_1_requires_baseline": Policy(
        policy_id="policy-phase-0-to-1-baseline",
        name="Phase 0 to 1 Requires Baseline",
        policy_type=PolicyType.PHASE_TRANSITION,
        effect=PolicyEffect.DENY,
        description="Cannot advance from Phase 0 to Phase 1 without completing baseline",
        conditions={
            "from_phase": "phase-00",
            "to_phase": "phase-01",
            "baseline_complete": False,
        },
    ),
    
    # Strategy deployment policies
    "strategy_deployment_requires_backtest": Policy(
        policy_id="policy-strategy-backtest",
        name="Strategy Deployment Requires Backtest",
        policy_type=PolicyType.STRATEGY_DEPLOYMENT,
        effect=PolicyEffect.DENY,
        description="Cannot deploy a strategy without passing backtest validation",
        conditions={
            "action": "deploy_strategy",
            "backtest_passed": False,
        },
    ),
    
    "strategy_deployment_requires_approval": Policy(
        policy_id="policy-strategy-deploy-approval",
        name="Strategy Deployment Requires Approval",
        policy_type=PolicyType.STRATEGY_DEPLOYMENT,
        effect=PolicyEffect.REQUIRE_APPROVAL,
        description="Strategy deployment requires approval from a strategist",
        conditions={
            "action": "deploy_strategy",
        },
    ),
    
    # Capital allocation policies
    "capital_allocation_requires_approval": Policy(
        policy_id="policy-capital-allocation-approval",
        name="Capital Allocation Requires Approval",
        policy_type=PolicyType.CAPITAL_ALLOCATION,
        effect=PolicyEffect.REQUIRE_APPROVAL,
        description="Capital allocation requires approval from a strategist",
        conditions={
            "action": "allocate_capital",
        },
    ),
    
    "capital_withdrawal_requires_admin": Policy(
        policy_id="policy-capital-withdrawal-admin",
        name="Capital Withdrawal Requires Admin",
        policy_type=PolicyType.CAPITAL_ALLOCATION,
        effect=PolicyEffect.REQUIRE_APPROVAL,
        description="Capital withdrawal requires approval from an administrator",
        conditions={
            "action": "withdraw_capital",
        },
    ),
    
    # Risk limit policies
    "max_position_size": Policy(
        policy_id="policy-max-position-size",
        name="Maximum Position Size",
        policy_type=PolicyType.RISK_LIMIT,
        effect=PolicyEffect.DENY,
        description="Cannot exceed maximum position size limit",
        conditions={
            "action": "open_position",
            "position_size_exceeds_limit": True,
        },
    ),
    
    "max_daily_loss": Policy(
        policy_id="policy-max-daily-loss",
        name="Maximum Daily Loss",
        policy_type=PolicyType.RISK_LIMIT,
        effect=PolicyEffect.DENY,
        description="Cannot exceed maximum daily loss limit",
        conditions={
            "action": "open_position",
            "daily_loss_exceeds_limit": True,
        },
    ),
    
    # Data access policies
    "data_access_requires_auth": Policy(
        policy_id="policy-data-access-auth",
        name="Data Access Requires Authentication",
        policy_type=PolicyType.DATA_ACCESS,
        effect=PolicyEffect.DENY,
        description="Cannot access data without authentication",
        conditions={
            "action": "access_data",
            "authenticated": False,
        },
    ),
    
    # System operation policies
    "system_admin_requires_admin": Policy(
        policy_id="policy-system-admin-admin",
        name="System Admin Requires Admin",
        policy_type=PolicyType.SYSTEM_OPERATION,
        effect=PolicyEffect.DENY,
        description="System administration requires admin authority",
        conditions={
            "action": "system_admin",
            "authority_level": "admin",
        },
    ),
}


def check_policy(policy_id: str, context: dict) -> PolicyEffect:
    """Check a policy against a context."""
    policy = DEFAULT_POLICIES.get(policy_id)
    if policy is None:
        raise ValueError(f"Policy not found: {policy_id}")
    return policy.evaluate(context)


def create_policy(
    name: str,
    policy_type: PolicyType,
    effect: PolicyEffect,
    description: str,
    conditions: Optional[dict] = None,
) -> Policy:
    """Create a new policy."""
    return Policy(
        policy_id=str(uuid4()),
        name=name,
        policy_type=policy_type,
        effect=effect,
        description=description,
        conditions=conditions or {},
    )


def update_policy(policy: Policy, **updates: Any) -> None:
    """Update a policy."""
    for key, value in updates.items():
        if hasattr(policy, key):
            setattr(policy, key, value)
    policy.updated_at = datetime.now(timezone.utc)


def delete_policy(policy_id: str) -> None:
    """Delete a policy (deactivate it)."""
    policy = DEFAULT_POLICIES.get(policy_id)
    if policy is not None:
        policy.deactivate()
