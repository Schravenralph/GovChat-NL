"""
Policy Scanner Authentication Middleware

Provides permission-based access control for Policy Scanner endpoints.
Integrates with existing OpenWebUI authentication system.
"""

import logging
from functools import wraps
from typing import List, Optional, Callable

from fastapi import HTTPException, status

from open_webui.models.users import UserModel
from open_webui.constants.policy_permissions import (
    PolicyPermissions,
    USER_PERMISSIONS,
    ADMIN_PERMISSIONS,
    is_admin_permission,
)
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("AUTH", logging.INFO))


def get_user_policy_permissions(user: UserModel) -> List[str]:
    """
    Get Policy Scanner permissions for a user based on their role.

    Args:
        user: The user model from OpenWebUI authentication

    Returns:
        List of permission strings the user has
    """
    if not user:
        return []

    # Admin users get all permissions
    if user.role == "admin":
        return ADMIN_PERMISSIONS

    # Regular users get standard user permissions
    if user.role in ["user", "pending"]:
        return USER_PERMISSIONS

    # Unknown role, no permissions
    log.warning(f"Unknown user role '{user.role}' for user {user.id}")
    return []


def has_policy_permission(user: UserModel, permission: str) -> bool:
    """
    Check if a user has a specific Policy Scanner permission.

    Args:
        user: The user model
        permission: Permission string to check (e.g., "policy:search")

    Returns:
        True if user has the permission, False otherwise
    """
    if not user:
        return False

    user_permissions = get_user_policy_permissions(user)
    return permission in user_permissions


def require_policy_permission(permission: str) -> Callable:
    """
    Decorator to require a specific Policy Scanner permission.

    Usage:
        @router.get("/documents")
        @require_policy_permission(PolicyPermissions.VIEW)
        async def get_documents(user=Depends(get_verified_user)):
            ...

    Args:
        permission: Required permission string

    Returns:
        Decorator function

    Raises:
        HTTPException: 401 if not authenticated, 403 if permission denied
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract user from kwargs (should be injected by Depends(get_current_user))
            user = kwargs.get("user")

            if user is None:
                log.warning(f"Authentication required for {func.__name__}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has the required permission
            if not has_policy_permission(user, permission):
                log.warning(
                    f"User {user.id} ({user.role}) denied access to {func.__name__}: "
                    f"missing permission '{permission}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission}",
                )

            log.debug(f"User {user.id} granted access to {func.__name__} with permission '{permission}'")
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Extract user from kwargs
            user = kwargs.get("user")

            if user is None:
                log.warning(f"Authentication required for {func.__name__}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has the required permission
            if not has_policy_permission(user, permission):
                log.warning(
                    f"User {user.id} ({user.role}) denied access to {func.__name__}: "
                    f"missing permission '{permission}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission}",
                )

            log.debug(f"User {user.id} granted access to {func.__name__} with permission '{permission}'")
            return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def require_policy_admin(func: Callable) -> Callable:
    """
    Decorator to require Policy Scanner admin permission.

    This is a convenience decorator equivalent to:
        @require_policy_permission(PolicyPermissions.ADMIN)

    Usage:
        @router.post("/sources")
        @require_policy_admin
        async def create_source(user=Depends(get_verified_user)):
            ...

    Args:
        func: Function to wrap

    Returns:
        Wrapped function

    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin
    """
    return require_policy_permission(PolicyPermissions.ADMIN)(func)


def check_permission_or_raise(
    user: Optional[UserModel],
    permission: str,
    error_message: Optional[str] = None
) -> None:
    """
    Check permission and raise HTTPException if not authorized.

    Utility function for explicit permission checks within endpoint logic.

    Args:
        user: User model
        permission: Permission string to check
        error_message: Custom error message (optional)

    Raises:
        HTTPException: 401 if user is None, 403 if permission denied
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message or "Authentication required",
        )

    if not has_policy_permission(user, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_message or f"Missing required permission: {permission}",
        )


def require_any_permission(*permissions: str) -> Callable:
    """
    Decorator to require ANY of the specified permissions (OR logic).

    Usage:
        @require_any_permission(PolicyPermissions.VIEW, PolicyPermissions.ADMIN)
        async def get_resource(user=Depends(get_verified_user)):
            ...

    Args:
        permissions: Variable number of permission strings

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            user = kwargs.get("user")

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has ANY of the required permissions
            user_permissions = get_user_policy_permissions(user)
            if not any(perm in user_permissions for perm in permissions):
                log.warning(
                    f"User {user.id} denied access to {func.__name__}: "
                    f"missing any of permissions {permissions}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing one of required permissions: {', '.join(permissions)}",
                )

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            user = kwargs.get("user")

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has ANY of the required permissions
            user_permissions = get_user_policy_permissions(user)
            if not any(perm in user_permissions for perm in permissions):
                log.warning(
                    f"User {user.id} denied access to {func.__name__}: "
                    f"missing any of permissions {permissions}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing one of required permissions: {', '.join(permissions)}",
                )

            return func(*args, **kwargs)

        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def require_all_permissions(*permissions: str) -> Callable:
    """
    Decorator to require ALL of the specified permissions (AND logic).

    Usage:
        @require_all_permissions(PolicyPermissions.ADMIN, PolicyPermissions.DELETE)
        async def delete_resource(user=Depends(get_verified_user)):
            ...

    Args:
        permissions: Variable number of permission strings

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            user = kwargs.get("user")

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has ALL of the required permissions
            user_permissions = get_user_policy_permissions(user)
            missing = [perm for perm in permissions if perm not in user_permissions]

            if missing:
                log.warning(
                    f"User {user.id} denied access to {func.__name__}: "
                    f"missing permissions {missing}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {', '.join(missing)}",
                )

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            user = kwargs.get("user")

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has ALL of the required permissions
            user_permissions = get_user_policy_permissions(user)
            missing = [perm for perm in permissions if perm not in user_permissions]

            if missing:
                log.warning(
                    f"User {user.id} denied access to {func.__name__}: "
                    f"missing permissions {missing}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {', '.join(missing)}",
                )

            return func(*args, **kwargs)

        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
