"""
Tests for Policy Scanner authentication middleware

Tests permission checking, decorators, and access control.
"""

import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException

from open_webui.middleware.policy_auth import (
    get_user_policy_permissions,
    has_policy_permission,
    require_policy_permission,
    require_policy_admin,
    check_permission_or_raise,
    require_any_permission,
    require_all_permissions,
)
from open_webui.constants.policy_permissions import (
    PolicyPermissions,
    USER_PERMISSIONS,
    ADMIN_PERMISSIONS,
)
from open_webui.models.users import UserModel


# Test fixtures
@pytest.fixture
def admin_user():
    """Create a mock admin user"""
    return UserModel(
        id="admin-123",
        name="Admin User",
        email="admin@example.com",
        role="admin",
        profile_image_url="/user.png",
        last_active_at=0,
        updated_at=0,
        created_at=0,
    )


@pytest.fixture
def regular_user():
    """Create a mock regular user"""
    return UserModel(
        id="user-123",
        name="Regular User",
        email="user@example.com",
        role="user",
        profile_image_url="/user.png",
        last_active_at=0,
        updated_at=0,
        created_at=0,
    )


@pytest.fixture
def pending_user():
    """Create a mock pending user"""
    return UserModel(
        id="pending-123",
        name="Pending User",
        email="pending@example.com",
        role="pending",
        profile_image_url="/user.png",
        last_active_at=0,
        updated_at=0,
        created_at=0,
    )


# Test get_user_policy_permissions
class TestGetUserPolicyPermissions:
    """Test user permission retrieval"""

    def test_admin_user_has_all_permissions(self, admin_user):
        """Admin users should have all permissions"""
        permissions = get_user_policy_permissions(admin_user)
        assert set(permissions) == set(ADMIN_PERMISSIONS)
        assert PolicyPermissions.ADMIN in permissions
        assert PolicyPermissions.SEARCH in permissions

    def test_regular_user_has_user_permissions(self, regular_user):
        """Regular users should have only user permissions"""
        permissions = get_user_policy_permissions(regular_user)
        assert set(permissions) == set(USER_PERMISSIONS)
        assert PolicyPermissions.SEARCH in permissions
        assert PolicyPermissions.ADMIN not in permissions

    def test_pending_user_has_user_permissions(self, pending_user):
        """Pending users should have user permissions"""
        permissions = get_user_policy_permissions(pending_user)
        assert set(permissions) == set(USER_PERMISSIONS)

    def test_none_user_has_no_permissions(self):
        """None user should have no permissions"""
        permissions = get_user_policy_permissions(None)
        assert permissions == []

    def test_unknown_role_has_no_permissions(self):
        """Unknown role should have no permissions"""
        user = UserModel(
            id="unknown-123",
            name="Unknown User",
            email="unknown@example.com",
            role="unknown_role",
            profile_image_url="/user.png",
            last_active_at=0,
            updated_at=0,
            created_at=0,
        )
        permissions = get_user_policy_permissions(user)
        assert permissions == []


# Test has_policy_permission
class TestHasPolicyPermission:
    """Test permission checking"""

    def test_admin_has_admin_permission(self, admin_user):
        """Admin should have admin permission"""
        assert has_policy_permission(admin_user, PolicyPermissions.ADMIN)

    def test_admin_has_user_permission(self, admin_user):
        """Admin should have user permissions"""
        assert has_policy_permission(admin_user, PolicyPermissions.SEARCH)
        assert has_policy_permission(admin_user, PolicyPermissions.VIEW)

    def test_user_has_user_permission(self, regular_user):
        """User should have user permissions"""
        assert has_policy_permission(regular_user, PolicyPermissions.SEARCH)
        assert has_policy_permission(regular_user, PolicyPermissions.VIEW)

    def test_user_lacks_admin_permission(self, regular_user):
        """User should not have admin permissions"""
        assert not has_policy_permission(regular_user, PolicyPermissions.ADMIN)
        assert not has_policy_permission(regular_user, PolicyPermissions.MANAGE_SOURCES)

    def test_none_user_lacks_all_permissions(self):
        """None user should lack all permissions"""
        assert not has_policy_permission(None, PolicyPermissions.SEARCH)
        assert not has_policy_permission(None, PolicyPermissions.ADMIN)


# Test require_policy_permission decorator
class TestRequirePolicyPermissionDecorator:
    """Test permission-required decorator"""

    @pytest.mark.asyncio
    async def test_decorator_allows_authorized_user(self, admin_user):
        """Decorator should allow authorized user"""
        @require_policy_permission(PolicyPermissions.ADMIN)
        async def protected_endpoint(user=None):
            return {"success": True}

        result = await protected_endpoint(user=admin_user)
        assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_decorator_blocks_unauthorized_user(self, regular_user):
        """Decorator should block unauthorized user"""
        @require_policy_permission(PolicyPermissions.ADMIN)
        async def protected_endpoint(user=None):
            return {"success": True}

        with pytest.raises(HTTPException) as exc_info:
            await protected_endpoint(user=regular_user)

        assert exc_info.value.status_code == 403
        assert "permission" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_decorator_blocks_no_user(self):
        """Decorator should block when no user provided"""
        @require_policy_permission(PolicyPermissions.SEARCH)
        async def protected_endpoint(user=None):
            return {"success": True}

        with pytest.raises(HTTPException) as exc_info:
            await protected_endpoint(user=None)

        assert exc_info.value.status_code == 401
        assert "authentication" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_decorator_user_permission_works(self, regular_user):
        """Decorator should allow user with user permission"""
        @require_policy_permission(PolicyPermissions.SEARCH)
        async def search_endpoint(user=None):
            return {"results": []}

        result = await search_endpoint(user=regular_user)
        assert result == {"results": []}

    def test_decorator_sync_function(self, admin_user):
        """Decorator should work with sync functions"""
        @require_policy_permission(PolicyPermissions.ADMIN)
        def protected_sync_endpoint(user=None):
            return {"success": True}

        result = protected_sync_endpoint(user=admin_user)
        assert result == {"success": True}


