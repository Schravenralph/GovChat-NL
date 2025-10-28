"""
Base scraper plugin interface for Policy Scanner.

This module defines the abstract base class that all scraper plugins
must implement. It provides the contract for discovering and downloading
policy documents from various government sources.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Dict, List, Optional, Any

from open_webui.scraper.models import (
    DocumentMetadata,
    ScraperConfig,
    ScrapeResult,
    ScraperStats
)
from open_webui.scraper.validators import (
    validate_url,
    validate_external_id,
    validate_rate_limit
)


logger = logging.getLogger(__name__)


class ScraperPlugin(ABC):
    """
    Abstract base class for all scraper plugins.

    Subclasses must implement:
    - discover_documents(): Find available documents
    - download_document(): Download document content
    - validate_config(): Validate plugin-specific configuration

    The plugin automatically handles:
    - Rate limiting
    - Statistics tracking
    - Basic error handling
    """

    def __init__(self, config: ScraperConfig):
        """
        Initialize the scraper plugin.

        Args:
            config: Scraper configuration
        """
        self.config = config
        self.stats = ScraperStats()
        self.logger = logger.getChild(self.__class__.__name__)

        # Validate configuration
        if not self.validate_config():
            raise ValueError(f"Invalid configuration for {self.__class__.__name__}")

        self.logger.info(
            f"Initialized {self.__class__.__name__} with base_url={config.base_url}"
        )

    @abstractmethod
    async def discover_documents(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_pages: Optional[int] = None,
        **kwargs
    ) -> List[DocumentMetadata]:
        """
        Discover available policy documents from the source.

        This method should handle:
        - Pagination through search results
        - Date filtering
        - Extracting document metadata
        - Respecting rate limits

        Args:
            start_date: Filter documents from this date onwards
            end_date: Filter documents up to this date
            max_pages: Maximum number of pages to scrape (None = all)
            **kwargs: Plugin-specific parameters

        Returns:
            List of DocumentMetadata objects

        Raises:
            Exception: If discovery fails
        """
        pass

    @abstractmethod
    async def download_document(self, doc_metadata: DocumentMetadata) -> bytes:
        """
        Download the actual document content.

        Args:
            doc_metadata: Metadata for the document to download

        Returns:
            bytes: Document content

        Raises:
            Exception: If download fails
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate plugin-specific configuration.

        This method should check:
        - Required selectors are present
        - Custom parameters are valid
        - Authentication credentials (if needed)

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If configuration is invalid (with descriptive message)
        """
        pass

    async def scrape(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_pages: Optional[int] = None,
        **kwargs
    ) -> ScrapeResult:
        """
        Main entry point for scraping operation.

        This method wraps discover_documents with timing and error handling.

        Args:
            start_date: Filter documents from this date onwards
            end_date: Filter documents up to this date
            max_pages: Maximum number of pages to scrape
            **kwargs: Plugin-specific parameters

        Returns:
            ScrapeResult: Contains discovered documents and statistics
        """
        start_time = datetime.now()
        errors = []
        documents = []

        try:
            self.logger.info(
                f"Starting scrape: start_date={start_date}, end_date={end_date}, "
                f"max_pages={max_pages}"
            )

            documents = await self.discover_documents(
                start_date=start_date,
                end_date=end_date,
                max_pages=max_pages,
                **kwargs
            )

            self.logger.info(f"Discovered {len(documents)} documents")

        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            errors.append(error_msg)

        duration = (datetime.now() - start_time).total_seconds()

        return ScrapeResult(
            documents=documents,
            total_found=len(documents),
            pages_scraped=self.stats.total_requests,
            duration_seconds=duration,
            errors=errors,
            success=len(errors) == 0
        )

    def get_stats(self) -> ScraperStats:
        """
        Get current scraper statistics.

        Returns:
            ScraperStats: Current statistics
        """
        return self.stats

    def reset_stats(self):
        """Reset statistics counters."""
        self.stats = ScraperStats()
        self.logger.debug("Statistics reset")

    async def test_connection(self) -> bool:
        """
        Test connection to the source website.

        Returns:
            bool: True if connection successful
        """
        try:
            # Try to discover just one page
            documents = await self.discover_documents(max_pages=1)
            self.logger.info("Connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}", exc_info=True)
            return False

    def _validate_base_config(self) -> bool:
        """
        Validate common configuration parameters.

        Returns:
            bool: True if base configuration is valid

        Raises:
            ValueError: If base configuration is invalid
        """
        # Validate base URL
        try:
            validate_url(self.config.base_url)
        except Exception as e:
            raise ValueError(f"Invalid base_url: {e}")

        # Validate rate limit
        try:
            validate_rate_limit(self.config.rate_limit)
        except Exception as e:
            raise ValueError(f"Invalid rate_limit: {e}")

        # Validate crawl delay
        if self.config.crawl_delay < 0:
            raise ValueError("crawl_delay cannot be negative")

        # Validate timeout
        if self.config.timeout < 1:
            raise ValueError("timeout must be at least 1 second")

        # Validate max retries
        if self.config.max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        return True

    def _record_request(self, success: bool, response_time_ms: float):
        """
        Record statistics for a request.

        Args:
            success: Whether request was successful
            response_time_ms: Response time in milliseconds
        """
        self.stats.total_requests += 1

        if success:
            self.stats.successful_requests += 1
        else:
            self.stats.failed_requests += 1

        # Update average response time
        total_time = (
            self.stats.avg_response_time_ms * (self.stats.total_requests - 1)
        )
        self.stats.avg_response_time_ms = (
            total_time + response_time_ms
        ) / self.stats.total_requests

    def _record_retry(self):
        """Record a retry attempt."""
        self.stats.retry_attempts += 1

    def _record_rate_limit(self):
        """Record a rate limit event."""
        self.stats.rate_limited_requests += 1

    def _record_document_discovered(self):
        """Record a discovered document."""
        self.stats.documents_discovered += 1


class BaseScraper(ScraperPlugin):
    """
    Base implementation with common scraping utilities.

    This class provides reusable methods for common scraping tasks.
    Plugin implementations can extend this class to avoid code duplication.
    """

    def __init__(self, config: ScraperConfig):
        """Initialize base scraper."""
        super().__init__(config)
        self._session = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        import aiohttp
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for requests.

        Returns:
            Dict of headers
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }

        # Add custom User-Agent or default
        if self.config.user_agent:
            headers['User-Agent'] = self.config.user_agent
        else:
            headers['User-Agent'] = (
                'Mozilla/5.0 (GovChat-NL Policy Scanner) '
                'AppleWebKit/537.36 (KHTML, like Gecko)'
            )

        # Add custom headers from config
        headers.update(self.config.headers)

        return headers

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
