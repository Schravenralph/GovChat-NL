"""
Plugin registry for scraper plugins.

This module provides a centralized registry for discovering and instantiating
scraper plugins by name.
"""

import logging
from typing import Dict, List, Optional, Type

from open_webui.scraper.base import ScraperPlugin
from open_webui.scraper.models import ScraperConfig


logger = logging.getLogger(__name__)


# Global plugin registry
_PLUGIN_REGISTRY: Dict[str, Type[ScraperPlugin]] = {}


def register_plugin(name: str, plugin_class: Type[ScraperPlugin]):
    """
    Register a scraper plugin.

    Args:
        name: Plugin name/identifier
        plugin_class: Plugin class (must inherit from ScraperPlugin)

    Raises:
        ValueError: If plugin is already registered or invalid
    """
    if not issubclass(plugin_class, ScraperPlugin):
        raise ValueError(
            f"Plugin class {plugin_class} must inherit from ScraperPlugin"
        )

    if name in _PLUGIN_REGISTRY:
        logger.warning(f"Overwriting existing plugin: {name}")

    _PLUGIN_REGISTRY[name] = plugin_class
    logger.info(f"Registered plugin: {name} -> {plugin_class.__name__}")


def get_plugin(name: str, config: ScraperConfig) -> ScraperPlugin:
    """
    Get a scraper plugin instance by name.

    Args:
        name: Plugin name/identifier
        config: Configuration for the plugin

    Returns:
        ScraperPlugin: Initialized plugin instance

    Raises:
        ValueError: If plugin not found
    """
    if name not in _PLUGIN_REGISTRY:
        available = ", ".join(_PLUGIN_REGISTRY.keys())
        raise ValueError(
            f"Plugin '{name}' not found. Available plugins: {available}"
        )

    plugin_class = _PLUGIN_REGISTRY[name]
    logger.debug(f"Creating plugin instance: {name}")

    try:
        return plugin_class(config)
    except Exception as e:
        logger.error(f"Failed to create plugin '{name}': {e}")
        raise


def list_plugins() -> List[str]:
    """
    List all registered plugin names.

    Returns:
        List[str]: List of plugin names
    """
    return list(_PLUGIN_REGISTRY.keys())


def plugin_info(name: str) -> Optional[Dict[str, str]]:
    """
    Get information about a plugin.

    Args:
        name: Plugin name

    Returns:
        Dict with plugin information, or None if not found
    """
    if name not in _PLUGIN_REGISTRY:
        return None

    plugin_class = _PLUGIN_REGISTRY[name]

    return {
        "name": name,
        "class": plugin_class.__name__,
        "module": plugin_class.__module__,
        "doc": plugin_class.__doc__ or "No documentation available",
    }


def unregister_plugin(name: str) -> bool:
    """
    Unregister a plugin.

    Args:
        name: Plugin name

    Returns:
        bool: True if plugin was unregistered
    """
    if name in _PLUGIN_REGISTRY:
        del _PLUGIN_REGISTRY[name]
        logger.info(f"Unregistered plugin: {name}")
        return True
    return False
