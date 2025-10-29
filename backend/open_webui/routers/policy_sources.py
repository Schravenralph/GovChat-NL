import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from open_webui.models.policy_sources import (
    PolicySources,
    ScanJobs,
    PolicySourceModel,
    PolicySourceForm,
    PolicySourceUpdate,
    ScanJobModel,
    ScanJobForm,
)
from open_webui.utils.auth import get_verified_user, get_current_user
from open_webui.middleware.policy_auth import require_policy_permission, require_policy_admin
from open_webui.constants import ERROR_MESSAGES
from open_webui.constants.policy_permissions import PolicyPermissions
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])

router = APIRouter()

############################
# Policy Sources Management
############################


@router.get("/", response_model=List[PolicySourceModel])
@require_policy_permission(PolicyPermissions.MANAGE_SOURCES)
async def get_policy_sources(
    active_only: bool = False,
    user=Depends(get_current_user),
):
    """
    Get all policy sources.
    Requires policy:manage_sources permission (admin only).
    """
    try:
        sources = PolicySources.get_sources(active_only=active_only)
        return sources
    except Exception as e:
        log.exception(f"Error getting policy sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.get("/{source_id}", response_model=PolicySourceModel)
@require_policy_permission(PolicyPermissions.MANAGE_SOURCES)
async def get_policy_source_by_id(
    source_id: str,
    user=Depends(get_current_user),
):
    """
    Get a specific policy source by ID.
    Requires policy:manage_sources permission (admin only).
    """
    try:
        source = PolicySources.get_source_by_id(source_id)
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND,
            )
        return source
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error getting policy source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.post("/", response_model=PolicySourceModel)
@require_policy_permission(PolicyPermissions.MANAGE_SOURCES)
async def create_policy_source(
    form_data: PolicySourceForm,
    user=Depends(get_current_user),
):
    """
    Create a new policy source.
    Requires policy:manage_sources permission (admin only).
    """
    try:
        source = PolicySources.insert_new_source(user.id, form_data)
        if not source:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Failed to create policy source"),
            )
        return source
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error creating policy source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.post("/{source_id}/update", response_model=PolicySourceModel)
@require_policy_permission(PolicyPermissions.MANAGE_SOURCES)
async def update_policy_source(
    source_id: str,
    form_data: PolicySourceUpdate,
    user=Depends(get_current_user),
):
    """
    Update a policy source.
    Requires policy:manage_sources permission (admin only).
    """
    try:
        # Check if source exists
        existing_source = PolicySources.get_source_by_id(source_id)
        if not existing_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND,
            )

        source = PolicySources.update_source_by_id(source_id, form_data)
        if not source:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Failed to update policy source"),
            )
        return source
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error updating policy source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.delete("/{source_id}/deactivate")
@require_policy_permission(PolicyPermissions.MANAGE_SOURCES)
async def deactivate_policy_source(
    source_id: str,
    user=Depends(get_current_user),
):
    """
    Deactivate a policy source (soft delete).
    Requires policy:manage_sources permission (admin only).
    """
    try:
        result = PolicySources.deactivate_source_by_id(source_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND,
            )
        return {"success": True, "message": "Policy source deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error deactivating policy source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.delete("/{source_id}/delete")
@require_policy_permission(PolicyPermissions.DELETE)
async def delete_policy_source(
    source_id: str,
    user=Depends(get_current_user),
):
    """
    Permanently delete a policy source.
    WARNING: This will cascade delete all related documents.
    Requires policy:delete permission (admin only).
    """
    try:
        result = PolicySources.delete_source_by_id(source_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND,
            )
        return {"success": True, "message": "Policy source deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error deleting policy source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


############################
# Scan Jobs Management
############################


@router.post("/{source_id}/scan", response_model=ScanJobModel)
@require_policy_permission(PolicyPermissions.TRIGGER_SCAN)
async def trigger_scan_job(
    source_id: str,
    form_data: ScanJobForm,
    user=Depends(get_current_user),
):
    """
    Trigger a manual scan job for a policy source.
    Requires policy:trigger_scan permission (admin only).
    Returns job ID for status tracking.
    """
    try:
        # Verify source exists
        source = PolicySources.get_source_by_id(source_id)
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Policy source not found",
            )

        if not source.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot scan inactive source",
            )

        # Override source_id from path
        form_data.source_id = source_id

        job = ScanJobs.create_scan_job(user.id, form_data)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Failed to create scan job"),
            )

        # TODO: Trigger actual scan job via background task/queue
        # For now, just return the created job
        return job
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error creating scan job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.get("/{source_id}/scan/jobs", response_model=List[ScanJobModel])
@require_policy_permission(PolicyPermissions.MANAGE_SOURCES)
async def get_scan_jobs_for_source(
    source_id: str,
    limit: int = 10,
    user=Depends(get_current_user),
):
    """
    Get recent scan jobs for a policy source.
    Requires policy:manage_sources permission (admin only).
    """
    try:
        # Verify source exists
        source = PolicySources.get_source_by_id(source_id)
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Policy source not found",
            )

        jobs = ScanJobs.get_scan_jobs_by_source(source_id, limit=limit)
        return jobs
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error getting scan jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )


@router.get("/scan/jobs/{job_id}", response_model=ScanJobModel)
@require_policy_permission(PolicyPermissions.MANAGE_SOURCES)
async def get_scan_job_status(
    job_id: str,
    user=Depends(get_current_user),
):
    """
    Get status of a specific scan job.
    Requires policy:manage_sources permission (admin only).
    """
    try:
        job = ScanJobs.get_scan_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan job not found",
            )
        return job
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error getting scan job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(e)),
        )
