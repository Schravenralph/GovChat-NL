"""Add Policy Scanner audit logs table

Revision ID: b7c8d9e0f1g2
Revises: a1b2c3d4e5f6
Create Date: 2025-10-29 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7c8d9e0f1g2"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create audit_logs table in policy_scanner schema
    op.execute("CREATE SCHEMA IF NOT EXISTS policy_scanner")

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String, primary_key=True, server_default=sa.text("gen_random_uuid()::text")),
        sa.Column("user_id", sa.String, nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String, nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="success"),
        sa.Column("timestamp", sa.BigInteger, nullable=False),
        schema="policy_scanner",
    )

    # Create indexes for efficient querying
    op.create_index(
        "idx_audit_logs_user_id",
        "audit_logs",
        ["user_id", "timestamp"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_audit_logs_action",
        "audit_logs",
        ["action"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_audit_logs_resource",
        "audit_logs",
        ["resource_type", "resource_id"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_audit_logs_timestamp",
        "audit_logs",
        ["timestamp"],
        schema="policy_scanner",
    )

    # Add foreign key to user table if it exists
    # Note: This assumes the user table is in the default/public schema
    try:
        op.create_foreign_key(
            "fk_audit_logs_user",
            "audit_logs",
            "user",
            ["user_id"],
            ["id"],
            source_schema="policy_scanner",
            referent_schema=None,  # default schema
            ondelete="CASCADE",
        )
    except Exception:
        # If user table doesn't exist or FK creation fails, continue without it
        pass


def downgrade():
    # Drop indexes
    op.drop_index(
        "idx_audit_logs_timestamp",
        table_name="audit_logs",
        schema="policy_scanner",
    )
    op.drop_index(
        "idx_audit_logs_resource",
        table_name="audit_logs",
        schema="policy_scanner",
    )
    op.drop_index(
        "idx_audit_logs_action",
        table_name="audit_logs",
        schema="policy_scanner",
    )
    op.drop_index(
        "idx_audit_logs_user_id",
        table_name="audit_logs",
        schema="policy_scanner",
    )

    # Drop table
    op.drop_table("audit_logs", schema="policy_scanner")
