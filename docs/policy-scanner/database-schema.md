# Policy Scanner Database Schema

## Overview

The Policy Scanner uses a dedicated PostgreSQL schema (`policy_scanner`) with 15 tables designed for scalability, efficient querying, and data integrity.

**Migration File**: `backend/open_webui/migrations/versions/a1b2c3d4e5f6_policy_scanner_schema.py`

## Schema Diagram

```
policy_scanner
├── sources (policy source configurations)
├── source_configurations (additional source settings)
├── documents (master document table)
├── document_content (extracted text and files)
├── document_versions (version history)
├── categories (hierarchical categories)
├── category_hierarchy (materialized path for tree queries)
├── document_categories (document-category assignments)
├── tags (flexible tagging)
├── document_tags (document-tag assignments)
├── scan_jobs (scanning operations)
├── scan_history (detailed scan logs)
├── search_queries (user search analytics)
├── saved_searches (user saved searches)
└── user_favorites (bookmarked documents)
```

## Table Definitions

### 1. sources

Policy source configurations (e.g., Gemeenteblad, DSO).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| name | VARCHAR(255) | NOT NULL, UNIQUE | Source name |
| source_type | VARCHAR(50) | NOT NULL, CHECK | Type: gemeenteblad, dso, custom |
| base_url | TEXT | NOT NULL | Base URL for scraping |
| selector_config | JSON | NOT NULL | CSS selectors, pagination rules |
| auth_config | JSON | NULL | API keys, auth headers (encrypted) |
| rate_limit | INTEGER | DEFAULT 10 | Requests per second |
| is_active | BOOLEAN | DEFAULT true | Soft delete flag |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| created_by | VARCHAR(36) | FK → user.id | Creator user ID |

**Indexes**:
- `idx_sources_active` on `is_active`
- `idx_sources_type` on `source_type`

### 2. documents

Master table for all policy documents.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| source_id | VARCHAR(36) | FK → sources.id | Source reference |
| external_id | VARCHAR(500) | NULL | ID from source system |
| title | TEXT | NOT NULL | Document title |
| description | TEXT | NULL | Document description |
| content_hash | VARCHAR(64) | NOT NULL, UNIQUE | SHA-256 for deduplication |
| document_url | TEXT | NOT NULL | Original URL |
| document_type | VARCHAR(20) | CHECK | pdf, html, docx, xlsx |
| municipality | VARCHAR(255) | NULL | Municipality name |
| publication_date | DATE | NULL | Publication date |
| effective_date | DATE | NULL | Effective date |
| file_size | BIGINT | NULL | File size in bytes |
| page_count | INTEGER | NULL | Number of pages |
| language | VARCHAR(10) | DEFAULT 'nl' | Document language |
| status | VARCHAR(20) | DEFAULT 'pending' | pending, processing, indexed, failed, archived |
| metadata | JSON | NULL | Additional metadata |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Last update timestamp |
| indexed_at | DATETIME | NULL | Indexing completion timestamp |

**Unique Constraints**:
- `(source_id, external_id)` - No duplicates from same source
- `content_hash` - Content-based deduplication

**Indexes**:
- `idx_documents_source` on `source_id`
- `idx_documents_status` on `status`
- `idx_documents_municipality` on `municipality`
- `idx_documents_pub_date` on `publication_date DESC`
- `idx_documents_hash` on `content_hash`

### 3. document_content

Stores extracted text and processed versions of documents.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| document_id | VARCHAR(36) | FK → documents.id | Document reference |
| content_type | VARCHAR(20) | CHECK | original, processed, text, preview |
| content_text | TEXT | NULL | Extracted text content |
| storage_path | TEXT | NULL | Path to stored file (MinIO/S3) |
| file_size | BIGINT | NULL | File size in bytes |
| mime_type | VARCHAR(100) | NULL | MIME type |
| checksum | VARCHAR(64) | NULL | File checksum |
| created_at | DATETIME | NOT NULL | Creation timestamp |

**Indexes**:
- `idx_document_content_document` on `document_id`
- `idx_document_content_type` on `content_type`

### 4. categories

Hierarchical category structure using LTREE (PostgreSQL).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| parent_id | VARCHAR(36) | FK → categories.id | Parent category |
| name | VARCHAR(255) | NOT NULL | Category name |
| slug | VARCHAR(255) | NOT NULL, UNIQUE | URL-friendly slug |
| description | TEXT | NULL | Category description |
| icon | VARCHAR(50) | NULL | Icon name |
| color | VARCHAR(7) | NULL | Hex color code |
| path | TEXT | NULL | LTREE hierarchical path |
| sort_order | INTEGER | DEFAULT 0 | Display order |
| is_active | BOOLEAN | DEFAULT true | Active flag |
| created_at | DATETIME | NOT NULL | Creation timestamp |

