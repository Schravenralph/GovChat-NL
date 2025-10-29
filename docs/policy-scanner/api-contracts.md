# Policy Scanner API Contracts

## Overview

The Policy Scanner exposes three main API routers for Phase 1:

1. **Policy Sources API** (`/api/v1/policy/sources`) - Admin-only source management
2. **Policy Documents API** (`/api/v1/policy/documents`) - Document retrieval and management
3. **Policy Search API** (`/api/v1/policy/search`) - Search functionality (stub for Phase 1)

All APIs follow OpenAPI 3.0 specification and integrate with existing GovChat-NL authentication.

## Authentication

All endpoints require authentication using the existing OpenWebUI auth system:

- **Bearer Token**: Include `Authorization: Bearer <token>` header
- **Roles**:
  - `user` - Authenticated user (can search, view documents, manage favorites)
  - `admin` - Administrator (can manage sources, trigger scans, create documents)

## Base URL

```
Production: https://your-domain.com/api/v1/policy
Development: http://localhost:8080/api/v1/policy
```

## API Routers

### 1. Policy Sources API

**Base Path**: `/api/v1/policy/sources`

**Router File**: `backend/open_webui/routers/policy_sources.py`

**Access**: Admin only

---

#### GET /sources

Get all policy sources.

**Query Parameters**:
- `active_only` (boolean, optional) - Filter for active sources only. Default: `false`

**Response**: 200 OK
```json
[
  {
    "id": "uuid-string",
    "name": "Gemeenteblad Amsterdam",
    "source_type": "gemeenteblad",
    "base_url": "https://gemeenteblad.nl/amsterdam",
    "selector_config": {
      "item": ".document-item",
      "title": "h2.title",
      "url": "a.download-link",
      "date": ".publication-date"
    },
    "auth_config": null,
    "rate_limit": 10,
    "is_active": true,
    "created_at": 1698765432,
    "created_by": "user-uuid"
  }
]
```

**Example**:
```bash
curl -H "Authorization: Bearer <token>" \
  "https://api.example.com/api/v1/policy/sources?active_only=true"
```

---

#### GET /sources/{source_id}

Get a specific policy source by ID.

**Path Parameters**:
- `source_id` (string, required) - Source UUID

**Response**: 200 OK
```json
{
  "id": "uuid-string",
  "name": "Gemeenteblad Amsterdam",
  "source_type": "gemeenteblad",
  "base_url": "https://gemeenteblad.nl/amsterdam",
  "selector_config": { ... },
  "auth_config": null,
  "rate_limit": 10,
  "is_active": true,
  "created_at": 1698765432,
  "created_by": "user-uuid"
}
```

**Errors**:
- `404 Not Found` - Source not found

---

#### POST /sources

Create a new policy source.

**Request Body**:
```json
{
  "name": "Gemeenteblad Rotterdam",
  "source_type": "gemeenteblad",
  "base_url": "https://gemeenteblad.nl/rotterdam",
  "selector_config": {
    "item": ".document-item",
    "title": "h2.title",
    "url": "a.download-link",
    "date": ".publication-date"
  },
  "auth_config": null,
  "rate_limit": 10,
  "is_active": true
}
```

**Field Validation**:
- `name`: 1-255 characters, unique
- `source_type`: Must be one of: `gemeenteblad`, `dso`, `custom`
- `base_url`: Valid URL
- `selector_config`: JSON object with selector mappings
- `rate_limit`: 1-100 requests per second

**Response**: 200 OK
```json
{
  "id": "new-uuid",
  "name": "Gemeenteblad Rotterdam",
  ...
}
```

**Errors**:
- `400 Bad Request` - Validation error or duplicate name

---

#### POST /sources/{source_id}/update

Update a policy source.

**Path Parameters**:
- `source_id` (string, required) - Source UUID

**Request Body** (all fields optional):
```json
{
  "name": "Updated Name",
  "rate_limit": 5,
  "is_active": false
}
```

**Response**: 200 OK
```json
{
  "id": "source-uuid",
  "name": "Updated Name",
  ...
}
```

**Errors**:
- `404 Not Found` - Source not found

---

#### DELETE /sources/{source_id}/deactivate

Deactivate a policy source (soft delete).

**Path Parameters**:
- `source_id` (string, required) - Source UUID

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Policy source deactivated successfully"
}
```

**Note**: This sets `is_active = false`. Documents are retained.

---

#### DELETE /sources/{source_id}/delete

Permanently delete a policy source.

**Path Parameters**:
- `source_id` (string, required) - Source UUID

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Policy source deleted successfully"
}
```

**Warning**: This CASCADE deletes all related documents!

---

#### POST /sources/{source_id}/scan

Trigger a manual scan job.

**Path Parameters**:
- `source_id` (string, required) - Source UUID

