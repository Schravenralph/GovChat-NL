# Policy Scanner Scraper Framework

## Overview

The Policy Scanner Scraper Framework provides an extensible, plugin-based architecture for discovering and downloading policy documents from government websites.

## Architecture

```
open_webui/scraper/
├── __init__.py          # Main exports
├── __main__.py          # CLI entry point
├── base.py              # ScraperPlugin abstract base class
├── models.py            # Pydantic data models
├── validators.py        # Validation utilities
├── middleware.py        # Rate limiting, retry logic
├── cli.py               # Command-line interface
└── plugins/
    ├── __init__.py
    ├── registry.py      # Plugin discovery
    └── gemeenteblad.py  # Gemeentebladen.nl scraper
```

## Core Components

### ScraperPlugin (Abstract Base Class)

All scraper plugins must inherit from `ScraperPlugin` and implement:

```python
from open_webui.scraper import ScraperPlugin, DocumentMetadata, ScraperConfig

class MyPlugin(ScraperPlugin):
    async def discover_documents(self, start_date=None, end_date=None, max_pages=None, **kwargs):
        """Discover available documents"""
        # Implementation

    async def download_document(self, doc_metadata: DocumentMetadata):
        """Download document content"""
        # Implementation

    def validate_config(self):
        """Validate plugin configuration"""
        # Implementation
```

### DocumentMetadata Model

```python
DocumentMetadata(
    title="Document Title",
    url="https://example.com/doc.pdf",
    external_id="unique-id",
    publication_date=date(2025, 1, 15),
    municipality="Amsterdam",
    document_type=DocumentType.PDF,
    description="Document description"
)
```

### ScraperConfig Model

```python
ScraperConfig(
    base_url="https://gemeentebladen.nl",
    rate_limit=10,  # requests per second
    crawl_delay=1.0,  # seconds between requests
    timeout=30,  # request timeout
    max_retries=3,  # retry attempts
    selectors={
        'item': 'div.document-item',
        'title': 'h2.title',
        'url': 'a.document-link',
        'date': 'span.publication-date'
    }
)
```

## Middleware Features

### Rate Limiting (Token Bucket)
- Configurable requests per second
- Non-blocking async implementation
- Automatic token refill

### Retry Logic (Exponential Backoff)
- Retries on 429, 500, 502, 503, 504
- Exponential backoff with jitter
- Configurable max retries

### Anti-Bot Detection
- User-Agent rotation
- Realistic browser headers
- Crawl-delay from robots.txt
- Automatic blocking detection

## CLI Usage

### List Available Plugins
```bash
python -m open_webui.scraper list
```

### Test a Plugin
```bash
python -m open_webui.scraper test gemeenteblad \
  --url https://gemeentebladen.nl \
  --max-pages 2 \
  --output json
```

### With Filtering
```bash
python -m open_webui.scraper test gemeenteblad \
  --url https://gemeentebladen.nl \
  --start-date 2025-01-01 \
  --end-date 2025-12-31 \
  --municipality Amsterdam \
  --verbose
```

### Get Plugin Info
```bash
python -m open_webui.scraper info gemeenteblad
```

## Programmatic Usage

```python
from open_webui.scraper import get_plugin, ScraperConfig
from datetime import date

# Configure scraper
config = ScraperConfig(
    base_url="https://gemeentebladen.nl",
    rate_limit=10,
    selectors={
        'item': 'div.document-item',
        'title': 'h2.title',
        'url': 'a.document-link',
        'date': 'span.publication-date'
    }
)

# Get plugin instance
plugin = get_plugin('gemeenteblad', config)

# Discover documents
result = await plugin.scrape(
    start_date=date(2025, 1, 1),
    end_date=date(2025, 12, 31),
    max_pages=10
)

print(f"Found {result.total_found} documents")
for doc in result.documents:
    print(f"- {doc.title} ({doc.publication_date})")

# Download a document
if result.documents:
    content = await plugin.download_document(result.documents[0])
    print(f"Downloaded {len(content)} bytes")

# Get statistics
stats = plugin.get_stats()
print(f"Success rate: {stats.success_rate:.1f}%")
print(f"Avg response time: {stats.avg_response_time_ms:.0f}ms")
```

## Testing

### Run All Tests
```bash
cd backend
python -m pytest open_webui/test/scraper/ -v
```

### With Coverage
```bash
python -m pytest open_webui/test/scraper/ --cov=open_webui.scraper --cov-report=html
```

### Test Individual Components
```bash
# Base plugin tests
python -m pytest open_webui/test/scraper/test_base_plugin.py -v

# Rate limiting tests
python -m pytest open_webui/test/scraper/test_rate_limiting.py -v

# Gemeenteblad plugin tests
python -m pytest open_webui/test/scraper/test_gemeenteblad_plugin.py -v
```

## Configuration Best Practices

1. **Rate Limiting**: Start with 10 req/s, adjust based on target website
2. **Crawl Delay**: Respect robots.txt, default to 1 second minimum
3. **Timeout**: 30 seconds for most websites
4. **Max Retries**: 3 attempts is usually sufficient
5. **User-Agent**: Use descriptive agent identifying your application

## Error Handling

The framework handles common errors automatically:

- **HTTP 429 (Too Many Requests)**: Exponential backoff retry
- **HTTP 500-504 (Server Errors)**: Retry with backoff
- **Bot Detection**: User-Agent rotation and header updates
- **Network Errors**: Automatic retry with timeout
- **Malformed HTML**: Graceful skip with logging

## Performance

- **Async/Await**: All I/O operations are non-blocking
- **Concurrent Requests**: Limited by rate limiter
- **Memory Efficient**: Streaming for large documents
- **Statistics Tracking**: Monitor performance in real-time

## Security

- **No Credentials in Code**: Use environment variables
- **URL Validation**: Prevent SSRF attacks
- **Filename Sanitization**: Prevent directory traversal
- **Rate Limiting**: Prevent server overload
- **Respect robots.txt**: Ethical web scraping

## Monitoring

Track scraper performance using built-in statistics:

```python
stats = plugin.get_stats()

print(f"Total Requests: {stats.total_requests}")
print(f"Successful: {stats.successful_requests}")
print(f"Failed: {stats.failed_requests}")
print(f"Rate Limited: {stats.rate_limited_requests}")
print(f"Retries: {stats.retry_attempts}")
print(f"Success Rate: {stats.success_rate:.1f}%")
print(f"Avg Response Time: {stats.avg_response_time_ms:.0f}ms")
```

## See Also

- [Adding New Scrapers](adding-scrapers.md) - Tutorial for creating plugins
- [Architecture Document](../../policy-scanner-architecture.md) - Overall system design
