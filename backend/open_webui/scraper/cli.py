"""
CLI tool for testing scraper plugins.

Usage:
    python -m open_webui.scraper test gemeenteblad --url https://gemeentebladen.nl

    python -m open_webui.scraper list

    python -m open_webui.scraper info gemeenteblad
"""

import argparse
import asyncio
import json
import sys
import logging
from datetime import date, datetime
from typing import Optional

from open_webui.scraper import (
    get_plugin,
    list_plugins,
    ScraperConfig,
)
from open_webui.scraper.plugins.registry import plugin_info


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_parser() -> argparse.ArgumentParser:
    """
    Set up argument parser.

    Returns:
        ArgumentParser: Configured parser
    """
    parser = argparse.ArgumentParser(
        description='Policy Scanner Scraper CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test Gemeenteblad scraper
  python -m open_webui.scraper test gemeenteblad --url https://gemeentebladen.nl

  # List all available plugins
  python -m open_webui.scraper list

  # Get plugin information
  python -m open_webui.scraper info gemeenteblad

  # Test with custom configuration
  python -m open_webui.scraper test gemeenteblad \\
    --url https://gemeentebladen.nl \\
    --rate-limit 5 \\
    --max-pages 2 \\
    --municipality Amsterdam

  # Test with date filtering
  python -m open_webui.scraper test gemeenteblad \\
    --url https://gemeentebladen.nl \\
    --start-date 2025-01-01 \\
    --end-date 2025-12-31

  # Enable debug logging
  python -m open_webui.scraper test gemeenteblad \\
    --url https://gemeentebladen.nl \\
    --verbose

  # Output as JSON
  python -m open_webui.scraper test gemeenteblad \\
    --url https://gemeentebladen.nl \\
    --output json
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Test command
    test_parser = subparsers.add_parser('test', help='Test a scraper plugin')
    test_parser.add_argument(
        'plugin',
        type=str,
        help='Plugin name (e.g., gemeenteblad)'
    )
    test_parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='Base URL for the scraper'
    )
    test_parser.add_argument(
        '--rate-limit',
        type=int,
        default=10,
        help='Requests per second (default: 10)'
    )
    test_parser.add_argument(
        '--crawl-delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    test_parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    test_parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Maximum retry attempts (default: 3)'
    )
    test_parser.add_argument(
        '--max-pages',
        type=int,
        help='Maximum pages to scrape (default: unlimited)'
    )
    test_parser.add_argument(
        '--start-date',
        type=str,
        help='Filter documents from this date (YYYY-MM-DD)'
    )
    test_parser.add_argument(
        '--end-date',
        type=str,
        help='Filter documents to this date (YYYY-MM-DD)'
    )
    test_parser.add_argument(
        '--municipality',
        type=str,
        help='Filter by municipality'
    )
    test_parser.add_argument(
        '--query',
        type=str,
        help='Search query'
    )
    test_parser.add_argument(
        '--selector',
        action='append',
        help='CSS selector (format: key=value, can be used multiple times)'
    )
    test_parser.add_argument(
        '--output',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )
    test_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable debug logging'
    )
    test_parser.add_argument(
        '--download-first',
        action='store_true',
        help='Download the first discovered document'
    )

    # List command
    list_parser = subparsers.add_parser('list', help='List available plugins')
    list_parser.add_argument(
        '--output',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )

    # Info command
    info_parser = subparsers.add_parser('info', help='Get plugin information')
    info_parser.add_argument(
        'plugin',
        type=str,
        help='Plugin name'
    )
    info_parser.add_argument(
        '--output',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )

    return parser


