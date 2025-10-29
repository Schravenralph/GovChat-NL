"""
Policy Scanner Audit Logging Service

Tracks user actions for compliance, analytics, and security monitoring.
"""

import logging
import json
import time
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta

from open_webui.internal.db import get_db
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("MAIN", logging.INFO))


class AuditService:
    """
    Service for logging and querying user actions in Policy Scanner.

    Tracks:
    - Search queries
    - Document views and downloads
    - Favorite additions/removals
    - Admin actions (source management, scans, categorization)
    """

    def __init__(self):
        self.enabled = True  # Will be configurable via env.py

    def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        status: str = "success",
    ) -> bool:
        """
        Log a user action to the audit log.

        Args:
            user_id: ID of the user performing the action
            action: Action type (e.g., "search", "view", "download", "create_source")
            resource_type: Type of resource (e.g., "document", "source", "category")
            resource_id: ID of the resource (optional)
            details: Additional metadata as dict (optional)
            ip_address: User's IP address (optional)
            status: Action status ("success", "failure", "error")

        Returns:
            True if logged successfully, False otherwise
        """
        if not self.enabled:
            return True  # Silently skip if disabled

        try:
            with get_db() as db:
                # Insert into audit_logs table
                query = """
                INSERT INTO policy_scanner.audit_logs
                (user_id, action, resource_type, resource_id, details, ip_address, status, timestamp)
                VALUES (:user_id, :action, :resource_type, :resource_id, :details, :ip_address, :status, :timestamp)
                """

                db.execute(
                    query,
                    {
                        "user_id": user_id,
                        "action": action,
                        "resource_type": resource_type,
                        "resource_id": resource_id,
                        "details": json.dumps(details) if details else None,
                        "ip_address": ip_address,
                        "status": status,
                        "timestamp": int(time.time()),
                    },
                )
                db.commit()

                log.debug(
                    f"Audit log: user={user_id}, action={action}, "
                    f"resource={resource_type}:{resource_id}, status={status}"
                )
                return True

        except Exception as e:
            log.exception(f"Failed to log audit action: {e}")
            return False

    def log_search(
        self,
        user_id: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        result_count: int = 0,
        response_time_ms: int = 0,
        ip_address: Optional[str] = None,
    ) -> bool:
        """
        Log a search action.

        Args:
            user_id: User ID
            query: Search query text
            filters: Search filters applied
            result_count: Number of results returned
            response_time_ms: Response time in milliseconds
            ip_address: User's IP address

        Returns:
            True if logged successfully
        """
        return self.log_action(
            user_id=user_id,
            action="search",
            resource_type="query",
            details={
                "query": query,
                "filters": filters,
                "result_count": result_count,
                "response_time_ms": response_time_ms,
            },
            ip_address=ip_address,
        )

    def log_document_view(
        self,
        user_id: str,
        document_id: str,
        ip_address: Optional[str] = None,
    ) -> bool:
        """
        Log a document view action.

        Args:
            user_id: User ID
            document_id: Document ID
            ip_address: User's IP address

        Returns:
            True if logged successfully
        """
        return self.log_action(
            user_id=user_id,
            action="view",
            resource_type="document",
            resource_id=document_id,
            ip_address=ip_address,
        )

    def log_document_download(
        self,
        user_id: str,
        document_id: str,
        format: str = "original",
        ip_address: Optional[str] = None,
    ) -> bool:
        """
        Log a document download action.

        Args:
            user_id: User ID
            document_id: Document ID
            format: Download format ("original", "pdf", "text")
            ip_address: User's IP address

        Returns:
            True if logged successfully
        """
        return self.log_action(
            user_id=user_id,
            action="download",
            resource_type="document",
            resource_id=document_id,
            details={"format": format},
            ip_address=ip_address,
        )

    def log_favorite_action(
        self,
        user_id: str,
        document_id: str,
        action: str,  # "add" or "remove"
        ip_address: Optional[str] = None,
    ) -> bool:
        """
        Log a favorite add/remove action.

        Args:
            user_id: User ID
            document_id: Document ID
            action: "add" or "remove"
            ip_address: User's IP address

        Returns:
            True if logged successfully
        """
        return self.log_action(
            user_id=user_id,
            action=f"favorite_{action}",
            resource_type="document",
            resource_id=document_id,
            ip_address=ip_address,
        )

    def log_admin_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        status: str = "success",
    ) -> bool:
        """
        Log an admin action (source management, scans, etc.).

        Args:
            user_id: Admin user ID
            action: Action type (e.g., "create_source", "trigger_scan", "delete_document")
            resource_type: Resource type (e.g., "source", "scan_job", "document")
            resource_id: Resource ID
            details: Additional metadata
            ip_address: User's IP address
            status: Action status

        Returns:
            True if logged successfully
        """
        return self.log_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            status=status,
        )

    def get_user_actions(
        self,
        user_id: str,
        action_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs for a specific user.

        Args:
            user_id: User ID
            action_type: Filter by action type (optional)
            limit: Maximum number of records
            offset: Pagination offset

        Returns:
            List of audit log records
        """
        try:
            with get_db() as db:
                query = """
                SELECT id, user_id, action, resource_type, resource_id,
                       details, ip_address, status, timestamp
                FROM policy_scanner.audit_logs
                WHERE user_id = :user_id
                """

                params = {"user_id": user_id, "limit": limit, "offset": offset}

                if action_type:
                    query += " AND action = :action_type"
                    params["action_type"] = action_type

                query += " ORDER BY timestamp DESC LIMIT :limit OFFSET :offset"

                result = db.execute(query, params)
                rows = result.fetchall()

                logs = []
                for row in rows:
                    log_entry = {
                        "id": row[0],
                        "user_id": row[1],
                        "action": row[2],
                        "resource_type": row[3],
                        "resource_id": row[4],
                        "details": json.loads(row[5]) if row[5] else None,
                        "ip_address": row[6],
                        "status": row[7],
                        "timestamp": row[8],
                    }
                    logs.append(log_entry)

                return logs

        except Exception as e:
            log.exception(f"Failed to get user actions: {e}")
            return []

    def get_resource_actions(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs for a specific resource.

        Args:
            resource_type: Resource type (e.g., "document", "source")
            resource_id: Resource ID
            limit: Maximum number of records

        Returns:
            List of audit log records
        """
        try:
            with get_db() as db:
                query = """
                SELECT id, user_id, action, resource_type, resource_id,
                       details, ip_address, status, timestamp
                FROM policy_scanner.audit_logs
                WHERE resource_type = :resource_type AND resource_id = :resource_id
                ORDER BY timestamp DESC
                LIMIT :limit
                """

                result = db.execute(
                    query,
                    {
                        "resource_type": resource_type,
                        "resource_id": resource_id,
                        "limit": limit,
                    },
                )
                rows = result.fetchall()

                logs = []
                for row in rows:
                    log_entry = {
                        "id": row[0],
                        "user_id": row[1],
                        "action": row[2],
                        "resource_type": row[3],
                        "resource_id": row[4],
                        "details": json.loads(row[5]) if row[5] else None,
                        "ip_address": row[6],
                        "status": row[7],
                        "timestamp": row[8],
                    }
                    logs.append(log_entry)

                return logs

        except Exception as e:
            log.exception(f"Failed to get resource actions: {e}")
            return []

    def get_audit_stats(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit log statistics for a date range.

        Args:
            start_date: Start date (default: 7 days ago)
            end_date: End date (default: now)

        Returns:
            Dictionary with statistics
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()

        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())

        try:
            with get_db() as db:
                # Total actions
                total_query = """
                SELECT COUNT(*) FROM policy_scanner.audit_logs
                WHERE timestamp >= :start_ts AND timestamp <= :end_ts
                """
                total_result = db.execute(
                    total_query, {"start_ts": start_ts, "end_ts": end_ts}
                )
                total_actions = total_result.fetchone()[0]

                # Actions by type
                type_query = """
                SELECT action, COUNT(*) as count
                FROM policy_scanner.audit_logs
                WHERE timestamp >= :start_ts AND timestamp <= :end_ts
                GROUP BY action
                ORDER BY count DESC
                """
                type_result = db.execute(
                    type_query, {"start_ts": start_ts, "end_ts": end_ts}
                )
                actions_by_type = {row[0]: row[1] for row in type_result.fetchall()}

                # Unique users
                users_query = """
                SELECT COUNT(DISTINCT user_id) FROM policy_scanner.audit_logs
                WHERE timestamp >= :start_ts AND timestamp <= :end_ts
                """
                users_result = db.execute(
                    users_query, {"start_ts": start_ts, "end_ts": end_ts}
                )
                unique_users = users_result.fetchone()[0]

                return {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_actions": total_actions,
                    "unique_users": unique_users,
                    "actions_by_type": actions_by_type,
                }

        except Exception as e:
            log.exception(f"Failed to get audit stats: {e}")
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_actions": 0,
                "unique_users": 0,
                "actions_by_type": {},
            }

    def cleanup_old_logs(self, retention_days: int = 90) -> int:
        """
        Delete audit logs older than retention period.

        Args:
            retention_days: Number of days to retain logs

        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cutoff_ts = int(cutoff_date.timestamp())

            with get_db() as db:
                result = db.execute(
                    """
                    DELETE FROM policy_scanner.audit_logs
                    WHERE timestamp < :cutoff_ts
                    """,
                    {"cutoff_ts": cutoff_ts},
                )
                deleted_count = result.rowcount
                db.commit()

                log.info(f"Deleted {deleted_count} audit logs older than {retention_days} days")
                return deleted_count

        except Exception as e:
            log.exception(f"Failed to cleanup old logs: {e}")
            return 0


# Singleton instance
_audit_service = None


def get_audit_service() -> AuditService:
    """
    Get or create the singleton AuditService instance.

    Returns:
        AuditService instance
    """
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service


# Convenience functions
def log_action(*args, **kwargs) -> bool:
    """Convenience wrapper for get_audit_service().log_action()"""
    return get_audit_service().log_action(*args, **kwargs)


def log_search(*args, **kwargs) -> bool:
    """Convenience wrapper for get_audit_service().log_search()"""
    return get_audit_service().log_search(*args, **kwargs)


def log_document_view(*args, **kwargs) -> bool:
    """Convenience wrapper for get_audit_service().log_document_view()"""
    return get_audit_service().log_document_view(*args, **kwargs)


def log_document_download(*args, **kwargs) -> bool:
    """Convenience wrapper for get_audit_service().log_document_download()"""
    return get_audit_service().log_document_download(*args, **kwargs)


def log_admin_action(*args, **kwargs) -> bool:
    """Convenience wrapper for get_audit_service().log_admin_action()"""
    return get_audit_service().log_admin_action(*args, **kwargs)
