import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from open_webui.models.policy_documents import (
    PolicyDocuments,
    SavedSearches,
    PolicyDocumentModel,
    PolicyDocumentForm,
    PolicyDocumentUpdate,
    SavedSearchModel,
    SavedSearchForm,
)
from open_webui.models.policy_categories import (
    PolicyCategories,
    Tags,
    PolicyCategoryModel,
    TagModel,
    DocumentCategoryForm,
)
from open_webui.utils.auth import get_verified_user, get_current_user
from open_webui.middleware.policy_auth import require_policy_permission
from open_webui.constants import ERROR_MESSAGES
from open_webui.constants.policy_permissions import PolicyPermissions
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])

router = APIRouter()

############################
# Document Retrieval
############################


@router.get("/{document_id}", response_model=PolicyDocumentModel)
@require_policy_permission(PolicyPermissions.VIEW)
async def get_document(
    document_id: str,
    user=Depends(get_current_user),
):
    """
    Get a specific policy document by ID.
    Requires policy:view permission (all authenticated users).
    """
    try:
        document = PolicyDocuments.get_document_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return document
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error getting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.get("/", response_model=List[PolicyDocumentModel])
@require_policy_permission(PolicyPermissions.VIEW)
async def get_documents(
    source_id: Optional[str] = None,
    municipality: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    user=Depends(get_current_user),
):
    """
    Get policy documents with optional filters.
    Requires policy:view permission (all authenticated users).
    """
    try:
        documents = PolicyDocuments.get_documents(
            source_id=source_id,
            municipality=municipality,
            status=status_filter,
            limit=min(limit, 100),  # Max 100 per page
            offset=offset,
        )
        return documents
    except Exception as e:
        log.exception(f"Error getting documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.post("/", response_model=PolicyDocumentModel)
@require_policy_permission(PolicyPermissions.ADMIN)
async def create_document(
    form_data: PolicyDocumentForm,
    user=Depends(get_current_user),
):
    """
    Create a new policy document.
    Requires policy:admin permission (admin only).
    """
    try:
        # Check for duplicates by content hash
        existing = PolicyDocuments.get_document_by_hash(form_data.content_hash)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document with this content hash already exists",
            )

        document = PolicyDocuments.insert_new_document(form_data)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create document",
            )
        return document
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error creating document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.post("/{document_id}/update", response_model=PolicyDocumentModel)
@require_policy_permission(PolicyPermissions.ADMIN)
async def update_document(
    document_id: str,
    form_data: PolicyDocumentUpdate,
    user=Depends(get_current_user),
):
    """
    Update a policy document.
    Requires policy:admin permission (admin only).
    """
    try:
        document = PolicyDocuments.update_document_by_id(document_id, form_data)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return document
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error updating document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


############################
# Document Categories
############################


@router.get("/{document_id}/categories", response_model=List[PolicyCategoryModel])
@require_policy_permission(PolicyPermissions.VIEW)
async def get_document_categories(
    document_id: str,
    user=Depends(get_current_user),
):
    """
    Get all categories assigned to a document.
    Requires policy:view permission (all authenticated users).
    """
    try:
        # Verify document exists
        document = PolicyDocuments.get_document_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Get category assignments
        doc_categories = PolicyCategories.get_document_categories(document_id)

        # Fetch full category details
        categories = []
        for dc in doc_categories:
            category = PolicyCategories.get_category_by_id(dc.category_id)
            if category:
                categories.append(category)

        return categories
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error getting document categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.post("/{document_id}/categories")
@require_policy_permission(PolicyPermissions.CATEGORIZE)
async def assign_category_to_document(
    document_id: str,
    form_data: DocumentCategoryForm,
    user=Depends(get_current_user),
):
    """
    Assign a category to a document.
    Requires policy:categorize permission (admin only).
    """
    try:
        # Verify document exists
        document = PolicyDocuments.get_document_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Verify category exists
        category = PolicyCategories.get_category_by_id(form_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        result = PolicyCategories.assign_category_to_document(document_id, form_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign category",
            )

        return {"success": True, "message": "Category assigned successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error assigning category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.delete("/{document_id}/categories/{category_id}")
@require_policy_permission(PolicyPermissions.CATEGORIZE)
async def remove_category_from_document(
    document_id: str,
    category_id: str,
    user=Depends(get_current_user),
):
    """
    Remove a category from a document.
    Requires policy:categorize permission (admin only).
    """
    try:
        result = PolicyCategories.remove_category_from_document(document_id, category_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category assignment not found",
            )
        return {"success": True, "message": "Category removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error removing category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


############################
# User Favorites
############################


@router.get("/favorites/list", response_model=List[PolicyDocumentModel])
@require_policy_permission(PolicyPermissions.FAVORITE)
async def get_user_favorites(
    user=Depends(get_current_user),
):
    """
    Get all favorite documents for the current user.
    Requires policy:favorite permission (all authenticated users).
    """
    try:
        favorites = PolicyDocuments.get_user_favorites(user.id)
        return favorites
    except Exception as e:
        log.exception(f"Error getting favorites: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.post("/{document_id}/favorite")
@require_policy_permission(PolicyPermissions.FAVORITE)
async def add_to_favorites(
    document_id: str,
    notes: Optional[str] = None,
    user=Depends(get_current_user),
):
    """
    Add a document to user's favorites.
    Requires policy:favorite permission (all authenticated users).
    """
    try:
        # Verify document exists
        document = PolicyDocuments.get_document_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        result = PolicyDocuments.add_favorite(user.id, document_id, notes)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add favorite",
            )

        return {"success": True, "message": "Added to favorites"}
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error adding favorite: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.delete("/{document_id}/favorite")
@require_policy_permission(PolicyPermissions.FAVORITE)
async def remove_from_favorites(
    document_id: str,
    user=Depends(get_current_user),
):
    """
    Remove a document from user's favorites.
    Requires policy:favorite permission (all authenticated users).
    """
    try:
        result = PolicyDocuments.remove_favorite(user.id, document_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite not found",
            )

        return {"success": True, "message": "Removed from favorites"}
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error removing favorite: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


############################
# Saved Searches
############################


@router.get("/saved-searches/list", response_model=List[SavedSearchModel])
@require_policy_permission(PolicyPermissions.SAVE_SEARCH)
async def get_saved_searches(
    user=Depends(get_current_user),
):
    """
    Get all saved searches for the current user.
    Requires policy:save_search permission (all authenticated users).
    """
    try:
        searches = SavedSearches.get_user_saved_searches(user.id)
        return searches
    except Exception as e:
        log.exception(f"Error getting saved searches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.post("/saved-searches", response_model=SavedSearchModel)
@require_policy_permission(PolicyPermissions.SAVE_SEARCH)
async def create_saved_search(
    form_data: SavedSearchForm,
    user=Depends(get_current_user),
):
    """
    Create a new saved search for the current user.
    Requires policy:save_search permission (all authenticated users).
    """
    try:
        search = SavedSearches.create_saved_search(user.id, form_data)
        if not search:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create saved search",
            )
        return search
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error creating saved search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.delete("/saved-searches/{search_id}")
@require_policy_permission(PolicyPermissions.SAVE_SEARCH)
async def delete_saved_search(
    search_id: str,
    user=Depends(get_current_user),
):
    """
    Delete a saved search.
    Requires policy:save_search permission (all authenticated users).
    """
    try:
        result = SavedSearches.delete_saved_search(search_id, user.id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found",
            )

        return {"success": True, "message": "Saved search deleted"}
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error deleting saved search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )
