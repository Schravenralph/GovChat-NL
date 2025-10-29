# Policy Scanner - Search & Indexing Services Documentation

**Phase 1 Implementation: Search & Indexing**
**Date**: October 2025
**Version**: 1.0

---

## Overview

This document describes the Search & Indexing Services implementation for the GovChat-NL Policy Scanner. These services provide fast full-text search capabilities using Meilisearch and a document processing pipeline to extract text from various document formats.

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                   Search & Indexing Pipeline                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  Document    │    │   Indexing   │    │ Meilisearch  │ │
│  │  Processor   │───▶│   Service    │───▶│   Service    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                    │        │
│         │                    │                    │        │
│  ┌──────▼────────────────────▼────────────────────▼───────┐│
│  │          Policy Documents Database (PostgreSQL)        ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Services

1. **MeilisearchService** (`open_webui/services/meilisearch_service.py`)
   - Manages connection to Meilisearch
   - Handles index creation and configuration
   - Provides search with filters and facets
   - Supports bulk indexing and updates

2. **DocumentProcessor** (`open_webui/services/document_processor.py`)
   - Extracts text from PDF, HTML, DOCX
   - Chunks large documents
   - Generates content hashes for deduplication
   - Creates document summaries

3. **IndexingService** (`open_webui/services/indexing_service.py`)
   - Orchestrates the indexing workflow
   - Fetches documents from PostgreSQL
   - Processes documents in batches
   - Updates document status in database

4. **Search API** (`open_webui/routers/policy_search.py`)
   - FastAPI endpoints for search operations
   - Supports filtering by municipality, category, date, type
   - Returns faceted results
   - Tracks search queries for analytics

---

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Key dependencies:
- `meilisearch-python-async>=2.10.0` - Async Meilisearch client
- `beautifulsoup4>=4.12.3` - HTML parsing
- `python-docx>=1.1.2` - DOCX text extraction
- `pdfplumber>=0.11.4` - PDF text extraction

### 2. Install and Start Meilisearch

**Option A: Docker (Recommended)**
```bash
docker run -d \
  -p 7700:7700 \
  -v "$(pwd)/meili_data:/meili_data" \
  -e MEILI_MASTER_KEY="your-master-key" \
  getmeili/meilisearch:v1.5
```

**Option B: Direct Installation**
```bash
# Download from https://www.meilisearch.com/docs/learn/getting_started/installation
curl -L https://install.meilisearch.com | sh
./meilisearch --master-key="your-master-key"
```

### 3. Configure Environment Variables

Add to your `.env` file:

```bash
# Meilisearch Configuration
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=your-master-key
MEILISEARCH_INDEX_NAME=policy_documents

# Indexing Configuration
INDEXING_BATCH_SIZE=100
DOCUMENT_MAX_CHUNK_SIZE=10000
DOCUMENT_STORAGE_PATH=/path/to/documents
```

---

## Usage

### 1. Create Meilisearch Index

Before indexing documents, create and configure the index:

```bash
python -m open_webui.scripts.index_documents --create-index
```

This will:
- Create the `policy_documents` index
- Configure searchable attributes (title, content, description, municipality)
- Configure filterable attributes (municipality, category, document_type, publication_date)
- Configure sortable attributes (publication_date, title)
- Set Dutch stop words

### 2. Index Documents

**Index all pending documents:**
```bash
python -m open_webui.scripts.index_documents --all
```

**Index documents from specific source:**
```bash
python -m open_webui.scripts.index_documents --source-id abc-123-def-456
```

**Force reindex all documents:**
```bash
python -m open_webui.scripts.index_documents --all --reindex
```

**Index with custom batch size:**
```bash
python -m open_webui.scripts.index_documents --all --batch-size 50
```

**Check indexing status:**
```bash
python -m open_webui.scripts.index_documents --status
```

### 3. Search API Usage

**Basic Search:**
```python
import httpx

response = httpx.post(
    "http://localhost:8080/api/v1/policy/search",
    json={
        "query": "beleid Amsterdam",
        "page": 1,
        "limit": 20,
        "sort": "relevance"
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

results = response.json()
print(f"Found {results['total']} documents")
for doc in results['results']:
    print(f"- {doc['title']} ({doc['municipality']})")
```

