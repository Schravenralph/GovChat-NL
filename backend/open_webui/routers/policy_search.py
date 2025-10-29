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
    Search policy documents with filters.
    NOTE: This is a STUB implementation for Phase 1.
    Actual search integration with Meilisearch will be added in Phase 2.

    For now, this endpoint:
    - Accepts search requests
    - Records search queries for analytics
    - Returns basic filtered results from PostgreSQL
    - Returns empty facets
    """
    start_time = time.time()

    try:
        # Convert filters to database query parameters
        source_id = request.filters.sources[0] if request.filters and request.filters.sources else None
        municipality = request.filters.municipalities[0] if request.filters and request.filters.municipalities else None

        # Fetch documents from database (basic filtering only)
        offset = (request.page - 1) * request.limit
        documents = PolicyDocuments.get_documents(
            source_id=source_id,
            municipality=municipality,
            status="indexed",  # Only return indexed documents
            limit=request.limit,
            offset=offset,
        )

        # Calculate response time
        took_ms = int((time.time() - start_time) * 1000)

        # Record search query for analytics
        search_form = SearchQueryForm(
            query_text=request.query,
            filters=request.filters.model_dump() if request.filters else None,
            search_type="keyword",  # For now, only keyword search
        )
        SearchQueries.record_search(
            user_id=user.id,
            form_data=search_form,
            result_count=len(documents),
            response_time_ms=took_ms,
        )

        # Return response with empty facets (to be implemented in Phase 2)
        return SearchResponse(
            results=documents,
            total=len(documents),  # TODO: Implement proper count query
            facets=SearchFacets(
                sources=[],
                municipalities=[],
                categories=[],
            ),
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
    NOTE: This is a STUB implementation for Phase 1.

    Returns:
    - List of available municipalities
    - List of available sources
    - List of available categories
    """
    try:
        # TODO: Implement actual aggregation queries
        # For now, return empty lists
        return {
            "municipalities": [],
            "sources": [],
            "categories": [],
            "document_types": ["pdf", "html", "docx", "xlsx"],
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
