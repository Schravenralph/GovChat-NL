"""
Unit tests for base scraper plugin functionality.
"""

import pytest
import asyncio
from datetime import date
from typing import List, Optional

from open_webui.scraper.base import ScraperPlugin, BaseScraper
from open_webui.scraper.models import DocumentMetadata, ScraperConfig, DocumentType


class MockScraperPlugin(ScraperPlugin):
    """Mock scraper plugin for testing."""

    def __init__(self, config: ScraperConfig):
        super().__init__(config)
        self.discover_called = False
        self.download_called = False

    async def discover_documents(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_pages: Optional[int] = None,
        **kwargs
    ) -> List[DocumentMetadata]:
        self.discover_called = True
        return [
            DocumentMetadata(
                title="Test Document",
                url="https://example.com/doc1",
                external_id="test-doc-1",
                document_type=DocumentType.PDF
            )
        ]

    async def download_document(self, doc_metadata: DocumentMetadata) -> bytes:
        self.download_called = True
        return b"Mock PDF content"

    def validate_config(self) -> bool:
        return self._validate_base_config()


class MockBaseScraperPlugin(BaseScraper):
    """Mock base scraper plugin for testing BaseScraper features."""

    def __init__(self, config: ScraperConfig):
        super().__init__(config)
        self.discover_called = False
        self.download_called = False

    async def discover_documents(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_pages: Optional[int] = None,
        **kwargs
    ) -> List[DocumentMetadata]:
        self.discover_called = True
        return [
            DocumentMetadata(
                title="Test Document",
                url="https://example.com/doc1",
                external_id="test-doc-1",
                document_type=DocumentType.PDF
            )
        ]

    async def download_document(self, doc_metadata: DocumentMetadata) -> bytes:
        self.download_called = True
        return b"Mock PDF content"

    def validate_config(self) -> bool:
        return self._validate_base_config()