**Request Body**:
```json
{
  "job_type": "incremental",
  "job_config": {
    "start_date": "2025-01-01",
    "end_date": "2025-10-29"
  }
}
```

**Field Validation**:
- `job_type`: Must be one of: `full`, `incremental`, `manual`

**Response**: 200 OK
```json
{
  "id": "job-uuid",
  "source_id": "source-uuid",
  "job_type": "incremental",
  "status": "pending",
  "started_at": null,
  "completed_at": null,
  "documents_found": 0,
  "documents_new": 0,
  "documents_updated": 0,
  "documents_failed": 0,
  "error_details": null,
  "triggered_by": "user-uuid",
  "job_config": { ... },
  "created_at": 1698765432
}
```

**Errors**:
- `404 Not Found` - Source not found
- `400 Bad Request` - Source is inactive

---

#### GET /sources/{source_id}/scan/jobs

Get recent scan jobs for a source.

**Path Parameters**:
- `source_id` (string, required) - Source UUID

**Query Parameters**:
- `limit` (integer, optional) - Number of jobs to return. Default: `10`

**Response**: 200 OK
```json
[
  {
    "id": "job-uuid",
    "source_id": "source-uuid",
    "job_type": "incremental",
    "status": "completed",
    "started_at": 1698765432,
    "completed_at": 1698765532,
    "documents_found": 150,
    "documents_new": 10,
    "documents_updated": 5,
    "documents_failed": 2,
    "error_details": null,
    "triggered_by": "user-uuid",
    "job_config": null,
    "created_at": 1698765430
  }
]
```

---

#### GET /sources/scan/jobs/{job_id}

Get status of a specific scan job.

**Path Parameters**:
- `job_id` (string, required) - Job UUID

**Response**: 200 OK
```json
{
  "id": "job-uuid",
  "source_id": "source-uuid",
  "job_type": "incremental",
  "status": "running",
  "started_at": 1698765432,
  "completed_at": null,
  "documents_found": 50,
  "documents_new": 3,
  "documents_updated": 1,
  "documents_failed": 0,
  "error_details": null,
  "triggered_by": "user-uuid",
  "job_config": null,
  "created_at": 1698765430
}
```

**Job Statuses**:
- `pending` - Not yet started
- `running` - In progress
- `completed` - Finished successfully
- `failed` - Failed with errors

---

### 2. Policy Documents API

**Base Path**: `/api/v1/policy/documents`

**Router File**: `backend/open_webui/routers/policy_documents.py`

**Access**: Authenticated users (some endpoints admin-only)

---

#### GET /documents/{document_id}

Get a specific policy document by ID.

**Access**: All authenticated users

**Path Parameters**:
- `document_id` (string, required) - Document UUID

**Response**: 200 OK
```json
{
  "id": "doc-uuid",
  "source_id": "source-uuid",
  "external_id": "GB-2025-12345",
  "title": "Verordening Parkeerbeleid Amsterdam 2025",
  "description": "Nieuwe regels voor parkeren in de binnenstad",
  "content_hash": "sha256-hash",
  "document_url": "https://gemeenteblad.nl/doc/12345",
  "document_type": "pdf",
  "municipality": "Amsterdam",
  "publication_date": "2025-01-15",
  "effective_date": "2025-02-01",
  "file_size": 2048576,
  "page_count": 25,
  "language": "nl",
  "status": "indexed",
  "metadata": {
    "author": "Gemeente Amsterdam",
    "department": "Verkeer en Vervoer"
  },
  "created_at": 1698765432,
  "updated_at": 1698765532,
  "indexed_at": 1698765600
}
```

**Errors**:
- `404 Not Found` - Document not found

---

#### GET /documents

Get policy documents with optional filters.

**Access**: All authenticated users

**Query Parameters**:
- `source_id` (string, optional) - Filter by source ID
- `municipality` (string, optional) - Filter by municipality
- `status_filter` (string, optional) - Filter by status (pending, processing, indexed, failed, archived)
- `limit` (integer, optional) - Results per page. Max: 100. Default: `20`
- `offset` (integer, optional) - Pagination offset. Default: `0`

**Response**: 200 OK
```json
[
  {
    "id": "doc-uuid-1",
    "title": "Document 1",
    ...
  },
  {
    "id": "doc-uuid-2",
    "title": "Document 2",
    ...
  }
]
```

**Example**:
```bash
curl -H "Authorization: Bearer <token>" \
  "https://api.example.com/api/v1/policy/documents?municipality=Amsterdam&limit=50&offset=0"
```

---

#### POST /documents

Create a new policy document.

**Access**: Admin only