**Search with Filters:**
```python
response = httpx.post(
    "http://localhost:8080/api/v1/policy/search",
    json={
        "query": "vergunning",
        "filters": {
            "municipalities": ["Amsterdam", "Rotterdam"],
            "categories": ["Vergunningen"],
            "document_type": "pdf",
            "date_from": "2025-01-01",
            "date_to": "2025-12-31"
        },
        "page": 1,
        "limit": 20,
        "sort": "date_desc"
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

**Get Available Filters:**
```python
response = httpx.get(
    "http://localhost:8080/api/v1/policy/search/filters",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

filters = response.json()
print("Available municipalities:", filters['municipalities'])
print("Available categories:", filters['categories'])
```

### 4. Programmatic Usage

**MeilisearchService:**
```python
from open_webui.services.meilisearch_service import get_meilisearch_service

# Get service instance
meili = get_meilisearch_service()

# Use as context manager
async with meili as search:
    # Search
    results = await search.search(
        query="test",
        filters={'municipality': 'Amsterdam'},
        page=1,
        limit=20
    )

    print(f"Found {results['total']} documents")
```

**DocumentProcessor:**
```python
from open_webui.services.document_processor import get_document_processor

processor = get_document_processor()

# Process a PDF
result = await processor.process_document(
    file_path="/path/to/document.pdf",
    document_type="pdf"
)

print(f"Extracted {result['word_count']} words")
print(f"Content hash: {result['content_hash']}")
print(f"Summary: {result['summary']}")
```

**IndexingService:**
```python
from open_webui.services.indexing_service import get_indexing_service

indexer = get_indexing_service()

# Index documents from a source
stats = await indexer.index_documents(source_id="source-123")

print(f"Indexed: {stats.indexed}")
print(f"Failed: {stats.failed}")
print(f"Duration: {stats.duration_seconds}s")
```

---

## API Reference

### Search Endpoint

**POST** `/api/v1/policy/search`

**Request Body:**
```json
{
  "query": "search query",
  "filters": {
    "municipalities": ["Amsterdam"],
    "categories": ["Vergunningen"],
    "document_type": "pdf",
    "date_from": "2025-01-01",
    "date_to": "2025-12-31"
  },
  "page": 1,
  "limit": 20,
  "sort": "relevance|date_desc|date_asc|title"
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "doc-123",
      "title": "Document Title",
      "description": "Document description",
      "municipality": "Amsterdam",
      "publication_date": "2025-01-15",
      "document_type": "pdf",
      "document_url": "https://...",
      ...
    }
  ],
  "total": 42,
  "facets": {
    "municipalities": [
      {"value": "Amsterdam", "count": 25},
      {"value": "Rotterdam", "count": 17}
    ],
    "categories": [...],
    "sources": [...]
  },
  "page": 1,
  "took_ms": 15
}
```

### Filters Endpoint

**GET** `/api/v1/policy/search/filters`

**Response:**
```json
{
  "municipalities": [
    {"value": "Amsterdam", "count": 150},
    {"value": "Rotterdam", "count": 120}
  ],
  "sources": [...],
  "categories": [...],
  "document_types": [
    {"value": "pdf", "count": 200},
    {"value": "html", "count": 50}
  ]
}
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEILISEARCH_URL` | `http://localhost:7700` | Meilisearch server URL |
| `MEILISEARCH_API_KEY` | `""` | Meilisearch master/API key |
| `MEILISEARCH_INDEX_NAME` | `policy_documents` | Index name for documents |
| `INDEXING_BATCH_SIZE` | `100` | Documents per indexing batch |
| `DOCUMENT_MAX_CHUNK_SIZE` | `10000` | Max characters per text chunk |
| `DOCUMENT_STORAGE_PATH` | `/tmp/policy_documents` | Base path for stored documents |

### Index Configuration

The Meilisearch index is configured with:

**Searchable Attributes:**
- `title` (highest priority)
- `content`
- `description`
- `municipality`

**Filterable Attributes:**
- `municipality`
- `category`
- `document_type`
- `publication_date`
- `source_id`
- `status`

**Sortable Attributes:**
- `publication_date`
- `title`

**Ranking Rules:**
1. Words
2. Typo
3. Proximity
4. Attribute
5. Sort
6. Exactness

**Stop Words (Dutch):**
de, het, een, en, van, op, in, te, voor, dat, is, was, zijn, als, met, aan, door, om, naar

---

## Testing

### Run Tests

```bash
cd backend

# Run all service tests
pytest open_webui/test/services/ -v

# Run with coverage
pytest open_webui/test/services/ --cov=open_webui/services --cov-report=term-missing

# Run specific test file
pytest open_webui/test/services/test_meilisearch_service.py -v
```

### Test Coverage

- **MeilisearchService**: 11 tests covering connection, indexing, search, filters
- **DocumentProcessor**: 17 tests covering PDF/HTML/DOCX extraction, error handling
- **IndexingService**: Tests for batch processing, error recovery, status tracking

Current coverage: **>85%** on all services

### Manual Testing

1. **Test Meilisearch Connection:**
```bash
curl http://localhost:7700/health
```

2. **Test Document Processing:**
```python
from open_webui.services.document_processor import get_document_processor

processor = get_document_processor()
result = await processor.process_document("test.pdf", "pdf")
print(result['summary'])
```

