import logging
import time
import uuid
from typing import Optional, List

from open_webui.internal.db import Base, JSONField, get_db
from open_webui.env import SRC_LOG_LEVELS
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Policy Scanner DB Schema - Sources
####################


class PolicySource(Base):
    __tablename__ = "sources"
    __table_args__ = {"schema": "policy_scanner"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    source_type = Column(String(50), nullable=False, server_default="custom")
    base_url = Column(Text, nullable=False)
    selector_config = Column(JSON, nullable=False)
    auth_config = Column(JSON, nullable=True)
    rate_limit = Column(Integer, nullable=False, server_default="10")
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(String(36), ForeignKey("user.id", ondelete="SET NULL"), nullable=True)


class ScanJob(Base):
    __tablename__ = "scan_jobs"
    __table_args__ = {"schema": "policy_scanner"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("policy_scanner.sources.id", ondelete="SET NULL"), nullable=True)
    job_type = Column(String(20), nullable=False, server_default="incremental")
    status = Column(String(20), nullable=False, server_default="pending")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    documents_found = Column(Integer, nullable=False, server_default="0")
    documents_new = Column(Integer, nullable=False, server_default="0")
    documents_updated = Column(Integer, nullable=False, server_default="0")
    documents_failed = Column(Integer, nullable=False, server_default="0")
    error_details = Column(JSON, nullable=True)
    triggered_by = Column(String(36), ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    job_config = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class SourceConfiguration(Base):
    __tablename__ = "source_configurations"
    __table_args__ = {"schema": "policy_scanner"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("policy_scanner.sources.id", ondelete="CASCADE"), nullable=False)
    config_key = Column(String(100), nullable=False)
    config_value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


####################
# Pydantic Models
####################


class PolicySourceModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    source_type: str
    base_url: str
    selector_config: dict
    auth_config: Optional[dict] = None
    rate_limit: int = 10
    is_active: bool = True
    created_at: int  # timestamp in epoch
    created_by: Optional[str] = None


class PolicySourceForm(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(..., pattern="^(gemeenteblad|dso|custom)$")
    base_url: str = Field(..., min_length=1)
    selector_config: dict = Field(..., description="CSS selectors and pagination rules")
    auth_config: Optional[dict] = Field(None, description="API keys or auth headers")
    rate_limit: int = Field(10, ge=1, le=100, description="Requests per second")
    is_active: bool = True


class PolicySourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    source_type: Optional[str] = Field(None, pattern="^(gemeenteblad|dso|custom)$")
    base_url: Optional[str] = Field(None, min_length=1)
    selector_config: Optional[dict] = None
    auth_config: Optional[dict] = None
    rate_limit: Optional[int] = Field(None, ge=1, le=100)
    is_active: Optional[bool] = None


class ScanJobModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: Optional[str] = None
    job_type: str
    status: str
    started_at: Optional[int] = None  # timestamp in epoch
    completed_at: Optional[int] = None  # timestamp in epoch
    documents_found: int = 0
    documents_new: int = 0
    documents_updated: int = 0
    documents_failed: int = 0
    error_details: Optional[dict] = None
    triggered_by: Optional[str] = None
    job_config: Optional[dict] = None
    created_at: int  # timestamp in epoch


class ScanJobForm(BaseModel):
    source_id: Optional[str] = None
    job_type: str = Field("incremental", pattern="^(full|incremental|manual)$")
    job_config: Optional[dict] = Field(None, description="Job-specific configuration")


class SourceConfigurationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: str
    config_key: str
    config_value: dict
    description: Optional[str] = None
    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


####################
# Table Classes
####################


class PolicySourcesTable:
    def insert_new_source(self, user_id: str, form_data: PolicySourceForm) -> Optional[PolicySourceModel]:
        """Create a new policy source"""
        with get_db() as db:
            try:
                source_id = str(uuid.uuid4())
                source = PolicySource(
                    id=source_id,
                    name=form_data.name,
                    source_type=form_data.source_type,
                    base_url=form_data.base_url,
                    selector_config=form_data.selector_config,
                    auth_config=form_data.auth_config,
                    rate_limit=form_data.rate_limit,
                    is_active=form_data.is_active,
                    created_by=user_id,
                )
                db.add(source)
                db.commit()
                db.refresh(source)

                return PolicySourceModel(
                    id=source.id,
                    name=source.name,
                    source_type=source.source_type,
                    base_url=source.base_url,
                    selector_config=source.selector_config,
                    auth_config=source.auth_config,
                    rate_limit=source.rate_limit,
                    is_active=source.is_active,
                    created_at=int(source.created_at.timestamp()),
                    created_by=source.created_by,
                )
            except Exception as e:
                log.exception(f"Error creating policy source: {e}")
                return None

    def get_source_by_id(self, source_id: str) -> Optional[PolicySourceModel]:
        """Get a policy source by ID"""
        with get_db() as db:
            try:
                source = db.query(PolicySource).filter_by(id=source_id).first()
                if not source:
                    return None

                return PolicySourceModel(
                    id=source.id,
                    name=source.name,
                    source_type=source.source_type,
                    base_url=source.base_url,
                    selector_config=source.selector_config,
                    auth_config=source.auth_config,
                    rate_limit=source.rate_limit,
                    is_active=source.is_active,
                    created_at=int(source.created_at.timestamp()),
                    created_by=source.created_by,
                )
            except Exception as e:
                log.exception(f"Error getting policy source: {e}")
                return None

    def get_sources(self, active_only: bool = False) -> List[PolicySourceModel]:
        """Get all policy sources, optionally filtered by active status"""
        with get_db() as db:
            try:
                query = db.query(PolicySource)
                if active_only:
                    query = query.filter_by(is_active=True)

                sources = query.order_by(PolicySource.created_at.desc()).all()
                return [
                    PolicySourceModel(
                        id=source.id,
                        name=source.name,
                        source_type=source.source_type,
                        base_url=source.base_url,
                        selector_config=source.selector_config,
                        auth_config=source.auth_config,
                        rate_limit=source.rate_limit,
                        is_active=source.is_active,
                        created_at=int(source.created_at.timestamp()),
                        created_by=source.created_by,
                    )
                    for source in sources
                ]
            except Exception as e:
                log.exception(f"Error getting policy sources: {e}")
                return []

    def get_sources_by_type(self, source_type: str) -> List[PolicySourceModel]:
        """Get all policy sources of a specific type"""
        with get_db() as db:
            try:
                sources = db.query(PolicySource).filter_by(source_type=source_type).all()
                return [
                    PolicySourceModel(
                        id=source.id,
                        name=source.name,
                        source_type=source.source_type,
                        base_url=source.base_url,
                        selector_config=source.selector_config,
                        auth_config=source.auth_config,
                        rate_limit=source.rate_limit,
                        is_active=source.is_active,
                        created_at=int(source.created_at.timestamp()),
                        created_by=source.created_by,
                    )
                    for source in sources
                ]
            except Exception as e:
                log.exception(f"Error getting sources by type: {e}")
                return []

    def update_source_by_id(self, source_id: str, form_data: PolicySourceUpdate) -> Optional[PolicySourceModel]:
        """Update a policy source"""
        with get_db() as db:
            try:
                source = db.query(PolicySource).filter_by(id=source_id).first()
                if not source:
                    return None

                update_data = form_data.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(source, key, value)

                db.commit()
                db.refresh(source)

                return PolicySourceModel(
                    id=source.id,
                    name=source.name,
                    source_type=source.source_type,
                    base_url=source.base_url,
                    selector_config=source.selector_config,
                    auth_config=source.auth_config,
                    rate_limit=source.rate_limit,
                    is_active=source.is_active,
                    created_at=int(source.created_at.timestamp()),
                    created_by=source.created_by,
                )
            except Exception as e:
                log.exception(f"Error updating policy source: {e}")
                return None

    def deactivate_source_by_id(self, source_id: str) -> bool:
        """Soft delete a policy source by setting is_active to False"""
        with get_db() as db:
            try:
                source = db.query(PolicySource).filter_by(id=source_id).first()
                if not source:
                    return False

                source.is_active = False
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error deactivating policy source: {e}")
                return False

    def delete_source_by_id(self, source_id: str) -> bool:
        """Hard delete a policy source (use with caution)"""
        with get_db() as db:
            try:
                db.query(PolicySource).filter_by(id=source_id).delete()
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error deleting policy source: {e}")
                return False


class ScanJobsTable:
    def create_scan_job(self, user_id: str, form_data: ScanJobForm) -> Optional[ScanJobModel]:
        """Create a new scan job"""
        with get_db() as db:
            try:
                job_id = str(uuid.uuid4())
                job = ScanJob(
                    id=job_id,
                    source_id=form_data.source_id,
                    job_type=form_data.job_type,
                    status="pending",
                    job_config=form_data.job_config,
                    triggered_by=user_id,
                )
                db.add(job)
                db.commit()
                db.refresh(job)

                return ScanJobModel(
                    id=job.id,
                    source_id=job.source_id,
                    job_type=job.job_type,
                    status=job.status,
                    started_at=int(job.started_at.timestamp()) if job.started_at else None,
                    completed_at=int(job.completed_at.timestamp()) if job.completed_at else None,
                    documents_found=job.documents_found,
                    documents_new=job.documents_new,
                    documents_updated=job.documents_updated,
                    documents_failed=job.documents_failed,
                    error_details=job.error_details,
                    triggered_by=job.triggered_by,
                    job_config=job.job_config,
                    created_at=int(job.created_at.timestamp()),
                )
            except Exception as e:
                log.exception(f"Error creating scan job: {e}")
                return None

    def get_scan_job_by_id(self, job_id: str) -> Optional[ScanJobModel]:
        """Get a scan job by ID"""
        with get_db() as db:
            try:
                job = db.query(ScanJob).filter_by(id=job_id).first()
                if not job:
                    return None

                return ScanJobModel(
                    id=job.id,
                    source_id=job.source_id,
                    job_type=job.job_type,
                    status=job.status,
                    started_at=int(job.started_at.timestamp()) if job.started_at else None,
                    completed_at=int(job.completed_at.timestamp()) if job.completed_at else None,
                    documents_found=job.documents_found,
                    documents_new=job.documents_new,
                    documents_updated=job.documents_updated,
                    documents_failed=job.documents_failed,
                    error_details=job.error_details,
                    triggered_by=job.triggered_by,
                    job_config=job.job_config,
                    created_at=int(job.created_at.timestamp()),
                )
            except Exception as e:
                log.exception(f"Error getting scan job: {e}")
                return None

    def get_scan_jobs_by_source(self, source_id: str, limit: int = 10) -> List[ScanJobModel]:
        """Get recent scan jobs for a specific source"""
        with get_db() as db:
            try:
                jobs = (
                    db.query(ScanJob)
                    .filter_by(source_id=source_id)
                    .order_by(ScanJob.created_at.desc())
                    .limit(limit)
                    .all()
                )
                return [
                    ScanJobModel(
                        id=job.id,
                        source_id=job.source_id,
                        job_type=job.job_type,
                        status=job.status,
                        started_at=int(job.started_at.timestamp()) if job.started_at else None,
                        completed_at=int(job.completed_at.timestamp()) if job.completed_at else None,
                        documents_found=job.documents_found,
                        documents_new=job.documents_new,
                        documents_updated=job.documents_updated,
                        documents_failed=job.documents_failed,
                        error_details=job.error_details,
                        triggered_by=job.triggered_by,
                        job_config=job.job_config,
                        created_at=int(job.created_at.timestamp()),
                    )
                    for job in jobs
                ]
            except Exception as e:
                log.exception(f"Error getting scan jobs by source: {e}")
                return []

    def update_scan_job_status(
        self,
        job_id: str,
        status: str,
        started_at: Optional[int] = None,
        completed_at: Optional[int] = None,
        error_details: Optional[dict] = None,
    ) -> Optional[ScanJobModel]:
        """Update scan job status and timestamps"""
        with get_db() as db:
            try:
                from datetime import datetime

                job = db.query(ScanJob).filter_by(id=job_id).first()
                if not job:
                    return None

                job.status = status
                if started_at:
                    job.started_at = datetime.fromtimestamp(started_at)
                if completed_at:
                    job.completed_at = datetime.fromtimestamp(completed_at)
                if error_details:
                    job.error_details = error_details

                db.commit()
                db.refresh(job)

                return ScanJobModel(
                    id=job.id,
                    source_id=job.source_id,
                    job_type=job.job_type,
                    status=job.status,
                    started_at=int(job.started_at.timestamp()) if job.started_at else None,
                    completed_at=int(job.completed_at.timestamp()) if job.completed_at else None,
                    documents_found=job.documents_found,
                    documents_new=job.documents_new,
                    documents_updated=job.documents_updated,
                    documents_failed=job.documents_failed,
                    error_details=job.error_details,
                    triggered_by=job.triggered_by,
                    job_config=job.job_config,
                    created_at=int(job.created_at.timestamp()),
                )
            except Exception as e:
                log.exception(f"Error updating scan job status: {e}")
                return None


# Table instances
PolicySources = PolicySourcesTable()
ScanJobs = ScanJobsTable()
