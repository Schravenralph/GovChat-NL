import logging
import time
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from open_webui.models.policy_documents import (
    PolicyDocuments,
    SearchQueries,
    PolicyDocumentModel,
    SearchQueryForm,
)
from open_webui.utils.auth import get_verified_user
from open_webui.constants import ERROR_MESSAGES
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])

router = APIRouter()

############################
# Search Models
############################


class SearchFilters(BaseModel):
    sources: Optional[List[str]] = Field(None, description="Filter by source IDs")
    municipalities: Optional[List[str]] = Field(None, description="Filter by municipality names")
    categories: Optional[List[str]] = Field(None, description="Filter by category IDs")
    date_from: Optional[str] = Field(None, description="Filter from publication date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="Filter to publication date (YYYY-MM-DD)")
    document_type: Optional[str] = Field(None, description="Filter by document type (pdf, html, etc)")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query text")
    filters: Optional[SearchFilters] = None
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Results per page")
    sort: str = Field("relevance", pattern="^(relevance|date_desc|date_asc|title)$")


class SearchFacet(BaseModel):
    value: str
    count: int


class SearchFacets(BaseModel):
    sources: List[SearchFacet] = []
    municipalities: List[SearchFacet] = []
    categories: List[SearchFacet] = []


class SearchResponse(BaseModel):
    results: List[PolicyDocumentModel]
    total: int
    facets: SearchFacets
    page: int
    took_ms: int


############################
# Search API (Stub for Phase 1)
############################


@router.post("/", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    user=Depends(get_verified_user),
):
    """
    Search policy documents with filters using Meilisearch.

    Features:
    - Full-text search with typo tolerance
    - Filtering by municipality, category, date range, document type
    - Faceted search results
    - Sorting options
    - Pagination
    - Analytics tracking
    """
    start_time = time.time()

    try:
        # Import here to avoid circular imports
        from open_webui.services.meilisearch_service import get_meilisearch_service

        # Get Meilisearch service
        meili = get_meilisearch_service()
        await meili.connect()

        # Build filters dict
        filters = {}
        if request.filters:
            if request.filters.municipalities:
                filters['municipality'] = request.filters.municipalities
            if request.filters.categories:
                filters['category'] = request.filters.categories
            if request.filters.document_type:
                filters['document_type'] = request.filters.document_type
            if request.filters.sources:
                filters['source_id'] = request.filters.sources[0]  # Single source for now
            if request.filters.date_from:
                filters['date_from'] = request.filters.date_from
            if request.filters.date_to:
                filters['date_to'] = request.filters.date_to

        # Build sort
        sort_list = None
        if request.sort == 'date_desc':
            sort_list = ['publication_date:desc']
        elif request.sort == 'date_asc':
            sort_list = ['publication_date:asc']
        elif request.sort == 'title':
            sort_list = ['title:asc']
        # 'relevance' = None (default Meilisearch ranking)

        # Execute search
        log.info(f"Searching: query='{request.query}', filters={filters}, page={request.page}")
        results = await meili.search(
            query=request.query,
            filters=filters,
            page=request.page,
            limit=request.limit,
            sort=sort_list
        )

        # Convert Meilisearch results to PolicyDocumentModel
        # Note: Meilisearch returns raw dicts, we need to convert them
        documents = []
        for hit in results['hits']:
            # Convert ISO date string back to date object if needed
            pub_date = None
            if hit.get('publication_date'):
                try:
                    from datetime import date
                    pub_date = date.fromisoformat(hit['publication_date'])
                except:
                    pass

            doc = PolicyDocumentModel(
                id=hit['id'],
                source_id=hit.get('source_id', ''),
                title=hit.get('title', ''),
                description=hit.get('description', ''),
                content_hash=hit.get('content_hash', ''),
                document_url=hit.get('document_url', ''),
                document_type=hit.get('document_type'),
                municipality=hit.get('municipality'),
                publication_date=pub_date,
                effective_date=None,
                file_size=hit.get('file_size'),
                page_count=hit.get('page_count'),
                language=hit.get('language', 'nl'),
                status=hit.get('status', 'indexed'),
                metadata=hit.get('metadata'),
                created_at=hit.get('created_at', 0),
                updated_at=hit.get('updated_at', 0),
                indexed_at=hit.get('indexed_at')
            )
            documents.append(doc)

        # Convert facets to SearchFacets format
        facet_dist = results.get('facetDistribution', {})
        facets = SearchFacets(
            municipalities=[
                SearchFacet(value=k, count=v)
                for k, v in facet_dist.get('municipality', {}).items()
            ],
            categories=[
                SearchFacet(value=k, count=v)
                for k, v in facet_dist.get('category', {}).items()
            ],
            sources=[
                SearchFacet(value=k, count=v)
                for k, v in facet_dist.get('source_id', {}).items()
            ]
        )

        # Calculate response time
        took_ms = results.get('processingTimeMs', 0)
        total_ms = int((time.time() - start_time) * 1000)

        # Record search query for analytics
        search_form = SearchQueryForm(
            query_text=request.query,
            filters=request.filters.model_dump() if request.filters else None,
            search_type="keyword",
        )
        SearchQueries.record_search(
            user_id=user.id,
            form_data=search_form,
            result_count=results.get('total', 0),
            response_time_ms=total_ms,
        )

        log.info(
            f"Search completed: {results.get('total', 0)} results in {took_ms}ms "
            f"(total {total_ms}ms)"
        )

        # Return response
        return SearchResponse(
            results=documents,
            total=results.get('total', 0),
            facets=facets,
            page=request.page,
            took_ms=took_ms,
        )

    except Exception as e:
        log.exception(f"Error searching documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.get("/filters", response_model=dict)
async def get_search_filters(
    user=Depends(get_verified_user),
):
    """
    Get available filter options for search.

    Returns facet counts from Meilisearch for:
    - Municipalities
    - Sources
    - Categories
    - Document types
    """
    try:
        from open_webui.services.meilisearch_service import get_meilisearch_service

        # Get Meilisearch service
        meili = get_meilisearch_service()
        await meili.connect()

        # Perform empty search to get all facets
        results = await meili.search(
            query='',
            filters={},
            page=1,
            limit=1,
            facets=['municipality', 'category', 'document_type', 'source_id']
        )

        facet_dist = results.get('facetDistribution', {})

        return {
            "municipalities": [
                {"value": k, "count": v}
                for k, v in facet_dist.get('municipality', {}).items()
            ],
            "sources": [
                {"value": k, "count": v}
                for k, v in facet_dist.get('source_id', {}).items()
            ],
            "categories": [
                {"value": k, "count": v}
                for k, v in facet_dist.get('category', {}).items()
            ],
            "document_types": [
                {"value": k, "count": v}
                for k, v in facet_dist.get('document_type', {}).items()
            ],
        }
    except Exception as e:
        log.exception(f"Error getting search filters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.post("/semantic")
async def semantic_search(
    request: SearchRequest,
    user=Depends(get_verified_user),
):
    """
    Semantic search using vector embeddings.
    NOTE: This is a STUB for Phase 3 (AI Features).

    Will be implemented with:
    - Qdrant vector database
    - Document embeddings
    - Hybrid search (keyword + semantic)
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Semantic search will be implemented in Phase 3 (AI Features)",
    )
