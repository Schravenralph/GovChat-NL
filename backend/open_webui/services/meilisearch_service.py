"""
Meilisearch Service for Policy Scanner.

This module provides integration with Meilisearch for fast full-text search
of policy documents. It handles index management, document indexing, and
search operations with filters and facets.
"""

import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from meilisearch_python_async import Client
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("MAIN", "INFO"))


class MeilisearchService:
    """
    Service for managing Meilisearch operations.

    Provides:
    - Connection management
    - Index creation and configuration
    - Document indexing (single and batch)
    - Search with filters and facets
    - Health checks
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None
    ):
        """
        Initialize Meilisearch service.

        Args:
            url: Meilisearch URL (defaults to env MEILISEARCH_URL)
            api_key: Meilisearch API key (defaults to env MEILISEARCH_API_KEY)
            index_name: Index name (defaults to env MEILISEARCH_INDEX_NAME)
        """
        self.url = url or os.getenv('MEILISEARCH_URL', 'http://localhost:7700')
        self.api_key = api_key or os.getenv('MEILISEARCH_API_KEY', '')
        self.index_name = index_name or os.getenv('MEILISEARCH_INDEX_NAME', 'policy_documents')
        self.client: Optional[Client] = None
        self._connected = False

        log.info(f"MeilisearchService initialized: url={self.url}, index={self.index_name}")

    async def connect(self):
        """
        Initialize Meilisearch client.

        Returns:
            self: For method chaining
        """
        try:
            self.client = Client(self.url, self.api_key)
            # Test connection
            await self.client.health()
            self._connected = True
            log.info("Connected to Meilisearch successfully")
            return self
        except Exception as e:
            log.error(f"Failed to connect to Meilisearch: {e}")
            self._connected = False
            raise ConnectionError(f"Cannot connect to Meilisearch at {self.url}: {e}")

    async def disconnect(self):
        """Close Meilisearch client."""
        if self.client:
            await self.client.aclose()
            self.client = None
            self._connected = False
            log.info("Disconnected from Meilisearch")

    async def health_check(self) -> bool:
        """
        Check Meilisearch health.

        Returns:
            bool: True if healthy
        """
        try:
            if not self.client:
                await self.connect()
            await self.client.health()
            return True
        except Exception as e:
            log.error(f"Meilisearch health check failed: {e}")
            return False

    async def create_index(self, primary_key: str = "id") -> bool:
        """
        Create and configure the policy documents index.

        Args:
            primary_key: Primary key field name

        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                await self.connect()

            # Create index
            log.info(f"Creating index: {self.index_name}")
            task = await self.client.create_index(self.index_name, primary_key=primary_key)

            # Wait for task to complete
            await self.client.wait_for_task(task.task_uid)

            # Get index
            index = self.client.index(self.index_name)

            # Configure searchable attributes
            log.info("Configuring searchable attributes")
            await index.update_searchable_attributes([
                'title',
                'content',
                'description',
                'municipality'
            ])

            # Configure filterable attributes
            log.info("Configuring filterable attributes")
            await index.update_filterable_attributes([
                'municipality',
                'category',
                'document_type',
                'publication_date',
                'source_id',
                'status'
            ])

            # Configure sortable attributes
            log.info("Configuring sortable attributes")
            await index.update_sortable_attributes([
                'publication_date',
                'title'
            ])

            # Configure ranking rules
            log.info("Configuring ranking rules")
            await index.update_ranking_rules([
                'words',
                'typo',
                'proximity',
                'attribute',
                'sort',
                'exactness'
            ])

            # Configure stop words (Dutch)
            log.info("Configuring stop words")
            dutch_stop_words = [
                'de', 'het', 'een', 'en', 'van', 'op', 'in', 'te', 'voor', 'dat',
                'is', 'was', 'zijn', 'als', 'met', 'aan', 'door', 'om', 'naar'
            ]
            await index.update_stop_words(dutch_stop_words)

            log.info(f"Index '{self.index_name}' created and configured successfully")
            return True

        except Exception as e:
            log.error(f"Failed to create index: {e}")
            raise

    async def delete_index(self) -> bool:
        """
        Delete the index.

        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                await self.connect()

            task = await self.client.delete_index(self.index_name)
            await self.client.wait_for_task(task.task_uid)
            log.info(f"Index '{self.index_name}' deleted")
            return True
        except Exception as e:
            log.error(f"Failed to delete index: {e}")
            return False

    async def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Index multiple documents.

        Args:
            documents: List of document dicts with fields:
                - id (required)
                - title
                - content
                - municipality
                - publication_date
                - document_type
                - source_id
                - category (optional)

        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                await self.connect()

            if not documents:
                log.warning("No documents to index")
                return True

            index = self.client.index(self.index_name)

            log.info(f"Indexing {len(documents)} documents")
            task = await index.add_documents(documents)

            # Wait for indexing to complete
            result = await self.client.wait_for_task(task.task_uid)

            if result.status == "succeeded":
                log.info(f"Successfully indexed {len(documents)} documents")
                return True
            else:
                log.error(f"Indexing failed with status: {result.status}")
                return False

        except Exception as e:
            log.error(f"Failed to index documents: {e}")
            raise

    async def update_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Update existing documents.

        Args:
            documents: List of document dicts with id field

        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                await self.connect()

            index = self.client.index(self.index_name)
            task = await index.update_documents(documents)
            result = await self.client.wait_for_task(task.task_uid)

            if result.status == "succeeded":
                log.info(f"Successfully updated {len(documents)} documents")
                return True
            else:
                log.error(f"Update failed with status: {result.status}")
                return False

        except Exception as e:
            log.error(f"Failed to update documents: {e}")
            raise

    async def delete_documents(self, document_ids: List[str]) -> bool:
        """
        Delete documents by IDs.

        Args:
            document_ids: List of document IDs

        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                await self.connect()

            index = self.client.index(self.index_name)
            task = await index.delete_documents(document_ids)
            result = await self.client.wait_for_task(task.task_uid)

            if result.status == "succeeded":
                log.info(f"Successfully deleted {len(document_ids)} documents")
                return True
            else:
                log.error(f"Deletion failed with status: {result.status}")
                return False

        except Exception as e:
            log.error(f"Failed to delete documents: {e}")
            raise

    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20,
        sort: Optional[List[str]] = None,
        facets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search documents with filters and facets.

        Args:
            query: Search query text
            filters: Filter dictionary with keys:
                - municipality: str or List[str]
                - category: str or List[str]
                - document_type: str
                - date_from: str (ISO date)
                - date_to: str (ISO date)
                - source_id: str
            page: Page number (1-indexed)
            limit: Results per page
            sort: Sort fields (e.g., ['publication_date:desc'])
            facets: Facet fields to return counts for

        Returns:
            Dict with keys:
                - hits: List of matching documents
                - total: Total number of matches
                - facetDistribution: Facet counts
                - processingTimeMs: Processing time
                - query: Original query
                - page: Current page
                - limit: Results per page
        """
        try:
            if not self.client:
                await self.connect()

            index = self.client.index(self.index_name)

            # Build filter string
            filter_parts = []
            if filters:
                if filters.get('municipality'):
                    munis = filters['municipality'] if isinstance(filters['municipality'], list) else [filters['municipality']]
                    muni_filters = [f"municipality = '{m}'" for m in munis]
                    if muni_filters:
                        filter_parts.append(f"({' OR '.join(muni_filters)})")

                if filters.get('category'):
                    cats = filters['category'] if isinstance(filters['category'], list) else [filters['category']]
                    cat_filters = [f"category = '{c}'" for c in cats]
                    if cat_filters:
                        filter_parts.append(f"({' OR '.join(cat_filters)})")

                if filters.get('document_type'):
                    filter_parts.append(f"document_type = '{filters['document_type']}'")

                if filters.get('source_id'):
                    filter_parts.append(f"source_id = '{filters['source_id']}'")

                if filters.get('date_from') or filters.get('date_to'):
                    date_filters = []
                    if filters.get('date_from'):
                        # Convert YYYY-MM-DD to timestamp
                        date_filters.append(f"publication_date >= {filters['date_from']}")
                    if filters.get('date_to'):
                        date_filters.append(f"publication_date <= {filters['date_to']}")
                    if date_filters:
                        filter_parts.append(f"({' AND '.join(date_filters)})")

            filter_str = ' AND '.join(filter_parts) if filter_parts else None

            # Default facets
            if facets is None:
                facets = ['municipality', 'category', 'document_type']

            # Calculate offset
            offset = (page - 1) * limit

            # Execute search
            log.debug(f"Searching: query='{query}', filter={filter_str}, limit={limit}, offset={offset}")

            results = await index.search(
                query,
                filter=filter_str,
                limit=limit,
                offset=offset,
                sort=sort,
                facets=facets
            )

            # Format response
            response = {
                'hits': results.hits,
                'total': results.estimated_total_hits,
                'facetDistribution': results.facet_distribution or {},
                'processingTimeMs': results.processing_time_ms,
                'query': query,
                'page': page,
                'limit': limit
            }

            log.info(f"Search completed: {results.estimated_total_hits} total hits in {results.processing_time_ms}ms")

            return response

        except Exception as e:
            log.error(f"Search failed: {e}")
            raise

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.

        Returns:
            Dict with stats like document count, index size, etc.
        """
        try:
            if not self.client:
                await self.connect()

            index = self.client.index(self.index_name)
            stats = await index.get_stats()

            return {
                'numberOfDocuments': stats.number_of_documents,
                'isIndexing': stats.is_indexing,
                'fieldDistribution': stats.field_distribution
            }
        except Exception as e:
            log.error(f"Failed to get stats: {e}")
            return {}

    async def clear_index(self) -> bool:
        """
        Delete all documents from the index.

        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                await self.connect()

            index = self.client.index(self.index_name)
            task = await index.delete_all_documents()
            result = await self.client.wait_for_task(task.task_uid)

            if result.status == "succeeded":
                log.info("Index cleared successfully")
                return True
            else:
                log.error(f"Clear failed with status: {result.status}")
                return False

        except Exception as e:
            log.error(f"Failed to clear index: {e}")
            raise

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Global service instance
_meilisearch_service: Optional[MeilisearchService] = None


def get_meilisearch_service() -> MeilisearchService:
    """
    Get or create the global Meilisearch service instance.

    Returns:
        MeilisearchService instance
    """
    global _meilisearch_service
    if _meilisearch_service is None:
        _meilisearch_service = MeilisearchService()
    return _meilisearch_service
