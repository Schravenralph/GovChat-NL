"""
Gemeenteblad.nl scraper plugin.

This plugin scrapes policy documents from Gemeentebladen.nl,
a Dutch government publication portal for municipal announcements.
"""

import asyncio
import logging
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse, parse_qs

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
    validate_municipality,
    normalize_url,
)
from open_webui.scraper.plugins.registry import register_plugin


logger = logging.getLogger(__name__)


class GemeentebladPlugin(BaseScraper):
    """
    Scraper plugin for Gemeentebladen.nl.

    This plugin implements document discovery and download for the
    Gemeentebladen.nl website, which publishes official municipal documents.

    Configuration Requirements:
        - base_url: Base URL for Gemeentebladen.nl
        - selectors: CSS selectors for parsing HTML
            - item: Selector for document items
            - title: Selector for document title
            - url: Selector for document URL
            - date: Selector for publication date
            - municipality: Selector for municipality name (optional)
    """

    REQUIRED_SELECTORS = ["item", "title", "url", "date"]

    def __init__(self, config: ScraperConfig):
        """
        Initialize Gemeenteblad plugin.

        Args:
            config: Scraper configuration
        """
        super().__init__(config)

        # Initialize middleware
        self.rate_limiter = RateLimiter(config.rate_limit)
        self.retry_middleware = RetryMiddleware(
            max_retries=config.max_retries,
            retry_on_status=[429, 500, 502, 503, 504]
        )
        self.bot_handler = BotDetectionHandler()
        self.robots_parser = RobotsTxtParser()

        # Plugin-specific state
        self._robots_fetched = False

    def validate_config(self) -> bool:
        """
        Validate Gemeenteblad-specific configuration.

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate base configuration
        self._validate_base_config()

        # Check required selectors
        missing_selectors = [
            sel for sel in self.REQUIRED_SELECTORS
            if sel not in self.config.selectors
        ]

        if missing_selectors:
            raise ValueError(
                f"Missing required selectors: {missing_selectors}. "
                f"Required: {self.REQUIRED_SELECTORS}"
            )

        return True

    async def discover_documents(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_pages: Optional[int] = None,
        **kwargs
    ) -> List[DocumentMetadata]:
        """
        Discover documents from Gemeentebladen.nl.

        Args:
            start_date: Filter documents from this date onwards
            end_date: Filter documents up to this date
            max_pages: Maximum number of pages to scrape
            **kwargs: Additional parameters:
                - municipality: Filter by municipality name
                - query: Search query

        Returns:
            List[DocumentMetadata]: Discovered documents
        """
        await self._ensure_session()

        # Fetch robots.txt if not done yet
        if not self._robots_fetched:
            await self._fetch_robots_txt()

        documents = []
        page = 1
        consecutive_empty_pages = 0

        self.logger.info(
            f"Starting document discovery: "
            f"start_date={start_date}, end_date={end_date}, max_pages={max_pages}"
        )

        while True:
            # Check if we should continue
            if max_pages and page > max_pages:
                self.logger.info(f"Reached max_pages limit: {max_pages}")
                break

            # Stop if we get too many empty pages in a row
            if consecutive_empty_pages >= 3:
                self.logger.info("Reached end of results (3 consecutive empty pages)")
                break

            # Rate limiting
            await self.rate_limiter.acquire()

            # Build URL for this page
            url = self._build_search_url(
                page=page,
                start_date=start_date,
                end_date=end_date,
                **kwargs
            )

            self.logger.debug(f"Fetching page {page}: {url}")

            try:
                # Fetch page with retry logic
                start_time = datetime.now()
                html = await self._fetch_page(url)
                response_time = (datetime.now() - start_time).total_seconds() * 1000

                self._record_request(success=True, response_time_ms=response_time)

                # Parse documents from page
                page_documents = self._parse_search_results(html)

                if not page_documents:
                    consecutive_empty_pages += 1
                    self.logger.debug(f"Page {page} returned no documents")
                else:
                    consecutive_empty_pages = 0
                    documents.extend(page_documents)
                    self.logger.info(
                        f"Page {page}: Found {len(page_documents)} documents "
                        f"(total: {len(documents)})"
                    )

                # Respect crawl delay
                crawl_delay = self.robots_parser.get_crawl_delay()
                if crawl_delay:
                    await asyncio.sleep(crawl_delay)
                else:
                    await asyncio.sleep(self.config.crawl_delay)

                page += 1

            except Exception as e:
                self.logger.error(f"Error fetching page {page}: {e}", exc_info=True)
                self._record_request(success=False, response_time_ms=0)
                break

        self.logger.info(f"Discovery complete: {len(documents)} documents found")
        self.stats.documents_discovered = len(documents)

        return documents

    async def download_document(self, doc_metadata: DocumentMetadata) -> bytes:
        """
        Download document content from URL.

        Args:
            doc_metadata: Document metadata containing URL

        Returns:
            bytes: Document content

        Raises:
            Exception: If download fails
        """
        await self._ensure_session()

        self.logger.info(f"Downloading document: {doc_metadata.title}")

        # Rate limiting
        await self.rate_limiter.acquire()

        try:
            start_time = datetime.now()

            async with self._session.get(
                doc_metadata.url,
                headers=self.get_headers()
            ) as response:
                response.raise_for_status()
                content = await response.read()

                response_time = (datetime.now() - start_time).total_seconds() * 1000
                self._record_request(success=True, response_time_ms=response_time)

                self.logger.info(
                    f"Downloaded {len(content)} bytes in {response_time:.0f}ms"
                )

                return content

        except Exception as e:
            self.logger.error(f"Download failed: {e}", exc_info=True)
            self._record_request(success=False, response_time_ms=0)
            raise

    async def _fetch_robots_txt(self):
        """Fetch and parse robots.txt."""
        try:
            await self._ensure_session()
            await self.robots_parser.fetch(self.config.base_url, self._session)
            self._robots_fetched = True
        except Exception as e:
            self.logger.warning(f"Failed to fetch robots.txt: {e}")
            self._robots_fetched = True  # Don't retry

    async def _fetch_page(self, url: str) -> str:
        """
        Fetch HTML page with retry and bot detection handling.

        Args:
            url: Page URL

        Returns:
            str: HTML content
        """
        headers = self.get_headers()

        async def make_request() -> aiohttp.ClientResponse:
            return await self.retry_middleware.request(
                'GET',
                url,
                self._session,
                headers=headers,
                on_retry=lambda attempt: self._record_retry()
            )

        response = await make_request()

        # Check for bot detection
        if self.bot_handler.is_blocked(response):
            self._record_rate_limit()
            self.logger.warning("Bot detection triggered, applying countermeasures")

            # Get updated headers
            updated_headers = await self.bot_handler.handle_block(response, 0)
            headers.update(updated_headers)

            # Retry with new headers
            response = await self.retry_middleware.request(
                'GET',
                url,
                self._session,
                headers=headers,
                on_retry=lambda attempt: self._record_retry()
            )

        if response.status != 200:
            raise Exception(f"HTTP {response.status}: {url}")

        return await response.text()

    def _build_search_url(
        self,
        page: int = 1,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> str:
        """
        Build search URL with parameters.

        Args:
            page: Page number
            start_date: Filter from date
            end_date: Filter to date
            **kwargs: Additional parameters (municipality, query)

        Returns:
            str: Search URL
        """
        base_search_url = f"{self.config.base_url}/search"

        params = []

        if page > 1:
            params.append(f"page={page}")

        if start_date:
            params.append(f"from_date={start_date.isoformat()}")

        if end_date:
            params.append(f"to_date={end_date.isoformat()}")

        if 'municipality' in kwargs and kwargs['municipality']:
            params.append(f"municipality={kwargs['municipality']}")

        if 'query' in kwargs and kwargs['query']:
            params.append(f"q={kwargs['query']}")

        # Add custom params from config
        for key, value in self.config.custom_params.items():
            params.append(f"{key}={value}")

        if params:
            return f"{base_search_url}?{'&'.join(params)}"

        return base_search_url

    def _parse_search_results(self, html: str) -> List[DocumentMetadata]:
        """
        Parse document metadata from search results HTML.

        Args:
            html: HTML content

        Returns:
            List[DocumentMetadata]: Parsed documents
        """
        soup = BeautifulSoup(html, 'html.parser')
        documents = []

        # Find all document items
        items = soup.select(self.config.selectors['item'])

        self.logger.debug(f"Found {len(items)} items with selector '{self.config.selectors['item']}'")

        for item in items:
            try:
                doc = self._parse_document_item(item)
                if doc:
                    documents.append(doc)
                    self._record_document_discovered()
            except Exception as e:
                self.logger.warning(f"Failed to parse document item: {e}")
                continue

        return documents

    def _parse_document_item(self, item) -> Optional[DocumentMetadata]:
        """
        Parse a single document item.

        Args:
            item: BeautifulSoup element

        Returns:
            DocumentMetadata or None if parsing fails
        """
        # Extract title
        title_elem = item.select_one(self.config.selectors['title'])
        if not title_elem:
            self.logger.debug("Title element not found")
            return None

        title = title_elem.get_text(strip=True)
        if not title:
            return None

        # Extract URL
        url_elem = item.select_one(self.config.selectors['url'])
        if not url_elem:
            self.logger.debug("URL element not found")
            return None

        # Get href attribute
        url = url_elem.get('href', '')
        if not url:
            return None

        # Normalize URL
        url = normalize_url(url, self.config.base_url)

        # Generate external ID from URL
        external_id = generate_external_id_hash(url)

        # Extract publication date
        publication_date = None
        date_elem = item.select_one(self.config.selectors['date'])
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            try:
                publication_date = validate_date(date_text)
            except Exception as e:
                self.logger.debug(f"Failed to parse date '{date_text}': {e}")

        # Extract municipality (if selector provided)
        municipality = None
        if 'municipality' in self.config.selectors:
            muni_elem = item.select_one(self.config.selectors['municipality'])
            if muni_elem:
                municipality = validate_municipality(muni_elem.get_text(strip=True))

        # Extract description (if selector provided)
        description = None
        if 'description' in self.config.selectors:
            desc_elem = item.select_one(self.config.selectors['description'])
            if desc_elem:
                description = desc_elem.get_text(strip=True)

        # Determine document type from URL
        from open_webui.scraper.validators import validate_document_type
        doc_type_str = validate_document_type(url)
        doc_type = DocumentType(doc_type_str)

        return DocumentMetadata(
            title=title,
            url=url,
            external_id=external_id,
            publication_date=publication_date,
            municipality=municipality,
            document_type=doc_type,
            description=description,
            metadata={
                'source': 'gemeenteblad',
                'scraped_at': datetime.now().isoformat(),
            }
        )


# Register the plugin
register_plugin('gemeenteblad', GemeentebladPlugin)