# Test require_policy_admin decorator
class TestRequirePolicyAdminDecorator:
    """Test admin-required decorator"""

    @pytest.mark.asyncio
    async def test_admin_decorator_allows_admin(self, admin_user):
        """Admin decorator should allow admin user"""
        @require_policy_admin
        async def admin_endpoint(user=None):
            return {"admin": True}

        result = await admin_endpoint(user=admin_user)
        assert result == {"admin": True}

    @pytest.mark.asyncio
    async def test_admin_decorator_blocks_regular_user(self, regular_user):
        """Admin decorator should block regular user"""
        @require_policy_admin
        async def admin_endpoint(user=None):
            return {"admin": True}

        with pytest.raises(HTTPException) as exc_info:
            await admin_endpoint(user=regular_user)

        assert exc_info.value.status_code == 403


# Test check_permission_or_raise
class TestCheckPermissionOrRaise:
    """Test explicit permission checking"""

    def test_check_allows_authorized_user(self, admin_user):
        """Should not raise for authorized user"""
        check_permission_or_raise(admin_user, PolicyPermissions.ADMIN)

    def test_check_raises_for_unauthorized_user(self, regular_user):
        """Should raise for unauthorized user"""
        with pytest.raises(HTTPException) as exc_info:
            check_permission_or_raise(regular_user, PolicyPermissions.ADMIN)

        assert exc_info.value.status_code == 403

    def test_check_raises_for_none_user(self):
        """Should raise 401 for None user"""
        with pytest.raises(HTTPException) as exc_info:
            check_permission_or_raise(None, PolicyPermissions.SEARCH)

        assert exc_info.value.status_code == 401

    def test_check_custom_error_message(self, regular_user):
        """Should use custom error message"""
        with pytest.raises(HTTPException) as exc_info:
            check_permission_or_raise(
                regular_user,
                PolicyPermissions.ADMIN,
                error_message="Custom error"
            )

        assert "Custom error" in str(exc_info.value.detail)


# Test require_any_permission decorator
class TestRequireAnyPermissionDecorator:
    """Test OR permission decorator"""

    @pytest.mark.asyncio
    async def test_any_permission_allows_with_one_permission(self, regular_user):
        """Should allow if user has any of the required permissions"""
        @require_any_permission(PolicyPermissions.SEARCH, PolicyPermissions.ADMIN)
        async def endpoint(user=None):
            return {"success": True}

        result = await endpoint(user=regular_user)
        assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_any_permission_blocks_without_permissions(self, regular_user):
        """Should block if user has none of the required permissions"""
        @require_any_permission(PolicyPermissions.ADMIN, PolicyPermissions.DELETE)
        async def endpoint(user=None):
            return {"success": True}

        with pytest.raises(HTTPException) as exc_info:
            await endpoint(user=regular_user)

        assert exc_info.value.status_code == 403


# Test require_all_permissions decorator
class TestRequireAllPermissionsDecorator:
    """Test AND permission decorator"""

    @pytest.mark.asyncio
    async def test_all_permissions_allows_with_all(self, admin_user):
        """Should allow if user has all required permissions"""
        @require_all_permissions(PolicyPermissions.SEARCH, PolicyPermissions.ADMIN)
        async def endpoint(user=None):
            return {"success": True}

        result = await endpoint(user=admin_user)
        assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_all_permissions_blocks_without_all(self, regular_user):
        """Should block if user is missing any permission"""
        @require_all_permissions(PolicyPermissions.SEARCH, PolicyPermissions.ADMIN)
        async def endpoint(user=None):
            return {"success": True}

        with pytest.raises(HTTPException) as exc_info:
            await endpoint(user=regular_user)

        assert exc_info.value.status_code == 403


# Integration tests
class TestPermissionIntegration:
    """Test permission system integration"""

    def test_admin_can_access_all_endpoints(self, admin_user):
        """Admin should be able to access all protected endpoints"""
        for permission in ADMIN_PERMISSIONS:
            assert has_policy_permission(admin_user, permission), \
                f"Admin missing permission: {permission}"

    def test_user_can_access_user_endpoints(self, regular_user):
        """User should be able to access user endpoints"""
        for permission in USER_PERMISSIONS:
            assert has_policy_permission(regular_user, permission), \
                f"User missing permission: {permission}"

    def test_user_cannot_access_admin_endpoints(self, regular_user):
        """User should not be able to access admin endpoints"""
        admin_only_perms = set(ADMIN_PERMISSIONS) - set(USER_PERMISSIONS)
        for permission in admin_only_perms:
            assert not has_policy_permission(regular_user, permission), \
                f"User should not have admin permission: {permission}"

    def test_permission_constants_are_strings(self):
        """All permission constants should be strings"""
        for perm in PolicyPermissions:
            assert isinstance(perm.value, str)
            assert perm.value.startswith("policy:")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
