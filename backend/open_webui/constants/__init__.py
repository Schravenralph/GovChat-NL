"""
OpenWebUI Constants Package
"""

from .policy_permissions import (
    PolicyPermissions,
    USER_PERMISSIONS,
    ADMIN_PERMISSIONS,
    PERMISSION_DESCRIPTIONS,
    get_user_permission_list,
    get_admin_permission_list,
    is_admin_permission,
    is_user_permission,
)

__all__ = [
    "PolicyPermissions",
    "USER_PERMISSIONS",
    "ADMIN_PERMISSIONS",
    "PERMISSION_DESCRIPTIONS",
    "get_user_permission_list",
    "get_admin_permission_list",
    "is_admin_permission",
    "is_user_permission",
]
