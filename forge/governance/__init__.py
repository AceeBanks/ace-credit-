"""
GLX FORGE Governance Authority

This module defines the governance authority for the GLX FORGE trading infrastructure.
Governance defines who can approve what actions and changes.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

__version__ = "0.1.0"

from forge.governance.authority import (
    Authority,
    AuthorityLevel,
    Permission,
    Approval,
    ApprovalStatus,
    check_permission,
    request_approval,
    grant_permission,
    revoke_permission,
)

from forge.governance.roles import (
    Role,
    RoleType,
    DEFAULT_ROLES,
    get_role,
    assign_role,
    remove_role,
)

from forge.governance.policies import (
    Policy,
    PolicyType,
    PolicyEffect,
    DEFAULT_POLICIES,
    check_policy,
    create_policy,
    update_policy,
    delete_policy,
)

__all__ = [
    # Authority
    "Authority",
    "AuthorityLevel",
    "Permission",
    "Approval",
    "ApprovalStatus",
    "check_permission",
    "request_approval",
    "grant_permission",
    "revoke_permission",
    # Roles
    "Role",
    "RoleType",
    "DEFAULT_ROLES",
    "get_role",
    "assign_role",
    "remove_role",
    # Policies
    "Policy",
    "PolicyType",
    "PolicyEffect",
    "DEFAULT_POLICIES",
    "check_policy",
    "create_policy",
    "update_policy",
    "delete_policy",
]
