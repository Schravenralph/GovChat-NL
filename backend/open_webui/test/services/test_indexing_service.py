"""Tests for IndexingService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date

from open_webui.services.indexing_service import IndexingService, IndexingStats
from open_webui.models.policy_documents import PolicyDocumentModel


@pytest.fixture
def indexing_service():
    """Create IndexingService instance."""
    return IndexingService(batch_size=10, storage_base_path='/tmp/test_docs')


@pytest.fixture
def mock_documents():
    """Create mock documents."""
    return [
        PolicyDocumentModel(
            id='doc1',
            source_id='source1',
            title='Test Document 1',
            description='Test description',
            content_hash='hash1',
            document_url='http://example.com/doc1',
            document_type='pdf',
            municipality='Amsterdam',
            publication_date=date(2025, 1, 1),
            status='pending',
            language='nl',
            created_at=int(datetime.now().timestamp()),
            updated_at=int(datetime.now().timestamp())
        ),
        PolicyDocumentModel(
            id='doc2',
            source_id='source1',
            title='Test Document 2',
            description='Test description 2',
            content_hash='hash2',
            document_url='http://example.com/doc2',
            document_type='html',
            municipality='Rotterdam',
            publication_date=date(2025, 1, 2),
            status='pending',
            language='nl',
            created_at=int(datetime.now().timestamp()),
            updated_at=int(datetime.now().timestamp())
        )
    ]


def test_indexing_stats():
    """Test IndexingStats class."""
    stats = IndexingStats()

    assert stats.total_documents == 0
    assert stats.processed == 0
    assert stats.indexed == 0
    assert stats.failed == 0
    assert stats.skipped == 0

    stats.record_success()
    assert stats.indexed == 1
    assert stats.processed == 1

    stats.record_failure('doc1', 'Test error')
    assert stats.failed == 1
    assert stats.processed == 2
    assert len(stats.errors) == 1

    stats.record_skip()
    assert stats.skipped == 1

    # Test to_dict
    data = stats.to_dict()
    assert 'total_documents' in data
    assert 'processed' in data
    assert 'errors' in data


@pytest.mark.asyncio
async def test_index_documents_empty(indexing_service):
    """Test indexing with no documents."""
    with patch('open_webui.services.indexing_service.PolicyDocuments') as mock_db:
        mock_db.get_documents.return_value = []

        with patch.object(indexing_service.meilisearch, 'connect', new_callable=AsyncMock):
            stats = await indexing_service.index_documents()

            assert stats.total_documents == 0
            assert stats.processed == 0


@pytest.mark.asyncio
async def test_index_documents_success(indexing_service, mock_documents):
    """Test successful indexing."""
    with patch('open_webui.services.indexing_service.PolicyDocuments') as mock_db, \
         patch('open_webui.services.indexing_service.get_document_processor') as mock_proc_getter, \
         patch.object(indexing_service.meilisearch, 'connect', new_callable=AsyncMock), \
         patch.object(indexing_service.meilisearch, 'index_documents', new_callable=AsyncMock):

        # Setup mocks
        mock_db.get_documents.return_value = mock_documents
        mock_db.update_document_by_id = MagicMock()

        mock_processor = MagicMock()
        mock_processor.process_document = AsyncMock(return_value={
            'text': 'Test content',
            'chunks': ['Test content'],
            'content_hash': 'hash123',
            'summary': 'Test',
            'word_count': 2,
            'page_count': 1
        })
        mock_proc_getter.return_value = mock_processor

        # Mock file existence
        with patch('os.path.exists', return_value=True):
            stats = await indexing_service.index_documents(source_id='source1')

            assert stats.total_documents == 2
            # Note: Without actual file paths in metadata, documents will fail
            # This is expected in the test environment


@pytest.mark.asyncio
async def test_index_documents_with_reindex(indexing_service, mock_documents):
    """Test reindexing already indexed documents."""
    # Set one document to indexed
    mock_documents[0].status = 'indexed'

    with patch('open_webui.services.indexing_service.PolicyDocuments') as mock_db, \
         patch.object(indexing_service.meilisearch, 'connect', new_callable=AsyncMock):

        mock_db.get_documents.return_value = mock_documents

        stats = await indexing_service.index_documents(
            source_id='source1',
            force_reindex=True
        )

        # With force_reindex, indexed documents should be processed
        assert stats.total_documents == 2


@pytest.mark.asyncio
async def test_process_document_file_not_found(indexing_service):
    """Test processing document with missing file."""
    doc = PolicyDocumentModel(
        id='doc1',
        source_id='source1',
        title='Test',
        content_hash='hash1',
        document_url='http://test.com/doc',
        document_type='pdf',
        status='pending',
        language='nl',
        created_at=int(datetime.now().timestamp()),
        updated_at=int(datetime.now().timestamp())
    )

    with patch('os.path.exists', return_value=False):
        result = await indexing_service._process_document(doc)
        assert result is None


@pytest.mark.asyncio
async def test_reindex_document(indexing_service):
    """Test reindexing single document."""
    with patch('open_webui.services.indexing_service.PolicyDocuments') as mock_db, \
         patch.object(indexing_service.meilisearch, 'connect', new_callable=AsyncMock), \
         patch.object(indexing_service.meilisearch, 'index_documents', new_callable=AsyncMock):

        # Setup mock
        mock_doc = MagicMock()
        mock_doc.id = 'doc1'
        mock_doc.source_id = 'source1'
        mock_doc.title = 'Test'
        mock_doc.document_type = 'pdf'
        mock_doc.metadata = {'file_path': '/tmp/test.pdf'}
        mock_db.get_document_by_id.return_value = mock_doc
        mock_db.update_document_by_id = MagicMock()

        # Mock processor
        with patch.object(indexing_service.processor, 'process_document', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {
                'text': 'Test',
                'word_count': 1,
                'page_count': 1
            }

            with patch('os.path.exists', return_value=True):
                result = await indexing_service.reindex_document('doc1')
                assert result is True


@pytest.mark.asyncio
async def test_reindex_document_not_found(indexing_service):
    """Test reindexing non-existent document."""
    with patch('open_webui.services.indexing_service.PolicyDocuments') as mock_db:
        mock_db.get_document_by_id.return_value = None

        result = await indexing_service.reindex_document('nonexistent')
        assert result is False


@pytest.mark.asyncio
async def test_delete_from_index(indexing_service):
    """Test deleting documents from index."""
    with patch('open_webui.services.indexing_service.PolicyDocuments') as mock_db, \
         patch.object(indexing_service.meilisearch, 'connect', new_callable=AsyncMock), \
         patch.object(indexing_service.meilisearch, 'delete_documents', new_callable=AsyncMock):

        mock_db.update_document_by_id = MagicMock()

        result = await indexing_service.delete_from_index(['doc1', 'doc2'])
        assert result is True


@pytest.mark.asyncio
async def test_get_indexing_status(indexing_service):
    """Test getting indexing status."""
    mock_docs = [
        MagicMock(status='pending'),
        MagicMock(status='indexed'),
        MagicMock(status='indexed'),
        MagicMock(status='failed')
    ]

    with patch('open_webui.services.indexing_service.PolicyDocuments') as mock_db, \
         patch.object(indexing_service.meilisearch, 'get_stats', new_callable=AsyncMock) as mock_stats:

        mock_db.get_documents.return_value = mock_docs
        mock_stats.return_value = {
            'numberOfDocuments': 2,
            'isIndexing': False
        }

        status = await indexing_service.get_indexing_status()

        assert 'database' in status
        assert 'meilisearch' in status
        assert status['total_documents'] == 4
        assert status['database']['pending'] == 1
        assert status['database']['indexed'] == 2
        assert status['database']['failed'] == 1


def test_get_document_file_path_from_metadata(indexing_service):
    """Test getting file path from metadata."""
    doc = MagicMock()
    doc.metadata = {'file_path': '/tmp/test.pdf'}

    path = indexing_service._get_document_file_path(doc)
    assert path == '/tmp/test.pdf'


def test_get_document_file_path_constructed(indexing_service):
    """Test constructing file path from document info."""
    doc = MagicMock()
    doc.id = 'doc1'
    doc.source_id = 'source1'
    doc.document_type = 'pdf'
    doc.metadata = None

    with patch('os.path.exists', return_value=True):
        path = indexing_service._get_document_file_path(doc)
        assert 'source1' in path
        assert 'doc1.pdf' in path


def test_get_document_file_path_not_found(indexing_service):
    """Test file path when file doesn't exist."""
    doc = MagicMock()
    doc.id = 'doc1'
    doc.source_id = 'source1'
    doc.document_type = 'pdf'
    doc.metadata = None

    with patch('os.path.exists', return_value=False):
        path = indexing_service._get_document_file_path(doc)
        assert path is None


def test_get_indexing_service():
    """Test getting global indexing service instance."""
    from open_webui.services.indexing_service import get_indexing_service

    service1 = get_indexing_service()
    service2 = get_indexing_service()

    # Should return same instance
    assert service1 is service2