class TestBasePlugin:
    """Test base plugin functionality."""

    def test_plugin_initialization(self):
        """Test plugin initialization with valid config."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        assert plugin.config == config
        assert plugin.stats.total_requests == 0

    def test_plugin_initialization_invalid_config(self):
        """Test plugin initialization with invalid config."""
        with pytest.raises(ValueError):
            config = ScraperConfig(
                base_url="invalid-url",  # Invalid URL
                rate_limit=10
            )
            MockScraperPlugin(config)

    @pytest.mark.asyncio
    async def test_scrape_method(self):
        """Test main scrape method."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        result = await plugin.scrape()

        assert plugin.discover_called
        assert result.success
        assert result.total_found == 1
        assert len(result.documents) == 1
        assert result.documents[0].title == "Test Document"

    @pytest.mark.asyncio
    async def test_scrape_with_date_filter(self):
        """Test scrape with date filtering."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        start_date = date(2025, 1, 1)
        end_date = date(2025, 12, 31)

        result = await plugin.scrape(start_date=start_date, end_date=end_date)

        assert result.success
        assert result.total_found == 1

    @pytest.mark.asyncio
    async def test_scrape_with_max_pages(self):
        """Test scrape with max_pages limit."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        result = await plugin.scrape(max_pages=2)

        assert result.success
        assert result.total_found == 1

    def test_get_stats(self):
        """Test getting statistics."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        stats = plugin.get_stats()

        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.failed_requests == 0

    def test_reset_stats(self):
        """Test resetting statistics."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        plugin.stats.total_requests = 10
        plugin.reset_stats()

        assert plugin.stats.total_requests == 0

    def test_record_request_success(self):
        """Test recording successful request."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        plugin._record_request(success=True, response_time_ms=100.0)

        assert plugin.stats.total_requests == 1
        assert plugin.stats.successful_requests == 1
        assert plugin.stats.failed_requests == 0
        assert plugin.stats.avg_response_time_ms == 100.0

    def test_record_request_failure(self):
        """Test recording failed request."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        plugin._record_request(success=False, response_time_ms=0.0)

        assert plugin.stats.total_requests == 1
        assert plugin.stats.successful_requests == 0
        assert plugin.stats.failed_requests == 1

    def test_record_multiple_requests(self):
        """Test averaging response times over multiple requests."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        plugin._record_request(success=True, response_time_ms=100.0)
        plugin._record_request(success=True, response_time_ms=200.0)
        plugin._record_request(success=True, response_time_ms=300.0)

        assert plugin.stats.total_requests == 3
        assert plugin.stats.successful_requests == 3
        assert plugin.stats.avg_response_time_ms == 200.0

    def test_record_retry(self):
        """Test recording retry attempts."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        plugin._record_retry()
        plugin._record_retry()

        assert plugin.stats.retry_attempts == 2

    def test_record_rate_limit(self):
        """Test recording rate limit events."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        plugin._record_rate_limit()

        assert plugin.stats.rate_limited_requests == 1

    def test_record_document_discovered(self):
        """Test recording discovered documents."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        plugin._record_document_discovered()
        plugin._record_document_discovered()

        assert plugin.stats.documents_discovered == 2

    @pytest.mark.asyncio
    async def test_test_connection(self):
        """Test connection testing."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockScraperPlugin(config)

        success = await plugin.test_connection()

        assert success
        assert plugin.discover_called


class TestBaseScraper:
    """Test BaseScraper utility class."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )

        async with MockBaseScraperPlugin(config) as plugin:
            assert plugin._session is not None

        # Session should be closed after exiting context
        assert plugin._session is None or plugin._session.closed

    def test_get_headers_default(self):
        """Test getting default headers."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10
        )
        plugin = MockBaseScraperPlugin(config)

        headers = plugin.get_headers()

        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Accept-Language' in headers
        assert 'GovChat-NL' in headers['User-Agent']

    def test_get_headers_custom_user_agent(self):
        """Test getting headers with custom User-Agent."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10,
            user_agent="Custom Bot/1.0"
        )
        plugin = MockBaseScraperPlugin(config)

        headers = plugin.get_headers()

        assert headers['User-Agent'] == "Custom Bot/1.0"

    def test_get_headers_custom_headers(self):
        """Test getting headers with custom additions."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10,
            headers={
                'X-Custom-Header': 'CustomValue',
                'Authorization': 'Bearer token123'
            }
        )
        plugin = MockBaseScraperPlugin(config)

        headers = plugin.get_headers()

        assert headers['X-Custom-Header'] == 'CustomValue'
        assert headers['Authorization'] == 'Bearer token123'


class TestConfigValidation:
    """Test configuration validation."""

    def test_valid_config(self):
        """Test valid configuration."""
        config = ScraperConfig(
            base_url="https://example.com",
            rate_limit=10,
            crawl_delay=1.0,
            timeout=30,
            max_retries=3
        )
        plugin = MockScraperPlugin(config)

        assert plugin.config.base_url == "https://example.com"
        assert plugin.config.rate_limit == 10

    def test_invalid_base_url(self):
        """Test invalid base URL."""
        with pytest.raises(ValueError):
            config = ScraperConfig(
                base_url="not-a-url",
                rate_limit=10
            )
            MockScraperPlugin(config)

    def test_invalid_rate_limit_too_low(self):
        """Test rate limit too low."""
        with pytest.raises(ValueError):
            config = ScraperConfig(
                base_url="https://example.com",
                rate_limit=0
            )
            MockScraperPlugin(config)

    def test_invalid_rate_limit_too_high(self):
        """Test rate limit too high."""
        with pytest.raises(ValueError):
            config = ScraperConfig(
                base_url="https://example.com",
                rate_limit=150
            )
            MockScraperPlugin(config)

    def test_negative_crawl_delay(self):
        """Test negative crawl delay."""
        with pytest.raises(ValueError):
            config = ScraperConfig(
                base_url="https://example.com",
                rate_limit=10,
                crawl_delay=-1.0
            )
            MockScraperPlugin(config)

    def test_invalid_timeout(self):
        """Test invalid timeout."""
        with pytest.raises(ValueError):
            config = ScraperConfig(
                base_url="https://example.com",
                rate_limit=10,
                timeout=0
            )
            MockScraperPlugin(config)

    def test_negative_max_retries(self):
        """Test negative max retries."""
        with pytest.raises(ValueError):
            config = ScraperConfig(
                base_url="https://example.com",
                rate_limit=10,
                max_retries=-1
            )
            MockScraperPlugin(config)
