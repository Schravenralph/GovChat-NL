"""
Policy Scanner Scraper Framework.

This package provides an extensible plugin-based framework for discovering
and downloading policy documents from various government sources.

Key Components:
- ScraperPlugin: Abstract base class for scraper plugins
- DocumentMetadata: Data model for document metadata
- RateLimiter: Token bucket rate limiting
- RetryMiddleware: Exponential backoff retry logic
- PluginRegistry: Plugin discovery and management

Example Usage:
    from open_webui.scraper import get_plugin, ScraperConfig

    config = ScraperConfig(
        base_url="https://gemeentebladen.nl",
        rate_limit=10
    )

    plugin = get_plugin("gemeenteblad", config)
    result = await plugin.scrape()

    print(f"Found {result.total_found} documents")
"""

__version__ = "1.0.0"

from open_webui.scraper.models import (
    DocumentMetadata,
    DocumentType,
    DocumentStatus,
    ScraperConfig,
    ScrapeResult,
    ScraperStats,
)

from open_webui.scraper.base import (
    ScraperPlugin,
    BaseScraper,
)

from open_webui.scraper.middleware import (
    RateLimiter,
    ExponentialBackoff,
    RetryMiddleware,
    UserAgentRotator,
    BotDetectionHandler,
    RobotsTxtParser,
)

from open_webui.scraper.validators import (
    ValidationError,
    validate_url,
    validate_external_id,
    generate_external_id_hash,
    generate_content_hash,
    validate_date,
    validate_municipality,
    validate_document_type,
    sanitize_filename,
    normalize_url,
)


# Import registry functions
from open_webui.scraper.plugins.registry import (
    register_plugin,
    get_plugin,
    list_plugins,
)


__all__ = [
    # Version
    "__version__",

    # Models
    "DocumentMetadata",
    "DocumentType",
    "DocumentStatus",
    "ScraperConfig",
    "ScrapeResult",
    "ScraperStats",

    # Base Classes
    "ScraperPlugin",
    "BaseScraper",

    # Middleware
    "RateLimiter",
    "ExponentialBackoff",
    "RetryMiddleware",
    "UserAgentRotator",
    "BotDetectionHandler",
    "RobotsTxtParser",

    # Validators
    "ValidationError",
    "validate_url",
    "validate_external_id",
    "generate_external_id_hash",
    "generate_content_hash",
    "validate_date",
    "validate_municipality",
    "validate_document_type",
    "sanitize_filename",
    "normalize_url",

    # Registry
    "register_plugin",
    "get_plugin",
    "list_plugins",
]
