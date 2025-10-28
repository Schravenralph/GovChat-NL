import logging
import time
import uuid
from typing import Optional, List
from decimal import Decimal

from open_webui.internal.db import Base, JSONField, get_db
from open_webui.env import SRC_LOG_LEVELS
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON, Numeric
from sqlalchemy.sql import func

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Policy Scanner DB Schema - Categories and Tags
####################


class PolicyCategory(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "policy_scanner"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String(36), ForeignKey("policy_scanner.categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)
    path = Column(Text, nullable=True)  # LTREE path for hierarchy
    sort_order = Column(Integer, nullable=False, server_default="0")
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class DocumentCategory(Base):
    __tablename__ = "document_categories"
    __table_args__ = {"schema": "policy_scanner"}

    document_id = Column(String(36), ForeignKey("policy_scanner.documents.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(String(36), ForeignKey("policy_scanner.categories.id", ondelete="CASCADE"), primary_key=True)
    confidence_score = Column(Numeric(precision=3, scale=2), nullable=True)
    assigned_by = Column(String(20), nullable=False, server_default="auto")
    assigned_at = Column(DateTime, nullable=False, server_default=func.now())


class CategoryHierarchy(Base):
    __tablename__ = "category_hierarchy"
    __table_args__ = {"schema": "policy_scanner"}

    ancestor_id = Column(String(36), ForeignKey("policy_scanner.categories.id", ondelete="CASCADE"), primary_key=True)
    descendant_id = Column(String(36), ForeignKey("policy_scanner.categories.id", ondelete="CASCADE"), primary_key=True)
    depth = Column(Integer, nullable=False)


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = {"schema": "policy_scanner"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class DocumentTag(Base):
    __tablename__ = "document_tags"
    __table_args__ = {"schema": "policy_scanner"}

    document_id = Column(String(36), ForeignKey("policy_scanner.documents.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(String(36), ForeignKey("policy_scanner.tags.id", ondelete="CASCADE"), primary_key=True)
    tagged_at = Column(DateTime, nullable=False, server_default=func.now())
    tagged_by = Column(String(36), ForeignKey("user.id", ondelete="SET NULL"), nullable=True)


####################
# Pydantic Models
####################


class PolicyCategoryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parent_id: Optional[str] = None
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    path: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    created_at: int  # timestamp in epoch


class PolicyCategoryForm(BaseModel):
    parent_id: Optional[str] = Field(None, min_length=36, max_length=36)
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    sort_order: int = Field(0, ge=0)


class PolicyCategoryUpdate(BaseModel):
    parent_id: Optional[str] = Field(None, min_length=36, max_length=36)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class DocumentCategoryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    category_id: str
    confidence_score: Optional[Decimal] = None
    assigned_by: str = "auto"
    assigned_at: int  # timestamp in epoch


class DocumentCategoryForm(BaseModel):
    category_id: str = Field(..., min_length=36, max_length=36)
    confidence_score: Optional[Decimal] = Field(None, ge=0, le=1)
    assigned_by: str = Field("auto", pattern="^(auto|rule|manual)$")


class TagModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    created_at: int  # timestamp in epoch


class TagForm(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


####################
# Table Classes
####################


class PolicyCategoriesTable:
    def insert_new_category(self, form_data: PolicyCategoryForm) -> Optional[PolicyCategoryModel]:
        """Create a new category"""
        with get_db() as db:
            try:
                category_id = str(uuid.uuid4())

                # Build path based on parent
                path = None
                if form_data.parent_id:
                    parent = db.query(PolicyCategory).filter_by(id=form_data.parent_id).first()
                    if parent and parent.path:
                        path = f"{parent.path}.{form_data.slug}"
                    else:
                        path = form_data.slug
                else:
                    path = form_data.slug

                category = PolicyCategory(
                    id=category_id,
                    parent_id=form_data.parent_id,
                    name=form_data.name,
                    slug=form_data.slug,
                    description=form_data.description,
                    icon=form_data.icon,
                    color=form_data.color,
                    path=path,
                    sort_order=form_data.sort_order,
                )
                db.add(category)

                # Update category hierarchy
                if form_data.parent_id:
                    # Add self-reference
                    db.add(CategoryHierarchy(ancestor_id=category_id, descendant_id=category_id, depth=0))

                    # Add all ancestor relationships
                    ancestors = (
                        db.query(CategoryHierarchy)
                        .filter_by(descendant_id=form_data.parent_id)
                        .all()
                    )
                    for ancestor in ancestors:
                        db.add(
                            CategoryHierarchy(
                                ancestor_id=ancestor.ancestor_id,
                                descendant_id=category_id,
                                depth=ancestor.depth + 1,
                            )
                        )
                else:
                    # Root category - just self-reference
                    db.add(CategoryHierarchy(ancestor_id=category_id, descendant_id=category_id, depth=0))

                db.commit()
                db.refresh(category)

                return self._category_to_model(category)
            except Exception as e:
                log.exception(f"Error creating category: {e}")
                return None

    def get_category_by_id(self, category_id: str) -> Optional[PolicyCategoryModel]:
        """Get a category by ID"""
        with get_db() as db:
            try:
                category = db.query(PolicyCategory).filter_by(id=category_id).first()
                if not category:
                    return None
                return self._category_to_model(category)
            except Exception as e:
                log.exception(f"Error getting category: {e}")
                return None

    def get_category_by_slug(self, slug: str) -> Optional[PolicyCategoryModel]:
        """Get a category by slug"""
        with get_db() as db:
            try:
                category = db.query(PolicyCategory).filter_by(slug=slug).first()
                if not category:
                    return None
                return self._category_to_model(category)
            except Exception as e:
                log.exception(f"Error getting category by slug: {e}")
                return None

    def get_categories(self, parent_id: Optional[str] = None, active_only: bool = True) -> List[PolicyCategoryModel]:
        """Get categories, optionally filtered by parent"""
        with get_db() as db:
            try:
                query = db.query(PolicyCategory)

                if parent_id is not None:
                    query = query.filter_by(parent_id=parent_id)
                if active_only:
                    query = query.filter_by(is_active=True)

                categories = query.order_by(PolicyCategory.sort_order.asc()).all()
                return [self._category_to_model(cat) for cat in categories]
            except Exception as e:
                log.exception(f"Error getting categories: {e}")
                return []

    def get_category_children(self, category_id: str, depth: Optional[int] = 1) -> List[PolicyCategoryModel]:
        """Get all children of a category up to specified depth"""
        with get_db() as db:
            try:
                query = (
                    db.query(PolicyCategory)
                    .join(
                        CategoryHierarchy,
                        PolicyCategory.id == CategoryHierarchy.descendant_id,
                    )
                    .filter(CategoryHierarchy.ancestor_id == category_id)
                    .filter(CategoryHierarchy.depth > 0)
                )

                if depth is not None:
                    query = query.filter(CategoryHierarchy.depth <= depth)

                categories = query.order_by(CategoryHierarchy.depth.asc(), PolicyCategory.sort_order.asc()).all()
                return [self._category_to_model(cat) for cat in categories]
            except Exception as e:
                log.exception(f"Error getting category children: {e}")
                return []

    def update_category_by_id(
        self, category_id: str, form_data: PolicyCategoryUpdate
    ) -> Optional[PolicyCategoryModel]:
        """Update a category"""
        with get_db() as db:
            try:
                category = db.query(PolicyCategory).filter_by(id=category_id).first()
                if not category:
                    return None

                update_data = form_data.model_dump(exclude_unset=True)

                # Handle parent change (rebuild hierarchy)
                if "parent_id" in update_data and update_data["parent_id"] != category.parent_id:
                    # This is complex - for MVP, prevent parent changes
                    # TODO: Implement full hierarchy rebuild
                    log.warning(f"Parent change not yet implemented for category {category_id}")
                    del update_data["parent_id"]

                for key, value in update_data.items():
                    setattr(category, key, value)

                db.commit()
                db.refresh(category)

                return self._category_to_model(category)
            except Exception as e:
                log.exception(f"Error updating category: {e}")
                return None

    def delete_category_by_id(self, category_id: str) -> bool:
        """Delete a category (will cascade to children due to FK constraints)"""
        with get_db() as db:
            try:
                db.query(PolicyCategory).filter_by(id=category_id).delete()
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error deleting category: {e}")
                return False

    def assign_category_to_document(
        self, document_id: str, form_data: DocumentCategoryForm
    ) -> Optional[DocumentCategoryModel]:
        """Assign a category to a document"""
        with get_db() as db:
            try:
                doc_category = DocumentCategory(
                    document_id=document_id,
                    category_id=form_data.category_id,
                    confidence_score=form_data.confidence_score,
                    assigned_by=form_data.assigned_by,
                )
                db.add(doc_category)
                db.commit()
                db.refresh(doc_category)

                return DocumentCategoryModel(
                    document_id=doc_category.document_id,
                    category_id=doc_category.category_id,
                    confidence_score=doc_category.confidence_score,
                    assigned_by=doc_category.assigned_by,
                    assigned_at=int(doc_category.assigned_at.timestamp()),
                )
            except Exception as e:
                log.exception(f"Error assigning category to document: {e}")
                return None

    def get_document_categories(self, document_id: str) -> List[DocumentCategoryModel]:
        """Get all categories assigned to a document"""
        with get_db() as db:
            try:
                doc_categories = db.query(DocumentCategory).filter_by(document_id=document_id).all()
                return [
                    DocumentCategoryModel(
                        document_id=dc.document_id,
                        category_id=dc.category_id,
                        confidence_score=dc.confidence_score,
                        assigned_by=dc.assigned_by,
                        assigned_at=int(dc.assigned_at.timestamp()),
                    )
                    for dc in doc_categories
                ]
            except Exception as e:
                log.exception(f"Error getting document categories: {e}")
                return []

    def remove_category_from_document(self, document_id: str, category_id: str) -> bool:
        """Remove a category assignment from a document"""
        with get_db() as db:
            try:
                db.query(DocumentCategory).filter_by(
                    document_id=document_id, category_id=category_id
                ).delete()
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error removing category from document: {e}")
                return False

    def _category_to_model(self, category: PolicyCategory) -> PolicyCategoryModel:
        """Convert SQLAlchemy model to Pydantic model"""
        return PolicyCategoryModel(
            id=category.id,
            parent_id=category.parent_id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            icon=category.icon,
            color=category.color,
            path=category.path,
            sort_order=category.sort_order,
            is_active=category.is_active,
            created_at=int(category.created_at.timestamp()),
        )


class TagsTable:
    def create_tag(self, form_data: TagForm) -> Optional[TagModel]:
        """Create a new tag"""
        with get_db() as db:
            try:
                tag_id = str(uuid.uuid4())
                tag = Tag(
                    id=tag_id,
                    name=form_data.name,
                    description=form_data.description,
                    color=form_data.color,
                )
                db.add(tag)
                db.commit()
                db.refresh(tag)

                return TagModel(
                    id=tag.id,
                    name=tag.name,
                    description=tag.description,
                    color=tag.color,
                    created_at=int(tag.created_at.timestamp()),
                )
            except Exception as e:
                log.exception(f"Error creating tag: {e}")
                return None

    def get_tags(self) -> List[TagModel]:
        """Get all tags"""
        with get_db() as db:
            try:
                tags = db.query(Tag).order_by(Tag.name.asc()).all()
                return [
                    TagModel(
                        id=tag.id,
                        name=tag.name,
                        description=tag.description,
                        color=tag.color,
                        created_at=int(tag.created_at.timestamp()),
                    )
                    for tag in tags
                ]
            except Exception as e:
                log.exception(f"Error getting tags: {e}")
                return []

    def add_tag_to_document(self, document_id: str, tag_id: str, user_id: Optional[str] = None) -> bool:
        """Add a tag to a document"""
        with get_db() as db:
            try:
                doc_tag = DocumentTag(
                    document_id=document_id,
                    tag_id=tag_id,
                    tagged_by=user_id,
                )
                db.add(doc_tag)
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error adding tag to document: {e}")
                return False

    def remove_tag_from_document(self, document_id: str, tag_id: str) -> bool:
        """Remove a tag from a document"""
        with get_db() as db:
            try:
                db.query(DocumentTag).filter_by(document_id=document_id, tag_id=tag_id).delete()
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error removing tag from document: {e}")
                return False

    def get_document_tags(self, document_id: str) -> List[TagModel]:
        """Get all tags for a document"""
        with get_db() as db:
            try:
                tags = (
                    db.query(Tag)
                    .join(DocumentTag, Tag.id == DocumentTag.tag_id)
                    .filter(DocumentTag.document_id == document_id)
                    .all()
                )
                return [
                    TagModel(
                        id=tag.id,
                        name=tag.name,
                        description=tag.description,
                        color=tag.color,
                        created_at=int(tag.created_at.timestamp()),
                    )
                    for tag in tags
                ]
            except Exception as e:
                log.exception(f"Error getting document tags: {e}")
                return []


# Table instances
PolicyCategories = PolicyCategoriesTable()
Tags = TagsTable()
