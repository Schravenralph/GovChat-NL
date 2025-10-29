"""
Scraper plugins for various government sources.

This package contains scraper plugin implementations for different
government websites and document sources.
"""

# Import plugins to register them
from open_webui.scraper.plugins.gemeenteblad import GemeentebladPlugin

__all__ = [
    "GemeentebladPlugin",
]