**Unique Constraints**:
- `slug` - Globally unique slug
- `(parent_id, name)` - Unique name within parent

**Indexes**:
- `idx_categories_parent` on `parent_id`
- `idx_categories_active` on `is_active`

### 5. document_categories

Many-to-many relationship between documents and categories.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| document_id | VARCHAR(36) | FK → documents.id, PK | Document reference |
| category_id | VARCHAR(36) | FK → categories.id, PK | Category reference |
| confidence_score | NUMERIC(3,2) | CHECK 0-1 | AI confidence score |
| assigned_by | VARCHAR(20) | CHECK | auto, rule, manual |
| assigned_at | DATETIME | NOT NULL | Assignment timestamp |

**Indexes**:
- `idx_doc_cats_category` on `category_id`

### 6. category_hierarchy

Materialized path for efficient category tree queries (closure table pattern).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| ancestor_id | VARCHAR(36) | FK → categories.id, PK | Ancestor category |
| descendant_id | VARCHAR(36) | FK → categories.id, PK | Descendant category |
| depth | INTEGER | NOT NULL | Levels between ancestor-descendant |

**Indexes**:
- `idx_category_hierarchy_ancestor` on `ancestor_id`
- `idx_category_hierarchy_descendant` on `descendant_id`

### 7. tags

Flexible tagging system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Tag name |
| description | TEXT | NULL | Tag description |
| color | VARCHAR(7) | NULL | Hex color code |
| created_at | DATETIME | NOT NULL | Creation timestamp |

### 8. document_tags

Many-to-many relationship between documents and tags.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| document_id | VARCHAR(36) | FK → documents.id, PK | Document reference |
| tag_id | VARCHAR(36) | FK → tags.id, PK | Tag reference |
| tagged_at | DATETIME | NOT NULL | Tagging timestamp |
| tagged_by | VARCHAR(36) | FK → user.id | User who tagged |

### 9. scan_jobs

Tracks scanning operations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| source_id | VARCHAR(36) | FK → sources.id | Source reference |
| job_type | VARCHAR(20) | CHECK | full, incremental, manual |
| status | VARCHAR(20) | DEFAULT 'pending' | Job status |
| started_at | DATETIME | NULL | Start timestamp |
| completed_at | DATETIME | NULL | Completion timestamp |
| documents_found | INTEGER | DEFAULT 0 | Total documents found |
| documents_new | INTEGER | DEFAULT 0 | New documents |
| documents_updated | INTEGER | DEFAULT 0 | Updated documents |
| documents_failed | INTEGER | DEFAULT 0 | Failed documents |
| error_details | JSON | NULL | Error information |
| triggered_by | VARCHAR(36) | FK → user.id | User who triggered |
| job_config | JSON | NULL | Job configuration |
| created_at | DATETIME | NOT NULL | Creation timestamp |

**Indexes**:
- `idx_scan_jobs_source` on `source_id`
- `idx_scan_jobs_status` on `status`
- `idx_scan_jobs_created` on `created_at DESC`

### 10. scan_history

Detailed log of scan operations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| job_id | VARCHAR(36) | FK → scan_jobs.id | Job reference |
| document_id | VARCHAR(36) | FK → documents.id | Document reference |
| action | VARCHAR(20) | CHECK | discover, download, extract, index, categorize |
| status | VARCHAR(20) | CHECK | success, failed, skipped |
| details | JSON | NULL | Additional details |
| error_message | TEXT | NULL | Error message |
| created_at | DATETIME | NOT NULL | Creation timestamp |

**Indexes**:
- `idx_scan_history_job` on `job_id`
- `idx_scan_history_document` on `document_id`

### 11. search_queries

User search analytics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| user_id | VARCHAR(36) | FK → user.id | User reference |
| query_text | TEXT | NULL | Search query |
| filters | JSON | NULL | Applied filters |
| result_count | INTEGER | DEFAULT 0 | Number of results |
| clicked_results | JSON | NULL | Array of clicked document IDs |
| search_type | VARCHAR(20) | DEFAULT 'keyword' | keyword, semantic, hybrid |
| response_time_ms | INTEGER | NULL | Response time in milliseconds |
| created_at | DATETIME | NOT NULL | Creation timestamp |

