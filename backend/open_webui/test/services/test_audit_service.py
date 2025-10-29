"""
Tests for Policy Scanner Audit Logging Service

Tests audit log creation, retrieval, and statistics.
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from open_webui.services.audit_service import (
    AuditService,
    get_audit_service,
    log_action,
    log_search,
    log_document_view,
    log_document_download,
    log_admin_action,
)


# Test fixtures
@pytest.fixture
def audit_service():
    """Create audit service instance"""
    return AuditService()


@pytest.fixture
def mock_db():
    """Create mock database connection"""
    db = MagicMock()
    db.execute = MagicMock(return_value=MagicMock())
    db.commit = MagicMock()
    return db


# Test basic logging
class TestAuditServiceLogging:
    """Test basic audit logging functionality"""

    @patch("open_webui.services.audit_service.get_db")
    def test_log_action_success(self, mock_get_db, audit_service, mock_db):
        """Test successful action logging"""
        mock_get_db.return_value.__enter__.return_value = mock_db

        result = audit_service.log_action(
            user_id="user-123",
            action="search",
            resource_type="query",
            resource_id="search-456",
            details={"query": "test query"},
            ip_address="127.0.0.1",
        )

        assert result is True
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch("open_webui.services.audit_service.get_db")
    def test_log_action_with_minimal_params(self, mock_get_db, audit_service, mock_db):
        """Test logging with only required parameters"""
        mock_get_db.return_value.__enter__.return_value = mock_db

        result = audit_service.log_action(
            user_id="user-123",
            action="view",
            resource_type="document",
        )

        assert result is True
        mock_db.execute.assert_called_once()

    @patch("open_webui.services.audit_service.get_db")
    def test_log_action_handles_failure(self, mock_get_db, audit_service):
        """Test graceful handling of logging failures"""
        mock_get_db.side_effect = Exception("Database error")

        result = audit_service.log_action(
            user_id="user-123",
            action="search",
            resource_type="query",
        )

        assert result is False

    def test_log_action_when_disabled(self, audit_service, mock_db):
        """Test that logging is skipped when disabled"""
        audit_service.enabled = False

        result = audit_service.log_action(
            user_id="user-123",
            action="search",
            resource_type="query",
        )

        assert result is True  # Returns True but doesn't actually log


# Test specific log methods
class TestSpecificLogMethods:
    """Test specialized logging methods"""

    @patch("open_webui.services.audit_service.get_db")
    def test_log_search(self, mock_get_db, audit_service, mock_db):
        """Test search logging"""
        mock_get_db.return_value.__enter__.return_value = mock_db

        result = audit_service.log_search(
            user_id="user-123",
            query="test query",
            filters={"municipality": "Amsterdam"},
            result_count=42,
            response_time_ms=150,
            ip_address="127.0.0.1",
        )

        assert result is True
        mock_db.execute.assert_called_once()

        # Verify query contains expected data
        call_args = mock_db.execute.call_args
        assert "search" in str(call_args)

    @patch("open_webui.services.audit_service.get_db")
    def test_log_document_view(self, mock_get_db, audit_service, mock_db):
        """Test document view logging"""
        mock_get_db.return_value.__enter__.return_value = mock_db

        result = audit_service.log_document_view(
            user_id="user-123",
            document_id="doc-456",
            ip_address="127.0.0.1",
        )

        assert result is True
        mock_db.execute.assert_called_once()

    @patch("open_webui.services.audit_service.get_db")
    def test_log_document_download(self, mock_get_db, audit_service, mock_db):
        """Test document download logging"""
        mock_get_db.return_value.__enter__.return_value = mock_db

        result = audit_service.log_document_download(
            user_id="user-123",
            document_id="doc-456",
            format="pdf",
            ip_address="127.0.0.1",
        )

        assert result is True
        mock_db.execute.assert_called_once()

    @patch("open_webui.services.audit_service.get_db")
    def test_log_favorite_action(self, mock_get_db, audit_service, mock_db):
        """Test favorite action logging"""
        mock_get_db.return_value.__enter__.return_value = mock_db

        result = audit_service.log_favorite_action(
            user_id="user-123",
            document_id="doc-456",
            action="add",
        )

        assert result is True
        mock_db.execute.assert_called_once()

    @patch("open_webui.services.audit_service.get_db")
    def test_log_admin_action(self, mock_get_db, audit_service, mock_db):
        """Test admin action logging"""
        mock_get_db.return_value.__enter__.return_value = mock_db

        result = audit_service.log_admin_action(
            user_id="admin-123",
            action="create_source",
            resource_type="source",
            resource_id="source-789",
            details={"name": "Test Source"},
            status="success",
        )

        assert result is True
        mock_db.execute.assert_called_once()


# Test retrieval methods
class TestAuditRetrieval:
    """Test audit log retrieval"""

    @patch("open_webui.services.audit_service.get_db")
    def test_get_user_actions(self, mock_get_db, audit_service):
        """Test retrieving user actions"""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (
                "log-1",
                "user-123",
                "search",
                "query",
                "search-456",
                '{"query": "test"}',
                "127.0.0.1",
                "success",
                int(time.time()),
            )
        ]
        mock_db.execute.return_value = mock_result
        mock_get_db.return_value.__enter__.return_value = mock_db

        logs = audit_service.get_user_actions(
            user_id="user-123",
            limit=10,
        )

        assert len(logs) == 1
        assert logs[0]["user_id"] == "user-123"
        assert logs[0]["action"] == "search"
        assert logs[0]["details"]["query"] == "test"

    @patch("open_webui.services.audit_service.get_db")
    def test_get_user_actions_with_filter(self, mock_get_db, audit_service):
        """Test retrieving user actions with action filter"""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result
        mock_get_db.return_value.__enter__.return_value = mock_db

        logs = audit_service.get_user_actions(
            user_id="user-123",
            action_type="search",
        )

        assert isinstance(logs, list)
        mock_db.execute.assert_called_once()

    @patch("open_webui.services.audit_service.get_db")
    def test_get_resource_actions(self, mock_get_db, audit_service):
        """Test retrieving actions for a resource"""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (
                "log-1",
                "user-123",
                "view",
                "document",
                "doc-456",
                None,
                "127.0.0.1",
                "success",
                int(time.time()),
            )
        ]
        mock_db.execute.return_value = mock_result
        mock_get_db.return_value.__enter__.return_value = mock_db

        logs = audit_service.get_resource_actions(
            resource_type="document",
            resource_id="doc-456",
        )

        assert len(logs) == 1
        assert logs[0]["resource_type"] == "document"
        assert logs[0]["resource_id"] == "doc-456"

    @patch("open_webui.services.audit_service.get_db")
    def test_get_user_actions_handles_error(self, mock_get_db, audit_service):
        """Test graceful handling of retrieval errors"""
        mock_get_db.side_effect = Exception("Database error")

        logs = audit_service.get_user_actions(user_id="user-123")

        assert logs == []


# Test statistics
class TestAuditStatistics:
    """Test audit statistics generation"""

    @patch("open_webui.services.audit_service.get_db")
    def test_get_audit_stats(self, mock_get_db, audit_service):
        """Test audit statistics retrieval"""
        mock_db = MagicMock()

        # Mock total count
        total_result = MagicMock()
        total_result.fetchone.return_value = (100,)

        # Mock actions by type
        type_result = MagicMock()
        type_result.fetchall.return_value = [
            ("search", 50),
            ("view", 30),
            ("download", 20),
        ]

        # Mock unique users
        users_result = MagicMock()
        users_result.fetchone.return_value = (15,)

        mock_db.execute.side_effect = [total_result, type_result, users_result]
        mock_get_db.return_value.__enter__.return_value = mock_db

        stats = audit_service.get_audit_stats()

        assert stats["total_actions"] == 100
        assert stats["unique_users"] == 15
        assert stats["actions_by_type"]["search"] == 50
        assert "start_date" in stats
        assert "end_date" in stats

    @patch("open_webui.services.audit_service.get_db")
    def test_get_audit_stats_with_date_range(self, mock_get_db, audit_service):
        """Test statistics with custom date range"""
        mock_db = MagicMock()
        mock_db.execute.return_value.fetchone.return_value = (0,)
        mock_db.execute.return_value.fetchall.return_value = []
        mock_get_db.return_value.__enter__.return_value = mock_db

        start = datetime.now() - timedelta(days=30)
        end = datetime.now()

        stats = audit_service.get_audit_stats(start_date=start, end_date=end)

        assert stats["start_date"] == start.isoformat()
        assert stats["end_date"] == end.isoformat()

    @patch("open_webui.services.audit_service.get_db")
    def test_get_audit_stats_handles_error(self, mock_get_db, audit_service):
        """Test graceful handling of statistics errors"""
        mock_get_db.side_effect = Exception("Database error")

        stats = audit_service.get_audit_stats()

        assert stats["total_actions"] == 0
        assert stats["unique_users"] == 0
        assert stats["actions_by_type"] == {}


# Test cleanup
class TestAuditCleanup:
    """Test audit log cleanup"""

    @patch("open_webui.services.audit_service.get_db")
    def test_cleanup_old_logs(self, mock_get_db, audit_service):
        """Test deletion of old logs"""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 50
        mock_db.execute.return_value = mock_result
        mock_get_db.return_value.__enter__.return_value = mock_db

        deleted_count = audit_service.cleanup_old_logs(retention_days=90)

        assert deleted_count == 50
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch("open_webui.services.audit_service.get_db")
    def test_cleanup_handles_error(self, mock_get_db, audit_service):
        """Test graceful handling of cleanup errors"""
        mock_get_db.side_effect = Exception("Database error")

        deleted_count = audit_service.cleanup_old_logs()

        assert deleted_count == 0


# Test singleton and convenience functions
class TestSingletonAndConvenience:
    """Test singleton pattern and convenience functions"""

    def test_get_audit_service_singleton(self):
        """Test that get_audit_service returns singleton"""
        service1 = get_audit_service()
        service2 = get_audit_service()

        assert service1 is service2

    @patch("open_webui.services.audit_service.get_audit_service")
    def test_log_action_convenience(self, mock_get_service):
        """Test log_action convenience wrapper"""
        mock_service = MagicMock()
        mock_service.log_action.return_value = True
        mock_get_service.return_value = mock_service

        result = log_action(user_id="user-123", action="test", resource_type="test")

        assert result is True
        mock_service.log_action.assert_called_once()

    @patch("open_webui.services.audit_service.get_audit_service")
    def test_log_search_convenience(self, mock_get_service):
        """Test log_search convenience wrapper"""
        mock_service = MagicMock()
        mock_service.log_search.return_value = True
        mock_get_service.return_value = mock_service

        result = log_search(user_id="user-123", query="test")

        assert result is True
        mock_service.log_search.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