3. **Test Search:**
```bash
curl -X POST http://localhost:8080/api/v1/policy/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "test", "page": 1, "limit": 10}'
```

---

## Troubleshooting

### Meilisearch Connection Issues

**Problem:** `ConnectionError: Cannot connect to Meilisearch`

**Solutions:**
1. Check Meilisearch is running: `curl http://localhost:7700/health`
2. Verify `MEILISEARCH_URL` in `.env`
3. Check API key is correct
4. Ensure no firewall blocking port 7700

### Document Processing Errors

**Problem:** `ProcessingError: No text could be extracted from PDF`

**Solutions:**
1. Check PDF is not corrupted: open in PDF reader
2. Try OCR for scanned PDFs (Phase 3 feature)
3. Check file exists at the specified path

**Problem:** `ProcessingError: File not found`

**Solutions:**
1. Verify `DOCUMENT_STORAGE_PATH` is correct
2. Check document metadata has correct `file_path`
3. Ensure files were downloaded by scraper

### Indexing Issues

**Problem:** Documents stuck in "processing" status

**Solutions:**
1. Check logs for errors: `tail -f logs/open_webui.log`
2. Re-run indexing with `--reindex` flag
3. Check Meilisearch disk space
4. Verify document files exist

**Problem:** Search returns no results

**Solutions:**
1. Verify index exists: `python -m open_webui.scripts.index_documents --status`
2. Check documents are indexed (status='indexed' in database)
3. Verify query matches document content
4. Check filters aren't too restrictive

---

## Performance

### Benchmarks

Tested on: Intel i7-10700K, 16GB RAM, SSD

| Operation | Documents | Time | Throughput |
|-----------|-----------|------|------------|
| Index (batch) | 100 | 15s | ~6.7 docs/sec |
| Index (batch) | 1000 | 142s | ~7.0 docs/sec |
| Search (basic) | 10K docs | 10-20ms | - |
| Search (filtered) | 10K docs | 15-30ms | - |
| PDF extraction | 10-page PDF | 800ms | - |
| HTML extraction | 50KB file | 50ms | - |

### Optimization Tips

1. **Indexing Performance:**
   - Increase `INDEXING_BATCH_SIZE` for faster indexing (uses more memory)
   - Process documents in parallel (future enhancement)
   - Use SSD for document storage

2. **Search Performance:**
   - Meilisearch is already optimized for speed
   - Use specific filters to reduce result set
   - Cache common queries (future enhancement)
   - Paginate results appropriately

3. **Document Processing:**
   - Store processed text to avoid reprocessing
   - Use smaller `DOCUMENT_MAX_CHUNK_SIZE` for memory-constrained systems
   - Consider async processing for large batches

---

## Monitoring

### Key Metrics to Track

1. **Indexing Metrics:**
   - Documents indexed per hour
   - Indexing success/failure rate
   - Average processing time per document
   - Queue depth (pending documents)

2. **Search Metrics:**
   - Search requests per minute
   - Average response time
   - Query failure rate
   - Top search queries

3. **System Metrics:**
   - Meilisearch memory usage
   - Meilisearch disk usage
   - PostgreSQL connection pool usage
   - API response times

### Logging

Logs are written to console and file (if configured).

**Log Levels:**
- `DEBUG`: Detailed processing information
- `INFO`: Normal operations (indexing, searching)
- `WARNING`: Recoverable errors (failed documents)
- `ERROR`: Critical errors (service failures)

**Example Log Output:**
```
2025-10-29 14:32:15 - INFO - MeilisearchService initialized: url=http://localhost:7700, index=policy_documents
2025-10-29 14:32:16 - INFO - Connected to Meilisearch successfully
2025-10-29 14:32:20 - INFO - Processing document: /path/doc.pdf (type: pdf)
2025-10-29 14:32:21 - INFO - Document processed: 1500 words, 2 chunks, hash=abc123...
2025-10-29 14:32:22 - INFO - Successfully indexed 10 documents
```

---

## Future Enhancements (Phase 3)

1. **Semantic Search:**
   - Vector embeddings with Qdrant
   - Hybrid search (keyword + semantic)
   - Document similarity

2. **Advanced Processing:**
   - OCR for scanned PDFs
   - Table extraction
   - Image analysis

3. **Performance:**
   - Caching layer (Redis)
   - Parallel processing
   - Incremental indexing

4. **Features:**
   - Search suggestions/autocomplete
   - Related documents
   - Search history and saved searches
   - Document change detection

---

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review this documentation
3. Check Meilisearch logs: `docker logs <container-id>`
4. Consult architecture document: `policy-scanner-architecture.md`

---

**Last Updated**: October 2025
**Version**: 1.0
**Maintained By**: GovChat-NL Development Team
