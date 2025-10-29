"""
Validation utilities for Policy Scanner scraper framework.

This module provides validation functions for URLs, metadata, and
configuration to ensure data quality and security.
"""

import hashlib
import re
from typing import Optional
from urllib.parse import urlparse, urljoin
from datetime import date


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_url(url: str, allowed_schemes: tuple = ('http', 'https')) -> bool:
    """
    Validate URL format and scheme.

    Args:
        url: URL string to validate
        allowed_schemes: Tuple of allowed URL schemes

    Returns:
        bool: True if URL is valid

    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}")

    if parsed.scheme not in allowed_schemes:
        raise ValidationError(
            f"URL scheme '{parsed.scheme}' not allowed. "
            f"Allowed schemes: {allowed_schemes}"
        )

    if not parsed.netloc:
        raise ValidationError("URL must have a valid domain")

    return True


def validate_external_id(external_id: str) -> bool:
    """
    Validate external ID format.

    Args:
        external_id: External ID to validate

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If external ID is invalid
    """
    if not external_id or not isinstance(external_id, str):
        raise ValidationError("external_id must be a non-empty string")

    if not external_id.strip():
        raise ValidationError("external_id cannot be only whitespace")

    if len(external_id) > 500:
        raise ValidationError("external_id cannot exceed 500 characters")

    return True


def generate_external_id_hash(url: str) -> str:
    """
    Generate a unique external ID from a URL using SHA-256.

    Args:
        url: URL to hash

    Returns:
        str: Hexadecimal hash string (first 32 characters)
    """
    return hashlib.sha256(url.encode('utf-8')).hexdigest()[:32]


def generate_content_hash(content: bytes) -> str:
    """
    Generate SHA-256 hash of document content.

    Args:
        content: Document content as bytes

    Returns:
        str: Hexadecimal hash string
    """
    return hashlib.sha256(content).hexdigest()


def validate_date(date_str: Optional[str]) -> Optional[date]:
    """
    Validate and parse date string.

    Args:
        date_str: Date string in ISO format (YYYY-MM-DD)

    Returns:
        date object or None if invalid

    Raises:
        ValidationError: If date format is invalid
    """
    if not date_str:
        return None

    if isinstance(date_str, date):
        return date_str

    # Try common date formats
    formats = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{2}-\d{2}-\d{4}$',  # DD-MM-YYYY
        r'^\d{2}/\d{2}/\d{4}$',  # DD/MM/YYYY
    ]

    matched = False
    for fmt in formats:
        if re.match(fmt, date_str):
            matched = True
            break

    if not matched:
        raise ValidationError(
            f"Invalid date format: {date_str}. "
            "Expected YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY"
        )

    # Parse date
    try:
        if '-' in date_str:
            parts = date_str.split('-')
            if len(parts[0]) == 4:  # YYYY-MM-DD
                return date.fromisoformat(date_str)
            else:  # DD-MM-YYYY
                day, month, year = parts
                return date(int(year), int(month), int(day))
        elif '/' in date_str:  # DD/MM/YYYY
            day, month, year = date_str.split('/')
            return date(int(year), int(month), int(day))
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid date: {date_str} - {e}")

    return None


def validate_municipality(municipality: Optional[str]) -> Optional[str]:
    """
    Validate and normalize municipality name.

    Args:
        municipality: Municipality name

    Returns:
        Normalized municipality name or None
    """
    if not municipality:
        return None

    # Strip whitespace
    normalized = municipality.strip()

    if not normalized:
        return None

    # Validate length
    if len(normalized) > 255:
        raise ValidationError("Municipality name cannot exceed 255 characters")

    # Remove excessive whitespace
    normalized = re.sub(r'\s+', ' ', normalized)

    return normalized


def validate_document_type(filename: str) -> str:
    """
    Determine document type from filename or URL.

    Args:
        filename: Filename or URL

    Returns:
        str: Document type ('pdf', 'html', 'docx', 'xlsx', 'unknown')
    """
    if not filename:
        return 'unknown'

    filename_lower = filename.lower()

    if filename_lower.endswith('.pdf'):
        return 'pdf'
    elif filename_lower.endswith(('.html', '.htm')):
        return 'html'
    elif filename_lower.endswith(('.docx', '.doc')):
        return 'docx'
    elif filename_lower.endswith(('.xlsx', '.xls')):
        return 'xlsx'
    else:
        return 'unknown'


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove potentially dangerous characters.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove directory traversal attempts
    filename = filename.replace('..', '')
    filename = filename.replace('/', '_')
    filename = filename.replace('\\', '_')

    # Remove null bytes
    filename = filename.replace('\0', '')

    # Keep only alphanumeric, dash, underscore, and period
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:250]
        filename = f"{name}.{ext}" if ext else name

    return filename


def validate_css_selector(selector: str) -> bool:
    """
    Basic validation of CSS selector format.

    Args:
        selector: CSS selector string

    Returns:
        bool: True if selector appears valid

    Raises:
        ValidationError: If selector is obviously invalid
    """
    if not selector or not isinstance(selector, str):
        raise ValidationError("CSS selector must be a non-empty string")

    if not selector.strip():
        raise ValidationError("CSS selector cannot be only whitespace")

    # Check for obvious invalid patterns
    if selector.count('(') != selector.count(')'):
        raise ValidationError("Unbalanced parentheses in CSS selector")

    if selector.count('[') != selector.count(']'):
        raise ValidationError("Unbalanced brackets in CSS selector")

    return True


def normalize_url(url: str, base_url: str) -> str:
    """
    Normalize a URL relative to a base URL.

    Args:
        url: URL to normalize (can be relative)
        base_url: Base URL for resolving relative URLs

    Returns:
        str: Absolute normalized URL
    """
    # Handle absolute URLs
    if url.startswith(('http://', 'https://')):
        return url

    # Handle protocol-relative URLs
    if url.startswith('//'):
        parsed_base = urlparse(base_url)
        return f"{parsed_base.scheme}:{url}"

    # Handle relative URLs
    return urljoin(base_url, url)


def validate_rate_limit(rate_limit: int) -> bool:
    """
    Validate rate limit configuration.

    Args:
        rate_limit: Requests per second

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If rate limit is invalid
    """
    if not isinstance(rate_limit, int):
        raise ValidationError("Rate limit must be an integer")

    if rate_limit < 1:
        raise ValidationError("Rate limit must be at least 1 request per second")

    if rate_limit > 100:
        raise ValidationError("Rate limit cannot exceed 100 requests per second")

    return True