**Indexes**:
- `idx_search_queries_user` on `(user_id, created_at DESC)`

### 12. saved_searches

User saved searches with notifications.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| user_id | VARCHAR(36) | FK → user.id | User reference |
| name | VARCHAR(255) | NOT NULL | Search name |
| query_text | TEXT | NULL | Search query |
| filters | JSON | NULL | Search filters |
| notification_enabled | BOOLEAN | DEFAULT false | Enable notifications |
| notification_frequency | VARCHAR(20) | CHECK | immediate, daily, weekly |
| last_notified_at | DATETIME | NULL | Last notification timestamp |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Last update timestamp |

**Indexes**:
- `idx_saved_searches_user` on `user_id`

### 13. user_favorites

User bookmarked documents.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | VARCHAR(36) | FK → user.id, PK | User reference |
| document_id | VARCHAR(36) | FK → documents.id, PK | Document reference |
| notes | TEXT | NULL | User notes |
| created_at | DATETIME | NOT NULL | Creation timestamp |

### 14. document_versions

Version history for documents.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| document_id | VARCHAR(36) | FK → documents.id | Document reference |
| version_number | INTEGER | NOT NULL | Version number |
| content_hash | VARCHAR(64) | NOT NULL | Content hash of this version |
| changes_summary | TEXT | NULL | Summary of changes |
| metadata | JSON | NULL | Version metadata |
| created_at | DATETIME | NOT NULL | Creation timestamp |

**Unique Constraints**:
- `(document_id, version_number)` - One version number per document

**Indexes**:
- `idx_document_versions_document` on `(document_id, version_number DESC)`

### 15. source_configurations

Additional source-specific configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| source_id | VARCHAR(36) | FK → sources.id | Source reference |
| config_key | VARCHAR(100) | NOT NULL | Configuration key |
| config_value | JSON | NOT NULL | Configuration value |
| description | TEXT | NULL | Configuration description |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Last update timestamp |

**Unique Constraints**:
- `(source_id, config_key)` - One value per key per source

## Migration Commands

### Apply Migration

```bash
cd backend/open_webui
alembic upgrade head
```

### Rollback Migration

```bash
cd backend/open_webui
alembic downgrade -1
```

### Verify Migration

```bash
cd backend/open_webui
alembic current
```

## Database Maintenance

### Vacuum and Analyze

```sql
VACUUM ANALYZE policy_scanner.documents;
VACUUM ANALYZE policy_scanner.categories;
```

### Check Index Usage

```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'policy_scanner'
ORDER BY idx_scan DESC;
```

### Table Sizes

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'policy_scanner'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Foreign Key Cascade Behavior

- `documents.source_id` → `sources.id` ON DELETE CASCADE
  - Deleting a source deletes all its documents
- `document_content.document_id` → `documents.id` ON DELETE CASCADE
  - Deleting a document deletes all its content
- `document_categories.document_id` → `documents.id` ON DELETE CASCADE
  - Deleting a document removes all category assignments
- `categories.parent_id` → `categories.id` ON DELETE SET NULL
  - Deleting a category orphans its children (parent_id = NULL)
- `user_favorites.document_id` → `documents.id` ON DELETE CASCADE
  - Deleting a document removes from all favorites

## Data Integrity

1. **Content Hash Uniqueness**: Prevents duplicate documents
2. **External ID Uniqueness**: Within a source, prevents duplicate imports
3. **Hierarchical Integrity**: Categories maintain proper parent-child relationships
4. **Referential Integrity**: All foreign keys enforce relationships
5. **Soft Deletes**: Sources use `is_active` for soft deletion

## Performance Considerations

1. **Partitioning**: Consider partitioning `documents` by `publication_date` for large datasets
2. **Archival**: Move old documents to `status='archived'` and separate storage
3. **Index Maintenance**: Regularly rebuild indexes on high-write tables
4. **Query Optimization**: Use EXPLAIN ANALYZE for slow queries
5. **Connection Pooling**: Configure appropriate pool size in `internal/db.py`

## Security

1. **Schema Isolation**: Separate schema for clear boundaries
2. **Encrypted Credentials**: `auth_config` should store encrypted API keys
3. **Audit Trail**: All tables track creation timestamps
4. **User Attribution**: `created_by` and `tagged_by` track user actions
5. **Parameterized Queries**: All queries use parameterized statements (SQLAlchemy)
