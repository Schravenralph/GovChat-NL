# Policy Scanner Documentation

## Overview

The Policy Scanner is a comprehensive document management system integrated into GovChat-NL for scanning, indexing, and searching Dutch government policy documents.

## Documentation Index

1. **[Database Schema](./database-schema.md)** - Complete database schema with 15 tables
2. **[API Contracts](./api-contracts.md)** - RESTful API documentation with examples
3. **[Architecture](../../policy-scanner-architecture.md)** - Full system architecture design

## Quick Start

### Prerequisites

- PostgreSQL 12+ with LTREE extension
- Python 3.10+
- Existing GovChat-NL installation

### Installation

1. **Apply Database Migration**:
```bash
cd backend/open_webui
alembic upgrade head
```

2. **Verify Migration**:
```bash
alembic current
# Should show: a1b2c3d4e5f6 (head)
```

3. **Check Tables**:
```sql
SELECT tablename FROM pg_tables WHERE schemaname = 'policy_scanner';
```

Expected output: 15 tables

### API Access

All API endpoints are prefixed with:
```
/api/v1/policy
```

**Routers**:
- `/sources` - Policy source management (admin)
- `/documents` - Document retrieval (authenticated)
- `/search` - Search functionality (authenticated)

### Authentication

Use existing GovChat-NL authentication:
```bash
curl -H "Authorization: Bearer <token>" \
  https://your-domain.com/api/v1/policy/documents
```

## Phase 1 Implementation Status

### ✅ Completed

- [x] Database schema (15 tables in `policy_scanner` schema)
- [x] Alembic migration with rollback support
- [x] SQLAlchemy models with CRUD operations
- [x] API routers with authentication integration
- [x] Source management API (admin-only)
- [x] Document retrieval API
- [x] Search API (stub for Phase 2)
- [x] User favorites and saved searches
- [x] Documentation (schema + API contracts)

### 🚧 Phase 2 (Not Yet Implemented)

- [ ] Meilisearch integration for full-text search
- [ ] Actual scraper implementations (Gemeenteblad, DSO)
- [ ] Document processing pipeline
- [ ] Background job queue (RabbitMQ)
- [ ] Rate limiting implementation
- [ ] Admin dashboard UI
- [ ] Search UI integration

### 📅 Phase 3 (Planned)

- [ ] Qdrant vector database
- [ ] Semantic search with embeddings
- [ ] AI-powered categorization
- [ ] Hybrid search (keyword + semantic)
- [ ] Performance optimization

## Database Models

### Core Models

1. **PolicySource** - Policy source configurations
   - CRUD: Create, Read, Update, Deactivate, Delete
   - File: `models/policy_sources.py`

2. **PolicyDocument** - Document master table
   - CRUD: Create, Read, Update, Delete
   - Favorites support
   - File: `models/policy_documents.py`

3. **PolicyCategory** - Hierarchical categories
   - CRUD: Create, Read, Update, Delete
   - Hierarchy traversal
   - File: `models/policy_categories.py`

4. **ScanJob** - Scan job tracking
   - Status tracking
   - Statistics (found, new, updated, failed)

5. **SavedSearch** - User saved searches
   - Notification support (immediate, daily, weekly)

## API Examples

### Get Documents

```bash
curl -H "Authorization: Bearer <token>" \
  "https://api.example.com/api/v1/policy/documents?municipality=Amsterdam&limit=10"
```

### Search Documents

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "parkeerbeleid",
    "filters": {
      "municipalities": ["Amsterdam"],
      "date_from": "2025-01-01"
    },
    "page": 1,
    "limit": 20,
    "sort": "date_desc"
  }' \
  https://api.example.com/api/v1/policy/search
```

### Create Policy Source (Admin)

```bash
curl -X POST \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gemeenteblad Amsterdam",
    "source_type": "gemeenteblad",
    "base_url": "https://gemeenteblad.nl/amsterdam",
    "selector_config": {
      "item": ".document-item",
      "title": "h2.title",
      "url": "a.download-link"
    },
    "rate_limit": 10
  }' \
  https://api.example.com/api/v1/policy/sources
```

## Database Maintenance

### Backup

```bash
pg_dump -U postgres -n policy_scanner govchat_db > policy_scanner_backup.sql
```

### Restore

```bash
psql -U postgres govchat_db < policy_scanner_backup.sql
```

### Check Table Sizes

```sql
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size('policy_scanner.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'policy_scanner'
ORDER BY pg_total_relation_size('policy_scanner.'||tablename) DESC;
```

## Troubleshooting

### Migration Fails

**Issue**: `relation "policy_scanner.sources" already exists`

**Solution**:
```bash
# Rollback migration
alembic downgrade -1

# Reapply migration
alembic upgrade head
```

### LTREE Extension Missing

**Issue**: `type "ltree" does not exist`

**Solution**:
```sql
CREATE EXTENSION IF NOT EXISTS ltree;
```

### Foreign Key Violations

**Issue**: Cannot delete source because documents exist

**Solution**:
```bash
# Use soft delete (deactivate)
curl -X DELETE \
  -H "Authorization: Bearer <token>" \
  https://api.example.com/api/v1/policy/sources/{source_id}/deactivate
```

## Security Considerations

1. **Admin-Only Operations**:
   - Source management
   - Document creation
   - Category assignment
   - Scan job triggering

2. **User Operations**:
   - Document viewing
   - Search
   - Favorites management
   - Saved searches

3. **Data Protection**:
   - `auth_config` should store encrypted credentials
   - All queries use parameterized statements
   - Schema isolation (`policy_scanner` namespace)

4. **Audit Trail**:
   - `created_by` tracks source creators
   - `tagged_by` tracks tag assignments
   - `triggered_by` tracks scan job initiators
   - All tables have `created_at` timestamps

## Performance Tips

1. **Indexing**: All critical queries have appropriate indexes
2. **Pagination**: Always use `limit` and `offset` for large result sets
3. **Caching**: Consider caching search filter options
4. **Partitioning**: For >1M documents, partition by `publication_date`
5. **Archival**: Move old documents to `status='archived'`

## Testing

### Unit Tests

```bash
cd backend/open_webui
pytest test/models/test_policy_sources.py -v
pytest test/models/test_policy_documents.py -v
pytest test/routers/test_policy_api.py -v
```

### Integration Tests

```bash
pytest test/integration/test_policy_scanner.py -v
```

### Coverage Report

```bash
pytest --cov=open_webui.models.policy_sources \
       --cov=open_webui.models.policy_documents \
       --cov=open_webui.models.policy_categories \
       --cov=open_webui.routers.policy_sources \
       --cov=open_webui.routers.policy_documents \
       --cov=open_webui.routers.policy_search \
       --cov-report=html
```

## Support

For questions or issues:

1. Check existing documentation
2. Review architecture document
3. Consult API contracts
4. Create GitHub issue with:
   - Description
   - Steps to reproduce
   - Expected vs actual behavior
   - Log excerpts

## Contributing

When contributing to Policy Scanner:

1. Follow existing code patterns
2. Write tests (target >90% coverage)
3. Update documentation
4. Use conventional commits
5. Run pre-commit hooks

## License

Same as GovChat-NL main project.