async def test_plugin(args) -> int:
    """
    Test a scraper plugin.

    Args:
        args: Command line arguments

    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Parse selectors
    selectors = {}
    if args.selector:
        for selector in args.selector:
            if '=' not in selector:
                logger.error(f"Invalid selector format: {selector} (expected key=value)")
                return 1
            key, value = selector.split('=', 1)
            selectors[key] = value

    # Set default selectors for gemeenteblad if not provided
    if args.plugin == 'gemeenteblad' and not selectors:
        selectors = {
            'item': 'div.document-item',
            'title': 'h2.title',
            'url': 'a.document-link',
            'date': 'span.publication-date',
        }
        logger.info("Using default Gemeenteblad selectors")

    # Parse dates
    start_date = None
    end_date = None

    if args.start_date:
        try:
            start_date = date.fromisoformat(args.start_date)
        except ValueError:
            logger.error(f"Invalid start date format: {args.start_date} (expected YYYY-MM-DD)")
            return 1

    if args.end_date:
        try:
            end_date = date.fromisoformat(args.end_date)
        except ValueError:
            logger.error(f"Invalid end date format: {args.end_date} (expected YYYY-MM-DD)")
            return 1

    # Create configuration
    config = ScraperConfig(
        base_url=args.url,
        rate_limit=args.rate_limit,
        crawl_delay=args.crawl_delay,
        timeout=args.timeout,
        max_retries=args.max_retries,
        selectors=selectors,
    )

    try:
        # Get plugin instance
        logger.info(f"Initializing plugin: {args.plugin}")
        plugin = get_plugin(args.plugin, config)

        # Test connection
        logger.info("Testing connection...")
        if not await plugin.test_connection():
            logger.error("Connection test failed")
            return 1

        logger.info("Connection successful!")

        # Run scraping
        logger.info("Starting document discovery...")

        kwargs = {}
        if args.municipality:
            kwargs['municipality'] = args.municipality
        if args.query:
            kwargs['query'] = args.query

        result = await plugin.scrape(
            start_date=start_date,
            end_date=end_date,
            max_pages=args.max_pages,
            **kwargs
        )

        # Download first document if requested
        downloaded_content = None
        if args.download_first and result.documents:
            logger.info(f"Downloading first document: {result.documents[0].title}")
            try:
                downloaded_content = await plugin.download_document(result.documents[0])
                logger.info(f"Downloaded {len(downloaded_content)} bytes")
            except Exception as e:
                logger.error(f"Download failed: {e}")

        # Get statistics
        stats = plugin.get_stats()

        # Close plugin
        await plugin.close()

        # Output results
        if args.output == 'json':
            output = {
                'success': result.success,
                'total_found': result.total_found,
                'pages_scraped': result.pages_scraped,
                'duration_seconds': result.duration_seconds,
                'errors': result.errors,
                'statistics': {
                    'total_requests': stats.total_requests,
                    'successful_requests': stats.successful_requests,
                    'failed_requests': stats.failed_requests,
                    'rate_limited_requests': stats.rate_limited_requests,
                    'retry_attempts': stats.retry_attempts,
                    'avg_response_time_ms': stats.avg_response_time_ms,
                    'success_rate': stats.success_rate,
                },
                'documents': [
                    {
                        'title': doc.title,
                        'url': doc.url,
                        'external_id': doc.external_id,
                        'publication_date': doc.publication_date.isoformat() if doc.publication_date else None,
                        'municipality': doc.municipality,
                        'document_type': doc.document_type.value,
                        'description': doc.description,
                    }
                    for doc in result.documents
                ],
            }
            if downloaded_content:
                output['downloaded_size'] = len(downloaded_content)

            print(json.dumps(output, indent=2))
        else:
            # Text output
            print(f"\n{'='*60}")
            print(f"Scraping Results")
            print(f"{'='*60}")
            print(f"Status: {'SUCCESS' if result.success else 'FAILED'}")
            print(f"Duration: {result.duration_seconds:.2f}s")
            print(f"Documents Found: {result.total_found}")
            print(f"Pages Scraped: {result.pages_scraped}")

            if result.errors:
                print(f"\nErrors:")
                for error in result.errors:
                    print(f"  - {error}")

            print(f"\n{'='*60}")
            print(f"Statistics")
            print(f"{'='*60}")
            print(f"Total Requests: {stats.total_requests}")
            print(f"Successful: {stats.successful_requests}")
            print(f"Failed: {stats.failed_requests}")
            print(f"Rate Limited: {stats.rate_limited_requests}")
            print(f"Retries: {stats.retry_attempts}")
            print(f"Avg Response Time: {stats.avg_response_time_ms:.0f}ms")
            print(f"Success Rate: {stats.success_rate:.1f}%")

            if result.documents:
                print(f"\n{'='*60}")
                print(f"Sample Documents (showing first 5)")
                print(f"{'='*60}")

                for i, doc in enumerate(result.documents[:5], 1):
                    print(f"\n{i}. {doc.title}")
                    print(f"   URL: {doc.url}")
                    print(f"   Type: {doc.document_type.value}")
                    if doc.publication_date:
                        print(f"   Date: {doc.publication_date.isoformat()}")
                    if doc.municipality:
                        print(f"   Municipality: {doc.municipality}")
                    if doc.description:
                        print(f"   Description: {doc.description[:100]}...")

                if len(result.documents) > 5:
                    print(f"\n... and {len(result.documents) - 5} more documents")

            if downloaded_content:
                print(f"\n{'='*60}")
                print(f"Downloaded Document")
                print(f"{'='*60}")
                print(f"Size: {len(downloaded_content)} bytes")

        return 0 if result.success else 1

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        return 1


def list_plugins_command(args) -> int:
    """
    List available plugins.

    Args:
        args: Command line arguments

    Returns:
        int: Exit code
    """
    plugins = list_plugins()

    if args.output == 'json':
        output = {
            'plugins': plugins,
            'count': len(plugins),
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nAvailable Plugins ({len(plugins)}):")
        print(f"{'='*60}")
        for plugin in plugins:
            info = plugin_info(plugin)
            if info:
                print(f"\n{plugin}")
                print(f"  Class: {info['class']}")
                if info['doc']:
                    # Print first line of docstring
                    first_line = info['doc'].strip().split('\n')[0]
                    print(f"  Description: {first_line}")

    return 0


def info_command(args) -> int:
    """
    Show plugin information.

    Args:
        args: Command line arguments

    Returns:
        int: Exit code
    """
    info = plugin_info(args.plugin)

    if not info:
        logger.error(f"Plugin not found: {args.plugin}")
        return 1

    if args.output == 'json':
        print(json.dumps(info, indent=2))
    else:
        print(f"\nPlugin Information: {args.plugin}")
        print(f"{'='*60}")
        print(f"Name: {info['name']}")
        print(f"Class: {info['class']}")
        print(f"Module: {info['module']}")
        print(f"\nDocumentation:")
        print(info['doc'])

    return 0


def main():
    """Main CLI entry point."""
    parser = setup_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to command handler
    if args.command == 'test':
        exit_code = asyncio.run(test_plugin(args))
    elif args.command == 'list':
        exit_code = list_plugins_command(args)
    elif args.command == 'info':
        exit_code = info_command(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        exit_code = 1

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
