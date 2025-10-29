# Adding New Scraper Plugins

## Tutorial: Creating a Custom Scraper Plugin

This guide walks you through creating a new scraper plugin for the Policy Scanner framework.

## Step 1: Create Plugin File

Create a new file in `backend/open_webui/scraper/plugins/`:

```bash
touch backend/open_webui/scraper/plugins/my_source.py
```

## Step 2: Implement Plugin Class

```python
"""
My Source scraper plugin.

Scrapes policy documents from MySource.nl
"""

import asyncio
from datetime import date
from typing import List, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from open_webui.scraper.base import BaseScraper
from open_webui.scraper.models import DocumentMetadata, DocumentType, ScraperConfig
from open_webui.scraper.middleware import (
    RateLimiter,
    RetryMiddleware,
    BotDetectionHandler,
    RobotsTxtParser,
)
from open_webui.scraper.validators import (
    generate_external_id_hash,
    validate_date,
    normalize_url,
)
from open_webui.scraper.plugins.registry import register_plugin


class MySourcePlugin(BaseScraper):
    """Scraper plugin for MySource.nl"""

    REQUIRED_SELECTORS = ["item", "title", "url"]

    def __init__(self, config: ScraperConfig):
        super().__init__(config)

        # Initialize middleware
        self.rate_limiter = RateLimiter(config.rate_limit)
        self.retry_middleware = RetryMiddleware(max_retries=config.max_retries)
        self.bot_handler = BotDetectionHandler()
        self.robots_parser = RobotsTxtParser()

        self._robots_fetched = False

    def validate_config(self) -> bool:
        """Validate configuration"""
        # Validate base config
        self._validate_base_config()

        # Check required selectors
        missing = [s for s in self.REQUIRED_SELECTORS if s not in self.config.selectors]
        if missing:
            raise ValueError(f"Missing required selectors: {missing}")

        return True

    async def discover_documents(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_pages: Optional[int] = None,
        **kwargs
    ) -> List[DocumentMetadata]:
        """Discover documents from source"""
        await self._ensure_session()

        # Fetch robots.txt
        if not self._robots_fetched:
            await self.robots_parser.fetch(self.config.base_url, self._session)
            self._robots_fetched = True

        documents = []
        page = 1

        while True:
            # Check limits
            if max_pages and page > max_pages:
                break

            # Rate limiting
            await self.rate_limiter.acquire()

            # Build URL
            url = self._build_search_url(page, start_date, end_date, **kwargs)

            try:
                # Fetch page
                html = await self._fetch_page(url)

                # Parse documents
                page_docs = self._parse_search_results(html)

                if not page_docs:
                    break

                documents.extend(page_docs)
                self.logger.info(f"Page {page}: Found {len(page_docs)} documents")

                # Crawl delay
                delay = self.robots_parser.get_crawl_delay() or self.config.crawl_delay
                await asyncio.sleep(delay)

                page += 1

            except Exception as e:
                self.logger.error(f"Error on page {page}: {e}")
                break

        return documents

    async def download_document(self, doc_metadata: DocumentMetadata) -> bytes:
        """Download document content"""
        await self._ensure_session()
        await self.rate_limiter.acquire()

        async with self._session.get(
            doc_metadata.url,
            headers=self.get_headers()
        ) as response:
            response.raise_for_status()
            return await response.read()

    async def _fetch_page(self, url: str) -> str:
        """Fetch HTML page with retry"""
        response = await self.retry_middleware.request(
            'GET',
            url,
            self._session,
            headers=self.get_headers(),
            on_retry=lambda _: self._record_retry()
        )

        if response.status != 200:
            raise Exception(f"HTTP {response.status}: {url}")

        return await response.text()

    def _build_search_url(
        self,
        page: int,
        start_date: Optional[date],
        end_date: Optional[date],
        **kwargs
    ) -> str:
        """Build search URL with parameters"""
        url = f"{self.config.base_url}/search"
        params = []

        if page > 1:
            params.append(f"page={page}")

        if start_date:
            params.append(f"from={start_date.isoformat()}")

        if end_date:
            params.append(f"to={end_date.isoformat()}")

        # Add custom kwargs
        for key, value in kwargs.items():
            if value:
                params.append(f"{key}={value}")

        return f"{url}?{'&'.join(params)}" if params else url

    def _parse_search_results(self, html: str) -> List[DocumentMetadata]:
        """Parse documents from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        documents = []

        items = soup.select(self.config.selectors['item'])

        for item in items:
            try:
                doc = self._parse_item(item)
                if doc:
                    documents.append(doc)
                    self._record_document_discovered()
            except Exception as e:
                self.logger.warning(f"Failed to parse item: {e}")

        return documents

    def _parse_item(self, item) -> Optional[DocumentMetadata]:
        """Parse single document item"""
        # Extract title
        title_elem = item.select_one(self.config.selectors['title'])
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)
        if not title:
            return None

        # Extract URL
        url_elem = item.select_one(self.config.selectors['url'])
        if not url_elem or not url_elem.get('href'):
            return None

        url = normalize_url(url_elem['href'], self.config.base_url)

        # Generate external ID
        external_id = generate_external_id_hash(url)

        # Extract date (optional)
        publication_date = None
        if 'date' in self.config.selectors:
            date_elem = item.select_one(self.config.selectors['date'])
            if date_elem:
                try:
                    publication_date = validate_date(date_elem.get_text(strip=True))
                except Exception:
                    pass

        return DocumentMetadata(
            title=title,
            url=url,
            external_id=external_id,
            publication_date=publication_date,
            document_type=DocumentType.PDF,  # Adjust as needed
            metadata={'source': 'my_source'}
        )


# Register the plugin
register_plugin('my_source', MySourcePlugin)
```

