"""
Pydantic models for Policy Scanner scraper framework.

This module defines the data models for document metadata, scraper configurations,
and validation schemas used throughout the scraper framework.
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, field_validator


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    XLSX = "xlsx"
    UNKNOWN = "unknown"


class DocumentStatus(str, Enum):
    """Document processing statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    ARCHIVED = "archived"


class DocumentMetadata(BaseModel):
    """
    Metadata for a discovered policy document.

    This model represents the structured information extracted from
    a government website about a policy document.
    """
    title: str = Field(..., description="Document title", min_length=1, max_length=1000)
    url: str = Field(..., description="URL to the document")
    external_id: str = Field(..., description="Unique identifier from source system")
    publication_date: Optional[date] = Field(None, description="Document publication date")
    effective_date: Optional[date] = Field(None, description="Date when policy becomes effective")
    municipality: Optional[str] = Field(None, description="Municipality name", max_length=255)
    document_type: DocumentType = Field(DocumentType.UNKNOWN, description="Document file type")
    description: Optional[str] = Field(None, description="Document description or summary")
    file_size: Optional[int] = Field(None, description="File size in bytes", ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {v}")
        return v

    @field_validator('external_id')
    @classmethod
    def validate_external_id(cls, v: str) -> str:
        """Validate external ID is not empty."""
        if not v or not v.strip():
            raise ValueError("external_id cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Gemeenteblad Amsterdam - Vergunning 2025-001",
                "url": "https://gemeentebladen.nl/documents/12345",
                "external_id": "gmb-ams-2025-001",
                "publication_date": "2025-01-15",
                "municipality": "Amsterdam",
                "document_type": "pdf",
                "description": "Vergunning voor evenement in Vondelpark"
            }
        }


class ScraperConfig(BaseModel):
    """
    Configuration for a scraper plugin.

    This model defines the settings required to configure and run
    a specific scraper plugin.
    """
    base_url: str = Field(..., description="Base URL for the source website")
    rate_limit: int = Field(10, description="Maximum requests per second", ge=1, le=100)
    crawl_delay: float = Field(1.0, description="Delay between requests in seconds", ge=0.1)
    timeout: int = Field(30, description="Request timeout in seconds", ge=5, le=300)
    max_retries: int = Field(3, description="Maximum retry attempts", ge=0, le=10)
    user_agent: Optional[str] = Field(
        None,
        description="Custom User-Agent header"
    )
    selectors: Dict[str, str] = Field(
        default_factory=dict,
        description="CSS selectors for parsing HTML"
    )
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional HTTP headers"
    )
    auth_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Authentication configuration"
    )
    custom_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Plugin-specific parameters"
    )

    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid base URL format: {v}")
        return v.rstrip('/')

    class Config:
        json_schema_extra = {
            "example": {
                "base_url": "https://gemeentebladen.nl",
                "rate_limit": 10,
                "crawl_delay": 1.0,
                "selectors": {
                    "item": "div.document-item",
                    "title": "h2.title",
                    "url": "a.document-link",
                    "date": "span.publication-date"
                }
            }
        }


class ScrapeResult(BaseModel):
    """
    Result of a scraping operation.

    This model contains the documents discovered and metadata about
    the scraping operation.
    """
    documents: List[DocumentMetadata] = Field(default_factory=list)
    total_found: int = Field(0, description="Total number of documents found")
    pages_scraped: int = Field(0, description="Number of pages processed")
    duration_seconds: float = Field(0.0, description="Time taken for scraping")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
    success: bool = Field(True, description="Whether scraping completed successfully")

    class Config:
        json_schema_extra = {
            "example": {
                "documents": [],
                "total_found": 42,
                "pages_scraped": 3,
                "duration_seconds": 12.5,
                "errors": [],
                "success": True
            }
        }


class ScraperStats(BaseModel):
    """
    Statistics about scraper performance.

    Used for monitoring and debugging scraper operations.
    """
    total_requests: int = Field(0, description="Total HTTP requests made")
    successful_requests: int = Field(0, description="Successful requests")
    failed_requests: int = Field(0, description="Failed requests")
    rate_limited_requests: int = Field(0, description="Requests that were rate limited")
    retry_attempts: int = Field(0, description="Total retry attempts")
    avg_response_time_ms: float = Field(0.0, description="Average response time in milliseconds")
    documents_discovered: int = Field(0, description="Total documents discovered")

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    class Config:
        json_schema_extra = {
            "example": {
                "total_requests": 50,
                "successful_requests": 48,
                "failed_requests": 2,
                "rate_limited_requests": 5,
                "retry_attempts": 3,
                "avg_response_time_ms": 450.2,
                "documents_discovered": 142
            }
        }
