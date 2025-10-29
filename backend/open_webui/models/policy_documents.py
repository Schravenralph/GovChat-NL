import logging
import time
import uuid
from typing import Optional, List
from datetime import date, datetime

from open_webui.internal.db import Base, JSONField, get_db
from open_webui.env import SRC_LOG_LEVELS
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, String, Text, BigInteger, Integer, Date, DateTime, ForeignKey, JSON, Numeric, Boolean
from sqlalchemy.sql import func

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Policy Scanner DB Schema - Documents
####################


class PolicyDocument(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "policy_scanner"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("policy_scanner.sources.id", ondelete="CASCADE"), nullable=False)
    external_id = Column(String(500), nullable=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=False, unique=True)
    document_url = Column(Text, nullable=False)
    document_type = Column(String(20), nullable=True)
    municipality = Column(String(255), nullable=True)
    publication_date = Column(Date, nullable=True)
    effective_date = Column(Date, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    page_count = Column(Integer, nullable=True)
    language = Column(String(10), nullable=False, server_default="nl")
    status = Column(String(20), nullable=False, server_default="pending")
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    indexed_at = Column(DateTime, nullable=True)


class DocumentContent(Base):
    __tablename__ = "document_content"
    __table_args__ = {"schema": "policy_scanner"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("policy_scanner.documents.id", ondelete="CASCADE"), nullable=False)
    content_type = Column(String(20), nullable=False)
    content_text = Column(Text, nullable=True)
    storage_path = Column(Text, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    mime_type = Column(String(100), nullable=True)
    checksum = Column(String(64), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = {"schema": "policy_scanner"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("policy_scanner.documents.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False)
    changes_summary = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class UserFavorite(Base):
    __tablename__ = "user_favorites"
    __table_args__ = {"schema": "policy_scanner"}

    user_id = Column(String(36), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    document_id = Column(String(36), ForeignKey("policy_scanner.documents.id", ondelete="CASCADE"), primary_key=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class SearchQuery(Base):
    __tablename__ = "search_queries"
    __table_args__ = {"schema": "policy_scanner"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    query_text = Column(Text, nullable=True)
    filters = Column(JSON, nullable=True)
    result_count = Column(Integer, nullable=False, server_default="0")
    clicked_results = Column(JSON, nullable=True)  # Array of document IDs
    search_type = Column(String(20), nullable=False, server_default="keyword")
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class SavedSearch(Base):
    __tablename__ = "saved_searches"
    __table_args__ = {"schema": "policy_scanner"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    query_text = Column(Text, nullable=True)
    filters = Column(JSON, nullable=True)
    notification_enabled = Column(Boolean, nullable=False, server_default="false")
    notification_frequency = Column(String(20), nullable=True)
    last_notified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


####################
# Pydantic Models
####################


class PolicyDocumentModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: str
    external_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    content_hash: str
    document_url: str
    document_type: Optional[str] = None
    municipality: Optional[str] = None
    publication_date: Optional[date] = None
    effective_date: Optional[date] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    language: str = "nl"
    status: str = "pending"
    metadata: Optional[dict] = None
    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch
    indexed_at: Optional[int] = None  # timestamp in epoch


class PolicyDocumentForm(BaseModel):
    source_id: str = Field(..., min_length=36, max_length=36)
    external_id: Optional[str] = Field(None, max_length=500)
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    content_hash: str = Field(..., min_length=64, max_length=64)
    document_url: str = Field(..., min_length=1)
    document_type: Optional[str] = Field(None, pattern="^(pdf|html|docx|xlsx)$")
    municipality: Optional[str] = Field(None, max_length=255)
    publication_date: Optional[date] = None
    effective_date: Optional[date] = None
    file_size: Optional[int] = Field(None, ge=0)
    page_count: Optional[int] = Field(None, ge=0)
    language: str = Field("nl", max_length=10)
    metadata: Optional[dict] = None


class PolicyDocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|processing|indexed|failed|archived)$")
    metadata: Optional[dict] = None
    indexed_at: Optional[int] = None


class DocumentContentModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    content_type: str
    content_text: Optional[str] = None
    storage_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    checksum: Optional[str] = None
    created_at: int  # timestamp in epoch


class DocumentContentForm(BaseModel):
    document_id: str = Field(..., min_length=36, max_length=36)
    content_type: str = Field(..., pattern="^(original|processed|text|preview)$")
    content_text: Optional[str] = None
    storage_path: Optional[str] = None
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    checksum: Optional[str] = Field(None, max_length=64)


class SearchQueryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    query_text: Optional[str] = None
    filters: Optional[dict] = None
    result_count: int = 0
    clicked_results: Optional[List[str]] = None
    search_type: str = "keyword"
    response_time_ms: Optional[int] = None
    created_at: int  # timestamp in epoch


class SearchQueryForm(BaseModel):
    query_text: Optional[str] = None
    filters: Optional[dict] = None
    search_type: str = Field("keyword", pattern="^(keyword|semantic|hybrid)$")


class SavedSearchModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    query_text: Optional[str] = None
    filters: Optional[dict] = None
    notification_enabled: bool = False
    notification_frequency: Optional[str] = None
    last_notified_at: Optional[int] = None
    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


class SavedSearchForm(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    query_text: Optional[str] = None
    filters: Optional[dict] = None
    notification_enabled: bool = False
    notification_frequency: Optional[str] = Field(None, pattern="^(immediate|daily|weekly)$")


####################
# Table Classes
####################


class PolicyDocumentsTable:
    def insert_new_document(self, form_data: PolicyDocumentForm) -> Optional[PolicyDocumentModel]:
        """Create a new policy document"""
        with get_db() as db:
            try:
                doc_id = str(uuid.uuid4())
                document = PolicyDocument(
                    id=doc_id,
                    source_id=form_data.source_id,
                    external_id=form_data.external_id,
                    title=form_data.title,
                    description=form_data.description,
                    content_hash=form_data.content_hash,
                    document_url=form_data.document_url,
                    document_type=form_data.document_type,
                    municipality=form_data.municipality,
                    publication_date=form_data.publication_date,
                    effective_date=form_data.effective_date,
                    file_size=form_data.file_size,
                    page_count=form_data.page_count,
                    language=form_data.language,
                    metadata=form_data.metadata,
                )
                db.add(document)
                db.commit()
                db.refresh(document)

                return self._document_to_model(document)
            except Exception as e:
                log.exception(f"Error creating policy document: {e}")
                return None

    def get_document_by_id(self, document_id: str) -> Optional[PolicyDocumentModel]:
        """Get a policy document by ID"""
        with get_db() as db:
            try:
                document = db.query(PolicyDocument).filter_by(id=document_id).first()
                if not document:
                    return None
                return self._document_to_model(document)
            except Exception as e:
                log.exception(f"Error getting policy document: {e}")
                return None

    def get_document_by_hash(self, content_hash: str) -> Optional[PolicyDocumentModel]:
        """Get a policy document by content hash (for deduplication)"""
        with get_db() as db:
            try:
                document = db.query(PolicyDocument).filter_by(content_hash=content_hash).first()
                if not document:
                    return None
                return self._document_to_model(document)
            except Exception as e:
                log.exception(f"Error getting policy document by hash: {e}")
                return None

    def get_documents(
        self,
        source_id: Optional[str] = None,
        municipality: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[PolicyDocumentModel]:
        """Get policy documents with optional filters"""
        with get_db() as db:
            try:
                query = db.query(PolicyDocument)

                if source_id:
                    query = query.filter_by(source_id=source_id)
                if municipality:
                    query = query.filter_by(municipality=municipality)
                if status:
                    query = query.filter_by(status=status)

                documents = (
                    query.order_by(PolicyDocument.publication_date.desc())
                    .limit(limit)
                    .offset(offset)
                    .all()
                )

                return [self._document_to_model(doc) for doc in documents]
            except Exception as e:
                log.exception(f"Error getting policy documents: {e}")
                return []

    def update_document_by_id(
        self, document_id: str, form_data: PolicyDocumentUpdate
    ) -> Optional[PolicyDocumentModel]:
        """Update a policy document"""
        with get_db() as db:
            try:
                document = db.query(PolicyDocument).filter_by(id=document_id).first()
                if not document:
                    return None

                update_data = form_data.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    if key == "indexed_at" and value:
                        setattr(document, key, datetime.fromtimestamp(value))
                    else:
                        setattr(document, key, value)

                db.commit()
                db.refresh(document)

                return self._document_to_model(document)
            except Exception as e:
                log.exception(f"Error updating policy document: {e}")
                return None

    def delete_document_by_id(self, document_id: str) -> bool:
        """Delete a policy document"""
        with get_db() as db:
            try:
                db.query(PolicyDocument).filter_by(id=document_id).delete()
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error deleting policy document: {e}")
                return False

    def add_favorite(self, user_id: str, document_id: str, notes: Optional[str] = None) -> bool:
        """Add a document to user favorites"""
        with get_db() as db:
            try:
                favorite = UserFavorite(user_id=user_id, document_id=document_id, notes=notes)
                db.add(favorite)
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error adding favorite: {e}")
                return False

    def remove_favorite(self, user_id: str, document_id: str) -> bool:
        """Remove a document from user favorites"""
        with get_db() as db:
            try:
                db.query(UserFavorite).filter_by(user_id=user_id, document_id=document_id).delete()
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error removing favorite: {e}")
                return False

    def get_user_favorites(self, user_id: str) -> List[PolicyDocumentModel]:
        """Get all favorite documents for a user"""
        with get_db() as db:
            try:
                favorites = (
                    db.query(PolicyDocument)
                    .join(UserFavorite, PolicyDocument.id == UserFavorite.document_id)
                    .filter(UserFavorite.user_id == user_id)
                    .all()
                )
                return [self._document_to_model(doc) for doc in favorites]
            except Exception as e:
                log.exception(f"Error getting user favorites: {e}")
                return []

    def _document_to_model(self, document: PolicyDocument) -> PolicyDocumentModel:
        """Convert SQLAlchemy model to Pydantic model"""
        return PolicyDocumentModel(
            id=document.id,
            source_id=document.source_id,
            external_id=document.external_id,
            title=document.title,
            description=document.description,
            content_hash=document.content_hash,
            document_url=document.document_url,
            document_type=document.document_type,
            municipality=document.municipality,
            publication_date=document.publication_date,
            effective_date=document.effective_date,
            file_size=document.file_size,
            page_count=document.page_count,
            language=document.language,
            status=document.status,
            metadata=document.metadata,
            created_at=int(document.created_at.timestamp()),
            updated_at=int(document.updated_at.timestamp()),
            indexed_at=int(document.indexed_at.timestamp()) if document.indexed_at else None,
        )


class SearchQueriesTable:
    def record_search(
        self,
        user_id: Optional[str],
        form_data: SearchQueryForm,
        result_count: int,
        response_time_ms: int,
    ) -> Optional[SearchQueryModel]:
        """Record a search query for analytics"""
        with get_db() as db:
            try:
                query_id = str(uuid.uuid4())
                search_query = SearchQuery(
                    id=query_id,
                    user_id=user_id,
                    query_text=form_data.query_text,
                    filters=form_data.filters,
                    result_count=result_count,
                    search_type=form_data.search_type,
                    response_time_ms=response_time_ms,
                )
                db.add(search_query)
                db.commit()
                db.refresh(search_query)

                return SearchQueryModel(
                    id=search_query.id,
                    user_id=search_query.user_id,
                    query_text=search_query.query_text,
                    filters=search_query.filters,
                    result_count=search_query.result_count,
                    clicked_results=search_query.clicked_results,
                    search_type=search_query.search_type,
                    response_time_ms=search_query.response_time_ms,
                    created_at=int(search_query.created_at.timestamp()),
                )
            except Exception as e:
                log.exception(f"Error recording search query: {e}")
                return None

    def update_clicked_results(self, query_id: str, document_ids: List[str]) -> bool:
        """Update which results were clicked for a search query"""
        with get_db() as db:
            try:
                search_query = db.query(SearchQuery).filter_by(id=query_id).first()
                if not search_query:
                    return False

                search_query.clicked_results = document_ids
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error updating clicked results: {e}")
                return False


class SavedSearchesTable:
    def create_saved_search(self, user_id: str, form_data: SavedSearchForm) -> Optional[SavedSearchModel]:
        """Create a saved search for a user"""
        with get_db() as db:
            try:
                search_id = str(uuid.uuid4())
                saved_search = SavedSearch(
                    id=search_id,
                    user_id=user_id,
                    name=form_data.name,
                    query_text=form_data.query_text,
                    filters=form_data.filters,
                    notification_enabled=form_data.notification_enabled,
                    notification_frequency=form_data.notification_frequency,
                )
                db.add(saved_search)
                db.commit()
                db.refresh(saved_search)

                return self._saved_search_to_model(saved_search)
            except Exception as e:
                log.exception(f"Error creating saved search: {e}")
                return None

    def get_user_saved_searches(self, user_id: str) -> List[SavedSearchModel]:
        """Get all saved searches for a user"""
        with get_db() as db:
            try:
                searches = db.query(SavedSearch).filter_by(user_id=user_id).all()
                return [self._saved_search_to_model(s) for s in searches]
            except Exception as e:
                log.exception(f"Error getting saved searches: {e}")
                return []

    def delete_saved_search(self, search_id: str, user_id: str) -> bool:
        """Delete a saved search"""
        with get_db() as db:
            try:
                db.query(SavedSearch).filter_by(id=search_id, user_id=user_id).delete()
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error deleting saved search: {e}")
                return False

    def _saved_search_to_model(self, saved_search: SavedSearch) -> SavedSearchModel:
        """Convert SQLAlchemy model to Pydantic model"""
        return SavedSearchModel(
            id=saved_search.id,
            user_id=saved_search.user_id,
            name=saved_search.name,
            query_text=saved_search.query_text,
            filters=saved_search.filters,
            notification_enabled=saved_search.notification_enabled,
            notification_frequency=saved_search.notification_frequency,
            last_notified_at=int(saved_search.last_notified_at.timestamp()) if saved_search.last_notified_at else None,
            created_at=int(saved_search.created_at.timestamp()),
            updated_at=int(saved_search.updated_at.timestamp()),
        )


# Table instances
PolicyDocuments = PolicyDocumentsTable()
SearchQueries = SearchQueriesTable()
SavedSearches = SavedSearchesTable()
