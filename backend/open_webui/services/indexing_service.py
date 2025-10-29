"""
Document Indexing Service for Policy Scanner.

This module orchestrates the document indexing workflow:
1. Fetch documents from PostgreSQL
2. Process documents (extract text)
3. Index documents in Meilisearch
4. Update document status in database
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

from open_webui.env import SRC_LOG_LEVELS
from open_webui.models.policy_documents import (
    PolicyDocuments,
    PolicyDocumentModel,
    PolicyDocumentUpdate
)
from open_webui.services.meilisearch_service import get_meilisearch_service
from open_webui.services.document_processor import get_document_processor, ProcessingError

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("MAIN", "INFO"))


class IndexingStats:
    """Statistics for an indexing run."""

    def __init__(self):
        self.total_documents = 0
        self.processed = 0
        self.indexed = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = datetime.now()
        self.errors: List[Dict[str, str]] = []

    def record_success(self):
        """Record a successful indexing."""
        self.processed += 1
        self.indexed += 1

    def record_failure(self, document_id: str, error: str):
        """Record a failed indexing."""
        self.processed += 1
        self.failed += 1
        self.errors.append({
            'document_id': document_id,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })

    def record_skip(self):
        """Record a skipped document."""
        self.skipped += 1

    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_documents': self.total_documents,
            'processed': self.processed,
            'indexed': self.indexed,
            'failed': self.failed,
            'skipped': self.skipped,
            'duration_seconds': self.duration_seconds,
            'errors': self.errors
        }


class IndexingService:
    """
    Service for orchestrating document indexing workflow.

    Handles:
    - Fetching documents from database
    - Processing documents (text extraction)
    - Indexing in Meilisearch
    - Status tracking in database
    - Batch processing
    - Error recovery
    """

    def __init__(
        self,
        batch_size: Optional[int] = None,
        storage_base_path: Optional[str] = None
    ):
        """
        Initialize indexing service.

        Args:
            batch_size: Documents per batch (defaults to env INDEXING_BATCH_SIZE)
            storage_base_path: Base path for document storage
        """
        self.batch_size = batch_size or int(os.getenv('INDEXING_BATCH_SIZE', '100'))
        self.storage_base_path = storage_base_path or os.getenv(
            'DOCUMENT_STORAGE_PATH',
            '/tmp/policy_documents'
        )
        self.meilisearch = get_meilisearch_service()
        self.processor = get_document_processor()

        log.info(
            f"IndexingService initialized: batch_size={self.batch_size}, "
            f"storage_path={self.storage_base_path}"
        )

    async def index_documents(
        self,
        source_id: Optional[str] = None,
        status: str = "pending",
        force_reindex: bool = False,
        max_documents: Optional[int] = None
    ) -> IndexingStats:
        """
        Index documents in batches.

        Args:
            source_id: Filter by source ID (None = all sources)
            status: Filter by status (default: 'pending')
            force_reindex: Reindex even if already indexed
            max_documents: Maximum number of documents to index

        Returns:
            IndexingStats with results
        """
        stats = IndexingStats()

        try:
            # Ensure Meilisearch is connected
            await self.meilisearch.connect()

            # Get documents from database
            log.info(
                f"Fetching documents: source_id={source_id}, status={status}, "
                f"force_reindex={force_reindex}"
            )

            documents = PolicyDocuments.get_documents(
                source_id=source_id,
                status=status if not force_reindex else None,
                limit=max_documents or 10000,
                offset=0
            )

            stats.total_documents = len(documents)
            log.info(f"Found {stats.total_documents} documents to index")

            if not documents:
                log.info("No documents to index")
                return stats

            # Process in batches
            for i in range(0, len(documents), self.batch_size):
                batch = documents[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                total_batches = (len(documents) + self.batch_size - 1) // self.batch_size

                log.info(
                    f"Processing batch {batch_num}/{total_batches} "
                    f"({len(batch)} documents)"
                )

                await self._process_batch(batch, stats, force_reindex)

            log.info(
                f"Indexing complete: {stats.indexed} indexed, {stats.failed} failed, "
                f"{stats.skipped} skipped in {stats.duration_seconds:.2f}s"
            )

            return stats

        except Exception as e:
            log.error(f"Indexing failed: {e}", exc_info=True)
            raise

    async def _process_batch(
        self,
        documents: List[PolicyDocumentModel],
        stats: IndexingStats,
        force_reindex: bool = False
    ):
        """
        Process a batch of documents.

        Args:
            documents: List of documents to process
            stats: Stats object to update
            force_reindex: Whether to reindex already-indexed documents
        """
        index_docs = []

        for doc in documents:
            try:
                # Skip already indexed documents unless force_reindex
                if doc.status == 'indexed' and not force_reindex:
                    log.debug(f"Skipping already indexed document: {doc.id}")
                    stats.record_skip()
                    continue

                # Update status to processing
                PolicyDocuments.update_document_by_id(
                    doc.id,
                    PolicyDocumentUpdate(status='processing')
                )

                # Process document
                log.debug(f"Processing document {doc.id}: {doc.title}")
                processed = await self._process_document(doc)

                if processed:
                    index_docs.append(processed)
                    stats.record_success()
                else:
                    stats.record_failure(doc.id, "Processing returned None")

            except Exception as e:
                error_msg = f"Processing failed: {str(e)}"
                log.error(f"Document {doc.id} failed: {error_msg}")
                stats.record_failure(doc.id, error_msg)

                # Update status to failed
                PolicyDocuments.update_document_by_id(
                    doc.id,
                    PolicyDocumentUpdate(
                        status='failed',
                        metadata={'error': error_msg}
                    )
                )

        # Bulk index to Meilisearch
        if index_docs:
            try:
                log.info(f"Indexing {len(index_docs)} documents to Meilisearch")
                await self.meilisearch.index_documents(index_docs)

                # Update all to indexed status
                for doc_data in index_docs:
                    PolicyDocuments.update_document_by_id(
                        doc_data['id'],
                        PolicyDocumentUpdate(
                            status='indexed',
                            indexed_at=int(datetime.now().timestamp())
                        )
                    )

                log.info(f"Successfully indexed {len(index_docs)} documents")

            except Exception as e:
                log.error(f"Bulk indexing failed: {e}")
                # Mark all as failed
                for doc_data in index_docs:
                    stats.record_failure(doc_data['id'], f"Indexing failed: {e}")
                    PolicyDocuments.update_document_by_id(
                        doc_data['id'],
                        PolicyDocumentUpdate(
                            status='failed',
                            metadata={'error': f"Indexing failed: {e}"}
                        )
                    )

    async def _process_document(
        self,
        doc: PolicyDocumentModel
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single document.

        Args:
            doc: Document model from database

        Returns:
            Dict ready for Meilisearch indexing, or None if processing fails
        """
        try:
            # Determine file path
            # In production, this would be retrieved from document storage
            # For now, we'll use metadata or construct path
            file_path = self._get_document_file_path(doc)

            if not file_path or not os.path.exists(file_path):
                raise ProcessingError(f"Document file not found: {file_path}")

            # Process document
            processed = await self.processor.process_document(
                file_path=file_path,
                document_type=doc.document_type or 'pdf'
            )

            # Prepare for indexing
            index_doc = {
                'id': doc.id,
                'title': doc.title,
                'content': processed['text'],
                'description': doc.description or processed['summary'],
                'municipality': doc.municipality or '',
                'publication_date': doc.publication_date.isoformat() if doc.publication_date else '',
                'document_type': doc.document_type or '',
                'source_id': doc.source_id,
                'status': 'indexed',
                'word_count': processed['word_count'],
                'page_count': processed.get('page_count', 0)
            }

            # Add category if present in metadata
            if doc.metadata and 'category' in doc.metadata:
                index_doc['category'] = doc.metadata['category']

            return index_doc

        except ProcessingError as e:
            log.error(f"Processing error for document {doc.id}: {e}")
            raise
        except Exception as e:
            log.error(f"Unexpected error processing document {doc.id}: {e}", exc_info=True)
            raise ProcessingError(f"Document processing failed: {e}")

    def _get_document_file_path(self, doc: PolicyDocumentModel) -> Optional[str]:
        """
        Get the file path for a document.

        This is a placeholder - in production, this would:
        1. Check document_content table for storage_path
        2. Download from MinIO/S3 if needed
        3. Cache locally

        Args:
            doc: Document model

        Returns:
            File path or None
        """
        # Check if path is in metadata
        if doc.metadata and 'file_path' in doc.metadata:
            return doc.metadata['file_path']

        # Otherwise construct from storage base path
        # This assumes files are stored as: {base_path}/{source_id}/{document_id}.{ext}
        if doc.document_type:
            filename = f"{doc.id}.{doc.document_type}"
            file_path = os.path.join(self.storage_base_path, doc.source_id, filename)
            if os.path.exists(file_path):
                return file_path

        log.warning(f"Could not determine file path for document {doc.id}")
        return None

    async def reindex_document(self, document_id: str) -> bool:
        """
        Reindex a single document.

        Args:
            document_id: Document ID

        Returns:
            bool: True if successful
        """
        try:
            doc = PolicyDocuments.get_document_by_id(document_id)
            if not doc:
                log.error(f"Document not found: {document_id}")
                return False

            await self.meilisearch.connect()

            # Process document
            processed = await self._process_document(doc)
            if not processed:
                return False

            # Index to Meilisearch
            await self.meilisearch.index_documents([processed])

            # Update status
            PolicyDocuments.update_document_by_id(
                document_id,
                PolicyDocumentUpdate(
                    status='indexed',
                    indexed_at=int(datetime.now().timestamp())
                )
            )

            log.info(f"Successfully reindexed document {document_id}")
            return True

        except Exception as e:
            log.error(f"Failed to reindex document {document_id}: {e}")
            return False

    async def delete_from_index(self, document_ids: List[str]) -> bool:
        """
        Remove documents from search index.

        Args:
            document_ids: List of document IDs

        Returns:
            bool: True if successful
        """
        try:
            await self.meilisearch.connect()
            await self.meilisearch.delete_documents(document_ids)

            # Update status in database
            for doc_id in document_ids:
                PolicyDocuments.update_document_by_id(
                    doc_id,
                    PolicyDocumentUpdate(status='pending')
                )

            log.info(f"Deleted {len(document_ids)} documents from index")
            return True

        except Exception as e:
            log.error(f"Failed to delete documents from index: {e}")
            return False

    async def get_indexing_status(self) -> Dict[str, Any]:
        """
        Get overall indexing status.

        Returns:
            Dict with counts by status
        """
        try:
            # Get counts from database
            # Note: This is a simplified version
            # In production, you'd want proper aggregation queries
            all_docs = PolicyDocuments.get_documents(limit=100000)

            status_counts = {
                'pending': 0,
                'processing': 0,
                'indexed': 0,
                'failed': 0,
                'archived': 0
            }

            for doc in all_docs:
                status = doc.status or 'pending'
                if status in status_counts:
                    status_counts[status] += 1

            # Get Meilisearch stats
            meili_stats = await self.meilisearch.get_stats()

            return {
                'database': status_counts,
                'meilisearch': meili_stats,
                'total_documents': len(all_docs)
            }

        except Exception as e:
            log.error(f"Failed to get indexing status: {e}")
            return {}


# Global service instance
_indexing_service: Optional[IndexingService] = None


def get_indexing_service() -> IndexingService:
    """
    Get or create the global IndexingService instance.

    Returns:
        IndexingService instance
    """
    global _indexing_service
    if _indexing_service is None:
        _indexing_service = IndexingService()
    return _indexing_service
