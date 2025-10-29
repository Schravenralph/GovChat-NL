"""Tests for MeilisearchService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from open_webui.services.meilisearch_service import MeilisearchService


class MockClient:
    """Mock Meilisearch client."""

    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.closed = False

    async def health(self):
        """Mock health check."""
        return {"status": "available"}

    async def aclose(self):
        """Mock close."""
        self.closed = True

    def index(self, name):
        """Mock index getter."""
        return MockIndex(name)

    async def create_index(self, name, primary_key=None):
        """Mock index creation."""
        task = MagicMock()
        task.task_uid = "test-task-123"
        return task

    async def delete_index(self, name):
        """Mock index deletion."""
        task = MagicMock()
        task.task_uid = "test-task-456"
        return task

    async def wait_for_task(self, task_uid):
        """Mock task waiting."""
        result = MagicMock()
        result.status = "succeeded"
        return result


class MockIndex:
    """Mock Meilisearch index."""

    def __init__(self, name):
        self.name = name
        self._documents = []

    async def update_searchable_attributes(self, attrs):
        """Mock update searchable attributes."""
        pass

    async def update_filterable_attributes(self, attrs):
        """Mock update filterable attributes."""
        pass

    async def update_sortable_attributes(self, attrs):
        """Mock update sortable attributes."""
        pass

    async def update_ranking_rules(self, rules):
        """Mock update ranking rules."""
        pass

    async def update_stop_words(self, words):
        """Mock update stop words."""
        pass

    async def add_documents(self, docs):
        """Mock add documents."""
        self._documents.extend(docs)
        task = MagicMock()
        task.task_uid = "add-task-123"
        return task

    async def update_documents(self, docs):
        """Mock update documents."""
        task = MagicMock()
        task.task_uid = "update-task-123"
        return task

    async def delete_documents(self, ids):
        """Mock delete documents."""
        task = MagicMock()
        task.task_uid = "delete-task-123"
        return task

    async def delete_all_documents(self):
        """Mock delete all."""
        self._documents = []
        task = MagicMock()
        task.task_uid = "delete-all-task-123"
        return task

    async def search(self, query, **kwargs):
        """Mock search."""
        result = MagicMock()
        result.hits = [
            {
                'id': 'doc1',
                'title': 'Test Document',
                'content': 'Test content with query keyword',
                'municipality': 'Amsterdam',
                'publication_date': '2025-01-01',
                'document_type': 'pdf',
                'source_id': 'source-123'
            }
        ]
        result.estimated_total_hits = 1
        result.facet_distribution = {
            'municipality': {'Amsterdam': 1},
            'category': {},
            'document_type': {'pdf': 1}
        }
        result.processing_time_ms = 5
        return result

    async def get_stats(self):
        """Mock get stats."""
        stats = MagicMock()
        stats.number_of_documents = len(self._documents)
        stats.is_indexing = False
        stats.field_distribution = {}
        return stats


@pytest.fixture
def meili_service():
    """Create MeilisearchService with mocked client."""
    service = MeilisearchService(
        url="http://test:7700",
        api_key="test-key",
        index_name="test-index"
    )
    return service


@pytest.mark.asyncio
async def test_connect(meili_service):
    """Test connecting to Meilisearch."""
    with patch('open_webui.services.meilisearch_service.Client', return_value=MockClient("http://test:7700", "test-key")):
        await meili_service.connect()
        assert meili_service._connected is True
        assert meili_service.client is not None


@pytest.mark.asyncio
async def test_disconnect(meili_service):
    """Test disconnecting from Meilisearch."""
    with patch('open_webui.services.meilisearch_service.Client', return_value=MockClient("http://test:7700", "test-key")):
        await meili_service.connect()
        await meili_service.disconnect()
        assert meili_service._connected is False


@pytest.mark.asyncio
async def test_health_check(meili_service):
    """Test health check."""
    with patch('open_webui.services.meilisearch_service.Client', return_value=MockClient("http://test:7700", "test-key")):
        result = await meili_service.health_check()
        assert result is True


@pytest.mark.asyncio
async def test_create_index(meili_service):
    """Test creating index."""
    with patch('open_webui.services.meilisearch_service.Client', return_value=MockClient("http://test:7700", "test-key")):
        await meili_service.connect()
        result = await meili_service.create_index()
        assert result is True


@pytest.mark.asyncio
async def test_index_documents(meili_service):
    """Test indexing documents."""
    with patch('open_webui.services.meilisearch_service.Client', return_value=MockClient("http://test:7700", "test-key")):
        await meili_service.connect()

        docs = [
            {
                'id': 'doc1',
                'title': 'Test Doc',
                'content': 'Test content',
                'municipality': 'Amsterdam',
                'publication_date': '2025-01-01',
                'document_type': 'pdf',
                'source_id': 'source-123'
            }
        ]

        result = await meili_service.index_documents(docs)
        assert result is True


@pytest.mark.asyncio
async def test_search_basic(meili_service):
    """Test basic search."""
    with patch('open_webui.services.meilisearch_service.Client', return_value=MockClient("http://test:7700", "test-key")):
        await meili_service.connect()

        results = await meili_service.search(
            query="test query",
            page=1,
            limit=20
        )

        assert 'hits' in results
        assert 'total' in results
        assert 'facetDistribution' in results
        assert len(results['hits']) > 0


@pytest.mark.asyncio
async def test_search_with_filters(meili_service):
    """Test search with filters."""
    with patch('open_webui.services.meilisearch_service.Client', return_value=MockClient("http://test:7700", "test-key")):
        await meili_service.connect()

        filters = {
            'municipality': ['Amsterdam'],
            'document_type': 'pdf',
            'date_from': '2025-01-01',
            'date_to': '2025-12-31'
        }

        results = await meili_service.search(
            query="test",
            filters=filters,
            page=1,
            limit=10
        )

        assert results is not None
        assert 'hits' in results


@pytest.mark.asyncio
async def test_delete_documents(meili_service):
    """Test deleting documents."""
    with patch('open_webui.services.meilisearch_service.Client', return_value=MockClient("http://test:7700", "test-key")):
        await meili_service.connect()

        result = await meili_service.delete_documents(['doc1', 'doc2'])
        assert result is True


@pytest.mark.asyncio
async def test_get_stats(meili_service):
    """Test getting stats."""
    with patch('open_webui.services.meilisearch_service.Client', return_value=MockClient("http://test:7700", "test-key")):
        await meili_service.connect()

        stats = await meili_service.get_stats()
        assert 'numberOfDocuments' in stats
        assert 'isIndexing' in stats


@pytest.mark.asyncio
async def test_context_manager(meili_service):
    """Test using service as context manager."""
    with patch('open_webui.services.meilisearch_service.Client', return_value=MockClient("http://test:7700", "test-key")):
        async with meili_service as service:
            assert service._connected is True

        # Should be disconnected after exit
        assert service._connected is False


@pytest.mark.asyncio
async def test_connection_error():
    """Test handling connection errors."""
    service = MeilisearchService(
        url="http://invalid:7700",
        api_key="test-key"
    )

    with patch('open_webui.services.meilisearch_service.Client') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.health = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(ConnectionError):
            await service.connect()
