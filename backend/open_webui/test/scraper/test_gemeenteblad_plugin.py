"""
Unit tests for Gemeenteblad scraper plugin.
"""

import pytest
import os
from datetime import date
from aioresponses import aioresponses

from open_webui.scraper import ScraperConfig, get_plugin
from open_webui.scraper.plugins.gemeenteblad import GemeentebladPlugin


# Path to test fixtures
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


def load_fixture(filename: str) -> str:
    """Load HTML fixture file."""
    filepath = os.path.join(FIXTURES_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


class TestGemeentebladPlugin:
    """Test Gemeenteblad plugin."""

    def test_plugin_registration(self):
        """Test that plugin is registered."""
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

        plugin = get_plugin('gemeenteblad', config)

        assert isinstance(plugin, GemeentebladPlugin)

    def test_plugin_initialization(self):
        """Test plugin initialization."""
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

        plugin = GemeentebladPlugin(config)

        assert plugin.config.base_url == "https://gemeentebladen.nl"
        assert plugin.rate_limiter is not None
        assert plugin.retry_middleware is not None

    def test_validate_config_missing_selectors(self):
        """Test config validation with missing selectors."""
        with pytest.raises(ValueError) as exc_info:
            config = ScraperConfig(
                base_url="https://gemeentebladen.nl",
                rate_limit=10,
                selectors={
                    'item': 'div.document-item',
                    # Missing required selectors
                }
            )
            GemeentebladPlugin(config)

        assert "Missing required selectors" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_discover_documents_success(self):
        """Test successful document discovery."""
        config = ScraperConfig(
            base_url="https://gemeentebladen.nl",
            rate_limit=100,  # High rate to avoid delays in tests
            crawl_delay=0.1,
            selectors={
                'item': 'div.document-item',
                'title': 'h2.title',
                'url': 'a.document-link',
                'date': 'span.publication-date',
                'municipality': 'span.municipality',
                'description': 'p.description'
            }
        )

        plugin = GemeentebladPlugin(config)

        # Mock HTTP responses
        with aioresponses() as mocked:
            # Mock robots.txt
            mocked.get(
                'https://gemeentebladen.nl/robots.txt',
                status=404
            )

            # Mock search page 1
            page1_html = load_fixture('gemeenteblad_search_page1.html')
            mocked.get(
                'https://gemeentebladen.nl/search',
                status=200,
                body=page1_html
            )

            # Mock empty page to signal end
            empty_html = load_fixture('gemeenteblad_empty_page.html')
            mocked.get(
                'https://gemeentebladen.nl/search?page=2',
                status=200,
                body=empty_html
            )
            mocked.get(
                'https://gemeentebladen.nl/search?page=3',
                status=200,
                body=empty_html
            )
            mocked.get(
                'https://gemeentebladen.nl/search?page=4',
                status=200,
                body=empty_html
            )

            documents = await plugin.discover_documents(max_pages=5)

        assert len(documents) == 5
        assert documents[0].title == "Vergunning Evenement Vondelpark 2025"
        assert documents[0].municipality == "Amsterdam"
        assert documents[0].publication_date == date(2025, 1, 15)
        assert "/documents/12345" in documents[0].url

    @pytest.mark.asyncio
    async def test_discover_documents_pagination(self):
        """Test document discovery with pagination."""
        config = ScraperConfig(
            base_url="https://gemeentebladen.nl",
            rate_limit=100,
            crawl_delay=0.1,
            selectors={
                'item': 'div.document-item',
                'title': 'h2.title',
                'url': 'a.document-link',
                'date': 'span.publication-date',
                'municipality': 'span.municipality',
                'description': 'p.description'
            }
        )

        plugin = GemeentebladPlugin(config)

        with aioresponses() as mocked:
            # Mock robots.txt
            mocked.get(
                'https://gemeentebladen.nl/robots.txt',
                status=404
            )

            # Mock page 1
            page1_html = load_fixture('gemeenteblad_search_page1.html')
            mocked.get(
                'https://gemeentebladen.nl/search',
                status=200,
                body=page1_html
            )

            # Mock page 2
            page2_html = load_fixture('gemeenteblad_search_page2.html')
            mocked.get(
                'https://gemeentebladen.nl/search?page=2',
                status=200,
                body=page2_html
            )

            # Mock empty pages
            empty_html = load_fixture('gemeenteblad_empty_page.html')
            for i in range(3, 6):
                mocked.get(
                    f'https://gemeentebladen.nl/search?page={i}',
                    status=200,
                    body=empty_html
                )

            documents = await plugin.discover_documents()

        # Should find documents from both pages
        assert len(documents) == 7  # 5 from page 1, 2 from page 2

    @pytest.mark.asyncio
    async def test_discover_documents_with_date_filter(self):
        """Test document discovery with date filtering."""
        config = ScraperConfig(
            base_url="https://gemeentebladen.nl",
            rate_limit=100,
            crawl_delay=0.1,
            selectors={
                'item': 'div.document-item',
                'title': 'h2.title',
                'url': 'a.document-link',
                'date': 'span.publication-date'
            }
        )

        plugin = GemeentebladPlugin(config)

        with aioresponses() as mocked:
            mocked.get(
                'https://gemeentebladen.nl/robots.txt',
                status=404
            )

            page1_html = load_fixture('gemeenteblad_search_page1.html')
            mocked.get(
                'https://gemeentebladen.nl/search?from_date=2025-01-01&to_date=2025-12-31',
                status=200,
                body=page1_html
            )

            empty_html = load_fixture('gemeenteblad_empty_page.html')
            for i in range(2, 5):
                mocked.get(
                    f'https://gemeentebladen.nl/search?page={i}&from_date=2025-01-01&to_date=2025-12-31',
                    status=200,
                    body=empty_html
                )

            documents = await plugin.discover_documents(
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31)
            )

        assert len(documents) > 0

    @pytest.mark.asyncio
    async def test_discover_documents_max_pages_limit(self):
        """Test max_pages limit is respected."""
        config = ScraperConfig(
            base_url="https://gemeentebladen.nl",
            rate_limit=100,
            crawl_delay=0.1,
            selectors={
                'item': 'div.document-item',
                'title': 'h2.title',
                'url': 'a.document-link',
                'date': 'span.publication-date'
            }
        )

        plugin = GemeentebladPlugin(config)

        with aioresponses() as mocked:
            mocked.get(
                'https://gemeentebladen.nl/robots.txt',
                status=404
            )

            page1_html = load_fixture('gemeenteblad_search_page1.html')

            # Mock multiple pages
            for i in range(1, 11):
                url = f'https://gemeentebladen.nl/search?page={i}' if i > 1 else 'https://gemeentebladen.nl/search'
                mocked.get(url, status=200, body=page1_html)

            documents = await plugin.discover_documents(max_pages=2)

        # Should only scrape 2 pages
        assert plugin.stats.total_requests <= 3  # robots.txt + 2 pages

    @pytest.mark.asyncio
    async def test_discover_documents_malformed_html(self):
        """Test handling of malformed HTML."""
        config = ScraperConfig(
            base_url="https://gemeentebladen.nl",
            rate_limit=100,
            crawl_delay=0.1,
            selectors={
                'item': 'div.document-item',
                'title': 'h2.title',
                'url': 'a.document-link',
                'date': 'span.publication-date'
            }
        )

        plugin = GemeentebladPlugin(config)

        with aioresponses() as mocked:
            mocked.get(
                'https://gemeentebladen.nl/robots.txt',
                status=404
            )

            malformed_html = load_fixture('gemeenteblad_malformed.html')
            mocked.get(
                'https://gemeentebladen.nl/search',
                status=200,
                body=malformed_html
            )

            empty_html = load_fixture('gemeenteblad_empty_page.html')
            for i in range(2, 5):
                mocked.get(
                    f'https://gemeentebladen.nl/search?page={i}',
                    status=200,
                    body=empty_html
                )

            documents = await plugin.discover_documents()

        # Should skip items with missing required elements
        # Malformed fixture has 3 items, all invalid
        assert len(documents) == 0

    @pytest.mark.asyncio
    async def test_discover_documents_404_error(self):
        """Test handling of 404 errors."""
        config = ScraperConfig(
            base_url="https://gemeentebladen.nl",
            rate_limit=100,
            crawl_delay=0.1,
            selectors={
                'item': 'div.document-item',
                'title': 'h2.title',
                'url': 'a.document-link',
                'date': 'span.publication-date'
            }
        )

        plugin = GemeentebladPlugin(config)

        with aioresponses() as mocked:
            mocked.get(
                'https://gemeentebladen.nl/robots.txt',
                status=404
            )

            # Return 404 for search
            mocked.get(
                'https://gemeentebladen.nl/search',
                status=404
            )

            documents = await plugin.discover_documents()

        # Should return empty list on error
        assert len(documents) == 0
        assert plugin.stats.failed_requests > 0

    @pytest.mark.asyncio
    async def test_download_document(self):
        """Test downloading a document."""
        config = ScraperConfig(
            base_url="https://gemeentebladen.nl",
            rate_limit=100,
            selectors={
                'item': 'div.document-item',
                'title': 'h2.title',
                'url': 'a.document-link',
                'date': 'span.publication-date'
            }
        )

        plugin = GemeentebladPlugin(config)

        from open_webui.scraper.models import DocumentMetadata, DocumentType

        doc = DocumentMetadata(
            title="Test Document",
            url="https://gemeentebladen.nl/documents/12345.pdf",
            external_id="test-12345",
            document_type=DocumentType.PDF
        )

        mock_pdf_content = b"%PDF-1.4\n%Mock PDF content"

        with aioresponses() as mocked:
            mocked.get(
                'https://gemeentebladen.nl/documents/12345.pdf',
                status=200,
                body=mock_pdf_content
            )

            content = await plugin.download_document(doc)

        assert content == mock_pdf_content
        assert plugin.stats.successful_requests == 1

    @pytest.mark.asyncio
    async def test_download_document_failure(self):
        """Test download failure handling."""
        config = ScraperConfig(
            base_url="https://gemeentebladen.nl",
            rate_limit=100,
            selectors={
                'item': 'div.document-item',
                'title': 'h2.title',
                'url': 'a.document-link',
                'date': 'span.publication-date'
            }
        )

        plugin = GemeentebladPlugin(config)

        from open_webui.scraper.models import DocumentMetadata, DocumentType

        doc = DocumentMetadata(
            title="Test Document",
            url="https://gemeentebladen.nl/documents/99999.pdf",
            external_id="test-99999",
            document_type=DocumentType.PDF
        )

        with aioresponses() as mocked:
            mocked.get(
                'https://gemeentebladen.nl/documents/99999.pdf',
                status=404
            )

            with pytest.raises(Exception):
                await plugin.download_document(doc)

        assert plugin.stats.failed_requests > 0

    @pytest.mark.asyncio
    async def test_scrape_method(self):
        """Test main scrape method."""
        config = ScraperConfig(
            base_url="https://gemeentebladen.nl",
            rate_limit=100,
            crawl_delay=0.1,
            selectors={
                'item': 'div.document-item',
                'title': 'h2.title',
                'url': 'a.document-link',
                'date': 'span.publication-date'
            }
        )

        plugin = GemeentebladPlugin(config)

        with aioresponses() as mocked:
            mocked.get(
                'https://gemeentebladen.nl/robots.txt',
                status=404
            )

            page1_html = load_fixture('gemeenteblad_search_page1.html')
            mocked.get(
                'https://gemeentebladen.nl/search',
                status=200,
                body=page1_html
            )

            empty_html = load_fixture('gemeenteblad_empty_page.html')
            for i in range(2, 5):
                mocked.get(
                    f'https://gemeentebladen.nl/search?page={i}',
                    status=200,
                    body=empty_html
                )

            result = await plugin.scrape()

        assert result.success
        assert result.total_found == 5
        assert len(result.documents) == 5
        assert result.duration_seconds > 0
        assert len(result.errors) == 0
