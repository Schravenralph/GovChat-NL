"""Policy Scanner schema - Create policy_scanner schema with 15 core tables

Revision ID: a1b2c3d4e5f6
Revises: c69f45358db4
Create Date: 2025-10-29 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "a1b2c3d4e5f6"
down_revision = "c69f45358db4"
branch_labels = None
depends_on = None


def upgrade():
    # Create policy_scanner schema
    op.execute("CREATE SCHEMA IF NOT EXISTS policy_scanner")

    # Enable LTREE extension for hierarchical categories (PostgreSQL only)
    # This will fail gracefully on SQLite/MySQL
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS ltree")
    except Exception:
        pass

    # 1. Sources - Policy source configuration
    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column(
            "source_type",
            sa.String(length=50),
            nullable=False,
            server_default="custom",
        ),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("selector_config", sa.JSON(), nullable=False),
        sa.Column("auth_config", sa.JSON(), nullable=True),
        sa.Column("rate_limit", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.CheckConstraint(
            "source_type IN ('gemeenteblad', 'dso', 'custom')",
            name="ck_sources_source_type",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["user.id"], ondelete="SET NULL"),
        schema="policy_scanner",
    )

    # 2. Documents - Master table for all policy documents
    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("external_id", sa.String(length=500), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("document_url", sa.Text(), nullable=False),
        sa.Column(
            "document_type",
            sa.String(length=20),
            nullable=True,
        ),
        sa.Column("municipality", sa.String(length=255), nullable=True),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=False, server_default="nl"),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.Column("indexed_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "document_type IN ('pdf', 'html', 'docx', 'xlsx')",
            name="ck_documents_document_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'indexed', 'failed', 'archived')",
            name="ck_documents_status",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["policy_scanner.sources.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("source_id", "external_id", name="uq_documents_source_external"),
        schema="policy_scanner",
    )

    # 3. Document Content - Extracted text and processed content
    op.create_table(
        "document_content",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("content_type", sa.String(length=20), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=True),
        sa.Column("storage_path", sa.Text(), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "content_type IN ('original', 'processed', 'text', 'preview')",
            name="ck_document_content_content_type",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["policy_scanner.documents.id"],
            ondelete="CASCADE",
        ),
        schema="policy_scanner",
    )

    # 4. Categories - Hierarchical category structure
    op.create_table(
        "categories",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("parent_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("path", sa.Text(), nullable=True),  # LTREE path for hierarchy
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["policy_scanner.categories.id"],
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint("parent_id", "name", name="uq_categories_parent_name"),
        schema="policy_scanner",
    )

    # 5. Document Categories - Many-to-many relationship
    op.create_table(
        "document_categories",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("category_id", sa.String(length=36), nullable=False),
        sa.Column("confidence_score", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column(
            "assigned_by",
            sa.String(length=20),
            nullable=False,
            server_default="auto",
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "confidence_score BETWEEN 0 AND 1",
            name="ck_document_categories_confidence",
        ),
        sa.CheckConstraint(
            "assigned_by IN ('auto', 'rule', 'manual')",
            name="ck_document_categories_assigned_by",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["policy_scanner.documents.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["policy_scanner.categories.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("document_id", "category_id"),
        schema="policy_scanner",
    )

    # 6. Tags - Flexible tagging system
    op.create_table(
        "tags",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        schema="policy_scanner",
    )

    # 7. Document Tags - Many-to-many relationship
    op.create_table(
        "document_tags",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("tag_id", sa.String(length=36), nullable=False),
        sa.Column(
            "tagged_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("tagged_by", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["policy_scanner.documents.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["policy_scanner.tags.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["tagged_by"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("document_id", "tag_id"),
        schema="policy_scanner",
    )

    # 8. Scan Jobs - Track scanning operations
    op.create_table(
        "scan_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_id", sa.String(length=36), nullable=True),
        sa.Column(
            "job_type",
            sa.String(length=20),
            nullable=False,
            server_default="incremental",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("documents_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("documents_new", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("documents_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("documents_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_details", sa.JSON(), nullable=True),
        sa.Column("triggered_by", sa.String(length=36), nullable=True),
        sa.Column("job_config", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "job_type IN ('full', 'incremental', 'manual')",
            name="ck_scan_jobs_job_type",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["policy_scanner.sources.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["triggered_by"], ["user.id"], ondelete="SET NULL"),
        schema="policy_scanner",
    )

    # 9. Scan History - Detailed log of scan operations
    op.create_table(
        "scan_history",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "action IN ('discover', 'download', 'extract', 'index', 'categorize')",
            name="ck_scan_history_action",
        ),
        sa.CheckConstraint(
            "status IN ('success', 'failed', 'skipped')",
            name="ck_scan_history_status",
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["policy_scanner.scan_jobs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["policy_scanner.documents.id"],
            ondelete="SET NULL",
        ),
        schema="policy_scanner",
    )

    # 10. Search Queries - Track user searches for analytics
    op.create_table(
        "search_queries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("query_text", sa.Text(), nullable=True),
        sa.Column("filters", sa.JSON(), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("clicked_results", sa.JSON(), nullable=True),  # Array of document IDs
        sa.Column(
            "search_type",
            sa.String(length=20),
            nullable=False,
            server_default="keyword",
        ),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "search_type IN ('keyword', 'semantic', 'hybrid')",
            name="ck_search_queries_search_type",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        schema="policy_scanner",
    )

    # 11. Saved Searches - User's saved search configurations
    op.create_table(
        "saved_searches",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=True),
        sa.Column("filters", sa.JSON(), nullable=True),
        sa.Column(
            "notification_enabled",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "notification_frequency",
            sa.String(length=20),
            nullable=True,
        ),
        sa.Column("last_notified_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.CheckConstraint(
            "notification_frequency IN ('immediate', 'daily', 'weekly')",
            name="ck_saved_searches_notification_frequency",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        schema="policy_scanner",
    )

    # 12. User Favorites - Bookmarked documents
    op.create_table(
        "user_favorites",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["policy_scanner.documents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "document_id"),
        schema="policy_scanner",
    )

    # 13. Document Versions - Track document changes over time
    op.create_table(
        "document_versions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("changes_summary", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["policy_scanner.documents.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "document_id", "version_number", name="uq_document_versions_doc_version"
        ),
        schema="policy_scanner",
    )

    # 14. Category Hierarchy - Materialized path for category tree
    op.create_table(
        "category_hierarchy",
        sa.Column("ancestor_id", sa.String(length=36), nullable=False),
        sa.Column("descendant_id", sa.String(length=36), nullable=False),
        sa.Column("depth", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ancestor_id"],
            ["policy_scanner.categories.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["descendant_id"],
            ["policy_scanner.categories.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("ancestor_id", "descendant_id"),
        schema="policy_scanner",
    )

    # 15. Source Configurations - Additional source-specific settings
    op.create_table(
        "source_configurations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("config_key", sa.String(length=100), nullable=False),
        sa.Column("config_value", sa.JSON(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["policy_scanner.sources.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("source_id", "config_key", name="uq_source_configurations_source_key"),
        schema="policy_scanner",
    )

    # Create indexes for optimal query performance

    # Sources indexes
    op.create_index(
        "idx_sources_active",
        "sources",
        ["is_active"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_sources_type",
        "sources",
        ["source_type"],
        schema="policy_scanner",
    )

    # Documents indexes
    op.create_index(
        "idx_documents_source",
        "documents",
        ["source_id"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_documents_status",
        "documents",
        ["status"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_documents_municipality",
        "documents",
        ["municipality"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_documents_pub_date",
        "documents",
        [sa.text("publication_date DESC")],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_documents_hash",
        "documents",
        ["content_hash"],
        schema="policy_scanner",
    )

    # Document content indexes
    op.create_index(
        "idx_document_content_document",
        "document_content",
        ["document_id"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_document_content_type",
        "document_content",
        ["content_type"],
        schema="policy_scanner",
    )

    # Categories indexes
    op.create_index(
        "idx_categories_parent",
        "categories",
        ["parent_id"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_categories_active",
        "categories",
        ["is_active"],
        schema="policy_scanner",
    )

    # Document categories indexes
    op.create_index(
        "idx_doc_cats_category",
        "document_categories",
        ["category_id"],
        schema="policy_scanner",
    )

    # Scan jobs indexes
    op.create_index(
        "idx_scan_jobs_source",
        "scan_jobs",
        ["source_id"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_scan_jobs_status",
        "scan_jobs",
        ["status"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_scan_jobs_created",
        "scan_jobs",
        [sa.text("created_at DESC")],
        schema="policy_scanner",
    )

    # Scan history indexes
    op.create_index(
        "idx_scan_history_job",
        "scan_history",
        ["job_id"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_scan_history_document",
        "scan_history",
        ["document_id"],
        schema="policy_scanner",
    )

    # Search queries indexes
    op.create_index(
        "idx_search_queries_user",
        "search_queries",
        ["user_id", sa.text("created_at DESC")],
        schema="policy_scanner",
    )

    # Saved searches indexes
    op.create_index(
        "idx_saved_searches_user",
        "saved_searches",
        ["user_id"],
        schema="policy_scanner",
    )

    # Document versions indexes
    op.create_index(
        "idx_document_versions_document",
        "document_versions",
        ["document_id", sa.text("version_number DESC")],
        schema="policy_scanner",
    )

    # Category hierarchy indexes
    op.create_index(
        "idx_category_hierarchy_ancestor",
        "category_hierarchy",
        ["ancestor_id"],
        schema="policy_scanner",
    )
    op.create_index(
        "idx_category_hierarchy_descendant",
        "category_hierarchy",
        ["descendant_id"],
        schema="policy_scanner",
    )


def downgrade():
    # Drop all indexes first
    op.drop_index("idx_category_hierarchy_descendant", table_name="category_hierarchy", schema="policy_scanner")
    op.drop_index("idx_category_hierarchy_ancestor", table_name="category_hierarchy", schema="policy_scanner")
    op.drop_index("idx_document_versions_document", table_name="document_versions", schema="policy_scanner")
    op.drop_index("idx_saved_searches_user", table_name="saved_searches", schema="policy_scanner")
    op.drop_index("idx_search_queries_user", table_name="search_queries", schema="policy_scanner")
    op.drop_index("idx_scan_history_document", table_name="scan_history", schema="policy_scanner")
    op.drop_index("idx_scan_history_job", table_name="scan_history", schema="policy_scanner")
    op.drop_index("idx_scan_jobs_created", table_name="scan_jobs", schema="policy_scanner")
    op.drop_index("idx_scan_jobs_status", table_name="scan_jobs", schema="policy_scanner")
    op.drop_index("idx_scan_jobs_source", table_name="scan_jobs", schema="policy_scanner")
    op.drop_index("idx_doc_cats_category", table_name="document_categories", schema="policy_scanner")
    op.drop_index("idx_categories_active", table_name="categories", schema="policy_scanner")
    op.drop_index("idx_categories_parent", table_name="categories", schema="policy_scanner")
    op.drop_index("idx_document_content_type", table_name="document_content", schema="policy_scanner")
    op.drop_index("idx_document_content_document", table_name="document_content", schema="policy_scanner")
    op.drop_index("idx_documents_hash", table_name="documents", schema="policy_scanner")
    op.drop_index("idx_documents_pub_date", table_name="documents", schema="policy_scanner")
    op.drop_index("idx_documents_municipality", table_name="documents", schema="policy_scanner")
    op.drop_index("idx_documents_status", table_name="documents", schema="policy_scanner")
    op.drop_index("idx_documents_source", table_name="documents", schema="policy_scanner")
    op.drop_index("idx_sources_type", table_name="sources", schema="policy_scanner")
    op.drop_index("idx_sources_active", table_name="sources", schema="policy_scanner")

    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_table("source_configurations", schema="policy_scanner")
    op.drop_table("category_hierarchy", schema="policy_scanner")
    op.drop_table("document_versions", schema="policy_scanner")
    op.drop_table("user_favorites", schema="policy_scanner")
    op.drop_table("saved_searches", schema="policy_scanner")
    op.drop_table("search_queries", schema="policy_scanner")
    op.drop_table("scan_history", schema="policy_scanner")
    op.drop_table("scan_jobs", schema="policy_scanner")
    op.drop_table("document_tags", schema="policy_scanner")
    op.drop_table("tags", schema="policy_scanner")
    op.drop_table("document_categories", schema="policy_scanner")
    op.drop_table("categories", schema="policy_scanner")
    op.drop_table("document_content", schema="policy_scanner")
    op.drop_table("documents", schema="policy_scanner")
    op.drop_table("sources", schema="policy_scanner")

    # Drop schema
    op.execute("DROP SCHEMA IF EXISTS policy_scanner CASCADE")