## Step 3: Register Plugin

Import your plugin in `backend/open_webui/scraper/plugins/__init__.py`:

```python
from open_webui.scraper.plugins.gemeenteblad import GemeentebladPlugin
from open_webui.scraper.plugins.my_source import MySourcePlugin  # Add this line

__all__ = [
    "GemeentebladPlugin",
    "MySourcePlugin",  # Add this line
]
```

## Step 4: Create Test Fixtures

Create HTML fixtures in `backend/open_webui/test/scraper/fixtures/`:

```html
<!-- my_source_page1.html -->
<!DOCTYPE html>
<html>
<body>
    <div class="results">
        <div class="doc-item">
            <h3 class="doc-title">Test Document 1</h3>
            <a class="doc-url" href="/docs/123">Download</a>
            <span class="doc-date">2025-01-15</span>
        </div>
    </div>
</body>
</html>
```

## Step 5: Write Tests

Create `backend/open_webui/test/scraper/test_my_source_plugin.py`:

```python
import pytest
from aioresponses import aioresponses

from open_webui.scraper import get_plugin, ScraperConfig


def load_fixture(name):
    with open(f"backend/open_webui/test/scraper/fixtures/{name}") as f:
        return f.read()


class TestMySourcePlugin:
    @pytest.mark.asyncio
    async def test_discover_documents(self):
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=100,
            selectors={
                'item': 'div.doc-item',
                'title': 'h3.doc-title',
                'url': 'a.doc-url',
                'date': 'span.doc-date'
            }
        )

        plugin = get_plugin('my_source', config)

        with aioresponses() as mocked:
            # Mock robots.txt
            mocked.get('https://example.com/robots.txt', status=404)

            # Mock search page
            html = load_fixture('my_source_page1.html')
            mocked.get('https://example.com/search', status=200, body=html)

            # Mock empty page
            mocked.get('https://example.com/search?page=2', status=200, body="<html></html>")

            documents = await plugin.discover_documents()

        assert len(documents) == 1
        assert documents[0].title == "Test Document 1"
```

## Step 6: Test Your Plugin

```bash
# Run tests
cd backend
python -m pytest open_webui/test/scraper/test_my_source_plugin.py -v

# Test CLI
python -m open_webui.scraper list
python -m open_webui.scraper info my_source
python -m open_webui.scraper test my_source \
  --url https://example.com \
  --selector item=div.doc-item \
  --selector title=h3.doc-title \
  --selector url=a.doc-url \
  --selector date=span.doc-date \
  --max-pages 1 \
  --verbose
```

## Key Points

1. **Inherit from BaseScraper**: Provides HTTP session management and utilities
2. **Implement Required Methods**: `discover_documents()`, `download_document()`, `validate_config()`
3. **Use Middleware**: Rate limiting, retry logic, bot detection
4. **Error Handling**: Catch and log errors, don't crash the entire scrape
5. **Statistics**: Use `_record_*()` methods to track performance
6. **Validation**: Validate all extracted data before returning
7. **Async/Await**: All I/O operations must be async
8. **Testing**: Mock HTTP requests with `aioresponses`

## Configuration Options

Your plugin can accept custom parameters via `ScraperConfig`:

```python
config = ScraperConfig(
    base_url="https://example.com",
    rate_limit=10,
    crawl_delay=1.0,
    timeout=30,
    max_retries=3,
    selectors={
        'item': 'div.document',
        'title': 'h2.title',
        'url': 'a.link',
        'date': 'span.date'
    },
    headers={
        'X-API-Key': 'your-key'
    },
    custom_params={
        'municipality': 'Amsterdam',
        'category': 'permits'
    }
)
```

Access custom params:
```python
municipality = self.config.custom_params.get('municipality')
```

## Best Practices

1. **Respect Rate Limits**: Use provided rate limiter
2. **Handle Pagination**: Continue until no more results
3. **Parse Dates Carefully**: Use `validate_date()` utility
4. **Normalize URLs**: Use `normalize_url()` for relative links
5. **Generate Stable IDs**: Use `generate_external_id_hash(url)`
6. **Log Appropriately**: Use `self.logger` for debugging
7. **Test Thoroughly**: Cover success, errors, edge cases
8. **Document Well**: Add docstrings and comments

## Troubleshooting

### Plugin Not Found
- Check plugin is imported in `plugins/__init__.py`
- Verify `register_plugin()` is called at module level

### Rate Limiting Issues
- Increase `rate_limit` parameter
- Check `crawl_delay` setting
- Review robots.txt compliance

### Parsing Failures
- Verify CSS selectors match HTML structure
- Check for dynamic content (JavaScript rendering)
- Use browser DevTools to inspect elements

### Bot Detection
- User-Agent rotation is automatic
- Adjust crawl delay if still blocked
- Consider adding delays between requests

## Example: Complete Plugin

See `backend/open_webui/scraper/plugins/gemeenteblad.py` for a complete, production-ready example implementing all best practices.