**Request Body**:
```json
{
  "source_id": "source-uuid",
  "external_id": "GB-2025-12345",
  "title": "Verordening Parkeerbeleid Amsterdam 2025",
  "description": "Nieuwe regels voor parkeren",
  "content_hash": "abc123...sha256hash",
  "document_url": "https://gemeenteblad.nl/doc/12345",
  "document_type": "pdf",
  "municipality": "Amsterdam",
  "publication_date": "2025-01-15",
  "effective_date": "2025-02-01",
  "file_size": 2048576,
  "page_count": 25,
  "language": "nl",
  "metadata": {}
}
```

**Field Validation**:
- `source_id`: Must reference existing source
- `content_hash`: 64-character SHA-256 hash (for deduplication)
- `document_type`: Must be one of: `pdf`, `html`, `docx`, `xlsx`
- `file_size`: Bytes (>= 0)
- `page_count`: Pages (>= 0)

**Response**: 200 OK
```json
{
  "id": "new-doc-uuid",
  "source_id": "source-uuid",
  ...
}
```

**Errors**:
- `409 Conflict` - Document with this content hash already exists
- `400 Bad Request` - Validation error

---

#### POST /documents/{document_id}/update

Update a policy document.

**Access**: Admin only

**Path Parameters**:
- `document_id` (string, required) - Document UUID

**Request Body** (all fields optional):
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "status": "indexed",
  "metadata": {
    "new_field": "value"
  },
  "indexed_at": 1698765600
}
```

**Field Validation**:
- `status`: Must be one of: `pending`, `processing`, `indexed`, `failed`, `archived`

**Response**: 200 OK
```json
{
  "id": "doc-uuid",
  "title": "Updated Title",
  ...
}
```

**Errors**:
- `404 Not Found` - Document not found

---

#### GET /documents/{document_id}/categories

Get all categories assigned to a document.

**Access**: All authenticated users

**Path Parameters**:
- `document_id` (string, required) - Document UUID

**Response**: 200 OK
```json
[
  {
    "id": "cat-uuid-1",
    "parent_id": null,
    "name": "Verkeer en Vervoer",
    "slug": "verkeer-vervoer",
    "description": "Regelgeving over verkeer",
    "icon": "car",
    "color": "#3B82F6",
    "path": "verkeer-vervoer",
    "sort_order": 0,
    "is_active": true,
    "created_at": 1698765432
  }
]
```

---

#### POST /documents/{document_id}/categories

Assign a category to a document.

**Access**: Admin only

**Path Parameters**:
- `document_id` (string, required) - Document UUID

**Request Body**:
```json
{
  "category_id": "cat-uuid",
  "confidence_score": 0.95,
  "assigned_by": "auto"
}
```

**Field Validation**:
- `confidence_score`: 0.0 to 1.0
- `assigned_by`: Must be one of: `auto`, `rule`, `manual`

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Category assigned successfully"
}
```

**Errors**:
- `404 Not Found` - Document or category not found

---

#### DELETE /documents/{document_id}/categories/{category_id}

Remove a category from a document.

**Access**: Admin only

**Path Parameters**:
- `document_id` (string, required) - Document UUID
- `category_id` (string, required) - Category UUID

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Category removed successfully"
}
```

---

#### GET /documents/favorites/list

Get all favorite documents for the current user.

**Access**: All authenticated users

**Response**: 200 OK
```json
[
  {
    "id": "doc-uuid-1",
    "title": "Favorite Document 1",
    ...
  }
]
```

---

#### POST /documents/{document_id}/favorite

Add a document to user's favorites.

**Access**: All authenticated users

**Path Parameters**:
- `document_id` (string, required) - Document UUID

**Query Parameters**:
- `notes` (string, optional) - User notes about this favorite

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Added to favorites"
}
```

**Errors**:
- `404 Not Found` - Document not found

---

#### DELETE /documents/{document_id}/favorite

Remove a document from user's favorites.

**Access**: All authenticated users

**Path Parameters**:
- `document_id` (string, required) - Document UUID

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Removed from favorites"
}
```

---

#### GET /documents/saved-searches/list

Get all saved searches for the current user.

**Access**: All authenticated users

**Response**: 200 OK
```json
[
  {
    "id": "search-uuid",
    "user_id": "user-uuid",
    "name": "Verkeer Amsterdam",
    "query_text": "verkeer",
    "filters": {
      "municipalities": ["Amsterdam"],
      "categories": ["verkeer-vervoer"]
    },
    "notification_enabled": true,
    "notification_frequency": "daily",
    "last_notified_at": 1698765432,
    "created_at": 1698765432,
    "updated_at": 1698765532
  }
]
```

---

#### POST /documents/saved-searches

Create a new saved search.

**Access**: All authenticated users

**Request Body**:
```json
{
  "name": "Verkeer Amsterdam",
  "query_text": "verkeer",
  "filters": {
    "municipalities": ["Amsterdam"]
  },
  "notification_enabled": true,
  "notification_frequency": "daily"
}
```

**Field Validation**:
- `name`: 1-255 characters
- `notification_frequency`: Must be one of: `immediate`, `daily`, `weekly`

**Response**: 200 OK
```json
{
  "id": "search-uuid",
  "user_id": "user-uuid",
  "name": "Verkeer Amsterdam",
  ...
}
```

---

#### DELETE /documents/saved-searches/{search_id}

Delete a saved search.

**Access**: All authenticated users

**Path Parameters**:
- `search_id` (string, required) - Saved search UUID

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Saved search deleted"
}
```

**Errors**:
- `404 Not Found` - Saved search not found or not owned by user

---

### 3. Policy Search API

**Base Path**: `/api/v1/policy/search`

**Router File**: `backend/open_webui/routers/policy_search.py`

**Access**: Authenticated users

**Status**: STUB implementation for Phase 1

---

#### POST /search

Search policy documents with filters.

**Access**: All authenticated users

**Request Body**:
```json
{
  "query": "parkeerbeleid",
  "filters": {
    "sources": ["source-uuid-1"],
    "municipalities": ["Amsterdam", "Rotterdam"],
    "categories": ["cat-uuid-1"],
    "date_from": "2025-01-01",
    "date_to": "2025-12-31",
    "document_type": "pdf"
  },
  "page": 1,
  "limit": 20,
  "sort": "relevance"
}
```

**Field Validation**:
- `query`: Min 1 character
- `page`: >= 1
- `limit`: 1-100
- `sort`: Must be one of: `relevance`, `date_desc`, `date_asc`, `title`

**Response**: 200 OK
```json
{
  "results": [
    {
      "id": "doc-uuid",
      "title": "Parkeerbeleid Amsterdam",
      ...
    }
  ],
  "total": 150,
  "facets": {
    "sources": [],
    "municipalities": [],
    "categories": []
  },
  "page": 1,
  "took_ms": 125
}
```

**Note**: Phase 1 implementation:
- Basic PostgreSQL filtering only
- No relevance ranking
- Empty facets
- Records search query for analytics

---

#### GET /search/filters

Get available filter options.

**Access**: All authenticated users

**Response**: 200 OK
```json
{
  "municipalities": [],
  "sources": [],
  "categories": [],
  "document_types": ["pdf", "html", "docx", "xlsx"]
}
```

**Note**: Phase 1 returns static data. Phase 2 will aggregate from database.

---

#### POST /search/semantic

Semantic search using vector embeddings.

**Access**: All authenticated users

**Status**: NOT IMPLEMENTED (Phase 3)

**Response**: 501 Not Implemented
```json
{
  "detail": "Semantic search will be implemented in Phase 3 (AI Features)"
}
```

---

## Error Responses

All endpoints use standard HTTP status codes:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Unauthorized"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 409 Conflict
```json
{
  "detail": "Resource already exists"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error: specific error message"
}
```

### 501 Not Implemented
```json
{
  "detail": "Feature not yet implemented"
}
```

## Rate Limiting

Rate limiting is configured per endpoint category (from architecture document):

- **Search endpoints**: 30 requests/minute
- **AI features** (Phase 3): 10 requests/minute
- **Admin operations**: 5 requests/minute

Rate limit headers:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 28
X-RateLimit-Reset: 1698765492
```

**Note**: Rate limiting implementation is planned for Phase 2.

## Pagination

Endpoints that return lists support pagination:

**Request**:
```
GET /api/v1/policy/documents?limit=20&offset=40
```

**Response**:
```json
{
  "results": [...],
  "total": 150,
  "page": 3,
  "limit": 20,
  "offset": 40
}
```

## Testing

### With cURL

```bash
# Get documents
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.example.com/api/v1/policy/documents?limit=5

# Search
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"verkeer","page":1,"limit":10,"sort":"date_desc"}' \
  https://api.example.com/api/v1/policy/search
```

### With Python

```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}

# Get documents
response = requests.get(
    "https://api.example.com/api/v1/policy/documents",
    headers=headers,
    params={"limit": 5, "municipality": "Amsterdam"}
)
documents = response.json()

# Search
search_payload = {
    "query": "verkeer",
    "filters": {"municipalities": ["Amsterdam"]},
    "page": 1,
    "limit": 20
}
response = requests.post(
    "https://api.example.com/api/v1/policy/search",
    headers=headers,
    json=search_payload
)
results = response.json()
```

## OpenAPI Specification

The full OpenAPI 3.0 specification can be accessed at:

```
https://api.example.com/docs
```

This provides:
- Interactive API documentation
- Request/response schemas
- Try-it-out functionality
- Code generation support
